<div align="center">

# MeetSpot 聚点

<img src="docs/logo.jpg" alt="MeetSpot Logo" width="180"/>

**智能多人会面地点推荐系统**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Build Status](https://github.com/JasonRobertDestiny/MeetSpot/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonRobertDestiny/MeetSpot/actions)
[![Render](https://img.shields.io/badge/部署-Render-46E3B7.svg)](https://meetspot-irq2.onrender.com)

[在线体验](https://meetspot-irq2.onrender.com) | [演示视频](https://www.bilibili.com/video/BV1aUK7zNEvo/) | [English](README.md) | 简体中文

</div>

---

## 项目简介

MeetSpot 解决一个常见问题：**为多人找到最公平的见面地点**。输入参与者地址，系统使用球面几何计算最优中心点，并通过 LLM 智能评分推荐周边场所。

<div align="center">
<img src="docs/show1.jpg" alt="MeetSpot 界面" width="85%"/>
</div>

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **LLM 智能评分** | AI 驱动的场所排序，综合用户需求、评分和距离 |
| **智能中心计算** | 球面几何算法确保每个人路程公平 |
| **多场景搜索** | 咖啡馆、餐厅、图书馆一次搜完 |
| **交互式地图** | 可视化中心点、参与者位置和场所标记 |
| **45+ 大学简称** | "北大"自动识别为"北京市海淀区北京大学" |
| **350+ 城市** | 基于高德地图 API 覆盖全国主要城市 |
| **AI 智能客服** | 内置 AI 助手解答使用问题 |
| **亚秒级响应** | 平均处理时间 0.3-0.8 秒 |

---

## 产品截图

<table>
<tr>
<td width="50%">
<img src="docs/show2.jpg" alt="输入地点"/>
<p align="center"><b>地点输入</b></p>
</td>
<td width="50%">
<img src="docs/show3.jpg" alt="选择场景"/>
<p align="center"><b>场景选择</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/show6地图展示.jpg" alt="地图展示"/>
<p align="center"><b>交互式地图</b></p>
</td>
<td width="50%">
<img src="docs/多维度智能评分show4.jpg" alt="智能评分"/>
<p align="center"><b>AI 评分系统</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/show5推荐地点.jpg" alt="推荐地点"/>
<p align="center"><b>场所推荐</b></p>
</td>
<td width="50%">
<img src="docs/show6停车建议.jpg" alt="交通建议"/>
<p align="center"><b>交通建议</b></p>
</td>
</tr>
</table>

<details>
<summary><b>更多截图</b></summary>

### AI 智能客服
<div align="center">
<img src="docs/AI客服.jpg" alt="AI 智能客服" width="80%"/>
</div>

### 高德地图导航
<div align="center">
<img src="docs/show7高德地图.jpg" alt="高德地图导航" width="80%"/>
</div>

</details>

---

## 快速开始

### 环境要求

- Python 3.11+
- 高德地图 API 密钥（[申请地址](https://lbs.amap.com/)）

### 安装

```bash
# 克隆仓库
git clone https://github.com/JasonRobertDestiny/MeetSpot.git
cd MeetSpot

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cp config/config.toml.example config/config.toml
# 编辑 config/config.toml，填入高德地图 API 密钥

# 启动服务
python web_server.py
```

浏览器访问 http://127.0.0.1:8000

### Docker 部署（可选）

```bash
docker build -t meetspot .
docker run -p 8000:8000 -e AMAP_API_KEY=your_key meetspot
```

---

## 使用方法

1. **输入地址**：添加 2-10 个参与者地址
2. **选择场所**：从 12 种类型中选择（咖啡馆、餐厅、图书馆、健身房、KTV 等）
3. **设置需求**（可选）：停车方便、环境安静、有包间
4. **查看结果**：交互式地图展示排名后的推荐场所

---

## API 文档

### 主要端点

```http
POST /api/find_meetspot
Content-Type: application/json
```

**请求体：**
```json
{
  "locations": ["北京大学", "清华大学"],
  "keywords": "咖啡馆 餐厅",
  "user_requirements": "停车方便"
}
```

**响应：**
```json
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250614_abc123.html",
  "locations_count": 2,
  "keywords": "咖啡馆 餐厅",
  "processing_time": 0.52
}
```

### 所有端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/api/find_meetspot` | POST | 主推荐接口 |
| `/api/ai_chat` | POST | AI 智能客服 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | OpenAPI 文档 |
| `/about` | GET | 关于页面 |
| `/faq` | GET | 常见问题 |
| `/how-it-works` | GET | 使用指南 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | FastAPI, Pydantic, aiohttp, SQLAlchemy |
| **前端** | HTML5, CSS3, Vanilla JS, Boxicons |
| **地图** | 高德地图 API - 地理编码 & POI 搜索 |
| **AI/LLM** | DeepSeek / GPT-4o-mini 智能评分 |
| **数据库** | SQLite + aiosqlite（可选，用于认证功能） |
| **部署** | Render, Railway, Docker |

---

## 系统架构

```
MeetSpot/
├── api/
│   ├── index.py                    # FastAPI 应用入口
│   ├── routers/                    # 路由处理
│   └── services/                   # 业务逻辑
├── app/
│   ├── tool/
│   │   └── meetspot_recommender.py # 核心推荐引擎
│   ├── config.py                   # 配置管理
│   ├── llm.py                      # LLM 集成
│   └── design_tokens.py            # 设计系统
├── public/                         # 静态前端文件
├── templates/                      # Jinja2 模板
├── config/                         # 配置文件
└── web_server.py                   # 应用入口
```

### 核心算法

1. **地址增强**：自动扩展简称（60+ 大学映射）
2. **中心计算**：2 点用球面几何，3+ 点用加权平均
3. **多场景搜索**：并发异步搜索 + 智能去重
4. **排名算法**：评分 (x10) + 距离分 (最高 20) + 场景匹配 (+15) + 需求匹配 (+10)

---

## 性能指标

| 场景 | 响应时间 |
|------|----------|
| 单场景推荐 | 0.3-0.4 秒 |
| 双场景推荐 | 0.5-0.6 秒 |
| 三场景推荐 | 0.7-0.8 秒 |

---

## 开发

```bash
# 热重载运行
uvicorn api.index:app --reload

# 运行测试
pytest tests/ -v

# 代码质量检查
black . && ruff check . && mypy app/
```

---

## 贡献指南

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing`）
3. 按照 [Conventional Commits](https://www.conventionalcommits.org/) 提交更改
4. 推送分支（`git push origin feature/amazing`）
5. 提交 Pull Request

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 联系方式

- **邮箱**：Johnrobertdestiny@gmail.com
- **问题反馈**：[GitHub Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues)
- **微信**：<img src="docs/Wechat.png" alt="微信" width="120"/>

---

## 致谢

- [高德地图](https://lbs.amap.com/) - 地理编码和 POI 搜索 API
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架
- [Boxicons](https://boxicons.com/) - 图标库
- [DeepSeek](https://www.deepseek.com/) - LLM 服务

---

<div align="center">

**觉得有用请给个 Star！**

Made by [JasonRobertDestiny](https://github.com/JasonRobertDestiny)

</div>
