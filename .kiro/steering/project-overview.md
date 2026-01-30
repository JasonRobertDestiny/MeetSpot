# MeetSpot Project Overview

## What is MeetSpot?

MeetSpot is an AI-powered multi-person meeting point recommendation system that finds fair meeting locations using geographic algorithms and LLM-based intelligent scoring. It integrates with Amap (高德地图) for geolocation services and uses GPT-4o for semantic analysis.

## Core Architecture

### Technology Stack
- **Backend**: FastAPI + SQLAlchemy (async) + aiosqlite
- **Frontend**: Jinja2 templates + CSS design tokens + Amap JS API
- **AI/LLM**: OpenAI SDK (GPT-4o, DeepSeek), tiktoken for token counting
- **External APIs**: Amap (高德地图) for geocoding and POI search
- **Deployment**: Docker, Render, Vercel support

### Key Components
1. **Intelligent Routing System**: Automatically selects between fast rule-based mode and deep LLM-enhanced Agent mode
2. **5-Step Recommendation Pipeline**: Geocoding → Center calculation → POI search → Ranking → HTML generation
3. **WCAG 2.1 AA Design System**: Accessible color tokens and responsive design
4. **SEO-Optimized Pages**: Schema.org structured data, meta tags, sitemap
5. **Authentication**: JWT + SMS verification system

## Project Structure
```
MeetSpot/
├── api/                    # FastAPI application layer
├── app/                    # Core business logic (authoritative source)
│   ├── tool/              # Tool implementations (recommender, search, etc.)
│   ├── agent/             # AI Agent system (currently disabled)
│   ├── auth/              # Authentication (JWT, SMS)
│   ├── models/            # SQLAlchemy ORM models
│   └── db/                # Database layer
├── templates/             # Jinja2 templates
├── static/                # CSS, design tokens
├── public/                # Marketing pages, SEO assets
├── workspace/js_src/      # Generated recommendation HTML pages
└── tests/                 # Test suite
```

## Development Workflow
- Use `python web_server.py` for local development
- Quality gates: `black .`, `ruff check .`, `mypy app/` must be clean
- Target ≥80% test coverage for `app/` package
- Follow Conventional Commits (`feat:`, `fix:`, `ci:`, `docs:`)

## Key Features
- **Complexity Assessment**: Automatically routes simple requests to fast rule mode, complex ones to LLM mode
- **Multi-factor Scoring**: Base score + popularity + distance + scenario + requirements
- **Brand Knowledge Base**: 60+ brand mappings with feature scores
- **Caching Strategy**: Optimized for memory constraints on cloud platforms
- **Accessibility First**: All colors meet WCAG 2.1 AA contrast requirements