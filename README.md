<div align="center">

# MeetSpot

<img src="docs/logo.jpg" alt="MeetSpot Logo" width="180"/>

**Intelligent Multi-Person Meeting Point Recommendation System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://github.com/JasonRobertDestiny/MeetSpot/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonRobertDestiny/MeetSpot/actions)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://meetspot-irq2.onrender.com)

[Live Demo](https://meetspot-irq2.onrender.com) | [Demo Video](https://www.bilibili.com/video/BV1aUK7zNEvo/) | English | [简体中文](README_ZH.md)

</div>

---

## Overview

MeetSpot solves a common problem: **finding the fairest meeting point for multiple people**. Input participant addresses, and the system calculates the optimal center point using spherical geometry, then recommends nearby venues with LLM-powered intelligent scoring.

<div align="center">
<img src="docs/show1.jpg" alt="MeetSpot Interface" width="85%"/>
</div>

---

## Key Features

| Feature | Description |
|---------|-------------|
| **LLM Intelligent Scoring** | AI-powered venue ranking based on user requirements, ratings, and distance |
| **Smart Center Calculation** | Spherical geometry ensures fairness for all participants |
| **Multi-Scenario Search** | Search cafes, restaurants, libraries simultaneously |
| **Interactive Map** | Visual markers for center point, participants, and venues |
| **45+ University Shortcuts** | "PKU" auto-expands to "Peking University, Beijing" |
| **350+ Cities** | Coverage across major Chinese cities via Amap API |
| **AI Customer Service** | Built-in assistant for usage questions |
| **Sub-second Response** | 0.3-0.8s average processing time |

---

## Screenshots

<table>
<tr>
<td width="50%">
<img src="docs/show2.jpg" alt="Enter Locations"/>
<p align="center"><b>Location Input</b></p>
</td>
<td width="50%">
<img src="docs/show3.jpg" alt="Select Scenarios"/>
<p align="center"><b>Venue Type Selection</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/show6地图展示.jpg" alt="Map Display"/>
<p align="center"><b>Interactive Map</b></p>
</td>
<td width="50%">
<img src="docs/多维度智能评分show4.jpg" alt="Intelligent Scoring"/>
<p align="center"><b>AI Scoring System</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/show5推荐地点.jpg" alt="Recommended Venues"/>
<p align="center"><b>Venue Recommendations</b></p>
</td>
<td width="50%">
<img src="docs/show6停车建议.jpg" alt="Transport Tips"/>
<p align="center"><b>Transport Suggestions</b></p>
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

## Quick Start

### Prerequisites

- Python 3.11+
- Amap API Key ([Get one here](https://lbs.amap.com/))

### Installation

```bash
# Clone repository
git clone https://github.com/JasonRobertDestiny/MeetSpot.git
cd MeetSpot

# Install dependencies
pip install -r requirements.txt

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

---

## Usage

1. **Enter Locations**: Add 2-10 participant addresses
2. **Select Venue Types**: Choose from 12 categories (cafe, restaurant, library, gym, KTV, etc.)
3. **Set Requirements** (Optional): parking, quiet environment, private rooms
4. **View Results**: Interactive map with ranked venue recommendations

---

## API Reference

### Main Endpoint

```http
POST /api/find_meetspot
Content-Type: application/json
```

**Request Body:**
```json
{
  "locations": ["Peking University", "Tsinghua University"],
  "keywords": "cafe restaurant",
  "user_requirements": "parking"
}
```

**Response:**
```json
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250614_abc123.html",
  "locations_count": 2,
  "keywords": "cafe restaurant",
  "processing_time": 0.52
}
```

### All Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage |
| `/api/find_meetspot` | POST | Main recommendation endpoint |
| `/api/ai_chat` | POST | AI customer service |
| `/health` | GET | Health check |
| `/docs` | GET | OpenAPI documentation |
| `/about` | GET | About page |
| `/faq` | GET | FAQ page |
| `/how-it-works` | GET | Usage guide |

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | FastAPI, Pydantic, aiohttp, SQLAlchemy |
| **Frontend** | HTML5, CSS3, Vanilla JS, Boxicons |
| **Map API** | Amap (Gaode Map) - Geocoding & POI Search |
| **AI/LLM** | DeepSeek / GPT-4o-mini for intelligent scoring |
| **Database** | SQLite + aiosqlite (optional, for auth features) |
| **Deployment** | Render, Railway, Docker |

---

## Architecture

```
MeetSpot/
├── api/
│   ├── index.py                    # FastAPI app entry
│   ├── routers/                    # Route handlers
│   └── services/                   # Business logic
├── app/
│   ├── tool/
│   │   └── meetspot_recommender.py # Core recommendation engine
│   ├── config.py                   # Configuration management
│   ├── llm.py                      # LLM integration
│   └── design_tokens.py            # Design system
├── public/                         # Static frontend files
├── templates/                      # Jinja2 templates
├── config/                         # Configuration files
└── web_server.py                   # Application entry point
```

### Core Algorithm

1. **Address Enhancement**: Auto-expands abbreviations (60+ university mappings)
2. **Center Calculation**: Spherical geometry for 2 locations, weighted average for 3+
3. **Multi-Scenario Search**: Concurrent async searches with smart deduplication
4. **Ranking**: Rating (x10) + Distance score (max 20) + Scenario match (+15) + Requirements (+10)

---

## Performance

| Scenario | Response Time |
|----------|---------------|
| Single venue type | 0.3-0.4s |
| Dual venue types | 0.5-0.6s |
| Triple venue types | 0.7-0.8s |

---

## Development

```bash
# Run with auto-reload
uvicorn api.index:app --reload

# Run tests
pytest tests/ -v

# Code quality
black . && ruff check . && mypy app/
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

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
