<div align="center">

# MeetSpot

<img src="docs/logo.png" alt="MeetSpot Logo" width="200"/>

**Intelligent Meeting Point Recommendation System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://github.com/JasonRobertDestiny/MeetSpot/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonRobertDestiny/MeetSpot/actions)

[Live Demo](https://meetspot-irq2.onrender.com) | [Demo Video](https://www.bilibili.com/video/BV1aUK7zNEvo/) | English | [简体中文](README_ZH.md)

</div>

## What is MeetSpot?

MeetSpot calculates the optimal meeting location based on multiple participants' positions and recommends nearby venues. Whether you need a quiet cafe for business talks, a lively restaurant for friends, or a library for study groups - MeetSpot finds the fairest meeting point for everyone.

## Features

- **Smart Center Point**: Geometric center calculation ensures fairness for all participants
- **Multi-Scenario Search**: Search cafes + restaurants + libraries simultaneously
- **2-10 Participants**: Support multiple locations in one search
- **Intelligent Ranking**: Sort by rating, distance, and user requirements
- **60+ University Shortcuts**: "PKU" auto-expands to "Peking University"
- **350+ Cities**: Coverage across major Chinese cities via Amap API
- **Navigation Theme UI**: Modern cartography-inspired design
- **SEO-Optimized Pages**: Built-in FAQ, About, and city landing pages

## Quick Start

### Requirements

- Python 3.11+
- Amap API Key ([Get one here](https://lbs.amap.com/))

### Installation

```bash
git clone https://github.com/JasonRobertDestiny/MeetSpot.git
cd MeetSpot
pip install -r requirements.txt

# Configure API key
cp config/config.toml.example config/config.toml
# Edit config/config.toml and add your Amap API key

# Start server
python web_server.py
```

Open browser: http://127.0.0.1:8000

## Usage

1. **Enter Locations**: Add 2-10 participant addresses (supports shortcuts like "PKU", "THU")
2. **Select Venue Types**: Choose 1-3 types (cafe, restaurant, library, KTV, gym, etc.)
3. **Set Requirements**: Optional - parking, quiet environment, private rooms
4. **Get Results**: Click search, results in 0.3-0.8 seconds

## API

### Main Endpoint

```bash
POST /api/find_meetspot
```

### Request

```bash
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": ["Peking University", "Tsinghua University"],
    "keywords": "cafe restaurant",
    "user_requirements": "parking"
  }'
```

### Response

```json
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250614_abc123.html",
  "locations_count": 2,
  "keywords": "cafe restaurant",
  "processing_time": 0.52
}
```

### Other Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Homepage |
| `GET /health` | Health check |
| `GET /about` | About page |
| `GET /faq` | FAQ page |
| `GET /how-it-works` | Usage guide |
| `GET /meetspot/{city}` | City landing page |

## Tech Stack

**Backend**: FastAPI, Pydantic, aiohttp, SQLAlchemy
**Frontend**: HTML5, CSS3, Vanilla JS, Boxicons
**Map API**: Amap (Gaode Map)
**Design**: Navigation/Cartography theme with Outfit, DM Sans, Space Mono fonts

## Performance

| Scenario | Response Time |
|----------|---------------|
| Single venue type | 0.3-0.4s |
| Dual venue types | 0.5-0.6s |
| Triple venue types | 0.7-0.8s |

## Testing

```bash
# Health check
curl http://127.0.0.1:8000/health

# SEO validation
python verify_seo.py

# Integration test
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'
```

## Project Structure

```
MeetSpot/
├── api/
│   ├── index.py              # FastAPI app and main endpoints
│   ├── routers/
│   │   ├── seo_pages.py      # SEO pages (/, /about, /faq, etc.)
│   │   └── auth.py           # Authentication endpoints
│   └── services/
│       └── seo_content.py    # SEO content generation
├── app/
│   ├── tool/
│   │   └── meetspot_recommender.py  # Core recommendation engine
│   ├── config.py             # Configuration models
│   └── design_tokens.py      # Design system tokens
├── templates/                # Jinja2 templates
│   ├── base.html
│   └── pages/
├── public/                   # Static files
│   └── meetspot_finder.html  # Demo page
├── config/
│   └── config.toml.example   # Config template
└── web_server.py             # Entry point
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE)

## Contact

- Email: Johnrobertdestiny@gmail.com
- Issues: [GitHub Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues)
- WeChat Group: <img src="vx_chat.png" alt="WeChat" width="150"/>

## Acknowledgments

- [Amap](https://lbs.amap.com/) - Geocoding and POI search
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Boxicons](https://boxicons.com/) - Icon library

---

<div align="center">

**Star this repo if it helps!**

Made by [JasonRobertDestiny](https://github.com/JasonRobertDestiny)

</div>
