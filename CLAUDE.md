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
# The project includes several test files (as mentioned in README):
python test_optimizations.py      # System optimization tests
python test_multi_scenario.py     # Multi-scenario feature tests
python comprehensive_test.py      # Comprehensive feature tests

# Basic import test
python -c "import app; print('App imports successfully')"

# Code style check
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Docker
```bash
# Build Docker image
docker build -t meetspot:test .

# Run with health check on port 8000
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
- Uses TOML configuration files (`config/config.toml`)
- Copy `config/config.toml.example` to `config/config.toml` for local setup
- Environment variable fallback for deployment (AMAP_API_KEY)
- Dual configuration system: full config.py for development, minimal config for production

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
- Requires valid Amap (Gaode Map) API key in configuration
- Handles geocoding, POI search, and map services
- Graceful fallback when API key is missing (minimal config mode)

### Recommendation Engine
- Multi-scenario support (cafes, restaurants, libraries, etc.)
- Geometric center calculation for fair meeting points
- Intelligent ranking with distance, ratings, and scenario matching
- Deduplication based on name and address similarity

### Error Handling
- Comprehensive exception handling in API endpoints
- Health check endpoint for monitoring
- Graceful degradation when dependencies are missing