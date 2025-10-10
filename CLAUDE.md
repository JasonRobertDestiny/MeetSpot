# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MeetSpot is an intelligent meeting point recommendation system built with FastAPI and Python 3.11+. It calculates optimal meeting locations based on multiple participants' geographical positions and recommends nearby venues using the Amap (Gaode Map) API.

## Development Commands

### Local Development
```bash
# Start development server
python web_server.py
# or
npm run dev

# Install dependencies
pip install -r requirements.txt

# Access application
# http://127.0.0.1:8000 (main application)
# http://127.0.0.1:8000/docs (API documentation)
# http://127.0.0.1:8000/health (health check)
```

### Testing
```bash
# Basic import test (used in CI/CD)
python -c "import app; print('App imports successfully')"

# Code style check
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Manual API testing
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'
```

### Docker
```bash
# Build Docker image
docker build -t meetspot:test .

# Run container with environment variables
docker run -d -p 8000:8000 \
  -e AMAP_API_KEY="your_api_key_here" \
  --name meetspot meetspot:test

# Check container health
docker ps
curl http://localhost:8000/health
```

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
├── llm.py             # LLM integration (unused in current MeetSpot functionality)
└── tool/              # Core recommendation logic
    ├── meetspot_recommender.py     # Main recommendation engine
    ├── file_operators.py           # File handling utilities
    ├── web_search.py              # Search utilities
    └── search/                    # Search implementations
```

### Configuration Management
**Dual Configuration System:**
- **Development Mode**: Full `config.py` with LLM, browser, search settings (not used for MeetSpot core)
- **Production Mode**: Simplified `config_simple.py` with only Amap and logging settings
- **Local Setup**: Copy `config/config.toml.example` to `config/config.toml`
- **Deployment**: Uses environment variables (`AMAP_API_KEY`, `AMAP_SECURITY_JS_CODE`)
- **Priority**: Environment variables override TOML config values
- **Graceful Fallback**: System creates minimal config if TOML file is missing

### API Architecture
- **FastAPI** with automatic OpenAPI documentation
- **CORS middleware** enabled for cross-origin requests
- **Static file serving** for frontend assets
- **Health check endpoint** at `/health`
- **Main recommendation endpoint** at `POST /api/find_meetspot`

### Key Dependencies
- `fastapi==0.116.1` - Web framework
- `uvicorn==0.35.0` - ASGI server
- `pydantic==2.11.7` - Data validation
- `aiohttp==3.12.15` - Async HTTP client for Amap API calls
- `loguru==0.7.3` - Enhanced logging

### Deployment Configuration
- **Render.com** deployment via `render.yaml`
- **Docker** support with multi-stage build
- **GitHub Actions** CI/CD with Python 3.11/3.12 matrix testing
- Environment variables: `AMAP_API_KEY`, `PORT`, `RAILWAY_ENVIRONMENT`

### Frontend Integration
- Static HTML/CSS/JS served from `public/` directory
- Generated recommendation pages in `workspace/js_src/`
- Uses Amap JavaScript API for map rendering

## Development Notes

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
| `/api/find_meetspot` | POST | Main recommendation endpoint |
| `/recommend` | POST | Legacy compatibility endpoint |
| `/health` | GET | Health check and config status |
| `/config` | GET | Configuration status (no secrets) |
| `/workspace/js_src/{filename}` | GET | Generated HTML recommendation pages |
| `/docs` | GET | Auto-generated API documentation |

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

### Adding a New Venue Type Theme
1. Add theme configuration to `PLACE_TYPE_CONFIG` in `meetspot_recommender.py`
2. Include Chinese name, icons (from Boxicons), and 6 color values
3. Theme is auto-applied based on primary keyword in search

### Modifying Ranking Algorithm
- Main logic in `_rank_places()` method
- Adjust scoring weights: rating (×10), distance (max 20), scenario match (+15), requirements (+10)
- Multi-scenario balancing in the same method ensures diversity

### Environment-Specific Behavior
- `web_server.py` detects `RAILWAY_ENVIRONMENT` env var for production mode
- Disables auto-reload in production
- `api/index.py` has fallback MinimalConfig for environments without full dependencies

### Working with Generated HTML
- HTML templates are embedded in `_generate_html_content()` method (line 875+)
- Uses f-strings with dynamic theming via CSS variables
- Map initialization via Amap Loader with security config
- Files are auto-saved to `workspace/js_src/` directory