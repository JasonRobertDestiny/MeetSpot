# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MeetSpot is an **AI Agent** for multi-person meeting point recommendations. Users provide locations and requirements; the Agent calculates the geographic center and recommends optimal venues. Built with FastAPI and Python 3.11+, uses Amap (Gaode Map) API for geocoding/POI search, and DeepSeek/GPT-4o-mini for semantic scoring.

**Live Demo**: https://meetspot-irq2.onrender.com

## Quick Reference

```bash
# Environment
conda activate meetspot                  # Or: source venv/bin/activate

# Development
uvicorn api.index:app --reload           # Preferred for iteration
python web_server.py                     # Full stack with auto env detection

# Test the main endpoint
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'

# Testing
pytest tests/ -v                         # Full suite
pytest tests/test_file.py::test_name -v  # Single test
pytest --cov=app tests/                  # Coverage (target: 80%)
python tests/test_seo.py http://localhost:8000  # SEO validation (standalone)

# Quality gates (run before PRs)
black . && ruff check . && mypy app/
```

**Key URLs**: Main UI (`/`), API docs (`/docs`), Health (`/health`)

## Environment Setup

**Conda**: `conda env create -f environment.yml && conda activate meetspot` (env name is `meetspot`, not `meetspot-dev`)
**Pip**: `python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

**Required Environment Variables**:
- `AMAP_API_KEY` - Gaode Map API key (required)
- `AMAP_SECURITY_JS_CODE` - JS security code for frontend map
- `LLM_API_KEY` - DeepSeek/OpenAI API key (for AI chat and LLM scoring)
- `LLM_API_BASE` - API base URL (default: `https://newapi.deepwisdom.ai/v1`)
- `LLM_MODEL` - Model name (default: `deepseek-chat`)

**Local Config**: Copy `config/config.toml.example` to `config/config.toml` and fill in API keys. Alternatively, create a `.env` file with the environment variables above.

## Architecture

### Request Flow

```
POST /api/find_meetspot
        ↓
Complexity Router (assess_request_complexity)
        ↓
Rule+LLM Mode (Agent mode disabled for memory savings on free tier)
        ↓
5-Step Pipeline: Geocode → Center Calc → POI Search → Ranking → HTML Gen
```

Complexity scoring: +10/location, +15 for complex keywords, +10 for special requirements. Currently all requests use Rule+LLM mode since Agent mode is disabled (`agent_available = False` in `api/index.py`).

### Entry Points
- `web_server.py` - Main entry, auto-detects production vs development
- `api/index.py` - FastAPI app with all endpoints, middleware, and request handling

### Three-Tier Configuration (Graceful Degradation)

| Mode | Trigger | What Works |
|------|---------|------------|
| Full | `config/config.toml` exists | All features, TOML-based config |
| Simplified | `RAILWAY_ENVIRONMENT` set | Uses `app/config_simple.py` |
| Minimal | Only `AMAP_API_KEY` env var | `MinimalConfig` class in `api/index.py`, basic recommendations only |

### Core Components

```
app/tool/meetspot_recommender.py    # Main recommendation engine (CafeRecommender class)
  |- university_mapping dict        # 45 abbreviations (e.g., "北大" -> "北京市海淀区北京大学")
  |- landmark_mapping dict          # 45 city landmarks (e.g., "陆家嘴" -> "上海市浦东新区陆家嘴")
  |- PLACE_TYPE_CONFIG dict         # 12 venue themes with colors, icons
  |- _rank_places()                 # 100-point scoring algorithm
  |- _generate_html_content()       # Standalone HTML with Amap JS API
  |- geocode_cache (max 30)         # LRU-style address cache (reduced for free tier)
  |- poi_cache (max 15)             # LRU-style POI cache (reduced for free tier)

app/design_tokens.py                # WCAG AA color palette, CSS generation
api/routers/seo_pages.py            # SEO landing pages
```

### LLM Scoring (Agent Mode)

When Agent Mode is enabled, final venue scores blend rule-based and LLM semantic analysis:
```
Final Score = Rule Score * 0.4 + LLM Score * 0.6
```
Agent Mode is currently disabled (`agent_available = False`) to conserve memory on free hosting tiers.

### Data Flow

```
1. Address enhancement (90+ university/landmark mappings)
2. Geocoding via Amap API (with retry + rate limiting)
3. Center point calculation (spherical geometry)
4. POI search (concurrent for multiple keywords)
   Fallback: tries 餐厅->咖啡馆->商场->美食, then expands to 50km
5. Ranking with multi-scenario balancing (max 8 venues)
6. HTML generation -> workspace/js_src/
```

### Optional Components

Database layer (`app/db/`, `app/models/`) is optional - core recommendation works without it. Used for auth/social features with SQLite + aiosqlite.

Experimental agent endpoint (`/api/find_meetspot_agent`) requires OpenManus framework - **not production-ready**.

## Key Patterns

### Ranking Algorithm
Edit `_rank_places()` in `meetspot_recommender.py`:
- Base: 30 points (rating x 6)
- Popularity: 20 points (log-scaled reviews)
- Distance: 25 points (500m = full score, decays)
- Scenario: 15 points (keyword match)
- Requirements: 10 points (parking/quiet/business)

### Distance Filtering
Two-stage distance handling in `meetspot_recommender.py`:
1. **POI Search**: Amap API `radius` parameter (hardcoded 5000m, fallback to 50000m)
2. **Post-filter**: `max_distance` parameter in `_rank_places()` (default 100km, in meters)

The `max_distance` filter applies after POI retrieval during ranking. To change search radius, modify `radius=5000` in `_search_places()` calls around lines 556-643.

### Brand Knowledge Base
`BRAND_FEATURES` dict in `meetspot_recommender.py` contains 50+ brand profiles (Starbucks, Haidilao, etc.) with feature scores (0.0-1.0) for: quiet, WiFi, business, parking, child-friendly, 24h. Used in requirements matching - brands scoring >=0.7 satisfy the requirement. Place types prefixed with `_` (e.g., `_library`) provide defaults.

### Adding Address Mappings
In `_enhance_address()` method:
- `university_mapping` dict for university abbreviations
- `landmark_mapping` dict for city landmarks (prevents cross-city geocoding errors)

### Adding Venue Themes
Add entry to `PLACE_TYPE_CONFIG` with: Chinese name, Boxicons icons, 6 color values.

## Debugging

| Issue | Solution |
|-------|----------|
| `未找到AMAP_API_KEY` | Set environment variable |
| Import errors in production | Check MinimalConfig fallback |
| Wrong city geocoding | Add to `landmark_mapping` with city prefix |
| Empty POI results | Fallback mechanism handles this automatically |
| Render OOM (512MB) | Caches are reduced (30/15 limits); Agent mode disabled |
| Render service down | Trigger redeploy: `git commit --allow-empty -m "trigger redeploy" && git push` |

**Logging**: Uses loguru via `app/logger.py`. `/health` endpoint shows config status.

## Deployment

Hosted on Render free tier (512MB RAM, cold starts after 15min idle).

**Redeploy**: Push to `main` branch triggers auto-deploy. For manual restart without code changes:
```bash
git commit --allow-empty -m "chore: trigger redeploy" && git push origin main
```

**Generated artifacts**: HTML files in `workspace/js_src/` are runtime-generated and should not be committed.

## Code Style

- Python: 4-space indent, type hints, `snake_case` functions, `PascalCase` classes
- CSS: BEM-like (`meetspot-header__title`), colors from `design_tokens.py`
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`)
