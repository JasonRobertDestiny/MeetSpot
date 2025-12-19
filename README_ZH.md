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

MeetSpot 解决一个常见问题：**为多人找到最公平的见面地点**。输入参与者地址，系统使用球面几何计算最优中心点，并通过 AI 智能评分推荐周边场所。

<div align="center">
<img src="docs/show1.jpg" alt="MeetSpot 界面" width="85%"/>
</div>

---

## 核心功能

### 主要特性

| 功能 | 说明 |
|------|------|
| **Agent 智能路由** | 智能决策引擎，根据查询复杂度自动选择最优处理模式 |
| **AI 多维评分** | 综合评分、距离、场景匹配和用户需求的智能排序 |
| **智能中心计算** | 球面几何算法确保每个人路程公平 |
| **多场景并发搜索** | 咖啡馆、餐厅、图书馆一次搜完，异步并发处理 |
| **交互式地图** | 可视化中心点、参与者位置和场所标记，集成高德 JS API |
| **60+ 大学简称** | "北大"自动识别为"北京市海淀区北京大学" |
| **350+ 城市** | 基于高德地图 API 覆盖全国主要城市 |

### Agent 思考体验

系统提供可视化的 "Agent 思考" 体验，实时展示 AI 决策过程：

```
Step 1: 解析地址     -> 获取各位置坐标信息
Step 2: 计算中心点   -> 寻找最公平的会面位置
Step 3: 搜索周边场所 -> 发现附近优质地点
Step 4: 智能评分排序 -> 综合评估最佳选择
Step 5: 生成推荐     -> 输出个性化推荐方案
```

### 动态主题系统

12 种预配置场所主题，包含自定义颜色、图标和中文命名：
- 咖啡馆、餐厅、图书馆、健身房、KTV、酒吧
- 电影院、商场、公园、博物馆、书店、茶馆

### UI/UX 特性

| 特性 | 说明 |
|------|------|
| **Agent 大脑动画** | 处理过程中展示脉冲动画和思考气泡的可视化大脑图标 |
| **分步进度展示** | 5 步思考可视化，配有图标和进度指示器 |
| **WCAG AA 无障碍** | 经过对比度验证的无障碍配色方案 |
| **响应式设计** | 移动优先的自适应布局 |
| **渐变背景** | 基于场所主题的动态颜色渐变 |
| **微动效** | 全局流畅的过渡效果和悬停动画 |
| **Boxicons 图标** | 统一的图标设计语言 |

---

## 产品截图

### 使用流程

<table>
<tr>
<td width="50%">
<img src="docs/homepage.jpg" alt="首页"/>
<p align="center"><b>首页</b></p>
</td>
<td width="50%">
<img src="docs/finder-input.jpg" alt="查找页面"/>
<p align="center"><b>会面地点查找</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/finder-filled.jpg" alt="输入地点"/>
<p align="center"><b>地点输入</b></p>
</td>
<td width="50%">
<img src="docs/complex-scenario-input.jpg" alt="复杂场景"/>
<p align="center"><b>多地点场景</b></p>
</td>
</tr>
</table>

### Agent 思考体验

<table>
<tr>
<td width="50%">
<img src="docs/agent-thinking.jpg" alt="Agent思考"/>
<p align="center"><b>AI 处理动画</b></p>
</td>
<td width="50%">
<img src="docs/agent-thinking-complex.jpg" alt="复杂处理"/>
<p align="center"><b>多步骤分析</b></p>
</td>
</tr>
</table>

### 结果与推荐

<table>
<tr>
<td width="50%">
<img src="docs/result-summary.jpg" alt="结果摘要"/>
<p align="center"><b>结果摘要</b></p>
</td>
<td width="50%">
<img src="docs/result-ai-process.jpg" alt="AI过程"/>
<p align="center"><b>AI 决策过程</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/result-map.jpg" alt="地图展示"/>
<p align="center"><b>交互式地图</b></p>
</td>
<td width="50%">
<img src="docs/result-recommendations.jpg" alt="推荐"/>
<p align="center"><b>场所推荐</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/result-traffic.jpg" alt="地点与地图"/>
<p align="center"><b>地点信息与地图</b></p>
</td>
<td width="50%">
<img src="docs/多维度智能评分show4.jpg" alt="智能评分"/>
<p align="center"><b>AI 评分系统</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/show6停车建议.jpg" alt="交通停车建议"/>
<p align="center"><b>交通与停车建议</b></p>
</td>
<td width="50%">
<img src="docs/show5推荐地点.jpg" alt="场所卡片"/>
<p align="center"><b>场所推荐卡片</b></p>
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

## 系统架构

### 整体流程

```
用户输入 -> 前端界面 -> API 网关 -> 智能路由
                                      |
                   +------------------+------------------+
                   |                                     |
              Agent 模式                            规则模式
           (复杂/个性化需求)                      (简单/快速查询)
                   |                                     |
              MeetSpotAgent                       CafeRecommender
                   |                                     |
                   +------------------+------------------+
                                      |
           地理编码 -> 计算中心点 -> POI搜索 -> 排序 -> 生成HTML
```

### 组件架构

```
MeetSpot/
├── api/
│   ├── index.py                    # FastAPI 应用入口，中间件和路由
│   ├── routers/
│   │   ├── auth.py                 # JWT 认证端点
│   │   └── seo_pages.py            # SEO 落地页路由
│   └── services/
│       └── seo_content.py          # SEO 内容生成
├── app/
│   ├── tool/
│   │   └── meetspot_recommender.py # 核心推荐引擎 (CafeRecommender)
│   ├── auth/
│   │   ├── jwt.py                  # JWT 令牌管理
│   │   └── sms.py                  # 短信验证
│   ├── db/
│   │   ├── database.py             # SQLAlchemy 异步引擎
│   │   └── crud.py                 # 数据库操作
│   ├── models/                     # SQLAlchemy ORM 模型
│   ├── config.py                   # 完整配置（基于 TOML）
│   ├── config_simple.py            # 生产环境简化配置
│   ├── design_tokens.py            # WCAG AA 无障碍设计系统
│   └── schema.py                   # Pydantic 数据模型
├── public/
│   ├── index.html                  # 主界面
│   ├── meetspot_finder.html        # 会面点查找页面
│   └── seo/                        # 静态 SEO 页面
├── workspace/js_src/               # 生成的推荐结果 HTML 页面
├── config/
│   └── config.toml.example         # 配置模板
└── web_server.py                   # 应用入口
```

### 核心算法

1. **地址增强**：自动扩展简称并补充城市信息（60+ 大学映射）
2. **中心计算**：2 点用球面几何，3+ 点用加权平均
3. **多场景搜索**：并发异步搜索 + 智能去重（基于名称+位置）
4. **排名公式**：
   - 基础分：评分 x 10（高德评分）
   - 距离分：最高 20 分，随距离衰减
   - 场景匹配：+15 分（匹配用户选择的场所类型）
   - 需求匹配：+10 分（停车/安静/商务/交通便利）
5. **多场景平衡**：每场景 2-3 个结果，总计最多 8 个推荐

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

# 安装依赖（任选其一）
pip install -r requirements.txt
# 或使用 conda:
conda env create -f environment.yml && conda activate meetspot

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

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `AMAP_API_KEY` | 是 | 高德地图 API 密钥 |
| `AMAP_SECURITY_JS_CODE` | 否 | 高德 JS API 安全密钥 |
| `PORT` | 否 | 服务端口（默认：8000） |
| `LLM_API_KEY` | 否 | LLM API 密钥（智能评分） |
| `LLM_API_BASE` | 否 | LLM API 基础 URL |

---

## 使用方法

1. **输入地址**：添加 2-10 个参与者地址（支持大学简称）
2. **选择场所**：从 12 种类型中选择（咖啡馆、餐厅、图书馆、健身房、KTV 等）
3. **设置需求**（可选）：停车方便、环境安静、有包间、交通便利
4. **查看结果**：交互式地图展示排名后的推荐场所，支持一键导航

---

## API 文档

### 核心端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/find_meetspot` | POST | 主推荐接口（规则模式） |
| `/api/find_meetspot_agent` | POST | Agent 模式推荐（AI 驱动） |
| `/api/ai_chat` | POST | AI 智能客服 |
| `/health` | GET | 健康检查和配置状态 |
| `/config` | GET | 配置状态（不含密钥） |
| `/docs` | GET | OpenAPI 文档 |

### SEO 与营销页面

| 端点 | 说明 |
|------|------|
| `/` | 首页 |
| `/about` | 关于页面 |
| `/faq` | 常见问题 |
| `/how-it-works` | 使用指南 |
| `/meetspot/{city}` | 城市专属落地页 |

### 认证端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | JWT 登录 |
| `/api/auth/sms/send` | POST | 发送短信验证码 |
| `/api/auth/sms/verify` | POST | 验证短信验证码 |

### 请求/响应示例

**POST /api/find_meetspot**

```json
// 请求
{
  "locations": ["北京大学", "清华大学"],
  "keywords": "咖啡馆 餐厅",
  "user_requirements": "停车方便"
}

// 成功响应
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250614_abc123.html",
  "locations_count": 2,
  "keywords": "咖啡馆 餐厅",
  "processing_time": 0.52,
  "output": "详细推荐文本..."
}

// 错误响应
{
  "success": false,
  "error": "错误信息",
  "processing_time": 0.12,
  "message": "推荐失败: ..."
}
```

**POST /api/find_meetspot_agent**

```json
// 请求（同上）

// 响应包含额外字段
{
  "success": true,
  "mode": "agent",
  "recommendation": "AI 生成的推荐内容",
  "geocode_results": [...],
  "center_point": {"lat": 39.99, "lng": 116.31},
  "search_results": [...],
  "steps_executed": 5,
  "processing_time": 1.2
}
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | FastAPI, Pydantic, aiohttp, SQLAlchemy 2.0 |
| **前端** | HTML5, CSS3, Vanilla JS, Boxicons |
| **地图** | 高德地图 API - 地理编码、POI 搜索、JS API |
| **AI/LLM** | DeepSeek / GPT-4o-mini 智能评分 |
| **数据库** | SQLite + aiosqlite（可选，用于认证功能） |
| **认证** | JWT (python-jose), bcrypt (passlib) |
| **限流** | SlowAPI 中间件 |
| **部署** | Render, Railway, Docker, Vercel |

---

## 性能指标

| 场景 | 响应时间 |
|------|----------|
| 单场景推荐（规则模式） | 0.3-0.4 秒 |
| 双场景推荐（规则模式） | 0.5-0.6 秒 |
| 三场景推荐（规则模式） | 0.7-0.8 秒 |
| Agent 模式（AI 驱动） | 1.0-2.0 秒 |

### 性能优化

- 地理编码和 POI 结果内存缓存
- 多场景并发异步搜索
- 内置限速延迟（0.5s-2s）避免 API 配额超限
- 失败请求自动指数退避重试

---

## 配置系统

### 三层配置架构

1. **完整配置模式** (`config/config.toml`)：
   - 用于本地开发，包含完整设置
   - 包括 LLM、浏览器、搜索和高德地图配置

2. **简化配置模式** (`app/config_simple.py`)：
   - 生产环境自动触发（如设置 `RAILWAY_ENVIRONMENT`）
   - 仅包含高德 API 密钥和日志设置

3. **最小回退模式**（仅环境变量）：
   - 仅需 `AMAP_API_KEY` 环境变量即可运行
   - 适用于 Vercel 或最小化部署

---

## 开发

```bash
# 热重载运行
uvicorn api.index:app --reload

# 运行测试
pytest tests/ -v
pytest --cov=app tests/  # 带覆盖率（目标：80%）

# 代码质量检查
black . && ruff check . && mypy app/
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# 验证设计令牌无障碍性
python tools/validate_colors.py

# SEO 审计（需要运行服务器）
python tests/test_seo.py http://127.0.0.1:8000
```

---

## 贡献指南

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing`）
3. 按照 [Conventional Commits](https://www.conventionalcommits.org/) 提交更改
4. 推送分支（`git push origin feature/amazing`）
5. 提交 Pull Request

### 提交信息格式

```
<type>(<scope>): <description>

类型: feat, fix, docs, style, refactor, perf, test, ci, chore
示例:
  feat(recommender): 添加多场景搜索支持
  fix(seo): 修复中文内容 meta 标签生成
```

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

**觉得有用请给个 Star!**

Made by [JasonRobertDestiny](https://github.com/JasonRobertDestiny)

</div>
