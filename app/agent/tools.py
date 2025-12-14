"""MeetSpot Agent 工具集 - 封装推荐系统的核心功能"""

import json
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.tool.base import BaseTool, ToolResult
from app.logger import logger


class GeocodeTool(BaseTool):
    """地理编码工具 - 将地址转换为经纬度坐标"""

    name: str = "geocode"
    description: str = """将地址或地点名称转换为经纬度坐标。
支持各种地址格式：
- 完整地址：'北京市海淀区中关村大街1号'
- 大学简称：'北大'、'清华'、'复旦'（自动扩展为完整地址）
- 知名地标：'天安门'、'外滩'、'广州塔'
- 商圈区域：'三里屯'、'王府井'

返回地址的经纬度坐标和格式化地址。"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "address": {
                "type": "string",
                "description": "地址或地点名称，如'北京大学'、'上海市浦东新区陆家嘴'"
            }
        },
        "required": ["address"]
    }

    class Config:
        arbitrary_types_allowed = True

    def _get_recommender(self):
        """延迟加载推荐器，并确保 API key 已设置"""
        if not hasattr(self, '_cached_recommender'):
            from app.tool.meetspot_recommender import CafeRecommender
            from app.config import config
            recommender = CafeRecommender()
            # 确保 API key 已设置
            if hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
                recommender.api_key = config.amap.api_key
            object.__setattr__(self, '_cached_recommender', recommender)
        return self._cached_recommender

    async def execute(self, address: str) -> ToolResult:
        """执行地理编码"""
        try:
            recommender = self._get_recommender()
            result = await recommender._geocode(address)

            if result:
                location = result.get("location", "")
                lng, lat = location.split(",") if location else (None, None)

                return BaseTool.success_response({
                    "address": address,
                    "formatted_address": result.get("formatted_address", ""),
                    "location": location,
                    "lng": float(lng) if lng else None,
                    "lat": float(lat) if lat else None,
                    "city": result.get("city", ""),
                    "district": result.get("district", "")
                })

            return BaseTool.fail_response(f"无法解析地址: {address}")

        except Exception as e:
            logger.error(f"地理编码失败: {e}")
            return BaseTool.fail_response(f"地理编码错误: {str(e)}")


class CalculateCenterTool(BaseTool):
    """计算中心点工具 - 计算多个位置的最佳会面点"""

    name: str = "calculate_center"
    description: str = """计算多个坐标点的几何中心作为最佳会面位置。
使用球面几何算法确保在地球表面上的精确计算。
对于两个点使用球面中点公式，多个点使用加权平均。"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "coordinates": {
                "type": "array",
                "description": "坐标点列表，每个元素包含 lng（经度）、lat（纬度）和可选的 name（名称）",
                "items": {
                    "type": "object",
                    "properties": {
                        "lng": {"type": "number", "description": "经度"},
                        "lat": {"type": "number", "description": "纬度"},
                        "name": {"type": "string", "description": "位置名称（可选）"}
                    },
                    "required": ["lng", "lat"]
                }
            }
        },
        "required": ["coordinates"]
    }

    class Config:
        arbitrary_types_allowed = True

    def _get_recommender(self):
        """延迟加载推荐器，并确保 API key 已设置"""
        if not hasattr(self, '_cached_recommender'):
            from app.tool.meetspot_recommender import CafeRecommender
            from app.config import config
            recommender = CafeRecommender()
            if hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
                recommender.api_key = config.amap.api_key
            object.__setattr__(self, '_cached_recommender', recommender)
        return self._cached_recommender

    async def execute(self, coordinates: List[Dict]) -> ToolResult:
        """计算中心点"""
        try:
            if not coordinates or len(coordinates) < 2:
                return BaseTool.fail_response("至少需要2个坐标点来计算中心")

            recommender = self._get_recommender()

            # 转换为 (lng, lat) 元组列表
            coord_tuples = [(c["lng"], c["lat"]) for c in coordinates]
            center = recommender._calculate_center_point(coord_tuples)

            # 计算每个点到中心的距离
            distances = []
            for c in coordinates:
                dist = recommender._calculate_distance(center, (c["lng"], c["lat"]))
                distances.append({
                    "name": c.get("name", f"({c['lng']:.4f}, {c['lat']:.4f})"),
                    "distance_to_center": round(dist, 0)
                })

            return BaseTool.success_response({
                "center": {
                    "lng": round(center[0], 6),
                    "lat": round(center[1], 6)
                },
                "input_count": len(coordinates),
                "distances": distances,
                "max_distance": max(d["distance_to_center"] for d in distances),
                "fairness_score": round(100 - (max(d["distance_to_center"] for d in distances) -
                                               min(d["distance_to_center"] for d in distances)) / 100, 1)
            })

        except Exception as e:
            logger.error(f"计算中心点失败: {e}")
            return BaseTool.fail_response(f"计算中心点错误: {str(e)}")


class SearchPOITool(BaseTool):
    """搜索POI工具 - 在指定位置周围搜索场所"""

    name: str = "search_poi"
    description: str = """在指定中心点周围搜索各类场所（POI）。
支持搜索：咖啡馆、餐厅、图书馆、健身房、KTV、电影院、商场等。
返回场所的名称、地址、评分、距离等信息。"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "center_lng": {
                "type": "number",
                "description": "中心点经度"
            },
            "center_lat": {
                "type": "number",
                "description": "中心点纬度"
            },
            "keywords": {
                "type": "string",
                "description": "搜索关键词，如'咖啡馆'、'餐厅'、'图书馆'"
            },
            "radius": {
                "type": "integer",
                "description": "搜索半径（米），默认3000米",
                "default": 3000
            }
        },
        "required": ["center_lng", "center_lat", "keywords"]
    }

    class Config:
        arbitrary_types_allowed = True

    def _get_recommender(self):
        """延迟加载推荐器，并确保 API key 已设置"""
        if not hasattr(self, '_cached_recommender'):
            from app.tool.meetspot_recommender import CafeRecommender
            from app.config import config
            recommender = CafeRecommender()
            if hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
                recommender.api_key = config.amap.api_key
            object.__setattr__(self, '_cached_recommender', recommender)
        return self._cached_recommender

    async def execute(
        self,
        center_lng: float,
        center_lat: float,
        keywords: str,
        radius: int = 3000
    ) -> ToolResult:
        """搜索POI"""
        try:
            recommender = self._get_recommender()
            center = f"{center_lng},{center_lat}"

            places = await recommender._search_pois(
                location=center,
                keywords=keywords,
                radius=radius,
                types="",
                offset=20
            )

            if not places:
                return BaseTool.fail_response(
                    f"在 ({center_lng:.4f}, {center_lat:.4f}) 附近 {radius}米范围内"
                    f"未找到与 '{keywords}' 相关的场所"
                )

            # 简化返回数据
            simplified = []
            for p in places[:15]:  # 最多返回15个
                biz_ext = p.get("biz_ext", {}) or {}
                location = p.get("location", "")
                lng, lat = location.split(",") if location else (0, 0)

                # 计算到中心的距离
                distance = recommender._calculate_distance(
                    (center_lng, center_lat),
                    (float(lng), float(lat))
                ) if location else 0

                simplified.append({
                    "name": p.get("name", ""),
                    "address": p.get("address", ""),
                    "rating": biz_ext.get("rating", "N/A"),
                    "cost": biz_ext.get("cost", ""),
                    "location": location,
                    "lng": float(lng) if lng else None,
                    "lat": float(lat) if lat else None,
                    "distance": round(distance, 0),
                    "tel": p.get("tel", ""),
                    "tag": p.get("tag", ""),
                    "type": p.get("type", "")
                })

            # 按距离排序
            simplified.sort(key=lambda x: x.get("distance", 9999))

            return BaseTool.success_response({
                "places": simplified,
                "count": len(simplified),
                "keywords": keywords,
                "center": {"lng": center_lng, "lat": center_lat},
                "radius": radius
            })

        except Exception as e:
            logger.error(f"POI搜索失败: {e}")
            return BaseTool.fail_response(f"POI搜索错误: {str(e)}")


class GenerateRecommendationTool(BaseTool):
    """生成推荐工具 - 分析并生成最终推荐结果"""

    name: str = "generate_recommendation"
    description: str = """根据搜索结果生成最终的会面地点推荐。
分析场所的评分、距离、特色等因素，
为用户提供个性化的推荐理由和建议。"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "places": {
                "type": "array",
                "description": "候选场所列表（来自search_poi的结果）",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "场所名称"},
                        "address": {"type": "string", "description": "地址"},
                        "rating": {"type": "string", "description": "评分"},
                        "distance": {"type": "number", "description": "距中心点距离"},
                        "location": {"type": "string", "description": "坐标"}
                    }
                }
            },
            "center": {
                "type": "object",
                "description": "中心点坐标",
                "properties": {
                    "lng": {"type": "number", "description": "经度"},
                    "lat": {"type": "number", "description": "纬度"}
                },
                "required": ["lng", "lat"]
            },
            "user_requirements": {
                "type": "string",
                "description": "用户的特殊需求，如'停车方便'、'环境安静'",
                "default": ""
            },
            "recommendation_count": {
                "type": "integer",
                "description": "推荐数量，默认5个",
                "default": 5
            }
        },
        "required": ["places", "center"]
    }

    class Config:
        arbitrary_types_allowed = True

    def _get_recommender(self):
        """延迟加载推荐器，并确保 API key 已设置"""
        if not hasattr(self, '_cached_recommender'):
            from app.tool.meetspot_recommender import CafeRecommender
            from app.config import config
            recommender = CafeRecommender()
            if hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
                recommender.api_key = config.amap.api_key
            object.__setattr__(self, '_cached_recommender', recommender)
        return self._cached_recommender

    async def execute(
        self,
        places: List[Dict],
        center: Dict,
        user_requirements: str = "",
        recommendation_count: int = 5
    ) -> ToolResult:
        """生成推荐"""
        try:
            if not places:
                return BaseTool.fail_response("没有候选场所可供推荐")

            recommender = self._get_recommender()
            center_point = (center["lng"], center["lat"])

            # 使用现有的排序算法
            ranked = recommender._rank_places(
                places=places,
                center_point=center_point,
                user_requirements=user_requirements,
                keywords=""
            )

            # 取前N个推荐
            top_places = ranked[:recommendation_count]

            # 生成推荐理由
            recommendations = []
            for i, place in enumerate(top_places, 1):
                score = place.get("_score", 0)
                distance = place.get("distance", 0)
                rating = place.get("rating", "N/A")

                # 构建推荐理由
                reasons = []
                if distance <= 500:
                    reasons.append("距离中心点很近")
                elif distance <= 1000:
                    reasons.append("距离适中")

                if rating != "N/A":
                    try:
                        r = float(rating)
                        if r >= 4.5:
                            reasons.append("口碑优秀")
                        elif r >= 4.0:
                            reasons.append("评价良好")
                    except (ValueError, TypeError):
                        pass

                tag = place.get("tag", "")
                if "停车" in tag or "车位" in tag:
                    reasons.append("有停车位")
                if "wifi" in tag.lower() or "无线" in tag:
                    reasons.append("提供WiFi")

                recommendations.append({
                    "rank": i,
                    "name": place.get("name", ""),
                    "address": place.get("address", ""),
                    "rating": rating,
                    "distance": round(distance, 0),
                    "score": round(score, 1),
                    "tel": place.get("tel", ""),
                    "reasons": reasons if reasons else ["综合评分较高"],
                    "location": place.get("location", "")
                })

            return BaseTool.success_response({
                "recommendations": recommendations,
                "total_candidates": len(places),
                "user_requirements": user_requirements,
                "center": center
            })

        except Exception as e:
            logger.error(f"生成推荐失败: {e}")
            return BaseTool.fail_response(f"生成推荐错误: {str(e)}")


# 导出所有工具
__all__ = [
    "GeocodeTool",
    "CalculateCenterTool",
    "SearchPOITool",
    "GenerateRecommendationTool"
]
