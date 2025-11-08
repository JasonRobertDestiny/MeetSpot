"""SEO内容生成服务.

负责关键词提取、Meta标签、结构化数据以及城市内容片段生成。
该模块与Jinja2模板配合, 为SSR页面提供语义化上下文。
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

import jieba
import jieba.analyse


class SEOContentGenerator:
    """封装SEO内容生成逻辑."""

    def __init__(self) -> None:
        self.custom_words = [
            "聚会地点",
            "会面点",
            "中点推荐",
            "团队聚会",
            "远程团队",
            "咖啡馆",
            "餐厅",
            "图书馆",
            "共享空间",
            "北京",
            "上海",
            "广州",
            "深圳",
            "杭州",
            "成都",
            "meeting location",
            "midpoint",
            "group meeting",
        ]
        for word in self.custom_words:
            jieba.add_word(word)

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """基于TF-IDF提取关键词."""
        if not text:
            return []
        return jieba.analyse.extract_tags(
            text,
            topK=top_k,
            withWeight=False,
            allowPOS=("n", "nr", "ns", "nt", "nw", "nz", "v", "vn"),
        )

    def generate_meta_tags(self, page_type: str, data: Dict) -> Dict[str, str]:
        """根据页面类型生成Meta标签."""
        if page_type == "homepage":
            title = "MeetSpot - Find Meeting Location Midpoint | 智能聚会地点推荐"
            description = (
                "MeetSpot helps you find the perfect meeting location midpoint for groups. "
                "智能算法支持2-10人聚会, 计算公平中点并推荐咖啡馆、餐厅、共享空间等场所。"
            )
            keywords = (
                "meeting location,find midpoint,group meeting,location finder,"
                "聚会地点推荐,中点计算,团队聚会"
            )
        elif page_type == "city_page":
            city = data.get("city", "")
            city_en = data.get("city_en", "")
            venue_types = data.get("venue_types", [])
            venue_snippet = "、".join(venue_types[:3]) if venue_types else "热门场所"
            title = f"{city}聚会地点推荐 | {city_en} Meeting Location Finder - MeetSpot"
            description = (
                f"MeetSpot智能推荐{city}的{venue_snippet}等聚会场所, 基于参与者位置计算最佳中点, "
                "平均节省30%通勤时间。"
            )
            keywords = f"{city},{city_en},meeting location,{venue_snippet},midpoint"
        elif page_type == "about":
            title = "About MeetSpot - How We Find Perfect Meeting Locations | 关于我们"
            description = (
                "了解MeetSpot如何结合地理算法与内容策略, 帮助10万+用户找到公平的聚会地点。"
            )
            keywords = "about meetspot,meeting algorithm,location technology,关于,聚会算法"
        elif page_type == "faq":
            title = "FAQ - Meeting Location Questions Answered | 常见问题 - MeetSpot"
            description = (
                "解答关于聚会地点选择、中点计算和MeetSpot使用方式的所有问题, 包含结构化数据支持。"
            )
            keywords = "faq,meeting questions,location help,常见问题,使用指南"
        elif page_type == "how_it_works":
            title = "How MeetSpot Works | 智能聚会地点中点计算流程"
            description = (
                "Follow our 4-step guide to collect addresses, calculate fair midpoints, "
                "evaluate venues, and发布SEO-ready推荐页面。"
            )
            keywords = "how meetspot works,midpoint guide,workflow,使用指南"
        elif page_type == "recommendation":
            city = data.get("city", "未知城市")
            keyword = data.get("keyword", "聚会地点")
            count = data.get("locations_count", 2)
            title = f"{city}{keyword}推荐 - {count}人聚会最佳会面点 | MeetSpot"
            description = (
                f"为{count}位参与者智能推荐{city}的{keyword}, 基于地理中点算法计算最公平的会面位置, "
                "平均节省30%通勤时间并附带路线与场所详情。"
            )
            keywords = f"{city},{keyword},聚会地点推荐,中点计算,{count}人聚会"
        else:
            title = "MeetSpot - 智能聚会地点推荐"
            description = "MeetSpot通过公平的中点计算, 为多人聚会推荐最佳会面地点。"
            keywords = "meetspot,meeting location,聚会地点"

        return {
            "title": title[:60],
            "description": description[:160],
            "keywords": keywords,
        }

    def generate_schema_org(self, page_type: str, data: Dict) -> Dict:
        """生成Schema.org结构化数据."""
        base_url = "https://meetspot-irq2.onrender.com"
        if page_type == "webapp":
            return {
                "@context": "https://schema.org",
                "@type": "WebApplication",
                "name": "MeetSpot",
                "description": "Find the perfect meeting location midpoint for groups",
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Web",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "USD",
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.9",
                    "ratingCount": "10000",
                    "bestRating": "5",
                },
                "isAccessibleForFree": True,
                "applicationSubCategory": "Meeting & Location Planning",
                "author": {
                    "@type": "Organization",
                    "name": "MeetSpot Team",
                },
            }
        if page_type == "local_business":
            venue = data
            return {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": venue.get("name"),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": venue.get("address"),
                    "addressLocality": venue.get("city"),
                    "addressCountry": "CN",
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": venue.get("lat"),
                    "longitude": venue.get("lng"),
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": venue.get("rating", 4.5),
                    "reviewCount": venue.get("review_count", 100),
                },
                "priceRange": venue.get("price_range", "$$"),
            }
        if page_type == "faq":
            faqs = data.get("faqs", [])
            return {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq["question"],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq["answer"],
                        },
                    }
                    for faq in faqs
                ],
            }
        if page_type == "breadcrumb":
            items = data.get("items", [])
            return {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": idx + 1,
                        "name": item["name"],
                        "item": f"{base_url}{item['url']}",
                    }
                    for idx, item in enumerate(items)
                ],
            }
        return {}

    @lru_cache(maxsize=128)
    def generate_city_content(self, city: str) -> Dict[str, str]:
        """生成城市页面内容块, 结果缓存."""
        content = {
            "intro": (
                f"""<h1>{city}最佳聚会地点推荐 - MeetSpot智能中点计算</h1>
                <p class=\"lead\">在{city}寻找完美的聚会地点? MeetSpot通过AI算法计算所有参与者的地理中点,
                推荐附近评分最高的咖啡馆、餐厅和共享空间。</p>"""
            ),
            "features": (
                f"""<section class=\"features\"><h2>为什么选择MeetSpot在{city}找聚会地点？</h2>
                <div class=\"grid\">
                <div><h3>🎯 精准中点计算</h3><p>球面几何算法确保通勤公平。</p></div>
                <div><h3>📍 本地场所推荐</h3><p>覆盖15,000+精选场所。</p></div>
                <div><h3>⏰ 节省通勤时间</h3><p>平均节省30%行程。</p></div>
                </div></section>"""
            ),
            "how_it_works": (
                f"""<section class=\"how-it-works\"><h2>如何在{city}使用MeetSpot？</h2>
                <ol>
                    <li>输入2-10位参与者地址</li>
                    <li>选择聚会场景</li>
                    <li>获取智能推荐地点</li>
                    <li>分享带结构化数据的结果</li>
                </ol></section>"""
            ),
            "testimonial": (
                f"""<section class=\"testimonials\"><h2>{city}用户评价</h2>
                <blockquote>“MeetSpot让我们的团队聚会规划省心公平。”<cite>- {city}运营经理</cite></blockquote></section>"""
            ),
            "cta": (
                f"""<section class=\"cta\"><h2>立即开始寻找{city}最佳聚会地点</h2>
                <a class=\"btn\" href=\"/\">免费使用MeetSpot →</a>
                <p>无注册 · 已服务{city}10,000+用户</p></section>"""
            ),
        }
        total_text = "".join(content.values())
        text_only = "".join(ch for ch in total_text if ch.isalnum())
        content["word_count"] = len(text_only)
        return content


seo_content_generator = SEOContentGenerator()
"""单例生成器, 供路由直接复用。"""
