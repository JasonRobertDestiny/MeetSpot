<div align="center">

# MeetSpot

<img src="docs/logo.jpg" alt="MeetSpot Logo" width="180"/>

**Intelligent Multi-Person Meeting Point Recommendation System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://github.com/JasonRobertDestiny/MeetSpot/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonRobertDestiny/MeetSpot/actions)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://meetspot-irq2.onrender.com)

[Live Demo](https://meetspot-irq2.onrender.com) | [Demo Video](https://www.bilibili.com/video/BV1aUK7zNEvo/) | English | [Chinese](README_ZH.md)

</div>

---

## Overview

MeetSpot solves a common problem: **finding the fairest meeting point for multiple people**. Input participant addresses, and the system calculates the optimal center point using spherical geometry, then recommends nearby venues with AI-powered intelligent scoring.

<div align="center">
<img src="docs/show1.jpg" alt="MeetSpot Interface" width="85%"/>
</div>

---

## Key Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Agent Intelligent Routing** | Smart decision engine that selects optimal processing mode based on query complexity |
| **AI-Powered Scoring** | Multi-dimensional venue ranking based on ratings, distance, scenario match, and user requirements |
| **Smart Center Calculation** | Spherical geometry ensures fairness for all participants |
| **Multi-Scenario Search** | Search cafes, restaurants, libraries simultaneously with concurrent async processing |
| **Interactive Map** | Visual markers for center point, participants, and venues with Amap JS API |
| **60+ University Shortcuts** | "PKU" auto-expands to "Peking University, Haidian District, Beijing" |
| **350+ Cities** | Coverage across major Chinese cities via Amap API |

### Agent Thinking Experience

The system provides a visual "Agent Thinking" experience that shows the AI decision process in real-time:

```
Step 1: Parse Addresses     -> Geocode participant locations
Step 2: Calculate Center    -> Find the fairest meeting point
Step 3: Search Venues       -> Discover nearby quality locations
Step 4: Intelligent Scoring -> Multi-dimensional evaluation
Step 5: Generate Results    -> Output personalized recommendations
```

### Dynamic Theming

12 pre-configured venue themes with custom colors, icons, and Chinese naming:
- Coffee Shop, Restaurant, Library, Gym, KTV, Bar
- Cinema, Shopping Mall, Park, Museum, Bookstore, Tea House

### UI/UX Features

| Feature | Description |
|---------|-------------|
| **Agent Brain Animation** | Visual brain icon with pulsing animation and thought bubbles during processing |
| **Step-by-Step Progress** | 5-step thinking visualization with icons and progress indicators |
| **WCAG AA Compliant** | Accessible color palette with verified contrast ratios |
| **Responsive Design** | Mobile-first approach with adaptive layouts |
| **Gradient Backgrounds** | Dynamic color gradients based on venue theme |
| **Micro-animations** | Smooth transitions and hover effects throughout |
| **Boxicons Integration** | Consistent iconography across all UI elements |

---

## Screenshots

### User Flow

<table>
<tr>
<td width="50%">
<img src="docs/homepage.jpg" alt="Homepage"/>
<p align="center"><b>Homepage</b></p>
</td>
<td width="50%">
<img src="docs/finder-input.jpg" alt="Finder Page"/>
<p align="center"><b>Meeting Point Finder</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/finder-filled.jpg" alt="Input Filled"/>
<p align="center"><b>Location Input</b></p>
</td>
<td width="50%">
<img src="docs/complex-scenario-input.jpg" alt="Complex Scenario"/>
<p align="center"><b>Multi-Location Scenario</b></p>
</td>
</tr>
</table>

### Agent Thinking Experience

<table>
<tr>
<td width="50%">
<img src="docs/agent-thinking.jpg" alt="Agent Thinking"/>
<p align="center"><b>AI Processing Animation</b></p>
</td>
<td width="50%">
<img src="docs/agent-thinking-complex.jpg" alt="Complex Processing"/>
<p align="center"><b>Multi-Step Analysis</b></p>
</td>
</tr>
</table>

### Results & Recommendations

<table>
<tr>
<td width="50%">
<img src="docs/result-summary.jpg" alt="Results Summary"/>
<p align="center"><b>Results Summary</b></p>
</td>
<td width="50%">
<img src="docs/result-ai-process.jpg" alt="AI Process"/>
<p align="center"><b>AI Decision Process</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/result-map.jpg" alt="Map Display"/>
<p align="center"><b>Interactive Map</b></p>
</td>
<td width="50%">
<img src="docs/result-recommendations.jpg" alt="Recommendations"/>
<p align="center"><b>Venue Recommendations</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/result-traffic.jpg" alt="Location & Map"/>
<p align="center"><b>Location Info & Map</b></p>
</td>
<td width="50%">
<img src="docs/多维度智能评分show4.jpg" alt="Intelligent Scoring"/>
<p align="center"><b>AI Scoring System</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/show6停车建议.jpg" alt="Transport Tips"/>
<p align="center"><b>Transport & Parking Tips</b></p>
</td>
<td width="50%">
<img src="docs/show5推荐地点.jpg" alt="Venue Cards"/>
<p align="center"><b>Venue Recommendation Cards</b></p>
</td>
</tr>
</table>

<details>
<summary><b>More Screenshots</b></summary>

### AI Customer Service
<div align="center">
<img src="docs/AI客服.jpg" alt="AI Customer Service" width="80%"/>
</div>

### Amap Navigation Integration
<div align="center">
<img src="docs/show7高德地图.jpg" alt="Amap Navigation" width="80%"/>
</div>

</details>

---

## System Architecture

### High-Level Flow

```
User Input -> Frontend -> API Gateway -> Intelligent Router
                                              |
                         +--------------------+--------------------+
                         |                                         |
                    Agent Mode                                Rule Mode
               (Complex/Personalized)                     (Simple/Fast)
                         |                                         |
                    MeetSpotAgent                          CafeRecommender
                         |                                         |
                         +--------------------+--------------------+
                                              |
              Geocoding -> Center Calculation -> POI Search -> Ranking -> HTML Generation
```

### Component Architecture

```
MeetSpot/
├── api/
│   ├── index.py                    # FastAPI app with middleware & routing
│   ├── routers/
│   │   ├── auth.py                 # JWT authentication endpoints
│   │   └── seo_pages.py            # SEO landing pages router
│   └── services/
│       └── seo_content.py          # SEO content generation
├── app/
│   ├── tool/
│   │   └── meetspot_recommender.py # Core recommendation engine (CafeRecommender)
│   ├── auth/
│   │   ├── jwt.py                  # JWT token management
│   │   └── sms.py                  # SMS verification
│   ├── db/
│   │   ├── database.py             # SQLAlchemy async engine
│   │   └── crud.py                 # Database operations
│   ├── models/                     # SQLAlchemy ORM models
│   ├── config.py                   # Full configuration (TOML-based)
│   ├── config_simple.py            # Simplified config for production
│   ├── design_tokens.py            # WCAG AA compliant design system
│   └── schema.py                   # Pydantic data models
├── public/
│   ├── index.html                  # Main UI
│   ├── meetspot_finder.html        # Meeting point finder page
│   └── seo/                        # Static SEO pages
├── workspace/js_src/               # Generated recommendation HTML pages
├── config/
│   └── config.toml.example         # Configuration template
└── web_server.py                   # Application entry point
```

### Core Algorithm

1. **Address Enhancement**: Auto-expands abbreviations with city info (60+ university mappings)
2. **Center Calculation**: Spherical geometry for 2 locations, weighted average for 3+
3. **Multi-Scenario Search**: Concurrent async searches with smart deduplication (name + location based)
4. **Ranking Formula**:
   - Base score: Rating x 10 (from Amap reviews)
   - Distance score: Max 20 points, decays with distance
   - Scenario match: +15 points if venue matches selected type
   - Requirements bonus: +10 points for parking/quiet/business/transit matches
5. **Multi-Scenario Balancing**: 2-3 venues per scenario, max 8 total results

---

## Quick Start

### Prerequisites

- Python 3.11+
- Amap API Key ([Get one here](https://lbs.amap.com/))

### Installation

```bash
# Clone repository
git clone https://github.com/JasonRobertDestiny/MeetSpot.git
cd MeetSpot

# Install dependencies (choose one)
pip install -r requirements.txt
# Or with conda:
conda env create -f environment.yml && conda activate meetspot

# Configure API key
cp config/config.toml.example config/config.toml
# Edit config/config.toml with your Amap API key

# Start server
python web_server.py
```

Open http://127.0.0.1:8000 in your browser.

### Docker (Alternative)

```bash
docker build -t meetspot .
docker run -p 8000:8000 -e AMAP_API_KEY=your_key meetspot
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AMAP_API_KEY` | Yes | Amap API key for geocoding and POI search |
| `AMAP_SECURITY_JS_CODE` | No | Amap JS API security code |
| `PORT` | No | Server port (default: 8000) |
| `LLM_API_KEY` | No | LLM API key for intelligent scoring |
| `LLM_API_BASE` | No | LLM API base URL |

---

## Usage

1. **Enter Locations**: Add 2-10 participant addresses (supports university abbreviations)
2. **Select Venue Types**: Choose from 12 categories (cafe, restaurant, library, gym, KTV, etc.)
3. **Set Requirements** (Optional): parking, quiet environment, private rooms, transit access
4. **View Results**: Interactive map with ranked venue recommendations and navigation links

---

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/find_meetspot` | POST | Main recommendation endpoint (rule-based) |
| `/api/find_meetspot_agent` | POST | Agent mode recommendation (AI-driven) |
| `/api/ai_chat` | POST | AI customer service |
| `/health` | GET | Health check and config status |
| `/config` | GET | Configuration status (no secrets) |
| `/docs` | GET | OpenAPI documentation |

### SEO & Marketing Pages

| Endpoint | Description |
|----------|-------------|
| `/` | Homepage |
| `/about` | About page |
| `/faq` | FAQ page |
| `/how-it-works` | Usage guide |
| `/meetspot/{city}` | City-specific landing pages |

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | JWT login |
| `/api/auth/sms/send` | POST | Send SMS verification |
| `/api/auth/sms/verify` | POST | Verify SMS code |

### Request/Response Examples

**POST /api/find_meetspot**

```json
// Request
{
  "locations": ["Peking University", "Tsinghua University"],
  "keywords": "cafe restaurant",
  "user_requirements": "parking"
}

// Success Response
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250614_abc123.html",
  "locations_count": 2,
  "keywords": "cafe restaurant",
  "processing_time": 0.52,
  "output": "Detailed recommendation text..."
}

// Error Response
{
  "success": false,
  "error": "Error message",
  "processing_time": 0.12,
  "message": "Recommendation failed: ..."
}
```

**POST /api/find_meetspot_agent**

```json
// Request (same as above)

// Response includes additional fields
{
  "success": true,
  "mode": "agent",
  "recommendation": "AI-generated recommendation",
  "geocode_results": [...],
  "center_point": {"lat": 39.99, "lng": 116.31},
  "search_results": [...],
  "steps_executed": 5,
  "processing_time": 1.2
}
```

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | FastAPI, Pydantic, aiohttp, SQLAlchemy 2.0 |
| **Frontend** | HTML5, CSS3, Vanilla JS, Boxicons |
| **Map API** | Amap (Gaode Map) - Geocoding, POI Search, JS API |
| **AI/LLM** | DeepSeek / GPT-4o-mini for intelligent scoring |
| **Database** | SQLite + aiosqlite (optional, for auth/social features) |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **Rate Limiting** | SlowAPI middleware |
| **Deployment** | Render, Railway, Docker, Vercel |

---

## Performance

| Scenario | Response Time |
|----------|---------------|
| Single venue type (rule mode) | 0.3-0.4s |
| Dual venue types (rule mode) | 0.5-0.6s |
| Triple venue types (rule mode) | 0.7-0.8s |
| Agent mode (AI-driven) | 1.0-2.0s |

### Optimizations

- In-memory caching for geocode and POI results
- Concurrent async searches for multiple scenarios
- Rate limiting with built-in delays (0.5s-2s) to avoid API quota limits
- Automatic retry with exponential backoff for failed requests

---

## Configuration

### Three-Tier Configuration System

1. **Full Configuration Mode** (`config/config.toml`):
   - Used for local development with complete settings
   - Includes LLM, browser, search, and Amap configurations

2. **Simplified Configuration Mode** (`app/config_simple.py`):
   - Triggered in production (e.g., `RAILWAY_ENVIRONMENT` set)
   - Only Amap API key and logging settings

3. **Minimal Fallback Mode** (environment variables only):
   - Works with just `AMAP_API_KEY` environment variable
   - Used for Vercel or minimal deployments

---

## Development

```bash
# Run with auto-reload
uvicorn api.index:app --reload

# Run tests
pytest tests/ -v
pytest --cov=app tests/  # With coverage (target: 80%)

# Code quality
black . && ruff check . && mypy app/
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Validate design tokens accessibility
python tools/validate_colors.py

# SEO audit (requires running server)
python tests/test_seo.py http://127.0.0.1:8000
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, perf, test, ci, chore
Examples:
  feat(recommender): add multi-scenario search support
  fix(seo): correct meta tag generation for Chinese content
```

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Contact

- **Email**: Johnrobertdestiny@gmail.com
- **Issues**: [GitHub Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues)
- **WeChat**: <img src="docs/Wechat.png" alt="WeChat" width="120"/>

---

## Acknowledgments

- [Amap](https://lbs.amap.com/) - Geocoding and POI search API
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework
- [Boxicons](https://boxicons.com/) - Icon library
- [DeepSeek](https://www.deepseek.com/) - LLM service

---

<div align="center">

**If this project helps you, please give it a star!**

Made by [JasonRobertDestiny](https://github.com/JasonRobertDestiny)

</div>
