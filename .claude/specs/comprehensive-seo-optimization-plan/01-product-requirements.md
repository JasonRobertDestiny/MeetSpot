# Product Requirements Document: MeetSpot 综合SEO优化计划

## Executive Summary

本PRD定义了MeetSpot的全面SEO优化策略，旨在通过内容优化、技术SEO和结构化数据实施，显著提升搜索引擎排名和自然流量。项目将在6个月内实现30%的流量增长，核心关键词进入Google前3页，推荐页面转化率提升20%。

**开发执行方式**: 本PRD的实施将由Codex AI执行，Sarah将提供详细的实施prompt和质量验证。

---

## Business Objectives

### Problem Statement

MeetSpot当前面临搜索引擎可见性不足的问题：
- 自然流量占比低，过度依赖直接访问和付费渠道
- 核心关键词"会面地点推荐"、"聚会场所"等未进入搜索引擎前5页
- 推荐页面缺乏结构化数据，搜索引擎无法充分理解内容价值
- 技术SEO基础薄弱，影响爬虫抓取和索引效率

这直接导致潜在用户无法通过搜索发现MeetSpot，限制了产品的增长潜力。

### Success Metrics

**核心KPI（6个月目标）**:
- 自然搜索流量提升30%（从当前基线测量）
- 核心关键词排名进入Google前3页（5个关键词）
- 推荐页面转化率提升20%（从点击到实际使用）
- 搜索引擎收录率提升到95%以上

**过程指标（每月监测）**:
- Google Search Console点击率（CTR）提升到5%以上
- 平均页面停留时间增加15%
- 跳出率降低10%
- 结构化数据覆盖率达到100%（所有推荐页面）

### Expected ROI

**量化收益**:
- 降低获客成本（CAC）25%：自然流量无需付费广告
- 提升用户质量：搜索流量意图明确，转化率高于其他渠道
- 长期复利效应：SEO优化成果可持续6-12个月

**战略价值**:
- 建立品牌权威性：高排名提升用户信任
- 竞争护城河：SEO优势需要时间积累，难以快速复制
- 数据资产：积累关键词和用户行为数据，指导产品迭代

---

## User Personas

### Primary Persona: 搜索驱动型用户（张伟）

- **Role**: 互联网用户，通过搜索引擎寻找解决方案
- **Goals**:
  - 快速找到可靠的会面地点推荐工具
  - 通过搜索结果预判服务质量
  - 获取权威性强的推荐建议
- **Pain Points**:
  - 搜索结果中无法找到MeetSpot
  - 点击进入页面后不确定是否可信
  - 页面加载慢或内容不清晰导致立即离开
- **Technical Proficiency**: 中等，熟悉基本搜索技巧

**SEO需求映射**:
- 关键词排名优化：确保在搜索结果中出现
- Meta描述优化：提供清晰的服务价值描述
- 页面性能优化：3秒内完成首屏加载
- 结构化数据：展示评分、服务范围等信任信号

### Secondary Persona: 搜索引擎爬虫（Googlebot）

- **Role**: 自动化内容抓取和索引系统
- **Goals**:
  - 高效抓取网站内容
  - 准确理解页面主题和价值
  - 正确索引动态生成的推荐页面
- **Pain Points**:
  - JavaScript渲染延迟导致内容不可见
  - 缺乏结构化数据，难以理解页面语义
  - 动态URL缺乏清晰的层级结构
- **Technical Proficiency**: 高，但依赖标准化的语义标记

**SEO需求映射**:
- 服务端渲染（SSR）或预渲染：确保内容可直接抓取
- Schema.org标记：明确页面类型和内容
- XML Sitemap：主动提交动态页面URL
- Robots.txt优化：引导爬虫抓取策略

---

## User Journey Maps

### Journey 1: 搜索发现 → 首次使用

1. **Trigger**: 用户在Google搜索"北京聚会地点推荐"
2. **Steps**:
   - **搜索结果展示**:
     - MeetSpot出现在第1-3位
     - Meta描述明确说明"智能推荐公平会面地点"
     - 结构化数据显示4.8星评分（如有）
   - **点击进入首页**:
     - 3秒内完成加载
     - H1标题"智能会面地点推荐工具"清晰可见
     - 首屏展示价值主张和快速输入框
   - **使用服务**:
     - 输入2个地址："北京大学"、"清华大学"
     - 系统生成推荐页面
   - **查看推荐结果**:
     - 推荐页面URL包含关键词（如 `/recommend/beijing-university-meetspot`）
     - 页面标题"北京大学-清华大学会面地点推荐"
     - 结构化数据标记推荐场所（LocalBusiness）
3. **Success Outcome**: 用户找到满意场所，加入书签，成为回访用户

**SEO优化点**:
- 关键词定位：首页 + 推荐页面双重优化
- 内容结构：清晰的H1-H3层级
- 内部链接：首页链接到热门推荐页面
- 用户信号：降低跳出率，提升停留时间

### Journey 2: 推荐页面被搜索引擎索引

1. **Trigger**: Googlebot发现新推荐页面（通过Sitemap或外部链接）
2. **Steps**:
   - **爬虫访问页面**:
     - Robots.txt允许抓取 `/workspace/js_src/` 路径
     - 服务端返回完整HTML（非空白页面等待JS渲染）
   - **内容解析**:
     - 识别LocalBusiness Schema标记
     - 提取关键词、位置信息、评分
     - 记录页面加载性能（Core Web Vitals）
   - **质量评估**:
     - 内容原创性检查（非重复内容）
     - 关键词密度和语义相关性
     - 外部链接质量（如有）
   - **索引决策**:
     - 符合质量标准 → 加入索引
     - 低质量 → 进入"已发现-未编入索引"状态
3. **Success Outcome**: 页面进入Google索引，可被用户搜索到

**SEO优化点**:
- 预渲染：确保爬虫直接获取完整内容
- Schema标记：LocalBusiness + AggregateRating
- Canonical URL：避免重复内容问题
- 性能优化：LCP < 2.5s, FID < 100ms, CLS < 0.1

---

## Functional Requirements

### Epic 1: 内容优化与关键词布局

**业务价值**: 提升关键词排名，增加自然搜索曝光

#### User Story 1.1: 首页SEO优化

**As a** 搜索用户
**I want to** 通过搜索"会面地点推荐"找到MeetSpot首页
**So that** 我能快速发现并使用这个工具

**Acceptance Criteria:**
- [ ] 页面标题优化为"智能会面地点推荐 - MeetSpot | 公平聚会场所选择工具"（60字符内）
- [ ] Meta描述包含核心关键词和价值主张："为多人聚会智能推荐公平的会面地点，支持北京、上海等城市，基于地理位置自动计算中心点并推荐咖啡馆、餐厅等场所"（155字符内）
- [ ] H1标题清晰："智能会面地点推荐工具"
- [ ] 首屏包含关键词"聚会地点"、"中心点计算"、"公平推荐"
- [ ] 添加FAQ版块回答常见问题（至少5个问题，使用FAQPage Schema）

**实施提示（Codex）**:
```
优化 public/index.html 的 SEO 元素：
1. 更新 <title> 标签为"智能会面地点推荐 - MeetSpot | 公平聚会场所选择工具"
2. 更新 <meta name="description"> 为"为多人聚会智能推荐公平的会面地点，支持北京、上海等城市，基于地理位置自动计算中心点并推荐咖啡馆、餐厅等场所"
3. 确保 H1 标签为"智能会面地点推荐工具"
4. 在首屏添加包含关键词的简介段落（100字左右）
5. 在页面底部添加 FAQ 版块（使用 <section> 标签），包含以下问题：
   - 什么是会面地点推荐？
   - 如何计算公平的聚会中心点？
   - 支持哪些城市？
   - 推荐哪些类型的场所？
   - 数据来源是什么？
6. 为 FAQ 添加 FAQPage 结构化数据（JSON-LD 格式）
```

#### User Story 1.2: 推荐页面标题和描述动态生成

**As a** 搜索引擎爬虫
**I want to** 每个推荐页面有唯一的标题和描述
**So that** 我能准确索引和展示这些页面

**Acceptance Criteria:**
- [ ] 推荐页面标题格式："{地点1}-{地点2}会面地点推荐 | MeetSpot"（如"北京大学-清华大学会面地点推荐 | MeetSpot"）
- [ ] Meta描述包含：地点名称、推荐场所类型、数量（如"为北京大学和清华大学之间推荐8个咖啡馆和餐厅，基于地理中心点智能筛选"）
- [ ] 描述长度控制在150-155字符
- [ ] 特殊字符正确转义（避免HTML注入）

**实施提示（Codex）**:
```
修改 app/tool/meetspot_recommender.py 的 _generate_html_content 方法：
1. 在 HTML <head> 中添加动态生成的 <title> 标签：
   - 格式："{location_names[0]}-{location_names[1]}会面地点推荐 | MeetSpot"
   - 如果地点超过2个，使用："{location_names[0]}等{len(locations)}地会面推荐 | MeetSpot"
2. 添加动态 Meta 描述：
   - 提取关键词（keywords）和推荐场所数量（len(sorted_places)）
   - 格式："为{地点列表}推荐{数量}个{关键词}，基于地理中心点智能筛选，含评分和导航信息"
3. HTML 转义所有用户输入（地点名称、关键词）防止注入
4. 确保标题长度不超过60字符，描述不超过155字符
```

#### User Story 1.3: 关键词密度优化

**As a** 搜索引擎算法
**I want to** 页面包含足够但不过度的关键词
**So that** 我能判断页面主题相关性

**Acceptance Criteria:**
- [ ] 主关键词"会面地点"在页面中出现3-5次（密度1-2%）
- [ ] 次要关键词"聚会场所"、"中心点推荐"各出现2-3次
- [ ] 长尾关键词"公平聚会地点选择"至少出现1次
- [ ] 关键词自然融入内容，避免堆砌
- [ ] 图片alt属性包含相关关键词（如"会面地点地图"、"推荐场所列表"）

**实施提示（Codex）**:
```
优化 public/index.html 和推荐页面模板：
1. 在首页简介中自然加入关键词：
   - "MeetSpot 是智能的会面地点推荐工具，为多人聚会自动计算地理中心点，推荐公平的场所..."
2. 在推荐页面添加说明文字：
   - "为 {地点} 推荐的聚会场所均基于地理中心点筛选，确保对所有参与者公平"
3. 为所有图片添加描述性 alt 属性：
   - 地图图片：alt="会面地点推荐地图"
   - 场所图标：alt="{场所名称} - 推荐聚会场所"
4. 使用 <strong> 或 <em> 标签适度强调关键词（不超过2处）
```

---

### Epic 2: 结构化数据实施

**业务价值**: 提升搜索结果展示丰富度，增加点击率

#### User Story 2.1: LocalBusiness Schema标记

**As a** 搜索用户
**I want to** 在搜索结果中看到推荐场所的评分和地址
**So that** 我能快速判断场所质量

**Acceptance Criteria:**
- [ ] 每个推荐场所生成LocalBusiness Schema（JSON-LD格式）
- [ ] 包含必填字段：name, address（PostalAddress类型）, geo（GeoCoordinates类型）
- [ ] 包含推荐字段：aggregateRating（如有高德评分）, telephone, priceRange
- [ ] 通过Google Rich Results Test验证无错误
- [ ] Schema数据嵌入HTML <head> 或 <script type="application/ld+json"> 中

**实施提示（Codex）**:
```
在 app/tool/meetspot_recommender.py 的 _generate_html_content 中：
1. 为每个推荐场所（sorted_places）生成 LocalBusiness Schema：
   {
     "@context": "https://schema.org",
     "@type": "LocalBusiness",
     "name": "{场所名称}",
     "address": {
       "@type": "PostalAddress",
       "streetAddress": "{详细地址}",
       "addressLocality": "{城市}",
       "addressRegion": "{省份}",
       "addressCountry": "CN"
     },
     "geo": {
       "@type": "GeoCoordinates",
       "latitude": "{纬度}",
       "longitude": "{经度}"
     },
     "aggregateRating": {
       "@type": "AggregateRating",
       "ratingValue": "{评分/10}",
       "bestRating": "5",
       "ratingCount": "1"
     },
     "telephone": "{电话}"
   }
2. 将所有场所的 Schema 嵌入 HTML <head> 中的 <script type="application/ld+json"> 标签
3. 确保 JSON 格式正确（使用 json.dumps 并设置 ensure_ascii=False）
4. 从高德API响应中提取：name, location（经纬度）, address, tel 字段
5. 评分转换：高德评分/10 = Schema 评分（5分制）
```

#### User Story 2.2: WebApplication Schema标记

**As a** 搜索引擎
**I want to** 理解MeetSpot是一个Web应用
**So that** 我能在应用搜索结果中展示它

**Acceptance Criteria:**
- [ ] 首页包含WebApplication Schema
- [ ] 包含字段：name, url, applicationCategory, operatingSystem, offers
- [ ] browserRequirements 说明支持的浏览器
- [ ] 通过Schema验证工具检查无误

**实施提示（Codex）**:
```
在 public/index.html 的 <head> 中添加 WebApplication Schema：
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "MeetSpot - 智能会面地点推荐",
  "url": "https://meetspot-irq2.onrender.com",
  "applicationCategory": "UtilitiesApplication",
  "operatingSystem": "All",
  "browserRequirements": "Requires JavaScript. Requires HTML5.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "CNY"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "120"
  }
}
</script>
注意：aggregateRating 仅在有真实用户评价时添加，否则省略此字段
```

#### User Story 2.3: BreadcrumbList 面包屑导航

**As a** 搜索用户
**I want to** 在搜索结果中看到页面层级结构
**So that** 我能理解页面在网站中的位置

**Acceptance Criteria:**
- [ ] 推荐页面包含BreadcrumbList Schema
- [ ] 层级：首页 > 推荐结果 > 当前页面
- [ ] 每个层级包含name和url
- [ ] 搜索结果中显示面包屑（Google需1-2周索引）

**实施提示（Codex）**:
```
在推荐页面 HTML <head> 中添加 BreadcrumbList Schema：
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "首页",
      "item": "https://meetspot-irq2.onrender.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "推荐结果",
      "item": "https://meetspot-irq2.onrender.com/workspace/js_src/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "{地点1}-{地点2}会面推荐"
    }
  ]
}
</script>
```

---

### Epic 3: 技术SEO优化

**业务价值**: 提升页面性能和爬虫抓取效率

#### User Story 3.1: 推荐页面预渲染

**As a** 搜索引擎爬虫
**I want to** 访问推荐页面时直接获取完整HTML
**So that** 我无需执行JavaScript即可抓取内容

**Acceptance Criteria:**
- [ ] 推荐页面生成时包含完整的场所列表HTML（非JavaScript动态渲染）
- [ ] Meta标签、标题、Schema标记在HTML源码中可见
- [ ] 使用curl抓取页面源码，验证内容完整性
- [ ] 页面初始HTML大小 < 500KB（优化加载速度）

**实施提示（Codex）**:
```
当前 _generate_html_content 已生成完整 HTML，需确保：
1. 所有场所卡片在 HTML 中静态渲染（当前实现已满足）
2. 检查 <meta> 标签是否在 <head> 中（不依赖 JS 动态插入）
3. Schema JSON-LD 在 HTML 源码中可见
4. 使用以下命令验证：
   curl -s https://meetspot-irq2.onrender.com/workspace/js_src/{filename}.html | grep -o "<title>.*</title>"
   应输出完整标题，而非空或"加载中..."
```

#### User Story 3.2: XML Sitemap生成

**As a** 搜索引擎
**I want to** 通过Sitemap发现所有推荐页面
**So that** 我能更快地索引新内容

**Acceptance Criteria:**
- [ ] 创建 `/sitemap.xml` 端点，动态生成Sitemap
- [ ] 包含首页 + 所有推荐页面URL（读取 `workspace/js_src/` 目录）
- [ ] 每个URL包含 `<lastmod>` 时间戳（文件修改时间）
- [ ] Sitemap符合XML格式规范
- [ ] 提交到Google Search Console和Bing Webmaster Tools

**实施提示（Codex）**:
```
在 api/index.py 中添加新端点：

@app.get("/sitemap.xml")
async def generate_sitemap():
    import os
    from datetime import datetime
    from pathlib import Path

    base_url = "https://meetspot-irq2.onrender.com"
    urls = [{"loc": base_url, "lastmod": datetime.now().isoformat()}]

    # 扫描推荐页面目录
    workspace_dir = Path("workspace/js_src")
    if workspace_dir.exists():
        for file in workspace_dir.glob("place_recommendation_*.html"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            urls.append({
                "loc": f"{base_url}/workspace/js_src/{file.name}",
                "lastmod": mtime
            })

    # 生成 XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f'  <url>\n    <loc>{url["loc"]}</loc>\n    <lastmod>{url["lastmod"]}</lastmod>\n  </url>\n'
    xml += '</urlset>'

    return Response(content=xml, media_type="application/xml")

测试：访问 http://127.0.0.1:8000/sitemap.xml 验证输出
```

#### User Story 3.3: Robots.txt优化

**As a** 搜索引擎爬虫
**I want to** 清晰的抓取指引
**So that** 我能高效抓取允许的内容

**Acceptance Criteria:**
- [ ] 创建 `/robots.txt` 端点或静态文件
- [ ] 允许抓取首页和推荐页面路径
- [ ] 禁止抓取API端点（/api/）和健康检查（/health）
- [ ] 包含Sitemap URL引用

**实施提示（Codex）**:
```
在 public/robots.txt 创建文件：

User-agent: *
Allow: /
Allow: /workspace/js_src/

Disallow: /api/
Disallow: /health
Disallow: /config

Sitemap: https://meetspot-irq2.onrender.com/sitemap.xml

在 api/index.py 中配置静态文件路由（如果尚未配置）：
app.mount("/", StaticFilesMiddleware(directory="public"), name="static")
```

#### User Story 3.4: Core Web Vitals优化

**As a** 搜索引擎排名算法
**I want to** 页面性能达标
**So that** 我给予更高的排名权重

**Acceptance Criteria:**
- [ ] LCP（Largest Contentful Paint）< 2.5秒
- [ ] FID（First Input Delay）< 100毫秒
- [ ] CLS（Cumulative Layout Shift）< 0.1
- [ ] 通过Google PageSpeed Insights测试达到"Good"评级
- [ ] 图片使用WebP格式并压缩（如适用）

**实施提示（Codex）**:
```
优化推荐页面性能：
1. 延迟加载地图（仅在用户滚动到地图区域时初始化）
2. 压缩内联CSS（移除注释和空格）
3. 异步加载高德地图API：
   <script async src="https://webapi.amap.com/maps?..."></script>
4. 为所有图片添加 width 和 height 属性（避免CLS）
5. 使用 font-display: swap 优化字体加载
6. 测试工具：https://pagespeed.web.dev/
```

---

### Epic 4: 监控与迭代系统

**业务价值**: 持续追踪SEO效果，及时调整策略

#### User Story 4.1: Google Search Console集成

**As a** SEO分析师
**I want to** 监控搜索表现数据
**So that** 我能评估优化效果

**Acceptance Criteria:**
- [ ] 注册并验证网站所有权（使用HTML文件验证或DNS验证）
- [ ] 提交Sitemap到Search Console
- [ ] 每周检查"覆盖率"报告（索引页面数量）
- [ ] 每周检查"效果"报告（点击、展示、CTR、排名）
- [ ] 设置邮件提醒（关键错误和警告）

**实施提示（人工操作）**:
```
手动操作步骤：
1. 访问 https://search.google.com/search-console
2. 添加资源：https://meetspot-irq2.onrender.com
3. 验证方式：上传HTML文件到 public/google{code}.html（推荐）
4. 验证后，提交 Sitemap：https://meetspot-irq2.onrender.com/sitemap.xml
5. 设置提醒：Search Console > 设置 > 用户和权限 > 邮件通知
```

#### User Story 4.2: 关键词排名追踪

**As a** 产品负责人
**I want to** 追踪核心关键词排名变化
**So that** 我能量化SEO投入的回报

**Acceptance Criteria:**
- [ ] 选定5个核心关键词：会面地点推荐、聚会场所、中心点计算、公平聚会地点、多人聚会推荐
- [ ] 每周记录排名位置（手动或使用工具如Ahrefs/SEMrush）
- [ ] 创建排名趋势图表（Google Sheets或可视化工具）
- [ ] 排名提升 > 10位视为显著改进

**实施提示（手动 + 自动化）**:
```
手动方法：
- 使用隐身模式搜索关键词，记录MeetSpot的排名位置
- 记录在 Google Sheets 中（日期、关键词、排名、URL）

自动化方法（可选）：
- 使用 SerpAPI 或 Google Custom Search API
- 创建 Python 脚本定期检查排名：
  import requests
  def check_ranking(keyword):
      api_key = "YOUR_SERPAPI_KEY"
      url = f"https://serpapi.com/search?q={keyword}&location=Beijing&hl=zh-cn&api_key={api_key}"
      response = requests.get(url).json()
      for i, result in enumerate(response.get("organic_results", [])):
          if "meetspot" in result["link"].lower():
              return i + 1
      return None
- 每周运行并记录结果
```

#### User Story 4.3: 流量来源分析

**As a** 数据分析师
**I want to** 区分自然流量和其他流量来源
**So that** 我能评估SEO的实际贡献

**Acceptance Criteria:**
- [ ] 集成Google Analytics 4（GA4）或类似工具
- [ ] 设置UTM参数区分流量来源（organic, direct, referral）
- [ ] 每月导出自然搜索流量报告
- [ ] 对比优化前后的自然流量增长率

**实施提示（手动操作）**:
```
在 public/index.html 和推荐页面添加 GA4 跟踪代码：
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>

分析步骤：
1. GA4 > 报告 > 流量获取 > 查看"Organic Search"数据
2. 对比优化前基线（记录当前周/月流量）
3. 每月导出CSV并计算增长率
```

---

## Non-Functional Requirements

### Performance

- **页面加载速度**: 首屏加载时间（LCP）< 2.5秒，测试环境：4G网络
- **API响应时间**: `/api/find_meetspot` 端点响应 < 3秒（含高德API调用）
- **并发处理**: 支持10个并发请求无明显性能下降
- **资源优化**:
  - HTML文件大小 < 500KB
  - 内联CSS < 50KB
  - JavaScript延迟加载（非首屏必需）

### Security

- **输入验证**:
  - 所有用户输入（地点名称、关键词）必须经过HTML转义
  - 防止XSS攻击：使用`html.escape()`处理动态内容
- **API密钥保护**:
  - 高德API密钥通过环境变量配置，不暴露在前端代码
  - 使用安全JavaScript代码（`AMAP_SECURITY_JS_CODE`）
- **HTTPS强制**:
  - 生产环境所有流量通过HTTPS
  - 设置HSTS头部（Strict-Transport-Security）

### Usability

- **可访问性**:
  - 符合WCAG 2.1 AA级标准
  - 所有图片包含alt描述
  - 键盘导航支持（Tab键可访问所有交互元素）
  - 色彩对比度 > 4.5:1
- **浏览器支持**:
  - Chrome/Edge（最新2个版本）
  - Firefox（最新2个版本）
  - Safari（最新2个版本）
  - 移动端浏览器（iOS Safari, Chrome Mobile）
- **响应式设计**:
  - 支持设备：桌面（1920×1080）、平板（768×1024）、手机（375×667）
  - 使用媒体查询适配不同屏幕

---

## Technical Constraints

### Integration Requirements

- **高德地图API**:
  - 当前集成：Geocoding API, POI Search API, JavaScript API
  - 限制：每日调用配额（需监控使用量）
  - 依赖：稳定的网络连接
- **Google Search Console**:
  - 需要验证网站所有权
  - Sitemap提交和索引状态监控
- **结构化数据验证**:
  - 使用Google Rich Results Test（https://search.google.com/test/rich-results）
  - 确保Schema.org标记符合规范

### Technology Constraints

- **现有技术栈**:
  - FastAPI + Python 3.11+
  - Jinja2模板（当前使用f-string模板，可迁移到Jinja2）
  - 静态文件托管（`public/` 目录）
- **部署平台**:
  - Render.com（生产环境）
  - Docker容器化支持
  - 环境变量配置（AMAP_API_KEY等）
- **限制**:
  - 无数据库（推荐页面基于文件系统存储）
  - 无用户认证系统（当前为公开服务）
  - 静态IP不固定（Render平台限制）

---

## Scope & Phasing

### MVP Scope (Phase 1 - 第1周)

**核心目标**: 快速提升搜索可见性，建立SEO基础

**功能清单**:
- [ ] 首页SEO优化（标题、描述、H1、关键词布局）
- [ ] 推荐页面动态标题和描述生成
- [ ] LocalBusiness Schema标记（推荐场所）
- [ ] WebApplication Schema标记（首页）
- [ ] Robots.txt和Sitemap.xml创建
- [ ] Google Search Console注册和验证

**验收标准**:
- 通过Google Rich Results Test验证无错误
- Sitemap成功提交到Search Console
- 首页和至少5个推荐页面被Google索引（可能需1-2周）

**预计工作量**: 3-5天（Codex执行 + 人工验证）

---

### Phase 2 Enhancements (第2-4周)

**目标**: 深化技术SEO，提升用户体验和排名

**功能清单**:
- [ ] FAQ版块和FAQPage Schema
- [ ] BreadcrumbList面包屑导航
- [ ] Core Web Vitals优化（LCP, FID, CLS）
- [ ] 图片alt属性批量优化
- [ ] 关键词密度自动检测工具（内部使用）
- [ ] Google Analytics 4集成
- [ ] 关键词排名基线测量

**验收标准**:
- PageSpeed Insights评分 > 90（移动端和桌面）
- 5个核心关键词排名进入前10页
- GA4成功追踪流量来源

**预计工作量**: 1-2周

---

### Future Considerations (Phase 3+ - 第2-6个月)

**长期优化方向**:
- [ ] 内容营销：发布SEO优化的博客文章（如"如何选择公平的聚会地点"）
- [ ] 外部链接建设：联系本地生活类网站交换友链
- [ ] 多语言支持：英文版页面（扩大国际市场）
- [ ] AMP（Accelerated Mobile Pages）实施（移动端加速）
- [ ] 视频内容：使用教程视频（VideoObject Schema）
- [ ] 用户生成内容：评论和评分系统（Review Schema）
- [ ] 地区性SEO：为主要城市创建专属登陆页（如"北京会面地点推荐"）

**优先级排序**:
1. 内容营销（博客）- 高优先级，提升长尾关键词排名
2. 外部链接建设 - 高优先级，提升域名权威性
3. 地区性SEO - 中优先级，适合已有用户基础后
4. 多语言支持 - 低优先级，需市场需求验证

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Google索引延迟（新页面未被及时收录） | High | Medium | 主动提交Sitemap，创建外部链接引导爬虫，使用Google Search Console"请求编入索引"功能 |
| 关键词竞争激烈（排名提升缓慢） | Medium | High | 聚焦长尾关键词（如"北京大学附近聚会地点"），避免与大型平台直接竞争 |
| 高德API配额耗尽（影响推荐生成） | Low | High | 实施请求缓存，监控API使用量，准备备用API密钥 |
| Schema标记错误（导致Rich Results失效） | Medium | Medium | 使用自动化验证工具（Rich Results Test），每次部署后验证 |
| Core Web Vitals不达标（影响排名） | Medium | Medium | 优先优化LCP（延迟加载、压缩资源），定期使用PageSpeed Insights测试 |
| 推荐页面被判定为低质量内容 | Low | High | 确保每个页面内容唯一（包含地点名称、评分、地图），添加用户价值（如导航链接、营业时间） |
| 竞争对手SEO优化（相对排名下降） | Medium | Medium | 持续监控竞争对手关键词策略，定期更新内容和Schema标记 |

---

## Dependencies

### 外部依赖
- **高德地图API稳定性**: 推荐页面生成依赖API响应，需监控可用性
- **Google索引速度**: SEO效果显现需要1-3个月，取决于Google爬虫频率
- **Render.com平台性能**: 页面加载速度受部署平台影响

### 内部依赖
- **推荐页面生成逻辑**: Schema标记需集成到现有 `_generate_html_content` 方法
- **静态文件路由**: Sitemap和Robots.txt需FastAPI正确配置静态文件访问
- **日志系统**: SEO监控需要完善的日志记录（关键词、访问来源）

### 时间线依赖
- **Phase 1完成后才能开始Phase 2**: 必须先建立Schema基础和Sitemap
- **Google Search Console验证需1-2天**: 影响Sitemap提交时间
- **索引生效需1-4周**: 影响排名监控的启动时间

---

## Appendix

### Glossary

- **SEO (Search Engine Optimization)**: 搜索引擎优化，通过技术和内容手段提升网站在搜索结果中的排名
- **Schema.org**: 结构化数据标记标准，帮助搜索引擎理解页面内容
- **LocalBusiness**: Schema类型，用于标记本地商家信息（名称、地址、评分等）
- **Core Web Vitals**: Google页面体验指标，包括LCP（加载性能）、FID（交互性）、CLS（视觉稳定性）
- **Sitemap**: 网站地图，XML格式文件列出所有可索引页面，提交给搜索引擎
- **Robots.txt**: 爬虫协议文件，指导搜索引擎哪些页面允许或禁止抓取
- **Rich Results**: 富媒体搜索结果，包含评分、图片、价格等额外信息
- **LCP (Largest Contentful Paint)**: 最大内容绘制时间，衡量页面主要内容加载速度
- **CTR (Click-Through Rate)**: 点击率，搜索结果展示次数与点击次数的比率

### References

- **Google搜索中心文档**: https://developers.google.com/search/docs
- **Schema.org官方文档**: https://schema.org/
- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **PageSpeed Insights**: https://pagespeed.web.dev/
- **高德地图API文档**: https://lbs.amap.com/api/
- **FastAPI文档**: https://fastapi.tiangolo.com/

---

## 开发执行说明

**本PRD将由Codex AI执行实施**，Sarah（Product Owner）将提供：

1. **详细实施Prompt**: 每个User Story的"实施提示"部分包含具体代码指导
2. **验收标准**: 明确的Acceptance Criteria用于质量验证
3. **优先级排序**: Phase 1（MVP）优先，Phase 2和3按需迭代

**Codex执行流程**:
1. 读取本PRD文档
2. 按照Phase顺序执行User Stories
3. 使用提供的代码示例和指导
4. 完成后通过验收标准（使用测试工具验证）
5. 向Sarah报告完成状态和发现的问题

**质量保证**:
- 所有Schema标记必须通过Google Rich Results Test
- 所有页面必须通过Core Web Vitals测试（评分 > 90）
- 代码符合PEP8规范（使用black和ruff格式化）
- 手动测试关键功能（首页加载、推荐生成、Schema展示）

---

**Document Version**: 1.0
**Date**: 2025-11-08
**Author**: Sarah (BMAD Product Owner)
**Quality Score**: 93/100
**Execution Partner**: Codex AI
**Estimated Timeline**: MVP 1周 | Phase 2 2-3周 | Phase 3 按需迭代
