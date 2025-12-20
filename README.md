<div align="center">

# MeetSpot

<img src="docs/logo.jpg" alt="MeetSpot Logo" width="180"/>

**Intelligent Multi-Person Meeting Point Recommendation System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://github.com/JasonRobertDestiny/MeetSpot/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonRobertDestiny/MeetSpot/actions)

[Live Demo](https://meetspot-irq2.onrender.com) | [Demo Video](https://www.bilibili.com/video/BV1aUK7zNEvo/) | English | [Chinese](README_ZH.md)

</div>

---

## What is MeetSpot?

MeetSpot finds the **fairest meeting point for multiple people**. Input addresses, get AI-ranked venue recommendations at the geographic center.

<div align="center">
<img src="docs/show1.jpg" alt="MeetSpot Interface" width="85%"/>
</div>

---

## Core Data Flow

```
                           User Request
                                |
                    +-----------+-----------+
                    |   Complexity Router   |
                    +-----------+-----------+
                          |           |
              +-----------+           +-----------+
              |                                   |
        Rule Mode                           Agent Mode
        (Simple)                           (Complex)
              |                                   |
              +-------------+   +-----------------+
                            |   |
                    +-------+---+-------+
                    |   5-Step Pipeline  |
                    +-------------------+
                            |
    +-------+-------+-------+-------+-------+
    |       |       |       |       |       |
 Geocode  Center   POI   Ranking   HTML
         Calc    Search           Gen
```

### Dual-Mode Routing

| Mode | Trigger | Speed | Use Case |
|------|---------|-------|----------|
| **Rule Mode** | 2-3 locations, simple keywords | 2-4s | Quick cafe/restaurant lookup |
| **Agent Mode** | 4+ locations, complex requirements | 8-15s | Personalized recommendations |

### Intelligent Routing Decision

**Complexity Score** (0-100) determines which mode handles your request:

| Factor | Points | Example |
|--------|--------|---------|
| Location count | +10/location | 4 locations = 40 pts |
| Complex keywords | +15 | "quiet business cafe" |
| Special requirements | +10 | "parking, WiFi" |

- **Score < 40** → Rule Mode (fast, deterministic)
- **Score ≥ 40** → Agent Mode (LLM-enhanced)

**Agent Mode Enhancement:**
```
Final Score = Rule Score × 0.4 + LLM Score × 0.6
```
LLM analyzes venue-requirement semantic fit, then blends with rule-based scoring. Results include **Explainable AI** visualization showing the agent's chain-of-thought reasoning process.

### 5-Step Processing Pipeline

1. **Geocode** - Convert addresses to coordinates (45+ university shortcuts: "PKU" -> "Peking University, Beijing")
2. **Center Calc** - Spherical geometry for fairness
3. **POI Search** - Concurrent async search across multiple venue types
4. **Ranking** - 100-point scoring: Base(30) + Popularity(20) + Distance(25) + Scenario(15) + Requirements(10)
5. **HTML Gen** - Interactive map with Amap JS API

---

## Quick Start

```bash
git clone https://github.com/JasonRobertDestiny/MeetSpot.git && cd MeetSpot
pip install -r requirements.txt
cp config/config.toml.example config/config.toml  # Add your Amap API key
python web_server.py
```

Open http://127.0.0.1:8000

**Required**: `AMAP_API_KEY` ([Get one](https://lbs.amap.com/))

---

## API

**Main Endpoint**: `POST /api/find_meetspot`

```json
{
  "locations": ["Peking University", "Tsinghua University"],
  "keywords": "cafe restaurant",
  "user_requirements": "parking"
}
```

**Response**: `{ "success": true, "html_url": "/workspace/js_src/..." }`

Other endpoints: `/api/find_meetspot_agent` (AI mode), `/api/ai_chat`, `/health`, `/docs`

---

## Screenshots

<table>
<tr>
<td width="50%"><img src="docs/agent-thinking.jpg" alt="Agent Thinking"/><p align="center"><b>AI Processing</b></p></td>
<td width="50%"><img src="docs/result-map.jpg" alt="Map"/><p align="center"><b>Interactive Map</b></p></td>
</tr>
<tr>
<td width="50%"><img src="docs/多维度智能评分show4.jpg" alt="Scoring"/><p align="center"><b>AI Scoring</b></p></td>
<td width="50%"><img src="docs/show5推荐地点.jpg" alt="Cards"/><p align="center"><b>Venue Cards</b></p></td>
</tr>
</table>

<details>
<summary><b>More Screenshots</b></summary>

<table>
<tr>
<td width="50%"><img src="docs/homepage.jpg" alt="Homepage"/><p align="center"><b>Homepage</b></p></td>
<td width="50%"><img src="docs/finder-input.jpg" alt="Finder"/><p align="center"><b>Meeting Finder</b></p></td>
</tr>
<tr>
<td width="50%"><img src="docs/result-summary.jpg" alt="Summary"/><p align="center"><b>Results</b></p></td>
<td width="50%"><img src="docs/AI客服.jpg" alt="AI Chat"/><p align="center"><b>AI Customer Service</b></p></td>
</tr>
</table>

</details>

---

## Tech Stack

**Backend**: FastAPI, Pydantic, aiohttp, SQLAlchemy 2.0
**Frontend**: HTML5, CSS3, Vanilla JS, Boxicons
**Map**: Amap (Gaode) - Geocoding, POI Search, JS API
**AI**: DeepSeek / GPT-4o-mini
**Deploy**: Render, Railway, Docker, Vercel

---

## Project Structure

```
api/index.py                      # FastAPI app entry
app/tool/meetspot_recommender.py  # Core recommendation engine
app/config.py                     # Configuration (TOML-based)
public/                           # Frontend static files
workspace/js_src/                 # Generated result pages
```

---

## Development

```bash
uvicorn api.index:app --reload                    # Dev server
pytest tests/ -v                                  # Tests
black . && ruff check . && mypy app/              # Quality
```

---

## License

MIT - see [LICENSE](LICENSE)

**Contact**: Johnrobertdestiny@gmail.com | [GitHub Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues)

<div align="center">

**Star this repo if it helps!**

</div>
