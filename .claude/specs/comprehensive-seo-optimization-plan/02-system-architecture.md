# System Architecture Document: Comprehensive SEO Optimization Plan

## Executive Summary

This architecture delivers a pragmatic, server-side SEO solution for MeetSpot that balances rapid deployment with measurable search engine impact. The design prioritizes simplicity and effectiveness over complexity, using proven technologies (Jinja2 SSR, jieba NLP, template-based content) to achieve 90+ quality scores across Core Web Vitals and SEO metrics within a 2-week MVP timeline.

Key architectural decisions stem from analyzing MeetSpot's specific constraints: limited team resources, Python-first stack, and need for immediate SEO impact. Rather than building complex systems, we leverage existing FastAPI infrastructure and add minimal, focused enhancements.

## Architecture Overview

### System Context

MeetSpot operates as a FastAPI-based web application serving Chinese users searching for optimal meeting locations. The current system focuses on API functionality with minimal SEO optimization. This architecture transforms it into a search-engine-friendly platform while preserving all existing functionality.

### Architecture Principles

1. **Server-Side First**: All content critical for SEO is rendered server-side before reaching the browser. Client-side JavaScript enhances but never replaces core content, ensuring search engines see complete, meaningful pages regardless of JavaScript execution.

2. **Progressive Enhancement**: The system works perfectly without JavaScript for search engines and basic users, then adds interactive features for capable browsers. This "baseline then enhance" approach guarantees accessibility and SEO performance.

3. **Minimal Complexity**: Every component must justify its existence. We reject microservices, complex build pipelines, and unnecessary abstractions. If a feature doesn't directly improve search rankings or user experience, it doesn't exist.

4. **Phased Deployment**: Deploy in measurable stages with clear rollback points. Never change everything at once. Each phase has specific metrics (CWV scores, ranking positions) that must improve before proceeding.

5. **Chinese-First Optimization**: All NLP, keyword extraction, and content generation is optimized for Chinese language characteristics. We use jieba for word segmentation and understand Chinese search behavior patterns.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │  Search Bot  │  │  Mobile App  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   FastAPI App    │
                    │   (api/index.py) │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  SSR Templates │  │  SEO Middleware │  │  Static Assets │
│  (Jinja2)      │  │  (Meta/Schema)  │  │  (CDN-ready)   │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   Core Services  │
                    │  (MeetSpot Logic)│
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  NLP Pipeline  │  │  Cache Layer    │  │  Amap API      │
│  (jieba)       │  │  (Redis/Memory) │  │  Integration   │
└────────────────┘  └─────────────────┘  └────────────────┘
```

## Component Architecture

### Frontend Layer

#### Technology Stack
- **Server-Side Rendering**: Jinja2 - Industry standard for Python, zero learning curve for team, proven performance with FastAPI integration
- **Styling**: Vanilla CSS with CSS Variables - No build step complexity, perfect browser support, easier debugging than Tailwind/frameworks
- **Client Enhancement**: Vanilla JavaScript ES6+ - Modern browser support (95%+ coverage), no bundler needed, faster development cycle
- **Static Assets**: CDN-served (Render.com/Cloudflare) - Automatic edge caching, zero configuration, free tier available

#### Component Structure
- **SEO Template System** (`app/templates/`): Base layouts with meta management, schema.org integration, semantic HTML5 structure
- **Page Templates** (`app/templates/pages/`): Homepage, location pages, guide pages - all with unique SEO optimization
- **Partial Templates** (`app/templates/partials/`): Reusable components (navigation, footers, structured data snippets)
- **Static Resources** (`public/`): CSS, minimal JS, optimized images (WebP with fallbacks)

### Backend Layer

#### Technology Stack
- **Language**: Python 3.11+ - Existing codebase, team expertise, excellent async performance
- **Framework**: FastAPI 0.116.1+ - Already in use, built-in OpenAPI docs, async-first architecture, Jinja2 integration
- **NLP Library**: jieba 0.42.1 - Best Chinese word segmentation, extensive dictionary support, active maintenance
- **Template Engine**: Jinja2 3.1.2+ - FastAPI native integration, powerful template inheritance, auto-escaping security

#### Service Architecture

**SEOManager Service** (`app/services/seo_manager.py`):
- Responsibilities: Central SEO orchestration, meta tag generation, schema.org markup, sitemap/robots.txt
- Interactions: Called by route handlers before template rendering
- Data Flow: Receives page context → enriches with SEO data → returns enhanced context for templates
- Caching: Keyword extraction results cached for 1 hour, template-rendered pages for 5 minutes

**ContentGenerator Service** (`app/services/content_generator.py`):
- Responsibilities: Template-based content for location guides, keyword expansion for meta descriptions
- Interactions: Works with SEOManager to provide unique content per page
- Data Flow: Takes location/keyword data → applies templates → returns SEO-optimized content
- Future: LLM integration point for dynamic content (Phase 2)

**NLPProcessor Service** (`app/services/nlp_processor.py`):
- Responsibilities: Chinese text segmentation, keyword extraction, synonym generation
- Interactions: Used by SEOManager and ContentGenerator
- Data Flow: Raw text → jieba segmentation → TF-IDF keyword extraction → ranked keywords
- Performance: Processes 1000-word articles in <50ms, cached results reused across requests

### Data Layer

#### Database Selection
- **Primary Database**: None for MVP - All data is statically generated or cached in memory. This eliminates database latency, simplifies deployment, and reduces operational complexity. Actual recommendation data comes from Amap API in real-time.
- **Cache**: Python dictionary (in-memory) for MVP, Redis for production - Stores keyword extraction results, rendered page fragments, Amap API responses. Redis migration path is straightforward when traffic increases.
- **Search**: Not applicable for MVP - Future consideration for internal site search if needed.

#### Data Architecture

```
SEO Data Flow:
┌─────────────┐
│ HTTP Request│
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────────────┐
│ Route Handler (e.g., /locations/{city}/{query})     │
└──────┬──────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│ SEOManager.generate_page_context(path, params)      │
│  ├─ Extract keywords (NLPProcessor + cache lookup)  │
│  ├─ Generate meta tags (title, description, OG)     │
│  ├─ Build schema.org JSON-LD                        │
│  └─ Compile breadcrumbs                             │
└──────┬──────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│ ContentGenerator.get_location_content(city, query)  │
│  ├─ Load template fragments                         │
│  ├─ Inject location-specific data                   │
│  └─ Return rendered content blocks                  │
└──────┬──────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│ Jinja2 Template Rendering                           │
│  ├─ base.html (structure + SEO slots)               │
│  ├─ location.html (content + schema)                │
│  └─ partials/*.html (nav, footer, etc.)             │
└──────┬──────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│ HTML Response (SSR with complete SEO metadata)      │
└─────────────────────────────────────────────────────┘
```

#### Data Models

**SEOContext** (Pydantic model):
```python
class SEOContext(BaseModel):
    title: str              # 60 chars max, keyword-optimized
    description: str        # 160 chars max, includes CTA
    keywords: List[str]     # Top 5-10 extracted keywords
    canonical_url: str      # Absolute URL
    og_tags: Dict[str, str] # Open Graph metadata
    schema_org: Dict        # JSON-LD structured data
    breadcrumbs: List[Dict] # Navigation path
    h1: str                 # Primary heading
    lang: str = "zh-CN"     # Language tag
```

**LocationPageData** (Pydantic model):
```python
class LocationPageData(BaseModel):
    city: str               # "北京"
    query: str              # "咖啡馆"
    location_names: List[str]  # ["北京大学", "清华大学"]
    intro_text: str         # Template-generated intro
    faq_items: List[Dict]   # Common questions
    related_queries: List[str]  # "图书馆", "餐厅"
    map_center: Dict        # {lat, lng} for map embed
```

## API Design

### API Standards
- **Protocol**: HTTP/1.1 with HTTP/2 support (Render.com provides automatically)
- **Format**: HTML for pages, JSON for API endpoints - Clear separation between user-facing and programmatic access
- **Versioning Strategy**: URL path versioning for JSON API (`/api/v1/`), no versioning for HTML pages (use redirects for breaking changes)

### Key Endpoints

| Method | Endpoint | Purpose | Response Type |
|--------|----------|---------|---------------|
| GET | `/` | Homepage with SEO-optimized intro | HTML (SSR) |
| GET | `/locations/{city}` | City-specific landing page | HTML (SSR) |
| GET | `/locations/{city}/{query}` | Location + query result page | HTML (SSR) |
| GET | `/guide/{topic}` | SEO content guides | HTML (SSR) |
| GET | `/sitemap.xml` | XML sitemap for search engines | XML |
| GET | `/robots.txt` | Crawler directives | Text |
| POST | `/api/v1/find_meetspot` | Existing recommendation API | JSON |
| GET | `/health` | Health check with SEO status | JSON |

**Example: Location Page Request**

Request:
```http
GET /locations/北京/咖啡馆 HTTP/1.1
Host: meetspot.example.com
Accept: text/html
```

Response:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>北京咖啡馆推荐 - 找到完美中点的聚会地点 | MeetSpot</title>
    <meta name="description" content="在北京寻找咖啡馆？MeetSpot帮您找到所有人都方便的中间位置。智能推荐最佳聚会地点，节省通勤时间。">
    <link rel="canonical" href="https://meetspot.example.com/locations/北京/咖啡馆">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "北京咖啡馆推荐",
      "description": "智能推荐北京中点咖啡馆",
      "breadcrumb": {...}
    }
    </script>
</head>
<body>
    <!-- SSR content here -->
</body>
</html>
```

## Security Architecture

### Authentication & Authorization
- **Authentication Method**: None for MVP - All pages are public. Rate limiting protects against abuse. Future user accounts can use JWT if personalization features are added.
- **Authorization Model**: Not applicable - No user-specific content or actions in current scope.
- **Token Management**: N/A for MVP

### Security Layers

1. **Network Security**:
   - HTTPS enforced (Render.com provides free SSL)
   - HTTP → HTTPS redirect middleware
   - Security headers (CSP, X-Frame-Options, HSTS)
   - DDoS protection via Render.com infrastructure

2. **Application Security**:
   - Jinja2 auto-escaping prevents XSS
   - Pydantic validation on all inputs
   - Rate limiting: 60 requests/minute per IP for HTML, 20/minute for API
   - No SQL injection risk (no database writes)
   - Input sanitization for URL parameters

3. **Data Security**:
   - No PII storage (stateless recommendation system)
   - Amap API key stored in environment variables (never in code)
   - Cache contains only non-sensitive aggregated data
   - Logs exclude user-identifiable information

### Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| XSS via user input in URLs | Medium | Jinja2 auto-escaping + Pydantic validation + URL encoding |
| DDoS overwhelming server | High | Rate limiting + Render.com CDN + caching |
| API key exposure | Medium | Environment variables only + .env in .gitignore + secret rotation |
| SEO spam injection | Low | Input validation + keyword whitelist + monitoring |
| Cache poisoning | Low | Cache keys include hash of inputs + short TTL (5 min) |

## Infrastructure & Deployment

### Infrastructure Architecture
- **Platform**: Render.com - Zero-config deployment, free SSL, automatic scaling, integrated CDN, superior to Railway for this use case (better SEO with custom domains, faster cold starts)
- **Container Strategy**: Render.com native Python environment (no Docker needed for simplicity) - Uses `requirements.txt` directly, faster deploys, easier debugging
- **CI/CD Pipeline**: GitHub Actions → Render.com auto-deploy on main branch push - Existing workflow extended with SEO validation checks

### Deployment Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ main branch│  │   PR check │  │  Tag release│            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
└────────┼───────────────┼───────────────┼────────────────────┘
         │               │               │
         │         ┌─────▼──────┐        │
         │         │GitHub Actions│       │
         │         │  - Lint      │       │
         │         │  - Test      │       │
         │         │  - SEO Check │       │
         │         └─────┬────────┘       │
         │               │                │
         └───────────────┼────────────────┘
                         │
                 ┌───────▼────────┐
                 │  Render.com    │
                 │  Auto Deploy   │
                 └───────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ Web Service   │ │  CDN Edge   │ │ Redis Cache │
│ (FastAPI)     │ │  (Static)   │ │ (Optional)  │
└───────┬───────┘ └──────┬──────┘ └──────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                 ┌───────▼────────┐
                 │  Production    │
                 │  Environment   │
                 └────────────────┘
```

### Environment Strategy

- **Development** (`localhost`):
  - Config: `config/config.toml`
  - Hot reload enabled
  - Verbose logging
  - No caching (for testing)
  - Local Amap API key (separate quota)

- **Staging** (Render.com preview deploys):
  - Config: Environment variables
  - Auto-deploy on PR creation
  - Production-like setup
  - Short cache TTLs (1 min)
  - Test Amap API key

- **Production** (Render.com main service):
  - Config: Environment variables only
  - Auto-deploy on main branch merge
  - Optimized cache settings
  - Error monitoring enabled
  - Production Amap API key with high quota

## Performance & Scalability

### Performance Requirements
- **Response Time**:
  - SSR pages: <800ms TTFB (Time to First Byte)
  - Static assets: <100ms (CDN-served)
  - API endpoints: <500ms (cached responses <50ms)
- **Throughput**: 100 requests/second sustained (typical small-scale traffic)
- **Concurrent Users**: 500 simultaneous users without degradation
- **Core Web Vitals Targets**:
  - LCP (Largest Contentful Paint): <2.5s
  - FID (First Input Delay): <100ms
  - CLS (Cumulative Layout Shift): <0.1

### Scaling Strategy
- **Horizontal Scaling**: Render.com auto-scaling when CPU >70% - Adds instances up to configured limit (start with 3 max)
- **Vertical Scaling**: Not needed for MVP - Default 0.5GB RAM sufficient, upgrade to 1GB if cache grows
- **Auto-scaling Rules**:
  - Scale up: CPU >70% for 2 minutes OR request queue >10
  - Scale down: CPU <30% for 5 minutes AND request queue <3

### Performance Optimizations

**Caching Strategy**:
- **L1 (In-Memory)**: Python dictionary cache for keyword extraction (1-hour TTL), 10MB limit
- **L2 (Redis - Production)**: Rendered page fragments (5-minute TTL), Amap API responses (1-hour TTL), 100MB limit
- **L3 (CDN)**: Static assets (24-hour TTL), sitemap/robots.txt (1-hour TTL), automatic invalidation on deploy
- **Cache Invalidation**: TTL-based for simplicity, manual purge via Render dashboard for emergencies

**Database Optimization**:
- Not applicable (no database for MVP)

**CDN Usage**:
- All static assets served from CDN (CSS, JS, images)
- Immutable URLs with content hashing (e.g., `style.a3f5b2.css`)
- WebP images with JPEG/PNG fallbacks for older browsers
- Lazy loading for below-fold images

**Code Optimizations**:
- Async/await for all I/O operations (Amap API, cache)
- Jinja2 template compilation cache
- Minimal dependencies (no heavy frameworks)
- Gzip compression for HTML/CSS/JS (automatic via Render.com)

## Reliability & Monitoring

### Reliability Targets
- **Availability**: 99.5% (3.6 hours downtime/month acceptable for MVP, upgrade to 99.9% for paid tier)
- **Recovery Time Objective (RTO)**: 10 minutes (time to redeploy from GitHub)
- **Recovery Point Objective (RPO)**: 0 seconds (stateless system, no data loss risk)

### Failure Handling
- **Circuit Breakers**:
  - Amap API: Opens after 5 consecutive failures, half-open retry after 30s
  - Cache: Bypass on error, fallback to direct computation
- **Retry Logic**:
  - Amap API: 3 retries with exponential backoff (0.5s, 1s, 2s)
  - Cache write failures: Log and continue (non-critical)
- **Graceful Degradation**:
  - If NLP fails: Use basic keyword from URL
  - If cache unavailable: Serve uncached (slower but functional)
  - If Amap API quota exceeded: Show informative error with retry time

### Monitoring & Observability

**Metrics** (collected via Render.com + custom logging):
- **Performance**: Response time (p50, p95, p99), TTFB, cache hit rate
- **Traffic**: Requests/second, unique visitors, top pages
- **Errors**: Error rate (%), 4xx/5xx counts, Amap API failures
- **SEO**: Core Web Vitals (via Google Search Console), crawl rate, indexation status
- **Business**: Recommendation requests, successful results, zero-result searches

**Logging** (loguru to stdout, ingested by Render.com):
- **Format**: JSON structured logs for parsing
- **Levels**:
  - DEBUG: Disabled in production
  - INFO: Request/response, cache hits/misses
  - WARNING: Slow responses (>1s), high cache miss rate
  - ERROR: Amap API failures, template rendering errors
- **Retention**: 7 days on Render.com free tier, 30 days on paid tier

**Tracing**:
- Not implemented for MVP (overkill for single-service architecture)
- Future: OpenTelemetry integration if microservices are added

**Alerting**:
- **Error Rate >5%**: Slack notification (via Render.com webhook)
- **Response Time p95 >2s**: Email alert
- **Amap API Failures >10/minute**: Page on-call engineer
- **Availability <99%**: Immediate investigation

## Technology Stack Summary

### Core Technologies

| Layer | Technology | Version | Justification |
|-------|------------|---------|---------------|
| Frontend | Jinja2 | 3.1.2+ | FastAPI native, proven SSR, zero learning curve |
| Backend | FastAPI | 0.116.1+ | Existing stack, async-first, excellent performance |
| Language | Python | 3.11+ | Team expertise, rich ecosystem, good for NLP |
| NLP | jieba | 0.42.1 | Best Chinese segmentation, 10+ years proven |
| Cache | Redis | 7.0+ (prod) | Industry standard, Render.com integration |
| Web Server | Uvicorn | 0.35.0+ | ASGI standard, production-ready with FastAPI |
| Platform | Render.com | N/A | Zero-config, free SSL, auto-scaling, CDN |

### Development Tools
- **IDE**: VS Code with Python + Jinja extensions
- **Version Control**: Git with feature branch workflow (main → feature/xxx → PR → merge)
- **Code Quality**:
  - black (formatting)
  - ruff (linting)
  - pre-commit hooks (auto-format on commit)
- **Testing Frameworks**:
  - pytest (unit + integration)
  - httpx (async API testing)
  - coverage.py (aim for 80%+ coverage)

## Implementation Considerations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Amap API quota exceeded | Medium | High | Cache aggressively, implement request pooling, monitor quota usage |
| Chinese NLP accuracy issues | Medium | Medium | Use jieba with custom dictionary, manual tuning, fallback to basic extraction |
| SSR performance bottleneck | Low | Medium | Template caching, async rendering, CDN for static parts |
| Search engine slow indexing | High | Medium | Submit sitemap, request indexing via Search Console, build backlinks |
| Cache stampede on popular pages | Low | Medium | Lock-based cache warming, stale-while-revalidate pattern |

### Technical Debt Considerations

**Planned Shortcuts** (with justification):
1. **In-memory cache for MVP**: Acceptable because traffic is low and state loss on restart is tolerable. Migrate to Redis when traffic >1000 req/day.
2. **Template-based content**: Faster than LLM for MVP, but limits uniqueness. Plan LLM integration for Phase 2 when SEO baseline is established.
3. **No database**: Simplifies deployment, but limits analytics. Add analytics DB when we need historical data (not critical for SEO).

**Future Refactoring**:
- **Cache Layer**: Migrate to Redis when scaling becomes necessary (clear migration path)
- **Content Generation**: Replace templates with LLM when quality becomes priority (API already designed for this)
- **Monitoring**: Add OpenTelemetry if system complexity increases (not needed for single-service architecture)

**Upgrade Path**:
- **Phase 1 (MVP)**: Current architecture as-is
- **Phase 2 (3 months)**: Add Redis cache, integrate LLM for content, implement A/B testing
- **Phase 3 (6 months)**: Add analytics DB, advanced monitoring, personalization features
- **Phase 4 (12 months)**: Evaluate microservices if traffic justifies complexity

### Team Considerations

**Required Skills**:
- Python backend development (FastAPI, async programming)
- Jinja2 templating (basic to intermediate)
- Chinese SEO knowledge (keyword research, meta optimization)
- Basic DevOps (GitHub Actions, Render.com deployment)

**Training Needs**:
- Jinja2 template syntax (2-hour workshop)
- SEO best practices for Chinese market (4-hour session)
- Core Web Vitals optimization (self-study resources provided)

**Team Structure**:
- **Backend Developer** (1 person): Implement SEOManager, NLPProcessor, API routes
- **Frontend Developer** (0.5 person): Create Jinja2 templates, optimize CSS/JS
- **SEO Specialist** (0.5 person): Keyword research, content strategy, monitoring
- **DevOps** (0.25 person): Set up CI/CD, monitoring, deployment automation

Total: 2.25 FTE for 2-week MVP, then 1 FTE for maintenance/iteration

## Migration Strategy

Not applicable - This is a new feature addition to existing system, not a migration. However, deployment strategy follows phased rollout:

**Phase 1: SSR Foundation (Week 1)**
1. Day 1-2: Set up Jinja2 templates, create base layout
2. Day 3-4: Implement SEOManager service, basic meta tags
3. Day 5: Deploy to staging, validate SSR functionality

**Phase 2: Content & NLP (Week 2)**
1. Day 1-2: Integrate jieba, implement keyword extraction
2. Day 3-4: Create location page templates, generate sitemap
3. Day 5: Deploy to production, submit to search engines

**Phase 3: Monitoring & Iteration (Week 3+)**
1. Week 3: Monitor Search Console, fix crawl errors
2. Week 4: Optimize based on Core Web Vitals data
3. Ongoing: Content expansion, backlink building

**Rollback Plan**:
- Each phase deployed to separate Render.com service
- DNS switch for instant rollback if issues arise
- Feature flags for gradual rollout (e.g., SSR only for 10% traffic initially)

## Appendix

### Architecture Decision Records (ADRs)

#### ADR-001: Server-Side Rendering with Jinja2
- **Context**: Need SEO-friendly HTML with minimal complexity. Options: Jinja2 SSR vs Next.js vs client-side + prerendering
- **Decision**: Jinja2 SSR integrated into existing FastAPI application
- **Consequences**:
  - Positive: Zero additional infrastructure, team already knows Python, perfect for search engines
  - Negative: Less rich interactivity than React-based solutions (acceptable for current use case)
  - Trade-off: Simplicity over maximum interactivity

#### ADR-002: jieba for Chinese NLP
- **Context**: Need reliable Chinese word segmentation for keyword extraction. Options: jieba vs THULAC vs HanLP vs cloud APIs
- **Decision**: jieba with custom dictionary tuning
- **Consequences**:
  - Positive: Mature library (10+ years), extensive documentation, offline processing (no API costs)
  - Negative: Less accurate than deep learning models for complex text (acceptable for short queries)
  - Trade-off: Reliability and simplicity over cutting-edge accuracy

#### ADR-003: Template-Based Content for MVP
- **Context**: Need unique content per page for SEO. Options: LLM generation vs templates vs manual writing
- **Decision**: Template-based with variable insertion for MVP, LLM integration in Phase 2
- **Consequences**:
  - Positive: Immediate deployment, predictable quality, zero API costs
  - Negative: Less uniqueness than LLM content (but sufficient for initial indexing)
  - Trade-off: Speed to market over perfect uniqueness

#### ADR-004: In-Memory Cache for MVP
- **Context**: Need caching for performance. Options: Redis vs in-memory dict vs no cache
- **Decision**: In-memory Python dict for MVP, Redis migration when traffic increases
- **Consequences**:
  - Positive: Zero infrastructure complexity, instant deployment
  - Negative: Cache lost on restarts (acceptable for low traffic)
  - Trade-off: Simplicity over maximum availability

#### ADR-005: Render.com Deployment
- **Context**: Need reliable hosting with SEO features. Options: Render.com vs Railway vs Vercel vs AWS
- **Decision**: Render.com with auto-deploy from GitHub
- **Consequences**:
  - Positive: Free SSL, CDN, custom domains, Python-native, better cold starts than Railway
  - Negative: Less control than AWS (not needed for current scale)
  - Trade-off: Convenience over maximum control

### Glossary
- **SSR (Server-Side Rendering)**: Generating HTML on the server before sending to client, crucial for SEO
- **Core Web Vitals**: Google's metrics for page experience (LCP, FID, CLS)
- **TTFB (Time to First Byte)**: Server response time, critical for perceived performance
- **Schema.org**: Structured data vocabulary for search engines to understand page content
- **Canonical URL**: The preferred URL for a page to avoid duplicate content issues
- **jieba**: Most popular Chinese word segmentation library, essential for NLP tasks
- **TF-IDF**: Term Frequency-Inverse Document Frequency, algorithm for keyword importance

### References
- [Google Search Essentials](https://developers.google.com/search/docs/essentials) - SEO best practices
- [Core Web Vitals Guide](https://web.dev/vitals/) - Performance optimization
- [FastAPI Jinja2 Templates](https://fastapi.tiangolo.com/advanced/templates/) - Integration documentation
- [jieba Documentation](https://github.com/fxsjy/jieba) - Chinese NLP library
- [Schema.org](https://schema.org/) - Structured data vocabulary
- [Render.com Python Docs](https://render.com/docs/deploy-fastapi) - Deployment guide

---

**Document Version**: 1.0
**Date**: 2025-11-08
**Author**: Winston (BMAD System Architect)
**Quality Score**: 92/100
**PRD Reference**: 01-product-requirements.md

---

## Implementation Notes for Codex

This section provides specific guidance for the development team (Codex) implementing this architecture.

### Critical Implementation Paths

**File Structure to Create**:
```
app/
├── services/
│   ├── __init__.py
│   ├── seo_manager.py      # SEO orchestration (priority 1)
│   ├── content_generator.py # Content templates (priority 2)
│   └── nlp_processor.py     # jieba integration (priority 3)
├── templates/
│   ├── base.html            # Base layout with SEO slots
│   ├── pages/
│   │   ├── index.html       # Homepage
│   │   ├── location.html    # Location page template
│   │   └── guide.html       # Guide page template
│   └── partials/
│       ├── head_seo.html    # Meta tags partial
│       ├── schema_org.html  # JSON-LD partial
│       └── breadcrumbs.html # Navigation partial
└── models/
    └── seo_models.py        # Pydantic models for SEO data
```

**Priority Order for Implementation**:
1. **Day 1-2**: Jinja2 integration + base template + SEOManager skeleton
2. **Day 3-4**: NLPProcessor with jieba + keyword extraction
3. **Day 5-6**: Location page routes + template rendering
4. **Day 7-8**: Content generation + schema.org markup
5. **Day 9-10**: Sitemap + robots.txt + testing

### Code Quality Requirements
- All Python code must pass `black` formatting and `ruff` linting
- Chinese comments for all SEO-specific logic
- Docstrings for public methods in services
- Type hints for all function signatures
- Error handling with informative messages

### Testing Requirements
- Unit tests for NLPProcessor keyword extraction (test with real Chinese queries)
- Integration tests for SEOManager meta tag generation
- Template rendering tests (validate HTML structure)
- End-to-end tests for key pages (homepage, location page)
- Performance tests: TTFB <800ms for SSR pages

### Deployment Checklist
- [ ] Environment variables configured on Render.com (AMAP_API_KEY, etc.)
- [ ] GitHub Actions workflow includes SEO validation step
- [ ] Sitemap submitted to Google Search Console
- [ ] robots.txt allows all necessary crawlers
- [ ] SSL certificate active and HTTP→HTTPS redirect working
- [ ] CDN caching configured for static assets
- [ ] Core Web Vitals monitoring enabled

### Success Metrics to Track
- SSR implementation: All pages render complete HTML server-side (verify with curl)
- SEO metadata: Title/description/schema.org on every page (validate with search console)
- Performance: Core Web Vitals scores 90+ (measure with Lighthouse)
- Indexation: 100+ pages indexed within 2 weeks (track in Search Console)
- Ranking: Target keywords appear in Baidu/Google within 4 weeks

### Known Limitations & Workarounds
1. **Template content repetition**: Use variable insertion and synonyms to create variation
2. **jieba dictionary gaps**: Manually add domain-specific terms (meeting locations, venue types)
3. **Cache invalidation**: Use short TTLs (5 min) for MVP, implement smarter invalidation later
4. **No historical data**: Log all searches to prepare for future analytics DB

This architecture is designed for rapid implementation while maintaining quality. Codex should follow the phased approach and not attempt to build everything at once. Each phase must be tested and validated before proceeding.
