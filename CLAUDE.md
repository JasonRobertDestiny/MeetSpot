# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MeetSpot is a meeting point recommendation system built with FastAPI and Python 3.11+. It calculates optimal meeting locations based on multiple participants' geographical positions and recommends nearby venues using the Amap (Gaode Map) API.

## Quick Reference

```bash
# Environment
conda activate meetspot-dev              # Or: source venv/bin/activate

# Development
uvicorn api.index:app --reload           # Preferred for iteration
python web_server.py                     # Full stack with auto env detection

# Test the main endpoint
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'

# Testing
pytest tests/ -v                         # Full suite
pytest --cov=app tests/                  # Coverage (target: 80%)
python tests/test_seo.py http://127.0.0.1:8000  # SEO audit (server must be running)

# Quality gates (run before PRs)
black . && ruff check . && mypy app/
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python tools/validate_colors.py          # Design token accessibility check
```

**Key URLs**: Main UI (`/`), API docs (`/docs`), Health (`/health`)

## Environment Setup

**Conda**: `conda env create -f environment.yml && conda activate meetspot`
**Pip**: `python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

**Configuration**:
- Local: Copy `config/config.toml.example` to `config/config.toml`, add Amap API key
- Production: Set `AMAP_API_KEY` and `AMAP_SECURITY_JS_CODE` environment variables

## Architecture

### Entry Points
- `web_server.py` - Main entry, auto-detects production vs development
- `api/index.py` - FastAPI app with all endpoints and middleware

### Three-Tier Configuration System

| Mode | Trigger | Config Source |
|------|---------|---------------|
| Full | `config/config.toml` exists | TOML file via `app/config.py` |
| Simplified | `RAILWAY_ENVIRONMENT` set | `app/config_simple.py` |
| Minimal | Only `AMAP_API_KEY` env var | `MinimalConfig` in `api/index.py` |

Environment variables always take precedence over TOML values.

### Core Components

```
app/tool/meetspot_recommender.py  # Main recommendation engine (CafeRecommender class)
  - UNIVERSITY_EXPANSIONS dict    # 60+ abbreviation mappings (e.g., "北大" -> "北京市海淀区北京大学")
  - PLACE_TYPE_CONFIG dict        # 12 venue themes with colors, icons, Chinese names
  - _rank_places() method         # Scoring: rating(x10) + distance(max 20) + scenario(+15) + requirements(+10)
  - _generate_html_content()      # Creates standalone HTML with Amap JS API

app/design_tokens.py              # WCAG AA color palette, CSS variable generation
api/routers/seo_pages.py          # SEO landing pages (static HTML in public/seo/)
api/services/seo_content.py       # Dynamic SEO content generation
```

### Data Flow

```
User Input -> api/index.py -> CafeRecommender
  1. Address enhancement (university abbreviations)
  2. Geocoding via Amap API (with retry + rate limiting)
  3. Center point calculation (spherical geometry for 2 locations)
  4. POI search (concurrent for multiple keywords like "咖啡馆 餐厅")
  5. Ranking with multi-scenario balancing (2-3 per type, max 8 total)
  6. HTML generation -> workspace/js_src/
```

### Optional Components

Database layer (`app/db/`, `app/models/`) is implemented but optional - core recommendation works without it. Used for auth/social features:
- SQLite + aiosqlite, file: `meetspot.db` (gitignored)
- Auth flow: Register/login -> JWT token (`app/auth/jwt.py`) -> Protected routes

Experimental agent endpoint (`/api/find_meetspot_agent`) requires OpenManus framework (untracked) - **not production-ready**.

## Key Patterns

### Adding a New Venue Theme
1. Add entry to `PLACE_TYPE_CONFIG` in `meetspot_recommender.py`
2. Include: Chinese name, Boxicons icon names, 6 color values
3. Theme auto-applies based on primary keyword match

### Modifying Ranking
Edit `_rank_places()` in `meetspot_recommender.py`:
- Base: Rating x 10
- Distance: Max 20, decays with distance
- Scenario match: +15 for matching venue type
- Requirements: +10 for parking/quiet/business/transit

### Working with Generated HTML
- Templates embedded in `_generate_html_content()` as f-strings
- Files saved to `workspace/js_src/place_recommendation_YYYYMMDDHHMMSS_HASH.html`
- Map uses Amap Loader with security config from environment

## Debugging

**Common Issues**:
- `未找到AMAP_API_KEY环境变量` - Set the environment variable
- Import errors in production - Check MinimalConfig fallback in `api/index.py`
- Empty POI results - Check API rate limits, verify geocoding succeeded
- HTML not generated - Ensure `workspace/js_src/` exists and is writable

**Logging**: Uses loguru via `app/logger.py`. Health endpoint (`/health`) shows config status.

## Code Style

- Python: 4-space indent, type hints, `snake_case` functions, `PascalCase` classes
- CSS: BEM-like (`meetspot-header__title`), colors from `design_tokens.py`
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
