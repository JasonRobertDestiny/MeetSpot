"""SEO页面路由 - 负责SSR页面与爬虫友好输出."""
from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.services.seo_content import seo_content_generator as seo_generator

router = APIRouter()
templates = Jinja2Templates(directory="templates")
limiter = Limiter(key_func=get_remote_address)


@lru_cache(maxsize=128)
def load_cities() -> List[Dict]:
    """加载城市数据, 如不存在则创建默认值."""
    cities_file = "data/cities.json"
    if not os.path.exists(cities_file):
        os.makedirs("data", exist_ok=True)
        default_payload = {"cities": []}
        with open(cities_file, "w", encoding="utf-8") as fh:
            json.dump(default_payload, fh, ensure_ascii=False, indent=2)
        return []

    with open(cities_file, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("cities", [])


def _get_city_by_slug(city_slug: str) -> Optional[Dict]:
    for city in load_cities():
        if city.get("slug") == city_slug:
            return city
    return None


def _build_schema_list(*schemas: Dict) -> List[Dict]:
    return [schema for schema in schemas if schema]


@router.get("/", response_class=HTMLResponse)
@limiter.limit("60/minute")
async def homepage(request: Request):
    """首页 - 提供SEO友好内容."""

    meta_tags = seo_generator.generate_meta_tags("homepage", {})
    faq_schema = seo_generator.generate_schema_org(
        "faq",
        {
            "faqs": [
                {
                    "question": "MeetSpot如何计算最佳聚会地点？",
                    "answer": "我们使用球面几何算法计算所有参与者位置的地理中点, 再推荐附近高评分场所。",
                },
                {
                    "question": "MeetSpot支持多少人的聚会?",
                    "answer": "默认支持2-10人, 满足大多数团队与家人聚会需求。",
                },
                {
                    "question": "需要付费吗?",
                    "answer": "MeetSpot完全免费且开源, 无需注册即可使用。",
                },
            ]
        },
    )
    schema_list = _build_schema_list(
        seo_generator.generate_schema_org("webapp", {}),
        seo_generator.generate_schema_org("website", {"search_url": "/search"}),
        seo_generator.generate_schema_org("organization", {}),
        seo_generator.generate_schema_org(
            "breadcrumb", {"items": [{"name": "Home", "url": "/"}]}
        ),
        faq_schema,
    )

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "meta_title": meta_tags["title"],
            "meta_description": meta_tags["description"],
            "meta_keywords": meta_tags["keywords"],
            "canonical_url": "https://meetspot-irq2.onrender.com/",
            "schema_jsonld": schema_list,
            "breadcrumbs": [],
            "cities": load_cities(),
        },
    )


@router.get("/meetspot/{city_slug}", response_class=HTMLResponse)
@limiter.limit("60/minute")
async def city_page(request: Request, city_slug: str):
    city = _get_city_by_slug(city_slug)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    meta_tags = seo_generator.generate_meta_tags(
        "city_page",
        {
            "city": city.get("name"),
            "city_en": city.get("name_en"),
            "venue_types": city.get("popular_venues", []),
        },
    )
    breadcrumb = seo_generator.generate_schema_org(
        "breadcrumb",
        {
            "items": [
                {"name": "Home", "url": "/"},
                {"name": city.get("name"), "url": f"/meetspot/{city_slug}"},
            ]
        },
    )
    schema_list = _build_schema_list(
        seo_generator.generate_schema_org("webapp", {}),
        seo_generator.generate_schema_org("website", {"search_url": "/search"}),
        seo_generator.generate_schema_org("organization", {}),
        breadcrumb,
    )
    city_content = seo_generator.generate_city_content(city.get("name", ""))

    return templates.TemplateResponse(
        "pages/city.html",
        {
            "request": request,
            "meta_title": meta_tags["title"],
            "meta_description": meta_tags["description"],
            "meta_keywords": meta_tags["keywords"],
            "canonical_url": f"https://meetspot-irq2.onrender.com/meetspot/{city_slug}",
            "schema_jsonld": schema_list,
            "breadcrumbs": [
                {"name": "首页", "url": "/"},
                {"name": city.get("name"), "url": f"/meetspot/{city_slug}"},
            ],
            "city": city,
            "city_content": city_content,
        },
    )


@router.get("/about", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def about_page(request: Request):
    meta_tags = seo_generator.generate_meta_tags("about", {})
    schema_list = _build_schema_list(
        seo_generator.generate_schema_org("organization", {}),
        seo_generator.generate_schema_org(
            "breadcrumb",
            {
                "items": [
                    {"name": "Home", "url": "/"},
                    {"name": "About", "url": "/about"},
                ]
            },
        )
    )
    return templates.TemplateResponse(
        "pages/about.html",
        {
            "request": request,
            "meta_title": meta_tags["title"],
            "meta_description": meta_tags["description"],
            "meta_keywords": meta_tags["keywords"],
            "canonical_url": "https://meetspot-irq2.onrender.com/about",
            "schema_jsonld": schema_list,
            "breadcrumbs": [
                {"name": "首页", "url": "/"},
                {"name": "关于我们", "url": "/about"},
            ],
        },
    )


@router.get("/how-it-works", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def how_it_works(request: Request):
    meta_tags = seo_generator.generate_meta_tags("how_it_works", {})
    how_to_schema = seo_generator.generate_schema_org(
        "how_to",
        {
            "name": "使用MeetSpot规划公平会面",
            "description": "4步流程, 从收集地址到导出SEO-ready页面, 15分钟内完成。",
            "total_time": "PT15M",
            "steps": [
                {
                    "name": "收集参与者地址",
                    "text": "邀请2-10位成员输入常用地址或地标, 系统自动校验经纬度与交通方式。",
                },
                {
                    "name": "设置场景与权重",
                    "text": "选择咖啡馆/餐厅/共享空间等场景, 调整预算与通勤权重保持公平。",
                },
                {
                    "name": "审核推荐结果",
                    "text": "查看多候选场所、评分、热力图与结构化数据, 与团队实时协作确认。",
                },
                {
                    "name": "导出与监控",
                    "text": "导出SEO-ready推荐页面, 上传至Search Console并追踪表现。",
                },
            ],
            "tools": ["MeetSpot Dashboard", "AMap API"],
            "supplies": ["成员清单", "交通偏好", "预算上限"],
        },
    )
    schema_list = _build_schema_list(
        seo_generator.generate_schema_org("website", {"search_url": "/search"}),
        seo_generator.generate_schema_org("organization", {}),
        seo_generator.generate_schema_org(
            "breadcrumb",
            {
                "items": [
                    {"name": "Home", "url": "/"},
                    {"name": "How it Works", "url": "/how-it-works"},
                ]
            },
        ),
        how_to_schema,
    )
    return templates.TemplateResponse(
        "pages/how_it_works.html",
        {
            "request": request,
            "meta_title": meta_tags["title"],
            "meta_description": meta_tags["description"],
            "meta_keywords": meta_tags["keywords"],
            "canonical_url": "https://meetspot-irq2.onrender.com/how-it-works",
            "schema_jsonld": schema_list,
            "breadcrumbs": [
                {"name": "首页", "url": "/"},
                {"name": "使用指南", "url": "/how-it-works"},
            ],
        },
    )


@router.get("/faq", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def faq_page(request: Request):
    meta_tags = seo_generator.generate_meta_tags("faq", {})
    faqs = [
        {
            "question": "什么是会面地点推荐？",
            "answer": "MeetSpot基于参与者位置计算公平的地理中点, 并推荐附近高评分场所。",
        },
        {
            "question": "支持哪些城市？",
            "answer": "目前覆盖北京、上海、广州、深圳、杭州等350+城市, 持续扩展中。",
        },
        {
            "question": "如何保证推荐公平?",
            "answer": "算法考虑每位参与者的距离与交通方式, 限制距离差值在15%以内。",
        },
        {
            "question": "是否免费?",
            "answer": "完全免费使用, 无需注册, 欢迎反馈需求。",
        },
    ]
    schema_list = _build_schema_list(
        seo_generator.generate_schema_org("website", {"search_url": "/search"}),
        seo_generator.generate_schema_org("organization", {}),
        seo_generator.generate_schema_org("faq", {"faqs": faqs}),
        seo_generator.generate_schema_org(
            "breadcrumb",
            {
                "items": [
                    {"name": "Home", "url": "/"},
                    {"name": "FAQ", "url": "/faq"},
                ]
            },
        ),
    )
    return templates.TemplateResponse(
        "pages/faq.html",
        {
            "request": request,
            "meta_title": meta_tags["title"],
            "meta_description": meta_tags["description"],
            "meta_keywords": meta_tags["keywords"],
            "canonical_url": "https://meetspot-irq2.onrender.com/faq",
            "schema_jsonld": schema_list,
            "breadcrumbs": [
                {"name": "首页", "url": "/"},
                {"name": "常见问题", "url": "/faq"},
            ],
            "faqs": faqs,
        },
    )


@router.get("/sitemap.xml")
async def sitemap():
    base_url = "https://meetspot-irq2.onrender.com"
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/about", "priority": "0.8", "changefreq": "monthly"},
        {"loc": "/faq", "priority": "0.8", "changefreq": "weekly"},
        {"loc": "/how-it-works", "priority": "0.7", "changefreq": "monthly"},
    ]
    city_urls = [
        {
            "loc": f"/meetspot/{city['slug']}",
            "priority": "0.9",
            "changefreq": "weekly",
        }
        for city in load_cities()
    ]
    entries = []
    for item in urls + city_urls:
        entries.append(
            f"    <url>\n        <loc>{base_url}{item['loc']}</loc>\n        <lastmod>{today}</lastmod>\n        <changefreq>{item['changefreq']}</changefreq>\n        <priority>{item['priority']}</priority>\n    </url>"
        )
    sitemap_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        + "\n".join(entries)
        + "\n</urlset>"
    )
    return Response(content=sitemap_xml, media_type="application/xml")


@router.get("/robots.txt")
async def robots_txt():
    today = datetime.now().strftime("%Y-%m-%d")
    robots = f"""# MeetSpot Robots.txt\n# Generated: {today}\n\nUser-agent: *\nAllow: /\nCrawl-delay: 1\n\nDisallow: /admin/\nDisallow: /api/internal/\nDisallow: /*.json$\n\nSitemap: https://meetspot-irq2.onrender.com/sitemap.xml\n\nUser-agent: Googlebot\nAllow: /\n\nUser-agent: Baiduspider\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nUser-agent: CCBot\nDisallow: /\n"""
    return Response(content=robots, media_type="text/plain")
