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
                "MeetSpot让2-10人团队快速找到公平会面中点, 智能推荐咖啡馆、餐厅、共享空间, 自动输出路线、"
                "预算与结构化数据, 15秒生成可索引聚会页面; Midpoint engine saves 30% commute, fuels SEO-ready recaps with clear CTA."
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
                f"{city or '所在城市'}聚会需要公平中点? MeetSpot根据2-10人轨迹计算平衡路线, 推荐{venue_snippet}等场所, "
                "输出中文/英文场地文案、预算与交通信息, 15秒生成可索引城市着陆页; Local insights boost trust, shareable cards unlock faster decisions."
            )
            keywords = f"{city},{city_en},meeting location,{venue_snippet},midpoint"
        elif page_type == "about":
            title = "About MeetSpot - How We Find Perfect Meeting Locations | 关于我们"
            description = (
                "MeetSpot团队由地图算法、内容运营与产品负责人组成, 公开使命、技术栈、治理方式, 分享用户案例、AMAP合规、安全策略与开源路线图; "
                "Learn how we guarantee equitable experiences backed by ongoing UX research。"
            )
            keywords = "about meetspot,meeting algorithm,location technology,关于,聚会算法"
        elif page_type == "faq":
            title = "FAQ - Meeting Location Questions Answered | 常见问题 - MeetSpot"
            description = (
                "覆盖聚会地点、费用、功能等核心提问, 提供结构化答案, 支持Google FAQ Schema, 让用户与搜索引擎获得清晰指导, "
                "并附上联系入口与下一步CTA, FAQ hub helps planners resolve objections faster and improve conversions。"
            )
            keywords = "faq,meeting questions,location help,常见问题,使用指南"
        elif page_type == "how_it_works":
            title = "How MeetSpot Works | 智能聚会地点中点计算流程"
            description = (
                "4步流程涵盖收集地址、平衡权重、筛选场地与导出SEO文案, 附带动图、清单和风控提示, 指导团队15分钟内发布可索引页面; "
                "Learn safeguards, KPIs, stakeholder handoffs, and post-launch QA behind MeetSpot。"
            )
            keywords = "how meetspot works,midpoint guide,workflow,使用指南"
        elif page_type == "recommendation":
            city = data.get("city", "未知城市")
            keyword = data.get("keyword", "聚会地点")
            count = data.get("locations_count", 2)
            title = f"{city}{keyword}推荐 - {count}人聚会最佳会面点 | MeetSpot"
            description = (
                f"{city}{count}人{keyword}推荐由MeetSpot中点引擎生成, 结合每位参与者的路程、预算与场地偏好, "
                "给出评分、热力图和可复制行程; Share SEO-ready cards、CTA, keep planning transparent, document-ready for clients, and measurable。"
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
        if page_type == "website":
            search_path = data.get("search_url", "/search")
            return {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "MeetSpot",
                "url": base_url + "/",
                "inLanguage": "zh-CN",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"{base_url}{search_path}?q={{query}}",
                    "query-input": "required name=query",
                },
            }
        if page_type == "organization":
            return {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "MeetSpot",
                "url": base_url,
                "logo": f"{base_url}/static/images/og-image.png",
                "foundingDate": "2023-08-01",
                "contactPoint": [
                    {
                        "@type": "ContactPoint",
                        "contactType": "customer support",
                        "email": "hello@meetspot.app",
                        "availableLanguage": ["zh-CN", "en"],
                    }
                ],
                "sameAs": [
                    "https://github.com/JasonRobertDestiny/MeetSpot",
                    "https://jasonrobert.me/",
                ],
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
        if page_type == "how_to":
            steps = data.get("steps", [])
            if not steps:
                return {}
            return {
                "@context": "https://schema.org",
                "@type": "HowTo",
                "name": data.get("name", "如何使用MeetSpot"),
                "description": data.get(
                    "description",
                    "Step-by-step guide to plan a fair meetup with MeetSpot.",
                ),
                "totalTime": data.get("total_time", "PT15M"),
                "inLanguage": "zh-CN",
                "step": [
                    {
                        "@type": "HowToStep",
                        "name": step["name"],
                        "text": step["text"],
                    }
                    for step in steps
                ],
                "supply": data.get("supplies", ["参与者地址", "交通方式偏好"]),
                "tool": data.get("tools", ["MeetSpot Dashboard"]),
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
