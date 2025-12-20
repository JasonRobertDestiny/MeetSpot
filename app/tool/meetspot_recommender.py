import asyncio
import html
import json
import math
import os
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import aiohttp
from pydantic import Field

from app.logger import logger
from app.tool.base import BaseTool, ToolResult
from app.config import config

# LLM 智能评分（延迟导入以避免循环依赖）
_llm_instance = None

def _get_llm():
    """延迟加载 LLM 实例"""
    global _llm_instance
    if _llm_instance is None:
        try:
            from app.llm import LLM
            from app.config import config
            # 检查 API Key 是否已配置
            llm_config = config.llm.get("default", {})
            api_key = getattr(llm_config, "api_key", "") if hasattr(llm_config, "api_key") else llm_config.get("api_key", "")
            if not api_key:
                logger.info("LLM API Key 未配置，跳过 LLM 初始化")
                return None
            _llm_instance = LLM()
            logger.info(f"LLM 初始化成功，模型: {_llm_instance.model}, base_url: {_llm_instance.base_url[:30]}..." if _llm_instance.base_url else f"LLM 初始化成功，模型: {_llm_instance.model}")
        except Exception as e:
            logger.warning(f"LLM 初始化失败，智能评分不可用: {e}")
    return _llm_instance


class CafeRecommender(BaseTool):
    """场所推荐工具，基于多个地点计算最佳会面位置并推荐周边场所"""

    name: str = "place_recommender"
    description: str = """推荐适合多人会面的场所。
该工具基于多个地点的位置信息，计算最佳会面地点，并推荐附近的各类场所。
工具会生成包含地图和推荐信息的HTML页面，提供详细的场所信息、地理位置和交通建议。
可以搜索各种类型的场所，如咖啡馆、餐厅、商场、电影院、篮球场等。
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "locations": {
                "type": "array",
                "description": "(必填) 所有参与者的位置描述列表，每个元素为一个地点描述字符串，如['北京朝阳区望京宝星园', '海淀中关村地铁站']",
                "items": {"type": "string"},
            },
            "keywords": {
                "type": "string",
                "description": "(可选) 搜索关键词，如'咖啡馆'、'篮球场'、'电影院'、'商场'等。前端会将选择的场所类型（如“图书馆”）合并到此关键词中。",
                "default": "咖啡馆",
            },
            "place_type": {
                "type": "string",
                "description": "(可选) 场所类型编码，如'050000'(餐饮),'080116'(篮球场),'080601'(电影院),'060100'(商场)等，默认为空。注意：通常前端会将场所类型通过keywords参数传递。",
                "default": "",
            },
            "user_requirements": {
                "type": "string",
                "description": "(可选) 用户的额外需求，如'停车方便'，'环境安静'等",
                "default": "",
            },
        },
        "required": ["locations"],
    }

    # 高德地图API密钥
    api_key: str = Field(default="")

    # 缓存请求结果以减少API调用
    geocode_cache: Dict[str, Dict] = Field(default_factory=dict)
    poi_cache: Dict[str, List] = Field(default_factory=dict)

    # ========== 品牌特征知识库 ==========
    # 用于三层匹配算法的第二层：基于品牌特征的需求推断
    # 分值范围 0.0-1.0，>=0.7 视为满足需求
    BRAND_FEATURES: Dict[str, Dict[str, float]] = {
        # ========== 咖啡馆 (15个) ==========
        "星巴克": {"安静": 0.8, "WiFi": 1.0, "商务": 0.7, "停车": 0.3, "可以久坐": 0.9},
        "瑞幸": {"安静": 0.4, "WiFi": 0.7, "商务": 0.4, "停车": 0.3, "可以久坐": 0.5},
        "Costa": {"安静": 0.9, "WiFi": 1.0, "商务": 0.8, "停车": 0.4, "可以久坐": 0.9},
        "漫咖啡": {"安静": 0.9, "WiFi": 0.9, "商务": 0.6, "停车": 0.5, "可以久坐": 1.0},
        "太平洋咖啡": {"安静": 0.8, "WiFi": 0.9, "商务": 0.7, "停车": 0.4, "可以久坐": 0.8},
        "Manner": {"安静": 0.5, "WiFi": 0.6, "商务": 0.4, "停车": 0.2, "可以久坐": 0.3},
        "Seesaw": {"安静": 0.8, "WiFi": 0.9, "商务": 0.6, "停车": 0.3, "可以久坐": 0.8},
        "M Stand": {"安静": 0.7, "WiFi": 0.8, "商务": 0.5, "停车": 0.3, "可以久坐": 0.7},
        "Tims": {"安静": 0.6, "WiFi": 0.8, "商务": 0.5, "停车": 0.4, "可以久坐": 0.6},
        "上岛咖啡": {"安静": 0.9, "WiFi": 0.8, "商务": 0.8, "停车": 0.6, "可以久坐": 0.9, "包间": 0.7},
        "Zoo Coffee": {"安静": 0.7, "WiFi": 0.8, "商务": 0.5, "停车": 0.4, "可以久坐": 0.8, "适合儿童": 0.6},
        "猫屎咖啡": {"安静": 0.8, "WiFi": 0.8, "商务": 0.6, "停车": 0.4, "可以久坐": 0.8},
        "皮爷咖啡": {"安静": 0.7, "WiFi": 0.8, "商务": 0.5, "停车": 0.3, "可以久坐": 0.7},
        "咖世家": {"安静": 0.8, "WiFi": 0.9, "商务": 0.7, "停车": 0.4, "可以久坐": 0.8},
        "挪瓦咖啡": {"安静": 0.5, "WiFi": 0.6, "商务": 0.4, "停车": 0.2, "可以久坐": 0.4},
        # ========== 中餐厅 (15个) ==========
        "海底捞": {"包间": 0.9, "停车": 0.8, "安静": 0.2, "适合儿童": 0.9, "24小时营业": 0.3},
        "西贝": {"包间": 0.7, "停车": 0.6, "安静": 0.5, "适合儿童": 0.7},
        "外婆家": {"包间": 0.5, "停车": 0.5, "安静": 0.3, "适合儿童": 0.6},
        "绿茶": {"包间": 0.4, "停车": 0.5, "安静": 0.4, "适合儿童": 0.5},
        "小龙坎": {"包间": 0.6, "停车": 0.5, "安静": 0.2, "适合儿童": 0.4},
        "呷哺呷哺": {"包间": 0.0, "停车": 0.4, "安静": 0.3, "适合儿童": 0.5},
        "大龙燚": {"包间": 0.5, "停车": 0.5, "安静": 0.2, "适合儿童": 0.4},
        "眉州东坡": {"包间": 0.8, "停车": 0.7, "安静": 0.6, "适合儿童": 0.7, "商务": 0.7},
        "全聚德": {"包间": 0.9, "停车": 0.7, "安静": 0.6, "适合儿童": 0.6, "商务": 0.8},
        "大董": {"包间": 0.9, "停车": 0.8, "安静": 0.8, "商务": 0.9},
        "鼎泰丰": {"包间": 0.5, "停车": 0.6, "安静": 0.6, "适合儿童": 0.7},
        "南京大牌档": {"包间": 0.6, "停车": 0.5, "安静": 0.3, "适合儿童": 0.6},
        "九毛九": {"包间": 0.4, "停车": 0.5, "安静": 0.4, "适合儿童": 0.6},
        "太二酸菜鱼": {"包间": 0.0, "停车": 0.4, "安静": 0.3, "适合儿童": 0.4},
        "湘鄂情": {"包间": 0.8, "停车": 0.7, "安静": 0.5, "商务": 0.7},
        # ========== 西餐/快餐 (10个) ==========
        "麦当劳": {"停车": 0.5, "WiFi": 0.8, "适合儿童": 0.9, "24小时营业": 0.8},
        "肯德基": {"停车": 0.5, "WiFi": 0.7, "适合儿童": 0.9, "24小时营业": 0.6},
        "必胜客": {"包间": 0.3, "停车": 0.5, "适合儿童": 0.8, "安静": 0.5},
        "萨莉亚": {"停车": 0.4, "适合儿童": 0.7, "安静": 0.4},
        "汉堡王": {"停车": 0.4, "WiFi": 0.6, "适合儿童": 0.7},
        "赛百味": {"停车": 0.3, "WiFi": 0.5, "可以久坐": 0.4},
        "棒约翰": {"停车": 0.4, "适合儿童": 0.7, "包间": 0.2},
        "达美乐": {"停车": 0.3, "适合儿童": 0.6},
        "DQ": {"适合儿童": 0.9, "停车": 0.4},
        "哈根达斯": {"适合儿童": 0.7, "安静": 0.6, "可以久坐": 0.5},
        # ========== 奶茶/饮品 (8个) ==========
        "喜茶": {"安静": 0.4, "可以久坐": 0.5, "停车": 0.3},
        "奈雪的茶": {"安静": 0.5, "可以久坐": 0.6, "停车": 0.4, "WiFi": 0.6},
        "茶百道": {"安静": 0.3, "可以久坐": 0.3, "停车": 0.2},
        "一点点": {"安静": 0.2, "可以久坐": 0.2, "停车": 0.2},
        "蜜雪冰城": {"安静": 0.2, "可以久坐": 0.2, "停车": 0.2},
        "茶颜悦色": {"安静": 0.4, "可以久坐": 0.4, "停车": 0.3},
        "古茗": {"安静": 0.3, "可以久坐": 0.3, "停车": 0.2},
        "CoCo": {"安静": 0.3, "可以久坐": 0.3, "停车": 0.2},
        # ========== 场所类型默认特征 (以下划线开头) ==========
        "_图书馆": {"安静": 1.0, "WiFi": 0.9, "可以久坐": 1.0},
        "_书店": {"安静": 1.0, "可以久坐": 0.8, "WiFi": 0.5},
        "_商场": {"停车": 0.9, "交通": 0.8, "适合儿童": 0.7},
        "_酒店": {"安静": 0.9, "商务": 0.9, "停车": 0.8, "WiFi": 0.9, "包间": 0.8},
        "_电影院": {"停车": 0.7, "适合儿童": 0.6},
        "_KTV": {"包间": 1.0, "停车": 0.6, "24小时营业": 0.5},
        "_健身房": {"停车": 0.6, "WiFi": 0.5},
        "_网咖": {"WiFi": 1.0, "24小时营业": 0.8, "可以久坐": 0.9},
        "_便利店": {"24小时营业": 0.9},
    }

    PLACE_TYPE_CONFIG: Dict[str, Dict[str, str]] = {
        "咖啡馆": {
            "topic": "咖啡会",
            "icon_header": "bxs-coffee-togo",
            "icon_section": "bx-coffee",
            "icon_card": "bxs-coffee-alt",
            "map_legend": "咖啡馆",
            "noun_singular": "咖啡馆",
            "noun_plural": "咖啡馆",
            "theme_primary": "#9c6644", # 棕色系
            "theme_primary_light": "#c68b59",
            "theme_primary_dark": "#7f5539",
            "theme_secondary": "#c9ada7",
            "theme_light": "#f2e9e4",
            "theme_dark": "#22223b",
        },
        "图书馆": {
            "topic": "知书达理会",
            "icon_header": "bxs-book",
            "icon_section": "bx-book",
            "icon_card": "bxs-book-reader",
            "map_legend": "图书馆",
            "noun_singular": "图书馆",
            "noun_plural": "图书馆",
            "theme_primary": "#4a6fa5", # 蓝色系
            "theme_primary_light": "#6e8fc5",
            "theme_primary_dark": "#305182",
            "theme_secondary": "#9dc0e5",
            "theme_light": "#f0f5fa",
            "theme_dark": "#2c3e50",
        },
        "餐厅": {
            "topic": "美食汇",
            "icon_header": "bxs-restaurant",
            "icon_section": "bx-restaurant",
            "icon_card": "bxs-restaurant",
            "map_legend": "餐厅",
            "noun_singular": "餐厅",
            "noun_plural": "餐厅",
            "theme_primary": "#e74c3c", # 红色系
            "theme_primary_light": "#f1948a",
            "theme_primary_dark": "#c0392b",
            "theme_secondary": "#fadbd8",
            "theme_light": "#fef5e7",
            "theme_dark": "#34222e",
        },
        "商场": {
            "topic": "乐购汇",
            "icon_header": "bxs-shopping-bag",
            "icon_section": "bx-shopping-bag",
            "icon_card": "bxs-store-alt",
            "map_legend": "商场",
            "noun_singular": "商场",
            "noun_plural": "商场",
            "theme_primary": "#8e44ad", # 紫色系
            "theme_primary_light": "#af7ac5",
            "theme_primary_dark": "#6c3483",
            "theme_secondary": "#d7bde2",
            "theme_light": "#f4ecf7",
            "theme_dark": "#3b1f2b",
        },
        "公园": {
            "topic": "悠然汇",
            "icon_header": "bxs-tree",
            "icon_section": "bx-leaf",
            "icon_card": "bxs-florist",
            "map_legend": "公园",
            "noun_singular": "公园",
            "noun_plural": "公园",
            "theme_primary": "#27ae60", # 绿色系
            "theme_primary_light": "#58d68d",
            "theme_primary_dark": "#1e8449",
            "theme_secondary": "#a9dfbf",
            "theme_light": "#eafaf1",
            "theme_dark": "#1e3b20",
        },
        "电影院": {
            "topic": "光影汇",
            "icon_header": "bxs-film",
            "icon_section": "bx-film",
            "icon_card": "bxs-movie-play",
            "map_legend": "电影院",
            "noun_singular": "电影院",
            "noun_plural": "电影院",
            "theme_primary": "#34495e", # 深蓝灰色系
            "theme_primary_light": "#5d6d7e",
            "theme_primary_dark": "#2c3e50",
            "theme_secondary": "#aeb6bf",
            "theme_light": "#ebedef",
            "theme_dark": "#17202a",
        },
        "篮球场": {
            "topic": "篮球部落",
            "icon_header": "bxs-basketball",
            "icon_section": "bx-basketball",
            "icon_card": "bxs-basketball",
            "map_legend": "篮球场",
            "noun_singular": "篮球场",
            "noun_plural": "篮球场",
            "theme_primary": "#f39c12", # 橙色系
            "theme_primary_light": "#f8c471",
            "theme_primary_dark": "#d35400",
            "theme_secondary": "#fdebd0",
            "theme_light": "#fef9e7",
            "theme_dark": "#4a2303",
        },
        "健身房": {
            "topic": "健身汇",
            "icon_header": "bx-dumbbell",
            "icon_section": "bx-dumbbell",
            "icon_card": "bx-dumbbell",
            "map_legend": "健身房",
            "noun_singular": "健身房",
            "noun_plural": "健身房",
            "theme_primary": "#e67e22", # 活力橙色系
            "theme_primary_light": "#f39c12",
            "theme_primary_dark": "#d35400",
            "theme_secondary": "#fdebd0",
            "theme_light": "#fef9e7",
            "theme_dark": "#4a2c03",
        },
        "KTV": {
            "topic": "欢唱汇",
            "icon_header": "bxs-microphone",
            "icon_section": "bx-microphone",
            "icon_card": "bxs-microphone",
            "map_legend": "KTV",
            "noun_singular": "KTV",
            "noun_plural": "KTV",
            "theme_primary": "#FF1493", # 音乐粉色系
            "theme_primary_light": "#FF69B4",
            "theme_primary_dark": "#DC143C",
            "theme_secondary": "#FFB6C1",
            "theme_light": "#FFF0F5",
            "theme_dark": "#8B1538",
        },
        "博物馆": {
            "topic": "博古汇",
            "icon_header": "bxs-institution",
            "icon_section": "bx-institution",
            "icon_card": "bxs-institution",
            "map_legend": "博物馆",
            "noun_singular": "博物馆",
            "noun_plural": "博物馆",
            "theme_primary": "#DAA520", # 文化金色系
            "theme_primary_light": "#FFD700",
            "theme_primary_dark": "#B8860B",
            "theme_secondary": "#F0E68C",
            "theme_light": "#FFFACD",
            "theme_dark": "#8B7355",
        },
        "景点": {
            "topic": "游览汇",
            "icon_header": "bxs-landmark",
            "icon_section": "bx-landmark",
            "icon_card": "bxs-landmark",
            "map_legend": "景点",
            "noun_singular": "景点",
            "noun_plural": "景点",
            "theme_primary": "#17A2B8", # 旅游青色系
            "theme_primary_light": "#20C997",
            "theme_primary_dark": "#138496",
            "theme_secondary": "#7FDBDA",
            "theme_light": "#E0F7FA",
            "theme_dark": "#00695C",
        },
        "酒吧": {
            "topic": "夜宴汇",
            "icon_header": "bxs-drink",
            "icon_section": "bx-drink",
            "icon_card": "bxs-drink",
            "map_legend": "酒吧",
            "noun_singular": "酒吧",
            "noun_plural": "酒吧",
            "theme_primary": "#2C3E50", # 夜晚蓝色系
            "theme_primary_light": "#5D6D7E",
            "theme_primary_dark": "#1B2631",
            "theme_secondary": "#85929E",
            "theme_light": "#EBF5FB",
            "theme_dark": "#17202A",
        },
        "茶楼": {
            "topic": "茶韵汇",
            "icon_header": "bxs-coffee-bean",
            "icon_section": "bx-coffee-bean",
            "icon_card": "bxs-coffee-bean",
            "map_legend": "茶楼",
            "noun_singular": "茶楼",
            "noun_plural": "茶楼",
            "theme_primary": "#52796F", # 茶香绿色系
            "theme_primary_light": "#84A98C",
            "theme_primary_dark": "#354F52",
            "theme_secondary": "#CAD2C5",
            "theme_light": "#F7F9F7",
            "theme_dark": "#2F3E46",
        },
        "default": { # 默认主题颜色 (同咖啡馆)
            "topic": "会面点",
            "icon_header": "bxs-map-pin",
            "icon_section": "bx-map-pin",
            "icon_card": "bxs-location-plus",
            "map_legend": "场所",
            "noun_singular": "场所",
            "noun_plural": "场所",
            "theme_primary": "#9c6644",
            "theme_primary_light": "#c68b59",
            "theme_primary_dark": "#7f5539",
            "theme_secondary": "#c9ada7",
            "theme_light": "#f2e9e4",
            "theme_dark": "#22223b",
        }
    }

    def _get_place_config(self, primary_keyword: str) -> Dict[str, str]:
        """获取指定场所类型的显示配置"""
        return self.PLACE_TYPE_CONFIG.get(primary_keyword, self.PLACE_TYPE_CONFIG["default"])

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_city_dataset() -> List[Dict]:
        """从数据文件读取城市信息（带缓存）."""
        try:
            with open("data/cities.json", "r", encoding="utf-8") as fh:
                payload = json.load(fh)
                return payload.get("cities", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _extract_city_from_locations(self, locations: List[Dict]) -> str:
        """尝试从参与者地址中推断城市."""
        city_dataset = self._load_city_dataset()
        for loc in locations:
            address = " ".join(
                filter(
                    None,
                    [
                        loc.get("formatted_address", ""),
                        loc.get("name", ""),
                        loc.get("city", ""),
                    ],
                )
            )

            for city in city_dataset:
                name = city.get("name", "")
                name_en = city.get("name_en", "")
                if name and name in address:
                    return name
                if name_en and name_en.lower() in address.lower():
                    return name
        return locations[0].get("city", "未知城市") if locations else "未知城市"

    def _format_schema_payload(self, place: Dict, city_name: str) -> Dict:
        """构建LocalBusiness schema所需数据."""
        lng = lat = None
        location_str = place.get("location", "")
        if location_str and "," in location_str:
            lng_str, lat_str = location_str.split(",", 1)
            try:
                lng = float(lng_str)
                lat = float(lat_str)
            except ValueError:
                lng = lat = None

        biz_ext = place.get("biz_ext", {}) or {}
        return {
            "name": place.get("name", ""),
            "address": place.get("address", ""),
            "city": city_name,
            "lat": lat,
            "lng": lng,
            "rating": biz_ext.get("rating", 4.5),
            "review_count": biz_ext.get("review_count", 100),
            "price_range": biz_ext.get("cost", "¥¥"),
        }

    async def execute(
        self,
        locations: List[str],
        keywords: str = "咖啡馆",
        place_type: str = "",
        user_requirements: str = "",
        theme: str = "",  # 添加主题参数
        min_rating: float = 0.0,  # 最低评分筛选
        max_distance: int = 100000,  # 最大距离筛选(米)
        price_range: str = "",  # 价格区间筛选
    ) -> ToolResult:
        # 尝试从多个来源获取API key
        if not self.api_key:
            # 首先尝试从config对象获取
            if hasattr(config, "amap") and config.amap and hasattr(config.amap, "api_key"):
                self.api_key = config.amap.api_key
            # 如果config不可用，尝试从环境变量获取
            elif not self.api_key:
                import os
                self.api_key = os.getenv("AMAP_API_KEY", "")
        
        if not self.api_key:
            logger.error("高德地图API密钥未配置。请在config.toml中设置 amap.api_key 或设置环境变量 AMAP_API_KEY。")
            return ToolResult(output="推荐失败: 高德地图API密钥未配置。")

        try:
            coordinates = []
            location_info = []
            geocode_results = []  # 存储原始 geocode 结果用于后续分析

            # 并行地理编码 - 大幅提升性能
            async def geocode_with_delay(location: str, index: int):
                """带轻微延迟的地理编码，避免API限流"""
                if index > 0:
                    await asyncio.sleep(0.05 * index)  # 50ms递增延迟，比原来的500ms快10倍
                return await self._geocode(location)

            # 使用 asyncio.gather 并行执行所有地理编码请求
            geocode_tasks = [geocode_with_delay(loc, i) for i, loc in enumerate(locations)]
            geocode_raw_results = await asyncio.gather(*geocode_tasks, return_exceptions=True)

            # 处理结果并检查错误
            for i, (location, result) in enumerate(zip(locations, geocode_raw_results)):
                if isinstance(result, Exception):
                    logger.error(f"地理编码异常: {location} - {result}")
                    result = None

                if not result:
                    # 检查是否为大学简称但地理编码失败
                    enhanced_address = self._enhance_address(location)
                    if enhanced_address != location:
                        return ToolResult(output=f"无法找到地点: {location}\n\n识别为大学简称\n您输入的 '{location}' 可能是大学简称，但未能成功解析。\n\n建议尝试：\n完整名称：'{enhanced_address}'\n添加城市：'北京 {location}'、'上海 {location}'\n具体地址：'北京市海淀区{enhanced_address}'\n校区信息：如 '{location}本部'、'{location}新校区'")
                    else:
                        # 提供更详细的地址输入指导
                        suggestions = self._get_address_suggestions(location)
                        return ToolResult(output=f"无法找到地点: {location}\n\n地址解析失败\n系统无法识别您输入的地址，请检查以下几点：\n\n具体建议：\n{suggestions}\n\n标准地址格式示例：\n完整地址：'北京市海淀区中关村大街27号'\n知名地标：'北京大学'、'天安门广场'、'上海外滩'\n商圈区域：'三里屯'、'王府井'、'南京路步行街'\n交通枢纽：'北京南站'、'上海虹桥机场'\n\n常见错误避免：\n避免过于简短：'大学' -> '北京大学'\n避免拼写错误：'北大' -> '北京大学'\n避免模糊描述：'那个商场' -> '王府井百货大楼'\n\n如果仍有问题：\n检查网络连接是否正常\n尝试使用地址的官方全称\n确认地点确实存在且对外开放")

                geocode_results.append({
                    "original_location": location,
                    "result": result
                })

            # 智能城市推断：检测是否有地点被解析到完全不同的城市
            if len(geocode_results) > 1:
                geocode_results = await self._smart_city_inference(locations, geocode_results)

            # 处理最终的 geocode 结果
            for item in geocode_results:
                geocode_result = item["result"]
                location = item["original_location"]
                lng, lat = geocode_result["location"].split(",")
                coordinates.append((float(lng), float(lat)))
                location_info.append({
                    "name": location,
                    "formatted_address": geocode_result.get("formatted_address", location),
                    "location": geocode_result["location"],
                    "lng": float(lng),
                    "lat": float(lat),
                    "city": geocode_result.get("city", "")
                })

            if not coordinates:
                error_msg = "❌ 未能解析任何有效的地点位置。\n\n"
                error_msg += "🔍 **解析失败的地址：**\n"
                for location in locations:
                    error_msg += f"• {location}\n"
                    suggestions = self._get_address_suggestions(location)
                    if suggestions:
                        error_msg += f"  💡 建议：{suggestions}\n"
                error_msg += "\n"
                
                error_msg += "📍 **地址输入检查清单：**\n"
                error_msg += "• **拼写准确性**：确保地名、路名拼写无误\n"
                error_msg += "• **地理层级**：包含省市区信息，如 '北京市海淀区...'\n"
                error_msg += "• **地址完整性**：提供门牌号或具体位置描述\n"
                error_msg += "• **地点真实性**：确认地点确实存在且可被地图服务识别\n\n"
                error_msg += "💡 **推荐格式示例：**\n"
                error_msg += "• **完整地址**：'北京市海淀区中关村大街1号'\n"
                error_msg += "• **知名地标**：'北京大学'、'上海外滩'、'广州塔'\n"
                error_msg += "• **商圈/区域**：'三里屯'、'南京路步行街'、'春熙路'\n"
                error_msg += "• **交通枢纽**：'北京南站'、'上海虹桥机场'、'广州白云机场'\n\n"
                error_msg += "📝 **多地点输入说明：**\n"
                error_msg += "• **方式一**：在不同输入框中分别填写，如第一个框填'北京大学'，第二个框填'中关村'\n"
                error_msg += "• **方式二**：在一个输入框中用空格分隔，如'北京大学 中关村'（系统会自动拆分）\n"
                error_msg += "• **注意**：完整地址（包含'市'、'区'、'县'）不会被拆分，如'北京市海淀区'\n"
                return ToolResult(output=error_msg)

            center_point = self._calculate_center_point(coordinates)
            
            # 处理多个关键词的搜索
            keywords_list = [kw.strip() for kw in keywords.split() if kw.strip()]
            primary_keyword = keywords_list[0] if keywords_list else "咖啡馆"
            
            searched_places = []
            
            # 如果有多个关键词，使用并发搜索提高性能
            if len(keywords_list) > 1:
                logger.info(f"多场景并发搜索: {keywords_list}")
                
                # 创建并发搜索任务
                async def search_keyword(keyword):
                    logger.info(f"开始搜索场景: '{keyword}'")
                    places = await self._search_pois(
                        f"{center_point[0]},{center_point[1]}",
                        keyword,
                        radius=5000,
                        types=""
                    )
                    if places:
                        # 为每个场所添加来源标记
                        for place in places:
                            place['_source_keyword'] = keyword
                        logger.info(f"'{keyword}' 找到 {len(places)} 个结果")
                        return places
                    else:
                        logger.info(f"'{keyword}' 未找到结果")
                        return []
                
                # 并发执行所有搜索
                tasks = [search_keyword(keyword) for keyword in keywords_list]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 合并结果
                all_places = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"搜索 '{keywords_list[i]}' 时出错: {result}")
                    elif result:
                        all_places.extend(result)
                
                # 去重（基于场所名称和坐标位置，更宽松的去重策略）
                seen = set()
                unique_places = []
                for place in all_places:
                    # 使用名称和坐标进行去重，而不是地址（地址可能格式不同）
                    location = place.get('location', '')
                    name = place.get('name', '')
                    identifier = f"{name}_{location}"
                    
                    if identifier not in seen:
                        seen.add(identifier)
                        unique_places.append(place)
                
                searched_places = unique_places
                logger.info(f"多场景搜索完成，去重后共 {len(searched_places)} 个结果")
            else:
                # 单个关键词的传统搜索
                searched_places = await self._search_pois(
                    f"{center_point[0]},{center_point[1]}",
                    keywords, 
                    radius=5000,
                    types=place_type 
                )

            if not searched_places:
                logger.info(f"使用 keywords '{keywords}' 和 types '{place_type}' 未找到结果，尝试仅使用 keywords 进行搜索。")
                searched_places = await self._search_pois(
                    f"{center_point[0]},{center_point[1]}",
                    keywords,
                    radius=5000,
                    types="" 
                )
                if not searched_places:
                    # 生成智能提示信息
                    location_names = [loc['name'] for loc in location_info]
                    formatted_addresses = [loc['formatted_address'] for loc in location_info]
                    
                    # 检查是否有地址被解析到意外的城市
                    unexpected_locations = []
                    for i, (name, addr) in enumerate(zip(location_names, formatted_addresses)):
                        enhanced = self._enhance_address(name)
                        if enhanced != name:  # 是简称
                            # 检查解析结果是否包含预期的城市关键词
                            expected_cities = {
                                "北京大学": ["北京", "海淀"],
                                "清华大学": ["北京", "海淀"],
                                "上海交通大学": ["上海", "闵行"],
                                "复旦大学": ["上海", "杨浦"],
                                "浙江大学": ["杭州", "西湖"],
                                "中山大学": ["广州", "海珠"],
                                "华中科技大学": ["武汉", "洪山"]
                            }
                            
                            if enhanced in expected_cities:
                                expected_city_keywords = expected_cities[enhanced]
                                if not any(keyword in addr for keyword in expected_city_keywords):
                                    unexpected_locations.append((name, enhanced, addr))
                    
                    error_msg = f"❌ 在计算的中心点附近找不到与 '{keywords}' 相关的场所。\n\n"
                    
                    if unexpected_locations:
                        error_msg += "🔍 **可能的问题分析：**\n"
                        for orig_name, enhanced_name, actual_addr in unexpected_locations:
                            error_msg += f"• '{orig_name}' 被解析到：{actual_addr}\n"
                            error_msg += f"  这可能不是您想要的 {enhanced_name}\n"
                        
                        error_msg += "\n💡 **建议解决方案：**\n"
                        error_msg += "• 使用完整的大学名称，如 '北京大学'、'上海交通大学'\n"
                        error_msg += "• 添加城市信息，如 '北京 清华大学'、'上海 复旦大学'\n"
                        error_msg += "• 使用具体的校区地址，如 '北京市海淀区清华大学'\n"
                    else:
                        # 提供更具体的建议
                        center_lng, center_lat = center_point
                        error_msg += "🔍 **当前搜索信息：**\n"
                        error_msg += f"• 搜索关键词：'{keywords}'\n"
                        error_msg += f"• 搜索中心点：({center_lng:.4f}, {center_lat:.4f})\n"
                        error_msg += f"• 搜索半径：5公里\n\n"
                        
                        error_msg += "💡 **建议尝试：**\n"
                        error_msg += "• **更换关键词**：尝试 '餐厅'、'商场'、'酒店'、'银行' 等\n"
                        error_msg += "• **使用更具体的地址**：请输入完整详细的地址信息\n"
                        error_msg += "  - 完整地址：'北京市朝阳区建国门外大街1号'\n"
                        error_msg += "  - 知名地标：'北京大学'、'天安门广场'、'上海外滩'\n"
                        error_msg += "  - 商圈区域：'三里屯太古里'、'王府井步行街'\n"
                        error_msg += "  - 交通枢纽：'北京南站'、'首都国际机场T3航站楼'\n"
                        error_msg += "• **避免模糊地址**：避免使用 '附近'、'那边'、'市中心' 等模糊描述\n"
                        error_msg += "• **检查拼写准确性**：确保地名、路名拼写正确无误\n"
                        error_msg += "• **尝试附近知名地标**：如果当前位置偏僻，选择附近的大型商场、地铁站等\n\n"
                        error_msg += "📝 **正确的地址输入格式：**\n"
                        error_msg += "• **多个地点请分别输入**：在不同的输入框中分别填写每个地点\n"
                        error_msg += "• **或用空格分隔**：如 '北京大学 中关村' 会被自动识别为两个地点\n"
                        error_msg += "• **完整地址示例**：'北京市海淀区北京大学' 和 '北京市海淀区中关村大街'\n"
                        error_msg += "• **地标名称示例**：'北京大学' 和 '中关村'\n"
                    
                    return ToolResult(output=error_msg)

            recommended_places = self._rank_places(
                searched_places, center_point, user_requirements, keywords,
                min_rating=min_rating, max_distance=max_distance, price_range=price_range
            )

            html_path = await self._generate_html_page(
                location_info,
                recommended_places,
                center_point,
                user_requirements,
                keywords,
                theme  # 添加主题参数
            )
            result_text = self._format_result_text(location_info, recommended_places, html_path, keywords) 
            return ToolResult(output=result_text)

        except Exception as e:
            logger.exception(f"场所推荐过程中发生错误: {str(e)}") 
            return ToolResult(output=f"推荐失败: {str(e)}")

    def _enhance_address(self, address: str) -> str:
        """智能地址增强 - 为常见简称添加更准确的搜索词，包含城市信息以避免歧义"""
        # 大学简称映射，包含城市信息以提高准确性
        university_mapping = {
            "北大": "北京市海淀区北京大学",
            "清华": "北京市海淀区清华大学", 
            "上交": "上海市闵行区上海交通大学",
            "复旦": "上海市杨浦区复旦大学",
            "浙大": "杭州市西湖区浙江大学",
            "南大": "南京市鼓楼区南京大学",
            "中大": "广州市海珠区中山大学",
            "华科": "武汉市洪山区华中科技大学",
            "西交": "西安市碑林区西安交通大学",
            "哈工大": "哈尔滨市南岗区哈尔滨工业大学",
            "中科大": "合肥市包河区中国科学技术大学",
            "人大": "北京市海淀区中国人民大学",
            "北师大": "北京市海淀区北京师范大学",
            "华师大": "上海市普陀区华东师范大学",
            "北理工": "北京市海淀区北京理工大学",
            "北航": "北京市海淀区北京航空航天大学",
            "同济": "上海市杨浦区同济大学",
            "东南": "南京市玄武区东南大学",
            "天大": "天津市南开区天津大学",
            "南开": "天津市南开区南开大学",
            "厦大": "厦门市思明区厦门大学",
            "山大": "济南市历城区山东大学",
            "川大": "成都市武侯区四川大学",
            "重大": "重庆市沙坪坝区重庆大学",
            "西大": "西安市碑林区西北大学",
            "兰大": "兰州市城关区兰州大学",
            "大连理工": "大连市甘井子区大连理工大学",
            "东北大学": "沈阳市和平区东北大学",
            "吉大": "长春市朝阳区吉林大学",
            "华南理工": "广州市天河区华南理工大学",
            "电子科大": "成都市郫都区电子科技大学",
            "西工大": "西安市碑林区西北工业大学",
            "中南": "长沙市岳麓区中南大学",
            "湖大": "长沙市岳麓区湖南大学",
            "华中师大": "武汉市洪山区华中师范大学",
            "西南": "重庆市北碚区西南大学",
            "暨大": "广州市天河区暨南大学",
            "华工": "广州市天河区华南理工大学",
            "中财": "北京市海淀区中央财经大学",
            "对外经贸": "北京市朝阳区对外经济贸易大学",
            "央美": "北京市朝阳区中央美术学院",
            "北影": "北京市海淀区北京电影学院",
            "中戏": "北京市东城区中央戏剧学院",
            "上戏": "上海市静安区上海戏剧学院",
            "中音": "北京市西城区中央音乐学院",
            "上音": "上海市徐汇区上海音乐学院"
        }
        
        # 检查是否为大学简称
        if address in university_mapping:
            enhanced = university_mapping[address]
            logger.info(f"地址增强: '{address}' -> '{enhanced}'")
            return enhanced
        
        return address

    def _get_address_suggestions(self, address: str) -> str:
        """根据输入的地址提供智能建议"""
        suggestions = []
        
        # 检查是否包含常见的模糊词汇
        vague_terms = {
            "大学": "**请输入完整大学名称**，如 '北京大学'、'清华大学'、'复旦大学'",
            "学校": "**请输入具体学校全名**，如 '北京市第一中学'、'上海交通大学附属中学'",
            "医院": "**请输入完整医院名称**，如 '北京协和医院'、'上海华山医院'",
            "商场": "**请输入具体商场名称**，如 '王府井百货大楼'、'上海环球港'",
            "火车站": "**请输入完整站名**，如 '北京站'、'上海虹桥站'、'广州南站'",
            "机场": "**请输入完整机场名称**，如 '北京首都国际机场'、'上海浦东国际机场'",
            "公园": "**请输入具体公园名称**，如 '颐和园'、'中山公园'、'西湖公园'",
            "广场": "**请输入具体广场名称**，如 '天安门广场'、'人民广场'",
            "地铁站": "**请输入完整地铁站名**，如 '中关村地铁站'、'人民广场地铁站'",
            "购物中心": "**请输入具体购物中心名称**，如 '北京apm'、'上海iapm'"
        }
        
        for term, suggestion in vague_terms.items():
            if term in address:
                suggestions.append(f"• {suggestion}")
        
        # 检查是否只是城市名
        major_cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "西安", "天津"]
        if address in major_cities:
            suggestions.append(f"• **城市名过于宽泛**，请添加具体区域，如 '{address}市海淀区中关村'")
            suggestions.append(f"• **或使用知名地标**，如 '{address}大学'、'{address}火车站'、'{address}机场'")
            suggestions.append(f"• **推荐格式**：'{address}市 + 区县 + 街道/地标'，如 '{address}市朝阳区三里屯'")
        
        # 检查长度
        if len(address) <= 2:
            suggestions.append("• **地址过于简短**，请提供更详细的信息")
            suggestions.append("• **标准格式**：'省市 + 区县 + 具体地点'，如 '北京市海淀区中关村大街'")
            suggestions.append("• **或使用完整地标名**：如 '北京大学'、'天安门广场'、'上海外滩'")
        elif len(address) <= 4:
            suggestions.append("• **地址信息不够具体**，建议添加更多细节")
            suggestions.append("• **如果是地标**：请使用完整名称，如 '北京大学' 而非 '北大'")
            suggestions.append("• **如果是地址**：请添加区县信息，如 '海淀区' + 您的地址")
        
        # 通用建议
        if not suggestions:
            suggestions.extend([
                "• **请输入具体地址**：如 '北京市海淀区中关村大街1号'",
                "• **使用知名地标**：如 '北京大学'、'天安门广场'、'上海外滩'",
                "• **添加省市区信息**：如 '北京市朝阳区三里屯'",
                "• **使用完整建筑名**：如 '王府井百货大楼'、'北京协和医院'",
                "• **检查拼写准确性**：确保地名无错别字",
                "• **尝试官方全称**：避免使用简称或昵称"
            ])
        else:
            # 如果有特定建议，添加通用的具体地址要求
            suggestions.insert(0, "• **请输入更具体的地址信息**")
        
        # 添加多地点输入说明
        suggestions.append("")
        suggestions.append("📝 **多地点输入提示：**")
        suggestions.append("• 可在一个输入框中用空格分隔多个地点，如 '北京大学 中关村'")
        suggestions.append("• 或在不同输入框中分别填写每个地点")
        suggestions.append("• 完整地址（含'市'、'区'、'县'）不会被自动拆分")
        
        return "\n".join(suggestions)

    async def _geocode(self, address: str) -> Optional[Dict[str, Any]]:
        if address in self.geocode_cache:
            return self.geocode_cache[address]
        
        # 确保API密钥已设置
        if not self.api_key:
            if hasattr(config, "amap") and config.amap and hasattr(config.amap, "api_key"):
                self.api_key = config.amap.api_key
            else:
                logger.error("高德地图API密钥未配置")
                return None
        
        # 智能地址增强
        enhanced_address = self._enhance_address(address)
        
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {"key": self.api_key, "address": enhanced_address, "output": "json"}
        
        # 重试机制，最多重试3次（优化延迟以提升性能）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 首次请求无延迟，重试时添加较短延迟
                if attempt > 0:
                    await asyncio.sleep(0.2 * attempt)  # 200ms递增延迟（优化：原为1s）

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status != 200:
                            logger.error(f"高德地图API地理编码请求失败: {response.status}, 地址: {address}, 尝试: {attempt + 1}")
                            if attempt == max_retries - 1:
                                return None
                            continue

                        data = await response.json()

                        # 检查API限制错误
                        if data.get("info") == "CUQPS_HAS_EXCEEDED_THE_LIMIT":
                            logger.warning(f"API并发限制超出，地址: {address}, 尝试: {attempt + 1}, 等待后重试")
                            if attempt == max_retries - 1:
                                logger.error(f"地理编码失败: API并发限制超出，地址: {address}")
                                return None
                            await asyncio.sleep(0.5 * (attempt + 1))  # 500ms延迟（优化：原为2s）
                            continue

                        if data["status"] != "1" or not data["geocodes"]:
                            logger.error(f"地理编码失败: {data.get('info', '未知错误')}, 地址: {address}")
                            return None

                        result = data["geocodes"][0]
                        self.geocode_cache[address] = result  # 使用原始地址作为缓存键
                        return result

            except Exception as e:
                logger.error(f"地理编码请求异常: {str(e)}, 地址: {address}, 尝试: {attempt + 1}")
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep(0.2 * (attempt + 1))  # 200ms递增延迟（优化：原为1s）
        
        return None

    async def _smart_city_inference(
        self,
        original_locations: List[str],
        geocode_results: List[Dict]
    ) -> List[Dict]:
        """智能城市推断：检测并修正被解析到错误城市的地点

        当用户输入简短地名（如"国贸"）时，高德API可能将其解析到全国任何同名地点。
        此方法检测这种情况，并尝试用其他地点的城市信息重新解析。
        """
        if len(geocode_results) < 2:
            return geocode_results

        # 提取所有地点的城市和坐标
        cities = []
        coords = []
        for item in geocode_results:
            result = item["result"]
            city = result.get("city", "") or result.get("province", "")
            cities.append(city)
            lng, lat = result["location"].split(",")
            coords.append((float(lng), float(lat)))

        # 找出主流城市（出现次数最多的城市）
        from collections import Counter
        city_counts = Counter(cities)
        if not city_counts:
            return geocode_results

        main_city, main_count = city_counts.most_common(1)[0]

        # 如果所有地点都在同一城市，无需修正
        if main_count == len(cities):
            return geocode_results

        # 检测异常地点：距离其他地点过远（超过500公里）
        updated_results = []
        for i, item in enumerate(geocode_results):
            result = item["result"]
            location = item["original_location"]
            current_city = cities[i]

            # 计算与其他地点的平均距离
            if len(coords) > 1:
                other_coords = [c for j, c in enumerate(coords) if j != i]
                avg_distance = sum(
                    self._calculate_distance(coords[i], c) for c in other_coords
                ) / len(other_coords)

                # 如果当前地点距离其他地点平均超过100公里，且城市不同，尝试重新解析
                if avg_distance > 100000 and current_city != main_city:  # 100km = 100000m
                    logger.warning(
                        f"检测到地点 '{location}' 被解析到远离其他地点的城市 "
                        f"({current_city})，尝试用 {main_city} 重新解析"
                    )

                    # 尝试用主流城市名作为前缀重新解析
                    new_address = f"{main_city}{location}"
                    new_result = await self._geocode(new_address)

                    if new_result:
                        new_lng, new_lat = new_result["location"].split(",")
                        new_coord = (float(new_lng), float(new_lat))
                        # 检查新结果是否更合理（距离其他地点更近）
                        new_avg_distance = sum(
                            self._calculate_distance(new_coord, c) for c in other_coords
                        ) / len(other_coords)

                        if new_avg_distance < avg_distance:
                            logger.info(
                                f"成功将 '{location}' 重新解析为 {new_result.get('formatted_address')}"
                            )
                            updated_results.append({
                                "original_location": location,
                                "result": new_result
                            })
                            continue

            updated_results.append(item)

        return updated_results

    def _calculate_center_point(self, coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
        """计算多个坐标点的中心点（使用球面几何）"""
        if not coordinates:
            raise ValueError("至少需要一个坐标来计算中心点。")

        if len(coordinates) == 1:
            return coordinates[0]

        # 对于两个点，使用球面中点计算
        if len(coordinates) == 2:
            lat1, lng1 = math.radians(coordinates[0][1]), math.radians(coordinates[0][0])
            lat2, lng2 = math.radians(coordinates[1][1]), math.radians(coordinates[1][0])

            dLng = lng2 - lng1

            Bx = math.cos(lat2) * math.cos(dLng)
            By = math.cos(lat2) * math.sin(dLng)

            lat3 = math.atan2(math.sin(lat1) + math.sin(lat2),
                              math.sqrt((math.cos(lat1) + Bx) * (math.cos(lat1) + Bx) + By * By))
            lng3 = lng1 + math.atan2(By, math.cos(lat1) + Bx)

            return (math.degrees(lng3), math.degrees(lat3))

        # 对于多个点，使用简单平均（可以进一步优化）
        avg_lng = sum(lng for lng, _ in coordinates) / len(coordinates)
        avg_lat = sum(lat for _, lat in coordinates) / len(coordinates)
        return (avg_lng, avg_lat)

    async def _calculate_smart_center(
        self,
        coordinates: List[Tuple[float, float]],
        keywords: str = "咖啡馆"
    ) -> Tuple[Tuple[float, float], Dict]:
        """智能中心点算法 - 考虑 POI 密度、交通便利性和公平性

        算法步骤：
        1. 计算几何中心作为基准点
        2. 在基准点周围生成候选点网格
        3. 评估每个候选点：POI 密度 + 交通便利性 + 公平性
        4. 返回最优中心点

        Returns:
            (最优中心点坐标, 评估详情)
        """
        logger.info("使用智能中心点算法")

        # 1. 计算几何中心
        geo_center = self._calculate_center_point(coordinates)
        logger.info(f"几何中心: {geo_center}")

        # 2. 生成候选点网格（在几何中心周围 1.5km 范围内）
        candidates = self._generate_candidate_points(geo_center, radius_km=1.5, grid_size=3)
        candidates.insert(0, geo_center)  # 几何中心作为第一个候选

        logger.info(f"生成了 {len(candidates)} 个候选中心点")

        # 3. 评估每个候选点
        best_candidate = geo_center
        best_score = -1
        evaluation_results = []

        for candidate in candidates:
            score, details = await self._evaluate_center_candidate(
                candidate, coordinates, keywords
            )
            evaluation_results.append({
                "point": candidate,
                "score": score,
                "details": details
            })

            if score > best_score:
                best_score = score
                best_candidate = candidate

        # 排序结果
        evaluation_results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"最优中心点: {best_candidate}, 评分: {best_score:.1f}")

        return best_candidate, {
            "geo_center": geo_center,
            "best_candidate": best_candidate,
            "best_score": best_score,
            "all_candidates": evaluation_results[:5]  # 返回前5个
        }

    def _generate_candidate_points(
        self,
        center: Tuple[float, float],
        radius_km: float = 1.5,
        grid_size: int = 3
    ) -> List[Tuple[float, float]]:
        """在中心点周围生成候选点网格

        Args:
            center: 中心点坐标 (lng, lat)
            radius_km: 搜索半径（公里）
            grid_size: 网格大小（每边的点数，不含中心）
        """
        candidates = []
        lng, lat = center

        # 经纬度偏移量（粗略计算）
        # 纬度1度 ≈ 111km，经度1度 ≈ 111km * cos(lat)
        lat_offset = radius_km / 111.0
        lng_offset = radius_km / (111.0 * math.cos(math.radians(lat)))

        step_lat = lat_offset / grid_size
        step_lng = lng_offset / grid_size

        for i in range(-grid_size, grid_size + 1):
            for j in range(-grid_size, grid_size + 1):
                if i == 0 and j == 0:
                    continue  # 跳过中心点
                new_lng = lng + j * step_lng
                new_lat = lat + i * step_lat
                candidates.append((new_lng, new_lat))

        return candidates

    async def _evaluate_center_candidate(
        self,
        candidate: Tuple[float, float],
        participant_coords: List[Tuple[float, float]],
        keywords: str
    ) -> Tuple[float, Dict]:
        """评估候选中心点的质量

        评分维度（满分100）：
        - POI 密度: 40分 - 周边是否有足够的目标场所
        - 交通便利性: 30分 - 是否靠近地铁站/公交站
        - 公平性: 30分 - 对所有参与者是否公平（最小化最大距离）
        """
        lng, lat = candidate
        location_str = f"{lng},{lat}"

        scores = {
            "poi_density": 0,
            "transit": 0,
            "fairness": 0
        }
        details = {}

        # 1. POI 密度评分（40分）
        try:
            # 搜索目标场所
            pois = await self._search_pois(
                location=location_str,
                keywords=keywords,
                radius=1500,
                offset=10
            )
            poi_count = len(pois)

            # 评分：0个=0分，5个=20分，10个=40分
            scores["poi_density"] = min(40, poi_count * 4)
            details["poi_count"] = poi_count

        except Exception as e:
            logger.debug(f"POI 搜索失败: {e}")
            scores["poi_density"] = 10  # 给个基础分

        # 2. 交通便利性评分（30分）
        try:
            # 搜索地铁站
            transit_pois = await self._search_pois(
                location=location_str,
                keywords="地铁站",
                radius=1000,
                offset=5
            )
            transit_count = len(transit_pois)

            # 有地铁站得高分
            if transit_count >= 2:
                scores["transit"] = 30
            elif transit_count == 1:
                scores["transit"] = 20
            else:
                # 搜索公交站
                bus_pois = await self._search_pois(
                    location=location_str,
                    keywords="公交站",
                    radius=500,
                    offset=5
                )
                scores["transit"] = min(15, len(bus_pois) * 5)

            details["transit_count"] = transit_count

        except Exception as e:
            logger.debug(f"交通搜索失败: {e}")
            scores["transit"] = 10

        # 3. 公平性评分（30分）
        distances = []
        for coord in participant_coords:
            dist = self._calculate_distance(candidate, coord)
            distances.append(dist)

        max_distance = max(distances) if distances else 0
        avg_distance = sum(distances) / len(distances) if distances else 0

        # 最大距离越小越好，基于 3km 作为基准
        # max_dist <= 1km: 30分, 2km: 20分, 3km: 10分, >3km: 5分
        if max_distance <= 1000:
            scores["fairness"] = 30
        elif max_distance <= 2000:
            scores["fairness"] = 25 - (max_distance - 1000) / 200
        elif max_distance <= 3000:
            scores["fairness"] = 15 - (max_distance - 2000) / 200
        else:
            scores["fairness"] = max(5, 10 - (max_distance - 3000) / 500)

        details["max_distance"] = max_distance
        details["avg_distance"] = avg_distance
        details["distances"] = distances

        total_score = sum(scores.values())
        details["scores"] = scores

        return total_score, details

    async def _search_pois(
        self,
        location: str,
        keywords: str,
        radius: int = 2000,
        types: str = "", 
        offset: int = 20
    ) -> List[Dict]:
        cache_key = f"{location}_{keywords}_{radius}_{types}"
        if cache_key in self.poi_cache:
            return self.poi_cache[cache_key]
        url = "https://restapi.amap.com/v3/place/around"
        params = {
            "key": self.api_key,
            "location": location,
            "keywords": keywords,
            "radius": radius,
            "offset": offset,
            "page": 1,
            "extensions": "all"
        }
        if types: 
            params["types"] = types

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"高德地图POI搜索失败: {response.status}, 参数: {params}")
                    return []
                data = await response.json()
                if data["status"] != "1":
                    logger.error(f"POI搜索API返回错误: {data.get('info', '未知错误')}, 参数: {params}")
                    return []
                pois = data.get("pois", [])
                self.poi_cache[cache_key] = pois
                return pois

    # ========== V2 多维度评分系统 ==========

    def _calculate_base_score(self, place: Dict) -> Tuple[float, float]:
        """计算基础评分 (满分30分)

        Returns:
            (score, raw_rating): 评分和原始rating值
        """
        biz_ext = place.get("biz_ext", {}) or {}
        rating_str = biz_ext.get("rating", "0") or "0"
        try:
            rating = float(rating_str)
        except (ValueError, TypeError):
            rating = 0

        # 无评分场所使用默认3.5分
        if rating == 0:
            rating = 3.5
            place["_has_rating"] = False
        else:
            place["_has_rating"] = True

        # 评分归一化到30分 (rating范围1-5)
        score = min(rating, 5) * 6
        return score, rating

    def _calculate_popularity_score(self, place: Dict) -> Tuple[float, int, int]:
        """计算热度分 (满分20分)

        基于评论数和图片数
        Returns:
            (score, review_count, photo_count): 热度分和原始数据
        """
        biz_ext = place.get("biz_ext", {}) or {}

        # 评论数
        review_count_str = biz_ext.get("review_count", "0") or "0"
        try:
            review_count = int(review_count_str)
        except (ValueError, TypeError):
            review_count = 0

        # 图片数 (高德API的photos字段)
        photos = place.get("photos", []) or []
        photo_count = len(photos) if isinstance(photos, list) else 0

        # 对数计算避免大数压倒一切
        # log10(100) = 2, log10(1000) = 3
        review_score = math.log10(review_count + 1) * 5 if review_count > 0 else 0
        photo_score = min(photo_count * 2, 6)  # 最多3张图贡献6分

        score = min(20, review_score + photo_score)
        return score, review_count, photo_count

    def _calculate_distance_score_v2(
        self,
        place: Dict,
        center_point: Tuple[float, float]
    ) -> Tuple[float, float]:
        """计算距离分 (满分25分) - 非线性衰减

        Returns:
            (score, distance): 距离分和实际距离(米)
        """
        location = place.get("location", "")
        if not location or "," not in location:
            return 0, float('inf')

        try:
            lng_str, lat_str = location.split(",")
            place_lng, place_lat = float(lng_str), float(lat_str)
        except (ValueError, TypeError):
            return 0, float('inf')

        distance = self._calculate_distance(center_point, (place_lng, place_lat))
        place["_distance"] = distance

        # 非线性衰减：500米内满分，之后快速衰减
        # 使用1.5次幂衰减曲线
        if distance <= 500:
            score = 25
        elif distance <= 2500:
            # (1 - (distance/2500)^1.5) * 25
            ratio = (distance - 500) / 2000  # 归一化到0-1
            decay = ratio ** 1.5
            score = 25 * (1 - decay * 0.8)  # 最低保留20%
        else:
            score = 5  # 超远距离给最低分

        return score, distance

    def _calculate_scenario_match_score(
        self,
        place: Dict,
        keywords: str
    ) -> Tuple[float, str]:
        """计算场景匹配分 (满分15分)

        Returns:
            (score, matched_keyword): 场景分和匹配的关键词
        """
        source_keyword = place.get('_source_keyword', '')

        if source_keyword and source_keyword in keywords:
            return 15, source_keyword

        # 部分匹配：检查type字段
        place_type = place.get("type", "")
        keywords_list = keywords.replace("、", " ").split()

        for kw in keywords_list:
            if kw in place_type:
                return 8, kw

        return 0, ""

    def _calculate_requirement_score(
        self,
        place: Dict,
        user_requirements: str
    ) -> Tuple[float, List[str], Dict[str, str]]:
        """计算需求匹配分 (满分10分) - 三层匹配算法

        三层匹配机制：
        - Layer 1: POI标签硬匹配 (高置信度 high, +4分)
        - Layer 2: 品牌特征匹配 (中置信度 medium, +2分)
        - Layer 3: 类型推断匹配 (低置信度 low, +1分)

        Returns:
            (score, matched_requirements, confidence_map):
            需求分、匹配的需求列表、置信度字典
        """
        if not user_requirements:
            return 0, [], {}

        # 需求规范化映射（将各种表达方式统一）
        requirement_aliases = {
            "停车": ["停车", "车位", "停车场", "免费停车", "方便停车", "停车方便"],
            "安静": ["安静", "环境好", "氛围", "静", "舒适", "环境安静"],
            "商务": ["商务", "会议", "办公", "谈事", "工作"],
            "交通": ["交通", "地铁", "公交", "方便", "交通便利"],
            "包间": ["包间", "私密", "独立", "包厢", "有包间"],
            "WiFi": ["wifi", "无线", "网络", "上网", "免费wifi"],
            "可以久坐": ["久坐", "可以久坐", "坐着办公", "长时间"],
            "适合儿童": ["儿童", "带娃", "亲子", "小孩", "适合儿童"],
            "24小时营业": ["24小时", "通宵", "夜间", "凌晨"],
        }

        # POI标签匹配规则（Layer 1）
        poi_match_rules = {
            "停车": {
                "check_fields": ["tag", "parking_type", "navi_poiid"],
                "match_values": ["停车", "车位", "免费停车", "parking"]
            },
            "安静": {
                "check_fields": ["tag"],
                "match_values": ["安静", "环境", "氛围", "舒适", "优雅"]
            },
            "商务": {
                "check_fields": ["tag", "type"],
                "match_values": ["商务", "会议", "办公", "商务区"]
            },
            "交通": {
                "check_fields": ["tag", "address"],
                "match_values": ["地铁", "公交", "站", "枢纽"]
            },
            "包间": {
                "check_fields": ["tag"],
                "match_values": ["包间", "包厢", "私密", "独立房间"]
            },
            "WiFi": {
                "check_fields": ["tag"],
                "match_values": ["wifi", "无线", "免费WiFi", "网络"]
            },
        }

        # 识别用户需求
        user_reqs = set()
        user_requirements_lower = user_requirements.lower()
        for req_name, aliases in requirement_aliases.items():
            for alias in aliases:
                if alias.lower() in user_requirements_lower:
                    user_reqs.add(req_name)
                    break

        if not user_reqs:
            return 0, [], {}

        matched = []
        confidence_map = {}  # 需求 -> 置信度 (high/medium/low)
        total_score = 0
        place_name = place.get("name", "")
        place_type = place.get("type", "")

        # ========== Layer 1: POI标签硬匹配（高置信度）==========
        for req_name in user_reqs:
            if req_name in matched:
                continue
            if req_name not in poi_match_rules:
                continue
            rule = poi_match_rules[req_name]
            for field in rule["check_fields"]:
                field_value = str(place.get(field, "")).lower()
                if any(mv.lower() in field_value for mv in rule["match_values"]):
                    matched.append(req_name)
                    confidence_map[req_name] = "high"
                    total_score += 4  # 高置信度 +4分
                    break

        # ========== Layer 2: 品牌特征匹配（中置信度）==========
        for brand, features in self.BRAND_FEATURES.items():
            if brand.startswith("_"):
                continue  # 跳过类型默认值
            if brand in place_name:
                for req_name in user_reqs:
                    if req_name in matched:
                        continue
                    score = features.get(req_name, 0)
                    if score >= 0.7:  # 0.7以上视为满足
                        matched.append(req_name)
                        confidence_map[req_name] = "medium"
                        total_score += 2  # 中置信度 +2分
                break  # 只匹配第一个品牌

        # ========== Layer 3: 类型推断匹配（低置信度）==========
        for type_key, features in self.BRAND_FEATURES.items():
            if not type_key.startswith("_"):
                continue  # 只处理类型默认值
            type_name = type_key[1:]  # 去掉下划线前缀
            if type_name in place_type or type_name in place_name:
                for req_name in user_reqs:
                    if req_name in matched:
                        continue
                    score = features.get(req_name, 0)
                    if score >= 0.8:  # 类型推断需要更高阈值
                        matched.append(req_name)
                        confidence_map[req_name] = "low"
                        total_score += 1  # 低置信度 +1分
                break  # 只匹配第一个类型

        return min(10, total_score), matched, confidence_map

    def _apply_diversity_adjustment(
        self,
        places: List[Dict]
    ) -> List[Dict]:
        """应用多样性调整

        - 同名连锁店惩罚
        - 确保价格区间多样性
        """
        # 统计店名出现次数
        name_counts = {}
        for place in places:
            name = place.get("name", "")
            # 提取品牌名（去掉括号内容和分店信息）
            brand_name = name.split("(")[0].split("（")[0]
            brand_name = brand_name.replace("店", "").replace("分店", "")
            name_counts[brand_name] = name_counts.get(brand_name, 0) + 1

        # 应用惩罚
        seen_brands = {}
        for place in places:
            name = place.get("name", "")
            brand_name = name.split("(")[0].split("（")[0].replace("店", "").replace("分店", "")

            if name_counts.get(brand_name, 0) > 1:
                seen_count = seen_brands.get(brand_name, 0)
                if seen_count > 0:
                    # 第二家及以后的同品牌店铺扣分
                    penalty = min(15, seen_count * 5)
                    place["_score"] = place.get("_score", 0) - penalty
                    place["_diversity_penalty"] = penalty
                seen_brands[brand_name] = seen_count + 1

        return places

    def _generate_recommendation_reason(
        self,
        place: Dict,
        all_places: List[Dict]
    ) -> str:
        """生成推荐理由

        基于场所在各维度的表现生成个性化推荐理由
        """
        reasons = []

        distance = place.get("_distance", float('inf'))
        rating = place.get("_raw_rating", 0)
        review_count = place.get("_review_count", 0)
        matched_reqs = place.get("_matched_requirements", [])
        scenario = place.get("_matched_scenario", "")

        # 距离优势
        if distance < 500:
            reasons.append(f"距离最近，仅{int(distance)}米")
        elif distance < 800:
            reasons.append(f"位置便利，约{int(distance)}米")

        # 评分优势
        if rating >= 4.5 and place.get("_has_rating"):
            reasons.append(f"口碑极佳，评分{rating}")
        elif rating >= 4.0 and place.get("_has_rating"):
            reasons.append(f"评价良好，{rating}分")

        # 热度优势
        if review_count >= 500:
            reasons.append(f"人气火爆，{review_count}条评价")
        elif review_count >= 100:
            reasons.append(f"热门推荐，{review_count}人评价")

        # 需求匹配
        if matched_reqs:
            req_text = "、".join(matched_reqs[:2])
            reasons.append(f"满足{req_text}需求")

        # 场景匹配
        if scenario:
            reasons.append(f"符合{scenario}场景")

        # 如果没有明显优势，给一个通用理由
        if not reasons:
            if distance < 1500:
                reasons.append("位置适中，综合评价不错")
            else:
                reasons.append("特色场所，值得一试")

        # 最多返回2个理由
        return "；".join(reasons[:2])

    async def _llm_smart_ranking(
        self,
        places: List[Dict],
        user_requirements: str,
        participant_locations: List[str],
        keywords: str,
        top_n: int = 8
    ) -> List[Dict]:
        """LLM 智能评分重排序

        使用 LLM 对候选场所进行智能评分和重排序，考虑：
        - 用户需求的语义理解
        - 场所特点与需求的匹配度
        - 对各参与者的公平性
        - 场所的综合吸引力

        Args:
            places: 候选场所列表（已经过初步筛选）
            user_requirements: 用户需求文本
            participant_locations: 参与者位置列表
            keywords: 搜索关键词
            top_n: 返回的推荐数量

        Returns:
            重排序后的场所列表
        """
        llm = _get_llm()
        if not llm or len(places) == 0:
            logger.info("LLM 不可用或无候选场所，跳过智能排序")
            return places[:top_n]

        # 准备场所摘要信息
        places_summary = []
        for i, place in enumerate(places[:15]):  # 最多分析15个
            summary = {
                "id": i,
                "name": place.get("name", ""),
                "type": place.get("type", ""),
                "rating": place.get("_raw_rating", 0),
                "review_count": place.get("_review_count", 0),
                "distance": round(place.get("_distance", 0)),
                "address": place.get("address", ""),
                "rule_score": round(place.get("_score", 0), 1),
                "features": place.get("tag", "")[:100] if place.get("tag") else ""
            }
            places_summary.append(summary)

        # 构建 LLM 评分 prompt
        prompt = f"""你是一个智能会面地点推荐助手。请对以下候选场所进行评分和排序。

## 会面信息
- **参与者位置**: {', '.join(participant_locations)}
- **寻找的场所类型**: {keywords}
- **用户特殊需求**: {user_requirements or '无特殊要求'}

## 候选场所
{json.dumps(places_summary, ensure_ascii=False, indent=2)}

## 评分要求
请综合考虑以下因素：
1. **需求匹配度** (30%): 场所是否满足用户的特殊需求
2. **位置公平性** (25%): 对所有参与者是否方便（距离是否均衡）
3. **场所品质** (25%): 评分、评论数等指标
4. **特色吸引力** (20%): 场所的独特卖点

## 输出格式
请直接返回 JSON 数组，包含你推荐的场所ID（按推荐度从高到低排序），以及每个场所的推荐理由：
```json
[
  {{"id": 0, "llm_score": 85, "reason": "距离适中，环境安静，非常适合商务会谈"}},
  {{"id": 2, "llm_score": 78, "reason": "评分高，位置对双方都比较公平"}}
]
```

只返回 JSON，不要其他内容。"""

        try:
            from app.schema import Message
            response = await llm.ask(
                messages=[Message.user_message(prompt)],
                system_msgs=[Message.system_message("你是一个专业的地点推荐助手，请直接返回 JSON 格式的评分结果。")]
            )

            if not response or not response.content:
                logger.warning("LLM 返回空响应")
                return places[:top_n]

            # 解析 LLM 返回的 JSON
            content = response.content.strip()
            # 提取 JSON 部分
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            llm_rankings = json.loads(content)

            # 应用 LLM 评分
            id_to_llm_result = {r["id"]: r for r in llm_rankings}
            for i, place in enumerate(places[:15]):
                if i in id_to_llm_result:
                    llm_result = id_to_llm_result[i]
                    place["_llm_score"] = llm_result.get("llm_score", 0)
                    place["_llm_reason"] = llm_result.get("reason", "")
                    # 综合得分 = 规则得分 * 0.4 + LLM 得分 * 0.6
                    place["_final_score"] = place.get("_score", 0) * 0.4 + place["_llm_score"] * 0.6
                else:
                    place["_llm_score"] = 0
                    place["_llm_reason"] = ""
                    place["_final_score"] = place.get("_score", 0) * 0.4

            # 按最终得分重排序
            places_with_llm = [p for p in places[:15] if p.get("_llm_score", 0) > 0]
            places_without_llm = [p for p in places[:15] if p.get("_llm_score", 0) == 0]

            # LLM 评分的排前面
            places_with_llm.sort(key=lambda x: x.get("_final_score", 0), reverse=True)
            places_without_llm.sort(key=lambda x: x.get("_score", 0), reverse=True)

            result = places_with_llm + places_without_llm
            logger.info(f"LLM 智能排序完成，返回 {len(result[:top_n])} 个推荐")

            return result[:top_n]

        except json.JSONDecodeError as e:
            logger.warning(f"LLM 返回的 JSON 解析失败: {e}")
            return places[:top_n]
        except Exception as e:
            logger.warning(f"LLM 智能排序失败: {e}")
            return places[:top_n]

    async def _llm_generate_transport_tips(
        self,
        places: List[Dict],
        center_point: Tuple[float, float],
        participant_locations: List[str],
        keywords: str
    ) -> str:
        """LLM 动态生成交通与停车建议

        根据实际场所位置、参与者出发地和场所类型，生成个性化的交通建议。

        Args:
            places: 推荐的场所列表
            center_point: 中心点坐标
            participant_locations: 参与者位置列表
            keywords: 搜索关键词（用于判断场所类型）

        Returns:
            HTML 格式的交通停车建议
        """
        llm = _get_llm()
        if not llm:
            logger.info("LLM 不可用，使用默认交通建议")
            return self._generate_default_transport_tips(keywords)

        try:
            # 构建场所信息摘要
            places_info = []
            for i, place in enumerate(places[:5]):
                places_info.append({
                    "name": place.get("name", ""),
                    "address": place.get("address", ""),
                    "distance": place.get("_distance", 0),
                    "type": place.get("type", "")
                })

            prompt = f"""你是一个本地出行专家。根据以下信息，生成个性化的交通与停车建议。

**参与者出发地**：
{chr(10).join([f"- {loc}" for loc in participant_locations])}

**推荐场所**：
{json.dumps(places_info, ensure_ascii=False, indent=2)}

**中心点坐标**：{center_point[0]:.6f}, {center_point[1]:.6f}

**场所类型**：{keywords}

请生成 4-5 条实用的交通与停车建议，要求：
1. 根据参与者的实际出发地，建议最佳交通方式（地铁、公交、打车、自驾）
2. 考虑场所周边的实际停车情况
3. 给出具体的时间规划建议
4. 如果是大学或商圈，提供特别提示

直接返回 JSON 数组，每条建议包含 icon 和 text 字段：
```json
[
  {{"icon": "bx-train", "text": "建议内容"}},
  {{"icon": "bxs-car-garage", "text": "停车建议"}}
]
```

可用图标：bx-train（地铁）、bx-bus（公交）、bx-taxi（打车）、bxs-car-garage（停车）、bx-time（时间）、bx-info-circle（提示）
"""

            from app.schema import Message
            response = await llm.ask(
                messages=[Message.user_message(prompt)],
                system_msgs=[Message.system_message("你是一个本地出行专家，请直接返回 JSON 格式的交通建议。")],
                stream=False  # 使用非流式调用，更可靠
            )

            if not response:
                logger.warning("LLM 返回空响应")
                return self._generate_default_transport_tips(keywords)

            # 非流式调用返回字符串，流式调用返回 Message 对象
            content = response if isinstance(response, str) else response.content
            content = content.strip()

            # 解析 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            tips = json.loads(content)

            # 生成 HTML
            html_items = []
            for tip in tips[:5]:
                icon = tip.get("icon", "bx-check")
                text = tip.get("text", "")
                html_items.append(f"<li><i class='bx {icon}'></i>{text}</li>")

            logger.info(f"LLM 生成了 {len(tips)} 条交通建议")
            return "\n                        ".join(html_items)

        except Exception as e:
            logger.warning(f"LLM 生成交通建议失败: {e}")
            return self._generate_default_transport_tips(keywords)

    def _generate_default_transport_tips(self, keywords: str) -> str:
        """生成默认交通建议（兜底逻辑）"""
        return """<li><i class='bx bx-check'></i>建议使用高德地图或百度地图导航到目的地</li>
                        <li><i class='bx bx-check'></i>高峰时段建议提前30分钟出发</li>
                        <li><i class='bx bx-check'></i>部分场所可能提供停车服务，建议提前确认</li>
                        <li><i class='bx bx-check'></i>如使用公共交通，可查询附近地铁站或公交站</li>"""

    async def _llm_generate_place_reasons(
        self,
        places: List[Dict],
        user_requirements: str,
        participant_locations: List[str],
        keywords: str
    ) -> Dict[str, str]:
        """LLM 批量生成场所推荐理由

        为每个场所生成个性化的推荐理由，考虑用户需求和参与者位置。

        Args:
            places: 场所列表
            user_requirements: 用户需求
            participant_locations: 参与者位置
            keywords: 搜索关键词

        Returns:
            场所名称到推荐理由的映射
        """
        llm = _get_llm()
        if not llm or len(places) == 0:
            return {}

        try:
            places_info = []
            for i, place in enumerate(places[:8]):
                places_info.append({
                    "id": i,
                    "name": place.get("name", ""),
                    "rating": place.get("_raw_rating", place.get("rating", 0)),
                    "distance": round(place.get("_distance", 0)),
                    "address": place.get("address", ""),
                    "type": place.get("type", "")
                })

            prompt = f"""你是一个本地生活推荐专家。为以下场所生成简洁的推荐理由。

**用户需求**：{user_requirements or "无特殊要求"}

**参与者出发地**：
{chr(10).join([f"- {loc}" for loc in participant_locations])}

**场所类型**：{keywords}

**候选场所**：
{json.dumps(places_info, ensure_ascii=False, indent=2)}

为每个场所生成一句话推荐理由（15-25字），要求：
1. 突出该场所最大的优势（距离近、评分高、环境好等）
2. 如果有用户需求，说明如何满足
3. 语言自然，避免模板化
4. 每个场所的理由要有差异化

直接返回 JSON 对象，key 是场所 id，value 是推荐理由：
```json
{{
  "0": "距离两校中心最近，步行5分钟可达",
  "1": "星巴克品质保证，适合安静交谈"
}}
```
"""

            from app.schema import Message
            response = await llm.ask(
                messages=[Message.user_message(prompt)],
                system_msgs=[Message.system_message("你是一个本地生活推荐专家，请直接返回 JSON 格式的推荐理由。")],
                stream=False  # 使用非流式调用，更可靠
            )

            if not response:
                logger.warning("LLM 返回空响应")
                return {}

            # 非流式调用返回字符串
            content = response if isinstance(response, str) else response.content
            content = content.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            reasons_map = json.loads(content)

            # 转换为场所名称映射
            result = {}
            for i, place in enumerate(places[:8]):
                if str(i) in reasons_map:
                    result[place.get("name", "")] = reasons_map[str(i)]

            logger.info(f"LLM 生成了 {len(result)} 条推荐理由")
            return result

        except Exception as e:
            logger.warning(f"LLM 生成推荐理由失败: {e}")
            return {}

    def _rank_places(
        self,
        places: List[Dict],
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str,
        min_rating: float = 0.0,
        max_distance: int = 100000,
        price_range: str = ""
    ) -> List[Dict]:
        """V2 多维度评分排序算法

        评分维度 (满分100分):
        - 基础评分: 30分 (基于rating)
        - 热度分: 20分 (基于评论数+图片数)
        - 距离分: 25分 (非线性衰减)
        - 场景匹配: 15分
        - 需求匹配: 10分

        筛选条件:
        - min_rating: 最低评分过滤
        - max_distance: 最大距离过滤(米)
        - price_range: 价格区间过滤
        """
        logger.info(f"开始V2多维度评分，共{len(places)}个场所")

        # ========== 硬筛选阶段 ==========
        original_count = len(places)

        # 1. 评分筛选
        if min_rating > 0:
            places = [p for p in places if float(p.get("rating", 0) or 0) >= min_rating]
            logger.info(f"评分筛选(>={min_rating}): {original_count} -> {len(places)}")

        # 2. 距离筛选
        if max_distance < 100000:
            filtered_places = []
            for p in places:
                try:
                    # Amap POI uses "location" field with "lng,lat" format
                    location = p.get("location", "")
                    if location and "," in location:
                        lng_str, lat_str = location.split(",")
                        place_lng, place_lat = float(lng_str), float(lat_str)
                    else:
                        # Fallback to separate fields
                        place_lng = float(p.get("lng", 0))
                        place_lat = float(p.get("lat", 0))
                    dist = self._calculate_distance(center_point, (place_lng, place_lat))
                    if dist <= max_distance:
                        filtered_places.append(p)
                except (ValueError, TypeError):
                    pass
            places = filtered_places
            logger.info(f"距离筛选(<={max_distance}米): 剩余{len(places)}个")

        # 3. 价格区间筛选（软筛选，作为排序权重）
        price_weight_map = {
            "economy": ["¥", "人均20", "人均30", "人均40"],
            "mid": ["¥¥", "人均50", "人均60", "人均80", "人均100"],
            "high": ["¥¥¥", "¥¥¥¥", "人均150", "人均200", "人均300"]
        }

        if not places:
            logger.warning("筛选后无符合条件的场所")
            return []

        for place in places:
            # 1. 基础评分 (满分30分)
            base_score, raw_rating = self._calculate_base_score(place)
            place["_raw_rating"] = raw_rating

            # 2. 热度分 (满分20分)
            popularity_score, review_count, photo_count = self._calculate_popularity_score(place)
            place["_review_count"] = review_count
            place["_photo_count"] = photo_count

            # 3. 距离分 (满分25分) - 非线性衰减
            distance_score, distance = self._calculate_distance_score_v2(place, center_point)

            # 4. 场景匹配分 (满分15分)
            scenario_score, matched_scenario = self._calculate_scenario_match_score(place, keywords)
            place["_matched_scenario"] = matched_scenario

            # 5. 需求匹配分 (满分10分) - 三层匹配算法
            requirement_score, matched_reqs, confidence_map = self._calculate_requirement_score(place, user_requirements)
            place["_matched_requirements"] = matched_reqs
            place["_requirement_confidence"] = confidence_map  # 置信度映射

            # 汇总得分
            total_score = base_score + popularity_score + distance_score + scenario_score + requirement_score
            place["_score"] = total_score

            # 记录评分明细用于调试
            place["_score_breakdown"] = {
                "base": round(base_score, 1),
                "popularity": round(popularity_score, 1),
                "distance": round(distance_score, 1),
                "scenario": round(scenario_score, 1),
                "requirement": round(requirement_score, 1)
            }

            logger.debug(
                f"{place.get('name')}: 总分{total_score:.1f} "
                f"(基础{base_score:.1f}+热度{popularity_score:.1f}+"
                f"距离{distance_score:.1f}+场景{scenario_score:.1f}+需求{requirement_score:.1f})"
            )

        # 初步排序
        ranked_places = sorted(places, key=lambda x: x.get("_score", 0), reverse=True)

        # 应用多样性调整（惩罚连锁店）
        ranked_places = self._apply_diversity_adjustment(ranked_places)

        # 重新排序
        ranked_places = sorted(ranked_places, key=lambda x: x.get("_score", 0), reverse=True)

        # 生成推荐理由（优先使用 LLM 生成的理由，否则使用规则生成）
        for place in ranked_places:
            # 如果 LLM 智能排序已经生成了理由，优先使用
            if place.get("_llm_reason"):
                place["_recommendation_reason"] = place["_llm_reason"]
            else:
                place["_recommendation_reason"] = self._generate_recommendation_reason(place, ranked_places)

        # 对于多场景搜索，确保每个场景都有代表性
        if any(place.get('_source_keyword') for place in ranked_places):
            logger.info("应用多场景平衡策略")
            # 按场景类型分组
            by_keyword = {}
            for place in ranked_places:
                keyword = place.get('_source_keyword', '未知')
                if keyword not in by_keyword:
                    by_keyword[keyword] = []
                by_keyword[keyword].append(place)

            # 从每个场景选择最佳的场所，确保多样性
            balanced_places = []
            max_per_keyword = max(2, 8 // len(by_keyword))  # 每个场景至少2个，总共不超过8个

            for keyword, keyword_places in by_keyword.items():
                selected = keyword_places[:max_per_keyword]
                balanced_places.extend(selected)
                logger.info(f"从场景 '{keyword}' 选择了 {len(selected)} 个场所")

            # 按分数重新排序，但保持场景多样性
            balanced_places = sorted(balanced_places, key=lambda x: x.get("_score", 0), reverse=True)

            # 记录最终推荐
            for i, p in enumerate(balanced_places[:8]):
                logger.info(f"推荐#{i+1}: {p.get('name')} ({p.get('_score', 0):.1f}分) - {p.get('_recommendation_reason', '')}")

            return balanced_places[:8]  # 增加到8个推荐
        else:
            # 记录最终推荐
            for i, p in enumerate(ranked_places[:6]):
                logger.info(f"推荐#{i+1}: {p.get('name')} ({p.get('_score', 0):.1f}分) - {p.get('_recommendation_reason', '')}")

            return ranked_places[:6]  # 单场景增加到6个


    def _calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        lng1, lat1 = point1
        lng2, lat2 = point2
        x = (lng2 - lng1) * 85000 
        y = (lat2 - lat1) * 111000 
        return math.sqrt(x*x + y*y)

    async def _generate_html_page(
        self,
        locations: List[Dict],
        places: List[Dict],
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str,
        theme: str = "",  # 添加主题参数
        participant_locations: List[str] = None  # 参与者位置名称列表
    ) -> str:
        file_name_prefix = "place"

        # 提取参与者位置名称
        if participant_locations is None:
            participant_locations = [loc.get("formatted_address", loc.get("address", "")) for loc in locations]

        html_content = await self._generate_html_content(
            locations, places, center_point, user_requirements, keywords, theme, participant_locations
        )
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"{file_name_prefix}_recommendation_{timestamp}_{unique_id}.html"
        
        workspace_js_src_path = os.path.join("workspace", "js_src")
        os.makedirs(workspace_js_src_path, exist_ok=True)
        file_path = os.path.join(workspace_js_src_path, file_name)

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(html_content)
        return file_path

    async def _generate_html_content(
        self,
        locations: List[Dict],
        places: List[Dict],
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str,
        theme: str = "",  # 添加主题参数
        participant_locations: List[str] = None  # 参与者位置名称列表
    ) -> str:
        # 根据主题参数确定配置
        if theme:
            # 主题映射：前端theme -> 后端配置key
            theme_mapping = {
                'coffee': '咖啡馆',
                'restaurant': '餐厅', 
                'library': '图书馆',
                'shopping': '商场',
                'park': '公园',
                'cinema': '电影院',
                'gym': '健身房',
                'ktv': 'KTV',
                'museum': '博物馆',
                'attraction': '景点',
                'bar': '酒吧',
                'teahouse': '茶楼',
                'custom': 'default'
            }
            config_key = theme_mapping.get(theme, 'default')
            cfg = self._get_place_config(config_key)
            primary_keyword = config_key if config_key != 'default' else '场所'
        else:
            # 兼容旧逻辑：从关键词确定配置
            primary_keyword = keywords.split("、")[0] if keywords else "场所"
            cfg = self._get_place_config(primary_keyword)

        city_name = self._extract_city_from_locations(locations)
        meta_tags = {
            "title": f"{cfg['topic']} - 最佳会面{cfg['noun_singular']}推荐",
            "description": f"MeetSpot在{city_name}为多人聚会智能推荐公平会面地点, 支持{primary_keyword}等场景。",
            "keywords": f"{city_name},{primary_keyword},MeetSpot,聚会地点",
        }
        schema_graph: List[Dict] = []
        try:
            from api.services.seo_content import SEOContentGenerator

            seo_generator = SEOContentGenerator()
            meta_tags = seo_generator.generate_meta_tags(
                "recommendation",
                {
                    "city": city_name,
                    "keyword": primary_keyword,
                    "locations_count": len(locations),
                },
            )
            schema_graph = []
            for place in places[:3]:
                schema_obj = seo_generator.generate_schema_org(
                    "local_business", self._format_schema_payload(place, city_name)
                )
                if schema_obj:
                    schema_obj.pop("@context", None)
                    schema_graph.append(schema_obj)
        except Exception as exc:  # noqa: BLE001 - 非关键路径
            logger.warning(f"SEO meta fallback: {exc}")
            schema_graph = []

        meta_title = html.escape(meta_tags.get("title", "")) or f"{city_name}聚会地点推荐 - MeetSpot"
        meta_description = html.escape(
            meta_tags.get("description", "MeetSpot帮助团队计算公平的会面地点。")
        )
        meta_keywords = html.escape(meta_tags.get("keywords", f"{city_name},{primary_keyword}"))
        schema_block = ""
        if schema_graph:
            schema_block = json.dumps(
                {"@context": "https://schema.org", "@graph": [g for g in schema_graph if g]},
                ensure_ascii=False,
                indent=2,
            )
        canonical_url = "https://meetspot-irq2.onrender.com/"
        schema_script = ""
        if schema_block:
            schema_script = (
                '\n    <script type="application/ld+json">\n'
                f"{schema_block}\n"
                "    </script>\n"
            )

        search_process_html = self._generate_search_process(locations, center_point, user_requirements, keywords, places) 

        location_markers = []
        for idx, loc in enumerate(locations):
            location_markers.append({
                "name": f"地点{idx+1}: {loc['name']}",
                "position": [loc["lng"], loc["lat"]],
                "icon": "location"
            })

        place_markers = [] 
        for place in places:
            lng_str, lat_str = place.get("location", ",").split(",")
            if lng_str and lat_str:
                place_markers.append({
                    "name": place["name"],
                    "position": [float(lng_str), float(lat_str)],
                    "icon": "place" 
                })

        center_marker = {
            "name": "最佳会面点",
            "position": [center_point[0], center_point[1]],
            "icon": "center"
        }
        all_markers = [center_marker] + location_markers + place_markers

        location_rows_html = ""
        for idx, loc in enumerate(locations):
            location_rows_html += f"<tr><td>{idx+1}</td><td>{loc['name']}</td><td>{loc['formatted_address']}</td></tr>"

        location_distance_html = ""
        for loc in locations:
            distance = self._calculate_distance(center_point, (loc['lng'], loc['lat']))/1000
            location_distance_html += f"<li><i class='bx bx-map'></i><strong>{loc['name']}</strong>: 距离中心点约 <span class='distance'>{distance:.1f} 公里</span></li>"

        # LLM 动态生成交通与停车建议 (带超时保护)
        if participant_locations is None:
            participant_locations = [loc.get("name", loc.get("formatted_address", "")) for loc in locations]
        try:
            transport_tips_html = await asyncio.wait_for(
                self._llm_generate_transport_tips(places, center_point, participant_locations, keywords),
                timeout=15.0  # 15秒超时，避免Render 30秒请求超时
            )
        except asyncio.TimeoutError:
            logger.warning("LLM 交通建议生成超时，使用默认建议")
            transport_tips_html = self._generate_default_transport_tips(keywords)

        place_cards_html = "" 
        for place in places:
            rating = place.get("biz_ext", {}).get("rating", "暂无评分")
            address = place.get("address", "地址未知")
            business_hours = place.get("business_hours", "营业时间未知")
            if isinstance(business_hours, list) and business_hours:
                business_hours = "; ".join(business_hours)
            tel = place.get("tel", "电话未知")
            
            tags = place.get("tag", [])
            if isinstance(tags, str): tags = tags.split(";") if tags else []
            elif not isinstance(tags, list): tags = []
            
            tags_html = "".join([f"<span class='cafe-tag'>{tg.strip()}</span>" for tg in tags if tg.strip()])
            if not tags_html:
                tags_html = f"<span class='cafe-tag'>{cfg['noun_singular']}</span>"

            # 需求匹配置信度标签
            matched_reqs = place.get("_matched_requirements", [])
            confidence_map = place.get("_requirement_confidence", {})
            requirement_match_html = ""
            if matched_reqs:
                match_tags = []
                for req in matched_reqs:
                    confidence = confidence_map.get(req, "low")
                    if confidence == "high":
                        icon = "bx-check-circle"
                        tag_class = "match-tag-high"
                        tooltip = "已验证"
                    elif confidence == "medium":
                        icon = "bx-check"
                        tag_class = "match-tag-medium"
                        tooltip = "品牌特征"
                    else:
                        icon = "bx-question-mark"
                        tag_class = "match-tag-low"
                        tooltip = "建议确认"
                    match_tags.append(f"<span class='match-tag {tag_class}' title='{tooltip}'><i class='bx {icon}'></i>{req}</span>")
                requirement_match_html = f'''
                        <div class="requirement-match">
                            {"".join(match_tags)}
                        </div>'''

            lng_str, lat_str = place.get("location",",").split(",")
            distance_text = "未知距离"
            map_link_coords = ""
            if lng_str and lat_str:
                lng, lat = float(lng_str), float(lat_str)
                distance = self._calculate_distance(center_point, (lng, lat))
                distance_text = f"{distance/1000:.1f} 公里"
                map_link_coords = f"{lng},{lat}"

            # 获取推荐理由
            recommendation_reason = place.get("_recommendation_reason", "")
            reason_html = ""
            if recommendation_reason:
                reason_html = f'''
                        <div class="cafe-reason">
                            <i class='bx bx-bulb'></i>
                            <span>{recommendation_reason}</span>
                        </div>'''

            # 获取评分明细用于tooltip（可选展示）
            score_breakdown = place.get("_score_breakdown", {})
            total_score = place.get("_score", 0)
            score_title = f"综合评分: {total_score:.0f}/100"

            place_cards_html += f'''
            <div class="cafe-card" title="{score_title}">
                <div class="cafe-img">
                    <i class='bx {cfg["icon_card"]}'></i>
                </div>
                <div class="cafe-content">
                    <div class="cafe-header">
                        <div>
                            <h3 class="cafe-name">{place['name']}</h3>
                        </div>
                        <span class="cafe-rating">评分: {rating}</span>
                    </div>{reason_html}
                    <div class="cafe-details">
                        <div class="cafe-info">
                            <i class='bx bx-map'></i>
                            <div class="cafe-info-text">{address}</div>
                        </div>
                        <div class="cafe-info">
                            <i class='bx bx-time'></i>
                            <div class="cafe-info-text">{business_hours}</div>
                        </div>
                        <div class="cafe-info">
                            <i class='bx bx-phone'></i>
                            <div class="cafe-info-text">{tel}</div>
                        </div>
                        <div class="cafe-tags">
                            {tags_html}
                        </div>{requirement_match_html}
                    </div>
                    <div class="cafe-footer">
                        <div class="cafe-distance">
                            <i class='bx bx-walk'></i> {distance_text}
                        </div>
                        <div class="cafe-actions">
                            <a href="https://uri.amap.com/marker?position={map_link_coords}&name={place['name']}" target="_blank">
                                <i class='bx bx-navigation'></i>导航
                            </a>
                        </div>
                    </div>
                </div>
            </div>'''

        # 空状态设计：如果没有找到推荐结果
        if not places:
            place_cards_html = f'''
            <div class="empty-state">
                <i class='bx bx-coffee empty-state-icon'></i>
                <h3 class="empty-state-title">暂无推荐{cfg["noun_plural"]}</h3>
                <p class="empty-state-description">
                    很抱歉，在您指定的区域内未能找到符合条件的{cfg["noun_plural"]}。<br>
                    建议扩大搜索范围或调整搜索关键词。
                </p>
                <a href="/public/meetspot_finder.html" class="btn-modern btn-primary-modern">
                    <i class='bx bx-redo'></i>重新搜索
                </a>
            </div>'''

        markers_json = json.dumps(all_markers)

        amap_security_js_code = ""
        if hasattr(config, 'amap') and hasattr(config.amap, 'security_js_code') and config.amap.security_js_code:
            amap_security_js_code = config.amap.security_js_code

        # 读取设计token CSS内容，用于自包含HTML
        design_tokens_css = ""
        try:
            from pathlib import Path
            tokens_css_path = Path("static/css/design-tokens.css")
            if tokens_css_path.exists():
                design_tokens_css = tokens_css_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"无法读取design-tokens.css: {e}")

        # Dynamically set CSS variables using MeetSpot brand colors
        # 使用品牌色系统而非场所特定配色，确保一致性
        dynamic_style = f"""
        /* Design Tokens - Embedded for offline capability */
        {design_tokens_css}

        /* MeetSpot Brand Color System - 深海蓝+日落橙主题 */
        :root {{
            /* 主色：深海蓝系 - 沉稳、可信赖 */
            --primary: var(--brand-primary, #0A4D68);
            --primary-light: var(--brand-primary-light, #088395);
            --primary-dark: var(--brand-primary-dark, #05445E);
            /* 强调色：日落橙 - 温暖、活力 */
            --accent: var(--brand-accent, #FF6B35);
            --accent-light: var(--brand-accent-light, #FF8C61);
            /* 次要色：薄荷绿 - 清新、平衡 */
            --secondary: var(--brand-secondary, #06D6A0);
            /* 中性色 */
            --light: var(--neutral-50, #F8FAFC);
            --dark: var(--neutral-900, #0F172A);
            /* 功能色 */
            --success: var(--brand-success, #0C8A5D);
            --border-radius: var(--radius-lg, 12px);
            --box-shadow: var(--shadow-lg, 0 8px 30px rgba(0, 0, 0, 0.12));
            --transition: all 0.3s ease;

            /* 场所特定装饰色（保留图标色，但不影响主色调） */
            --venue-icon-bg: {cfg.get("theme_primary", "#0A4D68")};
        }}"""

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{meta_keywords}">
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{meta_title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="https://meetspot-irq2.onrender.com/static/og-image.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{meta_title}">
    <meta name="twitter:description" content="{meta_description}">

    <!-- MeetSpot Urban Navigator Theme Fonts - Distinctive Typography -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/boxicons@2.0.9/css/boxicons.min.css">

    <!-- Modern UI Components -->
    <link rel="stylesheet" href="/public/css/components.css">

    {schema_script}
    <style>
        {dynamic_style} /* Inject dynamic theme colors here */

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'DM Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; background-color: var(--light); color: var(--dark); padding-bottom: 50px; }}
        h1, h2, h3, h4, h5, h6 {{ font-family: 'Outfit', 'PingFang SC', sans-serif; font-weight: 700; letter-spacing: -0.02em; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: linear-gradient(135deg, #001524 0%, #0A4D68 50%, #001524 100%); color: white; padding: 60px 0 100px; text-align: center; position: relative; margin-bottom: 80px; box-shadow: 0 8px 32px rgba(0, 21, 36, 0.3); }}
        header::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: repeating-radial-gradient(circle at 30% 40%, transparent 0, transparent 40px, rgba(6, 214, 160, 0.05) 40px, rgba(6, 214, 160, 0.05) 42px); pointer-events: none; }}
        header::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 60px; background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60"><path fill="%23F8FAFC" fill-opacity="1" d="M0,32L80,42.7C160,53,320,75,480,64C640,53,800,11,960,5.3C1120,0,1280,32,1360,48L1440,64L1440,100L1360,100C1280,100,1120,100,960,100C800,100,640,100,480,100C320,100,160,100,80,100L0,100Z"></path></svg>'); background-size: cover; background-position: center; }}
        .header-logo {{ font-size: 3rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.03em; text-shadow: 0 2px 20px rgba(0, 0, 0, 0.3); }}
        .coffee-icon {{ font-size: 3rem; vertical-align: middle; margin-right: 10px; }}
        .header-subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
        .main-content {{ margin-top: -60px; }}
        .card {{ background-color: white; border-radius: var(--border-radius); padding: 30px; box-shadow: var(--box-shadow); margin-bottom: 30px; transition: var(--transition); }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1); }}
        .section-title {{ font-size: 1.8rem; color: var(--primary-dark); margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid var(--secondary); display: flex; align-items: center; }}
        .section-title i {{ margin-right: 12px; font-size: 1.6rem; color: var(--primary); }}
        .summary-card {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 15px; }}
        .summary-item {{ flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0,0,0,0.03); /* Adjusted for better contrast with various themes */ border-radius: 8px; border-left: 4px solid var(--primary); }}
        .summary-label {{ font-size: 0.9rem; color: var(--primary-dark); margin-bottom: 5px; }}
        .summary-value {{ font-size: 1.2rem; font-weight: 600; color: var(--dark); }}
        .map-container {{ height: 500px; border-radius: var(--border-radius); overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); position: relative; margin-bottom: 30px; }}
        #map {{ height: 100%; width: 100%; }}
        .map-legend {{ position: absolute; bottom: 15px; left: 15px; background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.15); z-index: 100; }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 8px; }}
        .legend-color {{ width: 20px; height: 20px; margin-right: 10px; border-radius: 50%; }}
        .legend-center {{ background-color: var(--brand-secondary, #06D6A0); }}  /* 薄荷绿 - 中心点 */
        .legend-location {{ background-color: var(--brand-primary, #0A4D68); }}  /* 深海蓝 - 参与地点 */
        .legend-place {{ background-color: var(--brand-accent, #FF6B35); }}  /* 日落橙 - 推荐场所 */ 
        .location-table {{ width: 100%; border-collapse: collapse; border-radius: 8px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 0 8px rgba(0, 0, 0, 0.1); }}
        .location-table th, .location-table td {{ padding: 15px; text-align: left; border-bottom: 1px solid #eee; }}
        .location-table th {{ background-color: var(--primary-light); color: white; font-weight: 600; }}
        .location-table tr:last-child td {{ border-bottom: none; }}
        .location-table tr:nth-child(even) {{ background-color: rgba(0,0,0,0.02); /* Adjusted for better contrast */ }}
        .cafe-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 28px; margin-top: 24px; }}
        .cafe-card {{ background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(10, 77, 104, 0.08), 0 1px 3px rgba(0,0,0,0.04); transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); display: flex; flex-direction: column; position: relative; }}
        .cafe-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 50%, var(--brand-accent, #FF6B35) 100%); opacity: 0; transition: opacity 0.3s ease; }}
        .cafe-card:hover {{ transform: translateY(-8px) scale(1.01); box-shadow: 0 20px 40px rgba(10, 77, 104, 0.15), 0 8px 16px rgba(0,0,0,0.08); }}
        .cafe-card:hover::before {{ opacity: 1; }}
        /* 推荐理由 - 地图标注风格 */
        .cafe-reason {{ position: relative; display: flex; align-items: center; gap: 10px; background: linear-gradient(135deg, rgba(255, 107, 53, 0.08) 0%, rgba(255, 107, 53, 0.03) 100%); padding: 12px 16px; margin: 0 0 12px 0; border-radius: 10px; border: 1px solid rgba(255, 107, 53, 0.15); }}
        .cafe-reason::before {{ content: ''; position: absolute; left: 12px; top: -6px; width: 12px; height: 12px; background: linear-gradient(135deg, var(--brand-accent, #FF6B35) 0%, #ff8c5a 100%); border-radius: 50%; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.4); animation: reasonPulse 2s ease-in-out infinite; }}
        .cafe-reason i {{ color: var(--brand-accent, #FF6B35); font-size: 1.2rem; margin-left: 8px; }}
        .cafe-reason span {{ color: #2c3e50; font-size: 0.88rem; font-weight: 600; letter-spacing: 0.01em; line-height: 1.4; }}
        @keyframes reasonPulse {{ 0%, 100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(1.2); opacity: 0.7; }} }}
        /* 卡片排名标记 */
        .cafe-card:nth-child(1) .cafe-img::after {{ content: '🥇 TOP 1'; position: absolute; top: 12px; right: 12px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: #1a1a1a; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4); }}
        .cafe-card:nth-child(2) .cafe-img::after {{ content: '🥈 TOP 2'; position: absolute; top: 12px; right: 12px; background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%); color: #1a1a1a; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(192, 192, 192, 0.4); }}
        .cafe-card:nth-child(3) .cafe-img::after {{ content: '🥉 TOP 3'; position: absolute; top: 12px; right: 12px; background: linear-gradient(135deg, #CD7F32 0%, #B8860B 100%); color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(205, 127, 50, 0.4); }}
        .cafe-img {{ height: 180px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 3.5rem; position: relative; overflow: hidden; }}
        .cafe-img::before {{ content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%); animation: shimmer 3s ease-in-out infinite; }}
        @keyframes shimmer {{ 0%, 100% {{ transform: translate(-30%, -30%); }} 50% {{ transform: translate(30%, 30%); }} }}
        .cafe-content {{ padding: 22px; flex: 1; display: flex; flex-direction: column; }}
        .cafe-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
        .cafe-name {{ font-size: 1.25rem; margin: 0; color: var(--primary-dark); font-weight: 700; letter-spacing: -0.01em; line-height: 1.3; }}
        .cafe-rating {{ display: inline-flex; align-items: center; gap: 4px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; white-space: nowrap; box-shadow: 0 2px 8px rgba(10, 77, 104, 0.25); }}
        .cafe-rating::before {{ content: '⭐'; font-size: 0.75rem; }}
        .cafe-details {{ flex: 1; }}
        .cafe-info {{ margin-bottom: 10px; display: flex; align-items: flex-start; }}
        .cafe-info i {{ color: var(--primary); margin-right: 10px; font-size: 1.05rem; min-width: 18px; margin-top: 2px; opacity: 0.85; }}
        .cafe-info-text {{ flex: 1; font-size: 0.9rem; color: #4a5568; line-height: 1.5; }}
        .cafe-tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
        .cafe-tag {{ background: linear-gradient(135deg, rgba(10, 77, 104, 0.06) 0%, rgba(8, 131, 149, 0.04) 100%); color: var(--primary-dark); padding: 5px 12px; border-radius: 16px; font-size: 0.78rem; font-weight: 500; border: 1px solid rgba(10, 77, 104, 0.08); transition: all 0.2s ease; }}
        .cafe-tag:hover {{ background: linear-gradient(135deg, rgba(10, 77, 104, 0.12) 0%, rgba(8, 131, 149, 0.08) 100%); transform: translateY(-1px); }}
        /* 需求匹配置信度标签样式 */
        .requirement-match {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; padding-top: 10px; border-top: 1px dashed rgba(0,0,0,0.08); }}
        .match-tag {{ display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 500; transition: all 0.2s ease; }}
        .match-tag i {{ font-size: 0.85rem; }}
        .match-tag-high {{ background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2); }}
        .match-tag-high i {{ color: #10B981; }}
        .match-tag-medium {{ background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.08) 100%); color: #B45309; border: 1px solid rgba(245, 158, 11, 0.2); }}
        .match-tag-medium i {{ color: #F59E0B; }}
        .match-tag-low {{ background: linear-gradient(135deg, rgba(148, 163, 184, 0.15) 0%, rgba(148, 163, 184, 0.08) 100%); color: #475569; border: 1px solid rgba(148, 163, 184, 0.2); }}
        .match-tag-low i {{ color: #94A3B8; }}
        .match-tag:hover {{ transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .cafe-footer {{ display: flex; align-items: center; justify-content: space-between; margin-top: 18px; padding-top: 16px; border-top: 1px solid rgba(0,0,0,0.06); }}
        .cafe-distance {{ display: inline-flex; align-items: center; gap: 6px; color: var(--primary-dark); font-weight: 600; font-size: 0.9rem; padding: 6px 12px; background: rgba(10, 77, 104, 0.04); border-radius: 8px; }}
        .cafe-distance i {{ font-size: 1.1rem; color: var(--primary); }}
        .cafe-actions a {{ display: inline-flex; align-items: center; justify-content: center; gap: 6px; background: linear-gradient(135deg, var(--brand-accent, #FF6B35) 0%, #ff8c5a 100%); color: white; padding: 10px 18px; border-radius: 10px; text-decoration: none; font-size: 0.88rem; font-weight: 600; transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1); box-shadow: 0 4px 12px rgba(255, 107, 53, 0.25); }}
        .cafe-actions a:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(255, 107, 53, 0.35); }}
        .cafe-actions i {{ font-size: 1.1rem; }}
        .transportation-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 20px; }}
        .transport-card {{ background-color: white; border-radius: 12px; padding: 25px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05); border-top: 5px solid var(--primary); }}
        .transport-title {{ font-size: 1.3rem; color: var(--primary-dark); margin-bottom: 15px; display: flex; align-items: center; }}
        .transport-title i {{ margin-right: 10px; font-size: 1.4rem; color: var(--primary); }}
        .transport-list {{ list-style: none; margin: 0; padding: 0; }}
        .transport-list li {{ padding: 10px 0; border-bottom: 1px solid #eee; display: flex; align-items: center; }}
        .transport-list li:last-child {{ border-bottom: none; }}
        .transport-list i {{ color: var(--primary); margin-right: 10px; }}
        .center-coords {{ display: inline-block; background-color: rgba(0,0,0,0.05); /* Adjusted for better contrast */ border-radius: 6px; padding: 3px 8px; margin: 0 5px; font-family: monospace; font-size: 0.9rem; }}
        .footer {{ text-align: center; background-color: var(--primary-dark); color: white; padding: 20px 0; margin-top: 50px; }}
        .back-button {{ display: inline-flex; align-items: center; justify-content: center; background-color: white; color: var(--primary); border: 2px solid var(--primary); padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1rem; transition: var(--transition); margin-top: 30px; }}
        .back-button:hover {{ background-color: var(--primary); color: white; transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }}
        .back-button i {{ margin-right: 8px; }}

        /* ========== AI Reasoning Panel - Neural Interface Theme ========== */
        .search-process-card {{
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            border: 1px solid rgba(6, 214, 160, 0.2);
            border-radius: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        }}
        .search-process-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image:
                radial-gradient(circle at 20% 80%, rgba(6, 214, 160, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.08) 0%, transparent 50%);
            pointer-events: none;
        }}
        /* Circuit pattern overlay */
        .search-process-card::after {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0v10M30 50v10M0 30h10M50 30h10' stroke='%2306D6A0' stroke-width='0.5' opacity='0.1' fill='none'/%3E%3Ccircle cx='30' cy='30' r='2' fill='%2306D6A0' opacity='0.1'/%3E%3C/svg%3E");
            background-size: 60px 60px;
            opacity: 0.5;
            pointer-events: none;
        }}

        /* Collapsible AI Thinking Section */
        .ai-thinking-details {{ width: 100%; position: relative; z-index: 1; }}
        .ai-thinking-summary {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 24px 28px;
            cursor: pointer;
            list-style: none;
            user-select: none;
            background: linear-gradient(135deg, rgba(6, 214, 160, 0.08) 0%, rgba(59, 130, 246, 0.05) 100%);
            border-radius: 16px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(6, 214, 160, 0.15);
        }}
        .ai-thinking-summary::-webkit-details-marker {{ display: none; }}
        .ai-thinking-summary:hover {{
            background: linear-gradient(135deg, rgba(6, 214, 160, 0.15) 0%, rgba(59, 130, 246, 0.1) 100%);
            border-color: rgba(6, 214, 160, 0.3);
            box-shadow: 0 0 30px rgba(6, 214, 160, 0.15);
        }}

        /* AI Brain Icon with Pulse */
        .ai-brain-icon {{
            position: relative;
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #06D6A0 0%, #3B82F6 100%);
            border-radius: 14px;
            box-shadow: 0 4px 20px rgba(6, 214, 160, 0.4);
        }}
        .ai-brain-icon i {{
            font-size: 1.8rem;
            color: white;
        }}
        .ai-brain-icon::before {{
            content: '';
            position: absolute;
            inset: -3px;
            background: linear-gradient(135deg, #06D6A0, #3B82F6, #06D6A0);
            border-radius: 17px;
            z-index: -1;
            opacity: 0.6;
            animation: neuralPulse 2s ease-in-out infinite;
        }}
        @keyframes neuralPulse {{
            0%, 100% {{ opacity: 0.4; transform: scale(1); }}
            50% {{ opacity: 0.8; transform: scale(1.05); }}
        }}

        /* Title and Badge */
        .ai-thinking-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .ai-thinking-header {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .ai-thinking-title {{
            font-size: 1.35rem;
            font-weight: 700;
            color: #f1f5f9;
            font-family: 'Outfit', sans-serif;
            letter-spacing: -0.02em;
        }}
        .ai-thinking-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            background: rgba(6, 214, 160, 0.15);
            border: 1px solid rgba(6, 214, 160, 0.3);
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            color: #06D6A0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .ai-thinking-badge::before {{
            content: '';
            width: 6px;
            height: 6px;
            background: #06D6A0;
            border-radius: 50%;
            animation: badgePulse 1.5s ease-in-out infinite;
        }}
        @keyframes badgePulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
        .ai-thinking-hint {{
            font-size: 0.85rem;
            color: #94a3b8;
            font-weight: 400;
        }}

        /* Expand Arrow */
        .ai-thinking-expand {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: #94a3b8;
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        .ai-thinking-summary:hover .ai-thinking-expand {{
            background: rgba(6, 214, 160, 0.1);
            border-color: rgba(6, 214, 160, 0.3);
            color: #06D6A0;
        }}
        .ai-thinking-arrow {{
            font-size: 1.2rem;
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .ai-thinking-details[open] .ai-thinking-arrow {{ transform: rotate(180deg); }}
        .ai-thinking-details[open] .ai-thinking-expand {{
            background: rgba(6, 214, 160, 0.15);
            color: #06D6A0;
        }}
        .ai-thinking-expand .collapse-text {{ display: none; }}
        .ai-thinking-details[open] .expand-text {{ display: none; }}
        .ai-thinking-details[open] .collapse-text {{ display: inline; }}

        /* Expanded State */
        .ai-thinking-details[open] .ai-thinking-summary {{
            border-bottom: 1px solid rgba(6, 214, 160, 0.15);
            border-radius: 16px 16px 0 0;
            margin-bottom: 0;
        }}
        .ai-thinking-details[open] .ai-thinking-badge::before {{
            background: #3B82F6;
            animation: none;
        }}

        /* Content Area */
        .ai-thinking-details .search-process {{
            padding: 28px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 0 0 16px 16px;
        }}

        /* Override step styles for dark theme */
        .search-process-card .process-step {{ color: #e2e8f0; }}
        .search-process-card .step-title {{ color: #f1f5f9; }}
        .search-process-card .step-details {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #cbd5e1;
        }}
        .search-process-card .step-icon {{
            background: linear-gradient(135deg, #06D6A0 0%, #0891b2 100%);
            box-shadow: 0 4px 15px rgba(6, 214, 160, 0.3);
        }}
        .search-process-card .step-number {{
            background: linear-gradient(135deg, #3B82F6 0%, #6366f1 100%);
        }}
        .search-process-card .highlight-text {{
            background: rgba(6, 214, 160, 0.2);
            color: #06D6A0;
        }}
        .search-process-card .code-block {{
            background: #020617;
            border: 1px solid rgba(6, 214, 160, 0.2);
        }}

        /* AI Location List */
        .ai-location-list {{ display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }}
        .ai-location-item {{ display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: white; border-radius: 10px; border: 1px solid rgba(0,0,0,0.06); }}
        .ai-loc-num {{ width: 28px; height: 28px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; }}
        .ai-loc-info {{ flex: 1; }}
        .ai-loc-info strong {{ display: block; color: var(--dark); font-size: 0.95rem; }}
        .ai-coords {{ font-size: 0.8rem; color: #64748b; font-family: 'SF Mono', 'Consolas', monospace; }}

        /* AI Algorithm Box */
        .ai-algo-box {{ background: white; border-radius: 12px; padding: 16px; margin: 12px 0; border: 1px solid rgba(10, 77, 104, 0.1); }}
        .ai-algo-formula {{ display: flex; align-items: center; gap: 12px; padding: 12px; background: linear-gradient(135deg, rgba(10, 77, 104, 0.05) 0%, rgba(6, 214, 160, 0.05) 100%); border-radius: 8px; }}
        .ai-algo-formula i {{ font-size: 1.8rem; color: var(--secondary); }}
        .ai-algo-label {{ font-size: 0.8rem; color: #64748b; display: block; }}
        .ai-algo-value {{ font-size: 1.1rem; font-weight: 700; color: var(--primary-dark); font-family: 'SF Mono', 'Consolas', monospace; }}
        .ai-algo-note {{ font-size: 0.85rem; color: #475569; margin-top: 10px; padding-left: 12px; border-left: 3px solid var(--secondary); }}

        /* AI Requirement Tags */
        .ai-req-detected {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }}
        .ai-req-tag {{ display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); color: white; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }}

        /* AI Matching Layers */
        .ai-matching-layers {{ display: flex; flex-direction: column; gap: 8px; margin-top: 12px; padding: 12px; background: white; border-radius: 10px; }}
        .ai-layer {{ display: flex; align-items: center; gap: 10px; padding: 8px 0; }}
        .ai-layer-badge {{ padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; color: white; }}
        .ai-layer-badge.high {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); }}
        .ai-layer-badge.medium {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }}
        .ai-layer-badge.low {{ background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%); }}
        .ai-layer-conf {{ font-size: 0.75rem; color: #94a3b8; margin-left: 8px; }}

        /* AI Score Dimensions */
        .ai-score-dimensions {{ display: flex; flex-direction: column; gap: 12px; margin-top: 12px; padding: 16px; background: white; border-radius: 12px; }}
        .ai-dim {{ display: flex; flex-direction: column; gap: 4px; }}
        .ai-dim-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .ai-dim-name {{ font-weight: 600; color: var(--dark); font-size: 0.9rem; }}
        .ai-dim-max {{ font-size: 0.8rem; color: #94a3b8; }}
        .ai-dim-bar {{ height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }}
        .ai-dim-fill {{ height: 100%; background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%); border-radius: 4px; transition: width 1s ease; }}
        .ai-dim-desc {{ font-size: 0.75rem; color: #64748b; }}

        /* AI Top Results */
        .ai-top-results {{ display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }}
        .ai-place-result {{ display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: white; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06); transition: all 0.3s ease; }}
        .ai-place-result:hover {{ transform: translateX(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        .ai-place-rank {{ font-size: 1.5rem; }}
        .ai-place-info {{ flex: 1; }}
        .ai-place-name {{ font-weight: 700; color: var(--dark); font-size: 1rem; margin-bottom: 2px; }}
        .ai-place-score {{ display: flex; align-items: baseline; }}
        .ai-total-score {{ font-size: 1.3rem; font-weight: 800; color: var(--primary); }}
        .ai-score-max {{ font-size: 0.85rem; color: #94a3b8; }}
        .ai-place-breakdown {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .ai-place-breakdown span {{ font-size: 0.75rem; padding: 4px 8px; background: #f1f5f9; border-radius: 6px; color: #475569; cursor: help; }}
        .ai-place-reqs {{ display: flex; gap: 6px; margin-top: 6px; }}
        .ai-conf-badge {{ font-size: 0.7rem; padding: 3px 8px; border-radius: 10px; font-weight: 600; }}
        .ai-conf-badge.high {{ background: rgba(16, 185, 129, 0.15); color: #059669; }}
        .ai-conf-badge.medium {{ background: rgba(245, 158, 11, 0.15); color: #b45309; }}
        .ai-conf-badge.low {{ background: rgba(148, 163, 184, 0.15); color: #475569; }}
        .search-process {{ position: relative; padding: 20px 0; }}
        .process-step {{ display: flex; margin-bottom: 30px; opacity: 0.5; transform: translateX(-20px); transition: opacity 0.5s ease, transform 0.5s ease; }}
        .process-step.active {{ opacity: 1; transform: translateX(0); }}
        .step-icon {{ flex: 0 0 60px; height: 60px; border-radius: 50%; background-color: var(--primary-light); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; margin-right: 20px; position: relative; }}
        .step-number {{ position: absolute; top: -5px; right: -5px; width: 25px; height: 25px; border-radius: 50%; background-color: var(--primary-dark); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; }}
        .step-content {{ flex: 1; }}
        .step-title {{ font-size: 1.3rem; color: var(--primary-dark); margin-bottom: 10px; }}
        .step-details {{ background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.05); }}
        .code-block {{ background-color: #2c3e50; color: #e6e6e6; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9rem; margin: 15px 0; white-space: pre; overflow-x: auto; }}
        .highlight-text {{ background-color: rgba(6, 214, 160, 0.2); color: var(--brand-primary-dark, #05445E); padding: 3px 6px; border-radius: 4px; font-weight: bold; }}  /* 薄荷绿高亮 */
        .search-animation {{ height: 200px; position: relative; display: flex; align-items: center; justify-content: center; margin: 20px 0; }}
        .radar-circle {{ position: absolute; width: 50px; height: 50px; border-radius: 50%; background-color: rgba(10, 77, 104, 0.1); animation: radar 3s infinite; }}  /* 深海蓝脉冲 */
        .radar-circle:nth-child(1) {{ animation-delay: 0s; }} .radar-circle:nth-child(2) {{ animation-delay: 1s; }} .radar-circle:nth-child(3) {{ animation-delay: 2s; }}
        .center-point {{ width: 15px; height: 15px; border-radius: 50%; background-color: var(--brand-accent, #FF6B35); z-index: 2; box-shadow: 0 0 0 5px rgba(255, 107, 53, 0.3); }}  /* 日落橙中心点 */
        .map-operation-animation {{ height: 200px; position: relative; border-radius: 8px; overflow: hidden; background-color: #f5f5f5; margin: 20px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
        .map-bg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23f0f0f0"/><path d="M0,0 L100,0 L100,100 L0,100 Z" fill="none" stroke="%23ccc" stroke-width="0.5"/><path d="M50,0 L50,100 M0,50 L100,50" stroke="%23ccc" stroke-width="0.5"/></svg>'); background-size: 50px 50px; opacity: 0.7; }}
        .map-cursor {{ position: absolute; width: 20px; height: 20px; background-color: rgba(255, 107, 53, 0.7); border-radius: 50%; top: 50%; left: 30%; transform: translate(-50%, -50%); animation: mapCursor 4s infinite ease-in-out; z-index: 2; }}  /* 日落橙光标 */
        .map-search-indicator {{ position: absolute; width: 80px; height: 80px; border: 2px dashed rgba(10, 77, 104, 0.6); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); animation: mapSearch 3s infinite ease-in-out; z-index: 1; }}  /* 深海蓝搜索圈 */
        @keyframes mapCursor {{ 0% {{ left: 30%; top: 30%; }} 30% {{ left: 60%; top: 40%; }} 60% {{ left: 40%; top: 70%; }} 100% {{ left: 30%; top: 30%; }} }}
        @keyframes mapSearch {{ 0% {{ width: 30px; height: 30px; opacity: 1; }} 100% {{ width: 150px; height: 150px; opacity: 0; }} }}
        @keyframes radar {{ 0% {{ width: 40px; height: 40px; opacity: 1; }} 100% {{ width: 300px; height: 300px; opacity: 0; }} }}
        .ranking-result {{ margin-top: 15px; }}
        .result-bar {{ height: 30px; background-color: var(--primary); color: white; margin-bottom: 8px; border-radius: 15px; padding: 0 15px; display: flex; align-items: center; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1); animation: growBar 2s ease; transform-origin: left; }}
        @keyframes growBar {{ 0% {{ width: 0; }} 100% {{ width: 100%; }} }}
        .mt-4 {{ margin-top: 1rem; }}
        @media (max-width: 768px) {{ .cafe-grid {{ grid-template-columns: 1fr; }} .transportation-info {{ grid-template-columns: 1fr; }} header {{ padding: 40px 0 80px; }} .header-logo {{ font-size: 2.2rem; }} .process-step {{ flex-direction: column; }} .step-icon {{ margin-bottom: 15px; margin-right: 0; }} }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-logo">
                <i class='bx {cfg["icon_header"]} coffee-icon'></i>{cfg["topic"]}
            </div>
            <div class="header-subtitle">为您找到的最佳会面{cfg["noun_plural"]}</div>
        </div>
    </header>

    <div class="container main-content">
        <div class="card glass-card">
            <h2 class="section-title"><i class='bx bx-info-circle'></i>推荐摘要</h2>
            <div class="summary-card">
                <div class="summary-item">
                    <div class="summary-label">参与地点数</div>
                    <div class="summary-value">{len(locations)} 个地点</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">推荐{cfg["noun_plural"]}数</div>
                    <div class="summary-value">{len(places)} 家{cfg["noun_plural"]}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">特殊需求</div>
                    <div class="summary-value">{user_requirements or "无特殊需求"}</div>
                </div>
            </div>
        </div>
        {search_process_html}
        <div class="card glass-card">
            <h2 class="section-title"><i class='bx bx-map-pin'></i>地点信息</h2>
            <table class="location-table">
                <thead><tr><th>序号</th><th>地点名称</th><th>详细地址</th></tr></thead>
                <tbody>{location_rows_html}</tbody>
            </table>
        </div>
        <div class="card glass-card">
            <h2 class="section-title"><i class='bx bx-map-alt'></i>地图展示</h2>
            <div class="map-container">
                <div id="map"></div>
                <div class="map-legend">
                    <div class="legend-item"><div class="legend-color legend-center"></div><span>最佳会面点</span></div>
                    <div class="legend-item"><div class="legend-color legend-location"></div><span>所在地点</span></div>
                    <div class="legend-item"><div class="legend-color legend-place"></div><span>{cfg["map_legend"]}</span></div>
                </div>
            </div>
        </div>
        <div class="card glass-card">
            <h2 class="section-title"><i class='bx {cfg["icon_section"]}'></i>推荐{cfg["noun_plural"]}</h2>
            <div class="cafe-grid">
                {place_cards_html}
            </div>
        </div>
        <div class="card glass-card">
            <h2 class="section-title"><i class='bx bx-car'></i>交通与停车建议</h2>
            <div class="transportation-info">
                <div class="transport-card">
                    <h3 class="transport-title"><i class='bx bx-trip'></i>前往方式</h3>
                    <p>最佳会面点位于<span class="center-coords">{center_point[0]:.6f}, {center_point[1]:.6f}</span>附近</p>
                    <ul class="transport-list">{location_distance_html}</ul>
                </div>
                <div class="transport-card">
                    <h3 class="transport-title"><i class='bx bxs-car-garage'></i>智能出行建议</h3>
                    <ul class="transport-list">
                        {transport_tips_html}
                    </ul>
                </div>
            </div>
            <a href="/" class="btn-modern btn-primary-modern">
                <i class='bx bx-left-arrow-alt'></i>返回首页
            </a>
        </div>
    </div>
    <footer class="footer">
        <div class="container">
            <p>© {datetime.now().year} {cfg["topic"]} - 智能{cfg["noun_singular"]}推荐服务 | 数据来源：高德地图</p>
        </div>
    </footer>
    <script type="text/javascript">
        var markersData = {markers_json};
        window._AMapSecurityConfig = {{ securityJsCode: "{amap_security_js_code}" }};
        window.onload = function() {{
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = 'https://webapi.amap.com/loader.js';
            script.onload = function() {{
                AMapLoader.load({{
                    key: "{self.api_key}", 
                    version: "2.0",
                    plugins: ["AMap.Scale", "AMap.ToolBar"],
                    AMapUI: {{ version: "1.1", plugins: ["overlay/SimpleMarker"] }}
                }})
                .then(function(AMap) {{ initMap(AMap); }})
                .catch(function(e) {{ console.error('地图加载失败:', e); }});
            }};
            document.body.appendChild(script);
            animateCafeCards(); 
        }};
        function initMap(AMap) {{
            var map = new AMap.Map('map', {{
                zoom: 12, center: [{center_point[0]}, {center_point[1]}],
                resizeEnable: true, viewMode: '3D'
            }});
            map.addControl(new AMap.ToolBar()); map.addControl(new AMap.Scale());
            var mapMarkers = []; 
            markersData.forEach(function(item) {{
                var markerContent, position = new AMap.LngLat(item.position[0], item.position[1]);
                var color = '#e74c3c';
                var labelText = '';
                if (item.icon === 'center') {{
                    color = '#2ecc71';
                    labelText = '最佳会面点';
                }} else if (item.icon === 'location') {{
                    color = '#3498db';
                    // Extract location name from "地点N: XXX" format
                    labelText = item.name.includes(': ') ? item.name.split(': ')[1] : item.name;
                }}

                // For center and location markers, show label with name
                if (item.icon === 'center' || item.icon === 'location') {{
                    markerContent = `<div style="display:flex;flex-direction:column;align-items:center;">
                        <div style="background-color: ${{color}}; width: 28px; height: 28px; border-radius: 14px; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>
                        <div style="background: white; padding: 4px 8px; border-radius: 4px; margin-top: 4px; font-size: 12px; font-weight: bold; color: #333; box-shadow: 0 2px 6px rgba(0,0,0,0.15); white-space: nowrap; max-width: 120px; overflow: hidden; text-overflow: ellipsis;">${{labelText}}</div>
                    </div>`;
                }} else {{
                    markerContent = `<div style="background-color: ${{color}}; width: 24px; height: 24px; border-radius: 12px; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3);"></div>`;
                }}

                var marker = new AMap.Marker({{
                    position: position, content: markerContent,
                    title: item.name, anchor: 'center', offset: new AMap.Pixel(0, item.icon === 'place' ? 0 : -20)
                }});
                var infoWindow = new AMap.InfoWindow({{
                    content: '<div style="padding:10px;font-size:14px;">' + item.name + '</div>',
                    offset: new AMap.Pixel(0, -12)
                }});
                marker.on('click', function() {{ infoWindow.open(map, marker.getPosition()); }});
                mapMarkers.push(marker);
                marker.setMap(map);
            }});
            if (markersData.length > 1) {{
                var pathCoordinates = [];
                markersData.filter(item => item.icon !== 'place').forEach(function(item) {{ 
                    pathCoordinates.push(new AMap.LngLat(item.position[0], item.position[1]));
                }});
                if (pathCoordinates.length > 1) {{ 
                    var polyline = new AMap.Polyline({{
                        path: pathCoordinates, strokeColor: '#3498db', strokeWeight: 4,
                        strokeStyle: 'dashed', strokeDasharray: [5, 5], lineJoin: 'round'
                    }});
                    polyline.setMap(map);
                }}
            }}
            if (mapMarkers.length > 0) {{ 
                 map.setFitView(mapMarkers);
            }}
        }}
        function animateCafeCards() {{
            const cards = document.querySelectorAll('.cafe-card');
            if ('IntersectionObserver' in window) {{
                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            entry.target.style.opacity = 1;
                            entry.target.style.transform = 'translateY(0)';
                            observer.unobserve(entry.target);
                        }}
                    }});
                }}, {{ threshold: 0.1 }});
                cards.forEach((card, index) => {{
                    card.style.opacity = 0; card.style.transform = 'translateY(30px)';
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    card.style.transitionDelay = (index * 0.1) + 's';
                    observer.observe(card);
                }});
            }} else {{
                cards.forEach((card, index) => {{
                    card.style.opacity = 0; card.style.transform = 'translateY(30px)';
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    setTimeout(() => {{ card.style.opacity = 1; card.style.transform = 'translateY(0)'; }}, 300 + (index * 100));
                }});
            }}
        }}
    </script>

    <!-- Modern Toast Notification System -->
    <script src="/public/js/toast.js"></script>
</body>
</html>"""
        return html_content

    def _format_result_text(
        self,
        locations: List[Dict],
        places: List[Dict], 
        html_path: str,
        keywords: str 
    ) -> str:
        primary_keyword = keywords.split("、")[0] if keywords else "场所"
        cfg = self._get_place_config(primary_keyword)
        num_places = len(places)

        result = [
            f"## 已为您找到{num_places}家适合会面的{cfg['noun_plural']}", 
            "",
            f"### 推荐{cfg['noun_plural']}:", 
        ]
        for i, place in enumerate(places):
            rating = place.get("biz_ext", {}).get("rating", "暂无评分")
            address = place.get("address", "地址未知")
            result.append(f"{i+1}. **{place['name']}** (评分: {rating})")
            result.append(f"   地址: {address}")
            result.append("")
        
        html_file_basename = os.path.basename(html_path)
        result.append(f"HTML页面: {html_file_basename}") 
        result.append(f"可在浏览器中打开查看详细地图和{cfg['noun_plural']}信息。") 

        return "\n".join(result)

    def _generate_search_process(
        self,
        locations: List[Dict],
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str,
        places: List[Dict] = None  # 新增：传入推荐结果用于显示评分详情
    ) -> str:
        primary_keyword = keywords.split("、")[0] if keywords else "场所"
        cfg = self._get_place_config(primary_keyword)
        search_steps = []

        # Step 1: 位置分析 - 显示坐标信息
        location_analysis = "<div class='ai-location-list'>"
        for idx, loc in enumerate(locations):
            lng, lat = loc.get('lng', 0), loc.get('lat', 0)
            location_analysis += f"""
            <div class='ai-location-item'>
                <span class='ai-loc-num'>{idx+1}</span>
                <div class='ai-loc-info'>
                    <strong>{loc['name']}</strong>
                    <span class='ai-coords'>({lat:.4f}°N, {lng:.4f}°E)</span>
                </div>
            </div>"""
        location_analysis += "</div>"
        search_steps.append({
            "icon": "bx-map-pin", "title": "Step 1: 位置解析与地理编码",
            "content": f"<p>成功解析 <span class='highlight-text'>{len(locations)}</span> 个地点坐标，准备计算最优会面点...</p>{location_analysis}"
        })

        # Step 2: 智能中点计算 - 显示球面几何算法
        center_lat, center_lng = center_point[1], center_point[0]
        algo_type = "球面几何中点算法" if len(locations) == 2 else "多点质心算法"
        search_steps.append({
            "icon": "bx-math", "title": "Step 2: 智能中点计算",
            "content": f"""
            <p>使用 <span class='highlight-text'>{algo_type}</span> 计算最优会面点：</p>
            <div class="ai-algo-box">
                <div class="ai-algo-formula">
                    <i class='bx bx-target-lock'></i>
                    <div>
                        <span class="ai-algo-label">最佳会面点坐标</span>
                        <span class="ai-algo-value">{center_lat:.6f}°N, {center_lng:.6f}°E</span>
                    </div>
                </div>
                <div class="ai-algo-note">
                    {f'采用球面几何学计算两点间的真实大圆中点，比简单平均更精确' if len(locations) == 2 else f'计算{len(locations)}个位置的地理质心，确保对所有人公平'}
                </div>
            </div>
            <div class="map-operation-animation">
                <div class="map-bg"></div> <div class="map-cursor"></div> <div class="map-search-indicator"></div>
            </div>"""
        })

        # Step 3: 需求解析 - 显示三层匹配机制
        requirement_analysis = ""
        if user_requirements:
            requirement_keywords_map = {
                "停车": ["停车", "车位", "停车场"], "安静": ["安静", "环境好", "氛围"],
                "商务": ["商务", "会议", "办公"], "交通": ["交通", "地铁", "公交"],
                "WiFi": ["wifi", "无线", "网络"], "包间": ["包间", "私密", "独立"]
            }
            detected_requirements = [key for key, kw_list in requirement_keywords_map.items() if any(kw.lower() in user_requirements.lower() for kw in kw_list)]
            if detected_requirements:
                req_tags = "".join([f"<span class='ai-req-tag'>{req}</span>" for req in detected_requirements])
                requirement_analysis = f"""
                <p>从您的需求 "<em>{user_requirements}</em>" 中识别到：</p>
                <div class="ai-req-detected">{req_tags}</div>
                <div class="ai-matching-layers">
                    <div class="ai-layer">
                        <span class="ai-layer-badge high">Layer 1</span>
                        <span>POI标签匹配 <span class="ai-layer-conf">高置信度</span></span>
                    </div>
                    <div class="ai-layer">
                        <span class="ai-layer-badge medium">Layer 2</span>
                        <span>品牌知识库匹配 <span class="ai-layer-conf">中置信度</span></span>
                    </div>
                    <div class="ai-layer">
                        <span class="ai-layer-badge low">Layer 3</span>
                        <span>场所类型推断 <span class="ai-layer-conf">低置信度</span></span>
                    </div>
                </div>"""
            else:
                requirement_analysis = f"<p>未检测到特定需求关键词，将基于综合评分推荐最佳{cfg['noun_plural']}。</p>"
        else:
            requirement_analysis = f"<p>未提供特殊需求，将使用多维度评分系统推荐{cfg['noun_plural']}。</p>"
        search_steps.append({"icon": "bx-brain", "title": "Step 3: 需求语义解析", "content": requirement_analysis})

        # Step 4: 场所检索
        search_places_explanation = f"""
        <p>以最佳会面点为圆心，在 <span class='highlight-text'>2公里</span> 范围内检索 "{primary_keyword}" 相关场所...</p>
        <div class="search-animation">
            <div class="radar-circle"></div> <div class="radar-circle"></div> <div class="radar-circle"></div>
            <div class="center-point"></div>
        </div>"""
        search_steps.append({"icon": "bx-search-alt", "title": f"Step 4: POI检索", "content": search_places_explanation})

        # Step 5: 智能评分 - 显示评分维度
        ranking_explanation = f"""
        <p>使用 <span class='highlight-text'>V2 多维度评分系统</span> 对候选场所进行智能排序：</p>
        <div class="ai-score-dimensions">
            <div class="ai-dim">
                <div class="ai-dim-header">
                    <span class="ai-dim-name">基础分</span>
                    <span class="ai-dim-max">30分</span>
                </div>
                <div class="ai-dim-bar"><div class="ai-dim-fill" style="width: 100%;"></div></div>
                <span class="ai-dim-desc">商家评分 × 6</span>
            </div>
            <div class="ai-dim">
                <div class="ai-dim-header">
                    <span class="ai-dim-name">距离分</span>
                    <span class="ai-dim-max">25分</span>
                </div>
                <div class="ai-dim-bar"><div class="ai-dim-fill" style="width: 83%;"></div></div>
                <span class="ai-dim-desc">非线性衰减，500m内满分</span>
            </div>
            <div class="ai-dim">
                <div class="ai-dim-header">
                    <span class="ai-dim-name">热度分</span>
                    <span class="ai-dim-max">20分</span>
                </div>
                <div class="ai-dim-bar"><div class="ai-dim-fill" style="width: 67%;"></div></div>
                <span class="ai-dim-desc">评论数(log) + 图片数</span>
            </div>
            <div class="ai-dim">
                <div class="ai-dim-header">
                    <span class="ai-dim-name">场景分</span>
                    <span class="ai-dim-max">15分</span>
                </div>
                <div class="ai-dim-bar"><div class="ai-dim-fill" style="width: 50%;"></div></div>
                <span class="ai-dim-desc">关键词匹配度</span>
            </div>
            <div class="ai-dim">
                <div class="ai-dim-header">
                    <span class="ai-dim-name">需求分</span>
                    <span class="ai-dim-max">10分</span>
                </div>
                <div class="ai-dim-bar"><div class="ai-dim-fill" style="width: 33%;"></div></div>
                <span class="ai-dim-desc">三层匹配算法</span>
            </div>
        </div>"""
        search_steps.append({"icon": "bx-calculator", "title": "Step 5: 多维度智能评分", "content": ranking_explanation})

        # Step 6: 评分结果 - 显示Top 3场所的评分详情
        if places and len(places) > 0:
            top_places_html = "<div class='ai-top-results'>"
            for idx, place in enumerate(places[:3]):
                name = place.get('name', '未知')
                total_score = place.get('_score', 0)
                breakdown = place.get('_score_breakdown', {})
                matched_reqs = place.get('_matched_requirements', [])
                confidence_map = place.get('_requirement_confidence', {})

                # 评分详情
                base = breakdown.get('base_score', 0)
                dist = breakdown.get('distance_score', 0)
                pop = breakdown.get('popularity_score', 0)
                scene = breakdown.get('scenario_score', 0)
                req = breakdown.get('requirement_score', 0)

                # 需求匹配标签
                req_badges = ""
                if matched_reqs:
                    for r in matched_reqs[:3]:
                        conf = confidence_map.get(r, 'low')
                        req_badges += f"<span class='ai-conf-badge {conf}'>{r}</span>"

                medal = ["🥇", "🥈", "🥉"][idx]
                top_places_html += f"""
                <div class="ai-place-result">
                    <div class="ai-place-rank">{medal}</div>
                    <div class="ai-place-info">
                        <div class="ai-place-name">{name}</div>
                        <div class="ai-place-score">
                            <span class="ai-total-score">{total_score:.0f}</span><span class="ai-score-max">/100</span>
                        </div>
                    </div>
                    <div class="ai-place-breakdown">
                        <span title="基础分">⭐{base:.0f}</span>
                        <span title="距离分">📍{dist:.0f}</span>
                        <span title="热度分">🔥{pop:.0f}</span>
                        <span title="场景分">🎯{scene:.0f}</span>
                        <span title="需求分">✓{req:.0f}</span>
                    </div>
                    {f'<div class="ai-place-reqs">{req_badges}</div>' if req_badges else ''}
                </div>"""
            top_places_html += "</div>"
            search_steps.append({
                "icon": "bx-trophy",
                "title": "Step 6: 推荐结果",
                "content": f"<p>经过智能评分，为您推荐以下最佳会面地点：</p>{top_places_html}"
            })
        else:
            search_steps.append({
                "icon": "bx-trophy",
                "title": "Step 6: 推荐结果",
                "content": f"<p>正在生成{cfg['noun_plural']}推荐结果...</p>"
            }) 

        search_process_html = ""
        for idx, step in enumerate(search_steps):
            search_process_html += f"""
            <div class="process-step" data-step="{idx+1}">
                <div class="step-icon"><i class='bx {step["icon"]}'></i><div class="step-number">{idx+1}</div></div>
                <div class="step-content"><h3 class="step-title">{step["title"]}</h3><div class="step-details">{step["content"]}</div></div>
            </div>"""

        search_process_javascript = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const steps = document.querySelectorAll('.process-step');
            let currentStep = 0;
            function showNextStep() {
                if (currentStep < steps.length) {
                    steps[currentStep].classList.add('active');
                    currentStep++;
                    setTimeout(showNextStep, 1500); 
                }
            }
            setTimeout(showNextStep, 500); 
        });
        </script>"""
        return f"""
        <div class="card glass-card search-process-card">
            <details class="ai-thinking-details">
                <summary class="ai-thinking-summary">
                    <div class="ai-brain-icon">
                        <i class='bx bx-brain'></i>
                    </div>
                    <div class="ai-thinking-content">
                        <div class="ai-thinking-header">
                            <span class="ai-thinking-title">AI 搜索过程</span>
                            <span class="ai-thinking-badge">Explainable</span>
                        </div>
                        <span class="ai-thinking-hint">点击展开 Agent 思维链可视化</span>
                    </div>
                    <div class="ai-thinking-expand">
                        <span class="expand-text">展开</span>
                        <span class="collapse-text">收起</span>
                        <i class='bx bx-chevron-down ai-thinking-arrow'></i>
                    </div>
                </summary>
                <div class="search-process">{search_process_html}</div>
            </details>
            {search_process_javascript}
        </div>"""

