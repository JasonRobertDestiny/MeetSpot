# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MeetSpot is an intelligent meeting point recommendation system built with FastAPI and Python 3.11+. It calculates optimal meeting locations based on multiple participants' geographical positions and recommends nearby venues using the Amap (Gaode Map) API.

## Quick Reference

```bash
# Start server
python web_server.py                     # Development server with auto-reload
uvicorn api.index:app --reload           # Alternative

# Test recommendation endpoint
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'

# Health/config check
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/config

# CI validation (what GitHub Actions runs)
python -c "import app; print('OK')"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Code quality (optional)
ruff check . && black .
```

**Key URLs**: Main UI (`/`), API docs (`/docs`), Health (`/health`)

## Environment Setup

**Conda (Recommended)**:
```bash
conda env create -f environment.yml && conda activate meetspot
# For dev tools: conda env create -f environment-dev.yml && conda activate meetspot-dev
```

**Pip alternative**:
```bash
python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

**Configuration**:
- Local: Copy `config/config.toml.example` to `config/config.toml`, add your Amap API key
- Production: Set `AMAP_API_KEY` and `AMAP_SECURITY_JS_CODE` environment variables

## Testing

Project focuses on integration testing. Automated unit tests are minimal.

```bash
# Manual integration test (start server first)
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'

# SEO validation
python verify_seo.py

# Design token color contrast validation
python tools/validate_colors.py

# Existing test files
tests/test_seo.py              # SEO page validation
verify_seo.py                  # SEO content verification
tools/validate_colors.py       # Design token color contrast validation
```

**Test Coverage Notes**:
- Target ≥80% coverage for `app/` package
- Focus on caching, concurrency, and SEO logic
- Integration checks run against live server (see `tests/test_seo.py`)

## Code Architecture

### Entry Points
- `web_server.py`: Main development server entry point, auto-detects production vs development environment
- `api/index.py`: FastAPI application with all endpoints and middleware setup

### Core Application Structure
```
app/
├── config.py          # Pydantic configuration models (LLM, AMap, Browser settings)
├── config_simple.py   # Simplified configuration loader
├── schema.py          # Pydantic data models for API requests/responses
├── logger.py          # Centralized logging setup
├── exceptions.py      # Custom exception classes
├── design_tokens.py   # Design system tokens (colors, spacing, typography)
├── llm.py             # LLM integration (unused in current MeetSpot functionality)
├── auth/              # Authentication (JWT, SMS verification)
│   ├── jwt.py
│   └── sms.py
├── db/                # Database layer (optional)
│   ├── database.py    # SQLAlchemy async engine and session
│   └── crud.py        # Database operations
├── models/            # SQLAlchemy ORM models
│   ├── user.py
│   ├── room.py
│   └── message.py
└── tool/              # Core recommendation logic
    ├── meetspot_recommender.py     # Main recommendation engine
    ├── file_operators.py           # File handling utilities
    ├── web_search.py              # Search utilities
    └── search/                    # Search implementations

api/
├── index.py           # FastAPI app initialization and middleware
├── routers/
│   ├── auth.py        # Authentication endpoints
│   └── seo_pages.py   # SEO landing pages router
└── services/
    └── seo_content.py # SEO content generation service

public/
├── index.html         # Main UI
├── seo/               # SEO landing pages (static HTML)
└── css/               # Stylesheets

workspace/js_src/      # Generated recommendation HTML pages (gitignored)

OpenManus/             # Experimental agent framework (untracked, not used in production)
```

### Configuration Management
**Three-Tier Configuration System:**

1. **Full Configuration Mode** (`config.py`):
   - Triggered when: `config/config.toml` exists and can be imported
   - Includes: LLM, browser, search, Amap settings (legacy components unused in core functionality)
   - Used for: Local development with full TOML configuration
   - Entry: `from app.config import config`

2. **Simplified Configuration Mode** (`config_simple.py`):
   - Triggered when: Production environment detected (e.g., `RAILWAY_ENVIRONMENT` set)
   - Includes: Only Amap API key and logging settings
   - Used for: Production deployments (Render, Railway)
   - Entry: `from app.config_simple import config`

3. **Minimal Fallback Mode** (`api/index.py` MinimalConfig):
   - Triggered when: Neither config file works, but `AMAP_API_KEY` env var exists
   - Includes: Only Amap API key (bare minimum)
   - Used for: Vercel or environments without full dependencies
   - Entry: `MinimalConfig` class instantiation in `api/index.py`

**Configuration Priority**: Environment variables > TOML config values

**Setup**:
- Local development: Copy `config/config.toml.example` to `config/config.toml`
- Deployment: Set environment variables (`AMAP_API_KEY`, `AMAP_SECURITY_JS_CODE`)
- Database: Optional SQLite database for auth/social features (see Database section)

**Troubleshooting**:
- "未找到AMAP_API_KEY环境变量": Set the `AMAP_API_KEY` environment variable
- Import errors in production: Check if MinimalConfig fallback is working
- `/health` endpoint shows current configuration mode

### API Architecture
- **FastAPI** with automatic OpenAPI documentation
- **CORS middleware** enabled for cross-origin requests
- **Rate limiting** via SlowAPI middleware
- **Static file serving** for frontend assets
- **Fallback configuration**: System works in minimal mode if full config unavailable
  - `api/index.py` contains MinimalConfig class for deployment environments
  - Can run with only AMAP_API_KEY environment variable
- **Health check endpoint** at `/health`
- **Main recommendation endpoint** at `POST /api/find_meetspot`

### Key Dependencies
- **FastAPI + Pydantic** - Web framework and data validation
- **aiohttp** - Async HTTP client for Amap API calls
- **SQLAlchemy + aiosqlite** - Async database (optional, for auth/social features)
- **python-jose + passlib** - JWT auth and password hashing
- **jieba** - Chinese text segmentation for SEO
- **slowapi** - Rate limiting middleware

See `requirements.txt` for full list with versions.

### Deployment
- **Render.com**: `render.yaml`
- **Railway**: Auto-detects via `RAILWAY_ENVIRONMENT` env var
- **Docker**: Multi-stage Dockerfile (`FROM python:3.12-slim`)
- **GitHub Actions**: Tests Python 3.11/3.12, runs import validation and flake8
- **Environment variables**: `AMAP_API_KEY`, `PORT`, `RAILWAY_ENVIRONMENT`, `AMAP_SECURITY_JS_CODE`

### Frontend Integration
- Static HTML/CSS/JS served from `public/` directory
- Generated recommendation pages in `workspace/js_src/`
- Uses Amap JavaScript API for map rendering
- SEO landing pages served via `/api/routers/seo_pages.py`:
  - Static SEO pages in `public/seo/` directory
  - Used for search engine optimization and social sharing

## Development Notes

### Experimental Agent Mode (Not Production-Ready)

The codebase includes an experimental agent endpoint (`/api/find_meetspot_agent`) that uses the OpenManus framework for AI-driven recommendations. This is NOT used in production:

- Located in `api/index.py:447-526`
- Requires OpenManus directory (currently untracked)
- Falls back to rule-based mode if agent unavailable
- **DO NOT USE** for production features without explicit discussion

### Database Architecture (Optional)

Database layer is implemented but optional. Core MeetSpot recommendation works without it.

- **SQLAlchemy 2.0** async with `aiosqlite`, file: `meetspot.db` (gitignored)
- **Models**: `app/models/` (User, Room, Message)
- **CRUD**: `app/db/crud.py`, Session: `app/db/database.py` (`get_db()` dependency)
- **Auth flow**: Register/login → JWT token (`app/auth/jwt.py`) → Protected routes validate via `Depends(get_current_user)`
- **Init**: Auto-runs `init_db()` on startup via `api/index.py`

### Amap API Integration
- **Geocoding API**: Converts address strings to coordinates with retry logic and rate limiting
- **POI Search API**: Searches venues within radius (default 5km) around center point
- **Concurrent Searches**: Multi-scenario searches run in parallel for better performance
- **Caching**: In-memory caching for geocode and POI results to reduce API calls
- **Rate Limiting**: Built-in delays (0.5s-2s) to avoid API quota limits
- **Error Recovery**: Automatic retry with exponential backoff for failed requests

### Recommendation Engine (`meetspot_recommender.py`)

**Core Features:**
1. **Intelligent Address Enhancement**
   - Auto-expands university abbreviations (e.g., "北大" → "北京市海淀区北京大学")
   - 60+ pre-configured university mappings with city info to avoid ambiguity
   - Smart error messages when geocoding fails

2. **Center Point Calculation**
   - Spherical geometry for 2 locations (accurate geodesic midpoint)
   - Simple average for 3+ locations
   - Optimized for fairness among all participants

3. **Multi-Scenario Search**
   - Concurrent async searches for multiple keywords (e.g., "咖啡馆 餐厅 图书馆")
   - Smart deduplication based on name + location (not address)
   - Balanced results: ensures representation from each scenario

4. **Ranking Algorithm**
   - Base score: Rating × 10 (from Amap reviews)
   - Distance score: Max 20 points, decays with distance from center
   - Scenario match bonus: +15 points if venue matches user's selected type
   - User requirements bonus: +10 points for parking/quiet/business/transit matches
   - Multi-scenario balancing: Ensures diversity (2-3 per scenario, max 8 total)

5. **Dynamic Theming System**
   - 12 pre-configured themes (coffee, restaurant, library, gym, KTV, etc.)
   - Each theme has custom colors, icons (Boxicons), and Chinese naming
   - CSS variables dynamically injected based on primary keyword
   - Responsive design with gradient backgrounds and animations

6. **HTML Generation**
   - Creates standalone HTML pages with embedded Amap JS API
   - Includes interactive map with custom markers (center, locations, venues)
   - Shows AI search process with step-by-step animations
   - Responsive card layout with venue details, ratings, navigation links
   - Files saved to `workspace/js_src/` with timestamp and UUID

### Design System (`app/design_tokens.py`)
- **WCAG AA compliant** color palette with accessibility verification
- **Design tokens** for colors, spacing, typography, and animations
- **CSS variable generation** for consistent theming across the application
- **Validation utilities** to ensure color contrast ratios meet accessibility standards
- Located in `app/design_tokens.py`, referenced in frontend CSS

### SEO Implementation
- **Static SEO pages** in `public/seo/` for different venue types and cities
- **Dynamic SEO content** generation via `api/services/seo_content.py`
- **Meta tags optimization** with proper Open Graph and Twitter Card tags
- **Structured data** (JSON-LD) for better search engine understanding
- **Chinese text segmentation** using jieba for keyword extraction
- **SEO router** at `api/routers/seo_pages.py` handles landing pages

### Error Handling
- **Address Validation**: Detailed error messages with suggestions for invalid addresses
- **Geocoding Failures**: Detects university abbreviations and provides enhanced suggestions
- **Empty Results**: Intelligent analysis of why no venues were found
- **API Errors**: Graceful handling of rate limits, network issues, and quota exceeded
- **Health Check**: `/health` endpoint reports configuration status
- **Fallback Mode**: Minimal functionality when config is incomplete

## API Endpoints

### Main Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage redirect to main UI |
| `/api/find_meetspot` | POST | Main recommendation endpoint (production) |
| `/api/find_meetspot_agent` | POST | Agent mode endpoint (experimental, not production) |
| `/recommend` | POST | Legacy compatibility endpoint |
| `/health` | GET | Health check and config status |
| `/config` | GET | Configuration status (no secrets) |
| `/api/status` | GET | API status and version info |
| `/workspace/js_src/{filename}` | GET | Generated HTML recommendation pages |
| `/docs` | GET | Auto-generated API documentation |
| `/seo/{city}/{venue_type}` | GET | SEO landing pages |
| `/google48ac1a797739b7b0.html` | GET/HEAD | Google Search Console verification |
| `/BingSiteAuth.xml` | GET/HEAD | Bing webmaster verification |

**Authentication Endpoints** (in `api/routers/auth.py`):
- `/api/auth/register` - User registration
- `/api/auth/login` - User login with JWT token
- `/api/auth/sms/send` - Send SMS verification code
- `/api/auth/sms/verify` - Verify SMS code
- Protected routes use JWT authentication via `Depends(get_current_user)`

### Request/Response Format

**POST /api/find_meetspot**
```json
{
  "locations": ["北京大学", "清华大学"],
  "keywords": "咖啡馆 餐厅",  // Space-separated for multi-scenario
  "place_type": "",            // Optional Amap POI type code
  "user_requirements": "停车方便"
}
```

**Success Response:**
```json
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250624_12345678.html",
  "locations_count": 2,
  "keywords": "咖啡馆 餐厅",
  "processing_time": 0.52,
  "output": "详细推荐文本..."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "错误信息",
  "processing_time": 0.12,
  "message": "推荐失败: ..."
}
```

## Common Development Patterns

### Important File Locations

**Configuration Files**:
- `config/config.toml.example` - Template for local configuration
- `config/config.toml` - Local config (gitignored, create from example)
- Environment variables take precedence over TOML config

**Generated Files** (gitignored):
- `workspace/js_src/*.html` - Dynamic recommendation pages
- Do not manually edit generated HTML files

**Static Assets**:
- `public/` - Static frontend files
- `public/seo/` - SEO landing pages
- `public/BingSiteAuth.xml` - Bing webmaster verification

**Documentation & Specs**:
- `.claude/specs/` - Feature specifications and architecture docs
- `AGENTS.md` - Repository guidelines and module organization
- `CONDA_SETUP_GUIDE.md` - Detailed conda environment setup

### Adding a New Venue Type Theme
1. Add theme configuration to `PLACE_TYPE_CONFIG` in `meetspot_recommender.py` (line ~63)
2. Include Chinese name, icons (from Boxicons), and 6 color values
3. Theme is auto-applied based on primary keyword in search
4. Consider accessibility (use `design_tokens.py` utilities to verify color contrast)

### Modifying Ranking Algorithm
- Main logic in `_rank_places()` method in `meetspot_recommender.py`
- Adjust scoring weights: rating (×10), distance (max 20), scenario match (+15), requirements (+10)
- Multi-scenario balancing in the same method ensures diversity

### Environment-Specific Behavior
- `web_server.py` detects `RAILWAY_ENVIRONMENT` env var for production mode
- Disables auto-reload in production
- `api/index.py` has fallback MinimalConfig for environments without full dependencies

### Working with Generated HTML
- HTML templates are embedded in `_generate_html_content()` method in `meetspot_recommender.py` (line 875+)
- Uses f-strings with dynamic theming via CSS variables
- Map initialization via Amap Loader with security config
- Files are auto-saved to `workspace/js_src/` directory
- Filename format: `place_recommendation_YYYYMMDDHHMMSS_HASH.html`

### University Abbreviation Mapping
- The system auto-expands 60+ university abbreviations to avoid geocoding ambiguity
- Mapping located in `meetspot_recommender.py` as `UNIVERSITY_EXPANSIONS` dict
- Example: "北大" → "北京市海淀区北京大学"
- When adding new universities, include city name to avoid ambiguity

### Debugging Tips

**Common Issues**:
- **Import errors in production**: Check if MinimalConfig fallback is working in `api/index.py`
- **Geocoding failures**: Verify AMAP_API_KEY is set correctly
- **Empty POI results**: Check API rate limits, verify location keywords
- **HTML not generated**: Ensure `workspace/js_src/` directory exists and is writable

**Logging**:
- All logs use loguru logger from `app/logger.py`
- Check console output for detailed error messages
- Health endpoint (`/health`) shows configuration status

### Authentication & Security

- **JWT**: `app/auth/jwt.py` issues tokens (30-day expiry), verified via `get_current_user` dependency
- **Passwords**: bcrypt hashed via `passlib`, verified with `verify_password()`
- **SMS**: Optional phone verification in `app/auth/sms.py`
- **Rate limiting**: SlowAPI middleware prevents abuse
- **CORS**: Configured for cross-origin requests

## Git Workflow

### Commit Message Format
Follow Conventional Commits specification:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore`

**Examples**:
```
feat(recommender): add multi-scenario search support
fix(seo): correct meta tag generation for Chinese content
docs(readme): update API endpoint documentation
ci: upgrade GitHub Actions to latest versions
```

### Branch Strategy
- `main`: Production-ready code
- Feature branches: `feature/description` or `feat/description`
- Bug fixes: `fix/description`
- Experimental work: `experiment/description`

### Pull Request Guidelines
1. Reference related issues in PR description
2. Include summary of changes and user impact
3. Add screenshots/GIFs for UI changes
4. List commands/tests run to verify changes
5. Note any config changes or migration requirements

## Code Style & Quality

### Python Conventions
- **Formatting**: 4-space indent, type hints everywhere
- **Naming**: `snake_case` for functions, `PascalCase` for classes, `SCREAMING_SNAKE_CASE` for constants
- **Functions**: Keep under ~50 lines, prefer dataclasses for structured payloads
- **Logging**: Use structured messages via `app/logger.py` (loguru)

### Quality Gates
Run before opening a PR:
```bash
black .                  # Auto-format code
ruff check .            # Lint checks
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Frontend Conventions
- **CSS**: BEM-like class names (`meetspot-header__title`)
- **Colors**: Declare shared colors via `static/css/design-tokens.css`
- **Inline styles**: Limited to offline-only HTML in `workspace/js_src/`
