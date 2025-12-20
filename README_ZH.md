<div align="center">

# MeetSpot 聚点

<img src="docs/logo.jpg" alt="MeetSpot Logo" width="180"/>

**智能多人会面地点推荐系统**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://github.com/JasonRobertDestiny/MeetSpot/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonRobertDestiny/MeetSpot/actions)

[在线体验](https://meetspot-irq2.onrender.com) | [演示视频](https://www.bilibili.com/video/BV1aUK7zNEvo/) | [English](README.md) | 简体中文

</div>

---

## 什么是 MeetSpot?

MeetSpot 为多人寻找**最公平的会面地点**。输入地址，获取地理中心点周边的 AI 智能排序推荐。

<div align="center">
<img src="docs/show1.jpg" alt="MeetSpot 界面" width="85%"/>
</div>

---

## 核心数据流

```
                           用户请求
                              |
                   +----------+----------+
                   |    复杂度路由器     |
                   +----------+----------+
                         |          |
             +-----------+          +-----------+
             |                                  |
        规则模式                           Agent模式
        (简单查询)                        (复杂需求)
             |                                  |
             +------------+   +-----------------+
                          |   |
                   +------+---+------+
                   |   5步处理流水线   |
                   +-----------------+
                          |
   +------+------+------+------+------+
   |      |      |      |      |      |
 地理编码  中心   POI   智能   HTML
        计算   搜索   排序   生成
```

### 双模式路由

| 模式 | 触发条件 | 速度 | 使用场景 |
|------|----------|------|----------|
| **规则模式** | 2-3个地点，简单关键词 | 2-4秒 | 快速查找咖啡馆/餐厅 |
| **Agent模式** | 4+地点，复杂需求 | 8-15秒 | 个性化推荐 |

### 智能路由决策

**复杂度评分** (0-100) 决定请求由哪种模式处理：

| 因素 | 分值 | 示例 |
|------|------|------|
| 地点数量 | +10/个 | 4个地点 = 40分 |
| 复杂关键词 | +15 | "安静的商务咖啡馆" |
| 特殊需求 | +10 | "停车方便、有WiFi" |

- **评分 < 40** → 规则模式（快速、确定性）
- **评分 ≥ 40** → Agent模式（LLM增强）

**Agent模式增强：**
```
最终得分 = 规则得分 × 0.4 + LLM得分 × 0.6
```
LLM 分析场所与需求的语义匹配度，再与规则评分融合。结果页面包含**可解释AI**可视化，展示 Agent 的思维链推理过程。

### 5步处理流水线

1. **地理编码** - 地址转坐标（90+智能映射：大学简称 + 城市地标）
2. **中心计算** - 球面几何保证公平
3. **POI搜索** - 多场景并发异步搜索
4. **智能排序** - 百分制评分: 基础分(30) + 热度分(20) + 距离分(25) + 场景匹配(15) + 需求匹配(10)
5. **HTML生成** - 集成高德JS API的交互式地图

---

## 快速开始

```bash
git clone https://github.com/JasonRobertDestiny/MeetSpot.git && cd MeetSpot
pip install -r requirements.txt
cp config/config.toml.example config/config.toml  # 填入高德API密钥
python web_server.py
```

浏览器访问 http://127.0.0.1:8000

**必需**: `AMAP_API_KEY` ([申请地址](https://lbs.amap.com/))

---

## API

**主接口**: `POST /api/find_meetspot`

```json
{
  "locations": ["北京大学", "清华大学"],
  "keywords": "咖啡馆 餐厅",
  "user_requirements": "停车方便"
}
```

**响应**: `{ "success": true, "html_url": "/workspace/js_src/..." }`

其他接口: `/api/find_meetspot_agent` (AI模式), `/api/ai_chat`, `/health`, `/docs`

---

## 产品截图

<table>
<tr>
<td width="50%"><img src="docs/agent-thinking.jpg" alt="Agent思考"/><p align="center"><b>AI处理过程</b></p></td>
<td width="50%"><img src="docs/result-map.jpg" alt="地图"/><p align="center"><b>交互式地图</b></p></td>
</tr>
<tr>
<td width="50%"><img src="docs/多维度智能评分show4.jpg" alt="评分"/><p align="center"><b>AI评分系统</b></p></td>
<td width="50%"><img src="docs/show5推荐地点.jpg" alt="卡片"/><p align="center"><b>场所推荐卡片</b></p></td>
</tr>
</table>

<details>
<summary><b>更多截图</b></summary>

<table>
<tr>
<td width="50%"><img src="docs/homepage.jpg" alt="首页"/><p align="center"><b>首页</b></p></td>
<td width="50%"><img src="docs/finder-input.jpg" alt="查找"/><p align="center"><b>会面点查找</b></p></td>
</tr>
<tr>
<td width="50%"><img src="docs/result-summary.jpg" alt="结果"/><p align="center"><b>推荐结果</b></p></td>
<td width="50%"><img src="docs/AI客服.jpg" alt="AI客服"/><p align="center"><b>AI智能客服</b></p></td>
</tr>
</table>

</details>

---

## 技术栈

**后端**: FastAPI, Pydantic, aiohttp, SQLAlchemy 2.0
**前端**: HTML5, CSS3, Vanilla JS, Boxicons
**地图**: 高德地图 - 地理编码、POI搜索、JS API
**AI**: DeepSeek / GPT-4o-mini
**部署**: Render, Railway, Docker, Vercel

---

## 项目结构

```
api/index.py                      # FastAPI应用入口
app/tool/meetspot_recommender.py  # 核心推荐引擎
app/config.py                     # 配置管理(TOML)
public/                           # 前端静态文件
workspace/js_src/                 # 生成的结果页面
```

---

## 开发

```bash
uvicorn api.index:app --reload                    # 开发服务器
pytest tests/ -v                                  # 测试
black . && ruff check . && mypy app/              # 代码质量
```

---

## 许可证

MIT - 详见 [LICENSE](LICENSE)

**联系方式**: Johnrobertdestiny@gmail.com | [GitHub Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues)

<div align="center">

**觉得有用请给个 Star!**

</div>
