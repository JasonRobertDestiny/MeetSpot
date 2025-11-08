# Development Prompt for Codex - Phase 2
**MeetSpot SEO优化系统 - 性能优化与监控集成**

---

## Context

### 当前系统状态

**已完成 (Phase 1)**:
- ✅ SEO基础设施：SEO内容服务（api/services/seo_content.py:15-235）
- ✅ SSR路由系统：主页、城市页、About/FAQ、sitemap.xml、robots.txt（api/routers/seo_pages.py:50-210）
- ✅ 模板系统：Jinja2 base layout + 内容页（templates/）
- ✅ 依赖包：jieba, whitenoise, slowapi, markdown2已安装
- ✅ 城市数据种子：5个主要城市（data/cities.json:1-33）
- ✅ 主应用集成：SEO路由注册、静态目录挂载、rate-limit（api/index.py:173-225）

**验证结果**:
```bash
python -m py_compile api/index.py api/services/seo_content.py api/routers/seo_pages.py
# ✅ 编译通过，无语法错误
```

**当前问题**:
1. WhiteNoise未激活，静态文件压缩未启用
2. 缺少Lighthouse CI监控流程
3. 城市数据仅5个，无法支撑长尾SEO流量
4. 推荐导出页面（workspace/js_src/*.html）未集成SEO优化
5. 缺少自动化SEO验证工具
6. Git状态混乱（__pycache__删除未提交）

### 相关文件
**需修改的文件**:
- `api/index.py` - 集成WhiteNoise中间件
- `app/tool/meetspot_recommender.py` - 增强HTML生成的SEO标签
- `.github/workflows/` - 添加Lighthouse CI workflow
- `data/cities.json` - 扩充到50个城市
- 新建 `tests/test_seo.py` - SEO自动化验证脚本

**当前架构**:
```
MeetSpot/
├── api/
│   ├── index.py              # FastAPI主应用（需修改：WhiteNoise集成）
│   ├── services/
│   │   └── seo_content.py    # SEO服务（已完成）
│   └── routers/
│       └── seo_pages.py      # SEO路由（已完成）
├── app/tool/
│   └── meetspot_recommender.py  # 推荐引擎（需修改：SEO导出）
├── data/
│   └── cities.json           # 城市数据（需扩充：5→50）
├── templates/                # Jinja2模板（已完成）
├── workspace/js_src/         # 推荐导出页面（需SEO优化）
└── .github/workflows/        # CI/CD（需添加Lighthouse）
```

---

## Objective

**主目标**: 完成SEO系统的性能优化、监控集成和规模化扩展

**子目标**:
1. 启用WhiteNoise静态文件压缩，提升Lighthouse Performance到90+
2. 集成Lighthouse CI，确保每次部署SEO/Performance不回退
3. 扩充城市数据到50个，覆盖国内主要城市
4. 在推荐导出HTML中注入SEO标签（meta、schema.org、og标签）
5. 创建自动化SEO验证工具，可命令行运行
6. 清理git状态，提交干净的代码库

**成功标准**:
- Lighthouse Performance ≥ 90分
- Lighthouse SEO = 100分（保持）
- 50个城市页面全部可访问，每页内容>500字
- 推荐导出页面包含完整SEO标签
- SEO验证脚本通过所有检查
- Git仓库干净，无未跟踪的缓存文件

---

## Technical Spec

### 1. WhiteNoise集成（静态文件压缩）

**文件**: `api/index.py`

**修改位置**: 第173-225行附近（中间件配置区）

**实现要求**:
```python
# 在现有CORS中间件后添加WhiteNoise
from whitenoise import WhiteNoise

# 包装应用
app.wsgi_app = WhiteNoise(
    app.wsgi_app,
    root='static/',
    prefix='static/',
    max_age=31536000  # 1年缓存
)

# 启用压缩
app.wsgi_app.add_files('public/', prefix='')
app.wsgi_app.compression = True
app.wsgi_app.mimetypes = {
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
}
```

**验证方法**:
```bash
# 启动服务器
python web_server.py

# 检查响应头
curl -I http://localhost:8000/static/css/main.css
# 预期：包含 Content-Encoding: gzip

curl -I http://localhost:8000/index.html
# 预期：Cache-Control: max-age=31536000
```

---

### 2. Lighthouse CI集成

**新建文件**: `.github/workflows/lighthouse-ci.yml`

**完整配置**:
```yaml
name: Lighthouse CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Start server
      run: |
        python web_server.py &
        sleep 10  # 等待服务启动

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install Lighthouse CI
      run: npm install -g @lhci/cli@0.12.x

    - name: Run Lighthouse CI
      run: |
        lhci autorun --config=lighthouserc.json
      env:
        LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: lighthouse-results
        path: .lighthouseci/
```

**新建文件**: `lighthouserc.json`（根目录）

```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:8000/",
        "http://localhost:8000/about",
        "http://localhost:8000/faq"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 1.0}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 1.0}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

**验证方法**:
```bash
# 本地测试
npm install -g @lhci/cli
lhci autorun --config=lighthouserc.json
```

---

### 3. 扩充城市数据（5→50）

**文件**: `data/cities.json`

**实现要求**:
- 保留现有5个城市（北京、上海、深圳、广州、杭州）
- 新增45个城市，覆盖：
  - 一线城市（4个已有）
  - 新一线城市（15个）：成都、重庆、武汉、西安、天津、南京、苏州等
  - 二线城市（30个）：厦门、青岛、长沙、郑州、昆明等

**数据结构**:
```json
{
  "cities": [
    {
      "name": "成都",
      "name_en": "Chengdu",
      "slug": "chengdu",
      "description": "天府之国，休闲之都，美食与文化的完美融合",
      "popular_venues": ["火锅店", "茶馆", "咖啡馆", "创意园区"],
      "priority": 1,
      "population": 21000000,
      "coordinates": {
        "lat": 30.5728,
        "lng": 104.0668
      },
      "keywords": ["成都聚会", "成都会面", "成都中点推荐", "chengdu meeting"]
    }
    // ... 共50个城市
  ]
}
```

**SEO优化要求**:
- `description`: 50-100字，包含城市特色
- `keywords`: 包含中英文关键词
- `popular_venues`: 至少4个本地化场景

**验证方法**:
```bash
# 验证JSON格式
python -c "import json; json.load(open('data/cities.json'))"

# 检查城市数量
python -c "import json; print(len(json.load(open('data/cities.json'))['cities']))"
# 预期输出：50
```

---

### 4. 推荐导出页面SEO优化

**文件**: `app/tool/meetspot_recommender.py`

**修改位置**: `_generate_html_content()` 方法（第875行附近）

**实现要求**:

在生成的HTML `<head>` 中添加完整SEO标签：

```python
def _generate_html_content(self, recommendations: List[Dict], center: Dict,
                          locations: List[Dict], search_metadata: Dict) -> str:
    """
    生成HTML内容 - SEO优化版
    """
    # 提取关键词
    keywords = search_metadata.get('keywords', '').split()
    primary_keyword = keywords[0] if keywords else '聚会地点'

    # 从SEO服务生成Meta标签
    from api.services.seo_content import SEOContentGenerator
    seo_gen = SEOContentGenerator()

    # 生成标题和描述
    city = self._extract_city_from_locations(locations)  # 新增方法，从地址提取城市
    meta_tags = seo_gen.generate_meta_tags('recommendation', {
        'city': city,
        'keyword': primary_keyword,
        'locations_count': len(locations)
    })

    # 生成Schema.org - 多个推荐地点
    schema_venues = [
        seo_gen.generate_schema_org('local_business', venue)
        for venue in recommendations[:3]  # 只为前3个生成
    ]

    combined_schema = {
        "@context": "https://schema.org",
        "@graph": schema_venues
    }

    # 生成HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta标签 -->
    <title>{meta_tags['title']}</title>
    <meta name="description" content="{meta_tags['description']}">
    <meta name="keywords" content="{meta_tags['keywords']}">

    <!-- Canonical URL -->
    <link rel="canonical" href="https://meetspot-irq2.onrender.com/">

    <!-- Open Graph -->
    <meta property="og:title" content="{meta_tags['title']}">
    <meta property="og:description" content="{meta_tags['description']}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://meetspot-irq2.onrender.com/">
    <meta property="og:image" content="https://meetspot-irq2.onrender.com/static/og-image.png">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{meta_tags['title']}">
    <meta name="twitter:description" content="{meta_tags['description']}">

    <!-- 结构化数据 -->
    <script type="application/ld+json">
    {json.dumps(combined_schema, ensure_ascii=False, indent=2)}
    </script>

    <!-- 现有的样式和脚本 -->
    ...
</head>
<body>
    ...
</body>
</html>
"""
    return html
```

**新增辅助方法**:
```python
def _extract_city_from_locations(self, locations: List[Dict]) -> str:
    """从地址列表中提取城市名"""
    for loc in locations:
        address = loc.get('address', '')
        # 尝试匹配城市（北京、上海等）
        for city_data in self._load_cities():
            if city_data['name'] in address:
                return city_data['name']
    return "未知城市"

def _load_cities(self) -> List[Dict]:
    """加载城市数据"""
    with open('data/cities.json', 'r', encoding='utf-8') as f:
        return json.load(f)['cities']
```

**SEO服务扩展** (`api/services/seo_content.py`):

在 `generate_meta_tags()` 方法中添加 `recommendation` 页面类型：

```python
elif page_type == 'recommendation':
    city = data.get('city', '未知')
    keyword = data.get('keyword', '聚会地点')
    count = data.get('locations_count', 2)

    title = f"{city}{keyword}推荐 - {count}人聚会最佳会面点 | MeetSpot"
    description = (
        f"为{count}位参与者智能推荐{city}的{keyword}。"
        f"基于地理中点算法，计算最公平的会面位置，"
        f"平均节省30%通勤时间。查看详细路线和场所信息。"
    )
    keywords = f"{city},{keyword},聚会地点推荐,中点计算,{count}人聚会"

    return {
        'title': title[:60],
        'description': description[:160],
        'keywords': keywords
    }
```

**验证方法**:
```bash
# 生成测试推荐
curl -X POST http://localhost:8000/api/find_meetspot \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'

# 检查生成的HTML文件
cat workspace/js_src/place_recommendation_*.html | grep -A 5 "<title>"
# 预期：包含优化后的标题
```

---

### 5. 自动化SEO验证脚本

**新建文件**: `tests/test_seo.py`

**完整实现**:
```python
"""
SEO自动化验证脚本
使用方法：python tests/test_seo.py http://localhost:8000
"""
import sys
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import json

class SEOValidator:
    """SEO验证器"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = {}

    def validate_page(self, path: str = '/') -> Dict:
        """验证单个页面"""
        url = f"{self.base_url}{path}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            return {'error': str(e), 'url': url}

        soup = BeautifulSoup(response.text, 'html.parser')

        checks = {
            # 基础SEO
            'url': url,
            'status_code': response.status_code,
            'title_exists': bool(soup.find('title')),
            'title_text': soup.find('title').text if soup.find('title') else '',
            'title_length': len(soup.find('title').text) if soup.find('title') else 0,
            'title_length_ok': 30 <= len(soup.find('title').text) <= 60 if soup.find('title') else False,

            # Meta标签
            'meta_description': bool(soup.find('meta', {'name': 'description'})),
            'meta_description_text': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
            'meta_description_length': len(soup.find('meta', {'name': 'description'})['content']) if soup.find('meta', {'name': 'description'}) else 0,
            'meta_description_length_ok': 120 <= len(soup.find('meta', {'name': 'description'})['content']) <= 160 if soup.find('meta', {'name': 'description'}) else False,
            'meta_keywords': bool(soup.find('meta', {'name': 'keywords'})),

            # 结构
            'h1_count': len(soup.find_all('h1')),
            'h1_single': len(soup.find_all('h1')) == 1,
            'h1_text': soup.find('h1').text if soup.find('h1') else '',

            # Canonical和Open Graph
            'canonical_url': bool(soup.find('link', {'rel': 'canonical'})),
            'canonical_href': soup.find('link', {'rel': 'canonical'})['href'] if soup.find('link', {'rel': 'canonical'}) else '',
            'og_title': bool(soup.find('meta', {'property': 'og:title'})),
            'og_description': bool(soup.find('meta', {'property': 'og:description'})),
            'og_image': bool(soup.find('meta', {'property': 'og:image'})),
            'twitter_card': bool(soup.find('meta', {'name': 'twitter:card'})),

            # 结构化数据
            'schema_org': bool(soup.find('script', {'type': 'application/ld+json'})),
            'schema_count': len(soup.find_all('script', {'type': 'application/ld+json'})),

            # 内容
            'word_count': len(soup.get_text().split()),
            'word_count_ok': len(soup.get_text().split()) >= 300,

            # 链接
            'internal_links': len([a for a in soup.find_all('a') if a.get('href', '').startswith('/')]),
            'external_links': len([a for a in soup.find_all('a') if a.get('href', '').startswith('http')]),

            # 移动和安全
            'viewport': bool(soup.find('meta', {'name': 'viewport'})),
            'https': url.startswith('https'),

            # 响应头
            'content_encoding': response.headers.get('Content-Encoding'),
            'cache_control': response.headers.get('Cache-Control'),
        }

        # 计算得分
        critical_checks = [
            'title_exists', 'title_length_ok', 'meta_description',
            'meta_description_length_ok', 'h1_single', 'canonical_url',
            'schema_org', 'word_count_ok', 'viewport'
        ]

        passed = sum([1 for check in critical_checks if checks.get(check)])
        checks['score'] = (passed / len(critical_checks)) * 100

        return checks

    def validate_multiple_pages(self, paths: List[str]) -> Dict:
        """验证多个页面"""
        results = {}
        for path in paths:
            print(f"Validating {path}...")
            results[path] = self.validate_page(path)
        return results

    def print_report(self, results: Dict):
        """打印验证报告"""
        print("\n" + "="*80)
        print("SEO Validation Report")
        print("="*80 + "\n")

        for path, checks in results.items():
            if 'error' in checks:
                print(f"❌ {path}: ERROR - {checks['error']}")
                continue

            score = checks.get('score', 0)
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"

            print(f"\n{status} {path} - Score: {score:.1f}/100")
            print("-" * 80)

            # 关键指标
            print(f"  Title: {checks['title_text'][:60]}")
            print(f"    Length: {checks['title_length']} chars {'✅' if checks['title_length_ok'] else '❌'}")

            print(f"  Description: {checks['meta_description_text'][:60]}...")
            print(f"    Length: {checks['meta_description_length']} chars {'✅' if checks['meta_description_length_ok'] else '❌'}")

            print(f"  H1: {checks['h1_text'][:40]} ({'✅' if checks['h1_single'] else '❌ Multiple H1s'})")
            print(f"  Word Count: {checks['word_count']} {'✅' if checks['word_count_ok'] else '❌ <300'}")
            print(f"  Schema.org: {'✅' if checks['schema_org'] else '❌'} ({checks['schema_count']} blocks)")
            print(f"  Internal Links: {checks['internal_links']}")
            print(f"  Compression: {checks['content_encoding'] or '❌ None'}")
            print(f"  HTTPS: {'✅' if checks['https'] else '❌'}")

        # 总体评分
        avg_score = sum([r.get('score', 0) for r in results.values()]) / len(results)
        print("\n" + "="*80)
        print(f"Overall Score: {avg_score:.1f}/100")
        print("="*80 + "\n")

        return avg_score >= 80

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python tests/test_seo.py <base_url>")
        print("Example: python tests/test_seo.py http://localhost:8000")
        sys.exit(1)

    base_url = sys.argv[1]

    # 定义要验证的页面
    pages = [
        '/',
        '/about',
        '/faq',
        '/how-it-works',
    ]

    # 验证
    validator = SEOValidator(base_url)
    results = validator.validate_multiple_pages(pages)

    # 打印报告
    success = validator.print_report(results)

    # 退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

**验证方法**:
```bash
# 本地测试
python tests/test_seo.py http://localhost:8000

# 预期输出
# ✅ / - Score: 90.0/100
# ✅ /about - Score: 85.0/100
# ...
```

---

### 6. Git状态清理

**实现要求**:
```bash
# 1. 删除所有__pycache__目录
find . -type d -name "__pycache__" -exec rm -rf {} +

# 2. 删除已标记删除的文件
git rm SEO_DEPLOYMENT_CHECKLIST.md
git rm SEO_OPTIMIZATION_COMPLETE.md
git rm SEO_OPTIMIZATION_SUMMARY.md
git rm seo_optimization_meetspot-irq2_onrender_com_2025-11-08_134518.md
git rm public/google48ac1a797739b7b0.html
git rm -r app/tool/__pycache__/

# 3. 添加所有新文件和修改
git add .

# 4. 提交
git commit -m "feat: Phase 2 SEO优化 - 性能提升与监控集成

- 集成WhiteNoise静态文件压缩和gzip
- 添加Lighthouse CI自动化监控
- 扩充城市数据从5个到50个
- 优化推荐导出页面SEO标签
- 创建自动化SEO验证脚本
- 清理__pycache__和临时文件

Performance: 预期提升到90+
SEO Score: 保持100分
Cities: 50个主要城市覆盖"
```

**验证方法**:
```bash
# 检查状态
git status
# 预期：working tree clean

# 查看提交
git log -1 --stat
```

---

## Implementation Steps

### Step 0: 环境准备（15分钟）- Conda环境配置

**重要提示**：本项目使用Conda管理依赖，而非pip。这确保了Python版本一致性和系统级依赖的自动处理。

#### 0.1 安装Conda（如果尚未安装）
```bash
# 检查conda是否已安装
conda --version

# 如果未安装，下载Miniconda（推荐）
# Linux/Mac
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Windows
# 下载并运行：https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
```

#### 0.2 创建项目环境
```bash
# 进入项目目录
cd /mnt/d/VibeCoding_pgm/MeetSpot

# 创建开发环境（包含测试、linting工具）
conda env create -f environment-dev.yml

# 验证环境创建成功
conda env list | grep meetspot-dev
# 预期输出：meetspot-dev    /path/to/conda/envs/meetspot-dev
```

#### 0.3 激活环境
```bash
# 激活开发环境
conda activate meetspot-dev

# 验证Python版本
python --version
# 预期输出：Python 3.11.x

# 验证关键包已安装
pip list | grep -E "(fastapi|jinja2|jieba|whitenoise)"
# 预期输出：
# fastapi       0.116.1
# jinja2        3.1.6
# jieba         0.42.1
# whitenoise    6.6.0
```

#### 0.4 配置环境变量
```bash
# 创建.env文件（如果不存在）
cat > .env << 'EOF'
AMAP_API_KEY=your_api_key_here
AMAP_SECURITY_JS_CODE=your_security_code_here
PORT=8000
ENVIRONMENT=development
EOF

# 或编辑config/config.toml
cp config/config.toml.example config/config.toml
# 在config.toml中填入真实的API密钥
```

#### 0.5 验证项目可运行
```bash
# 测试导入
python -c "import app; print('✅ App imports successfully')"

# 启动服务器（后台运行）
python web_server.py &
PID=$!
sleep 5  # 等待启动

# 健康检查
curl http://localhost:8000/health
# 预期输出：{"status":"healthy",...}

# 关闭测试服务器
kill $PID
```

**故障排除**:
```bash
# 如果遇到"conda: command not found"
export PATH="/home/user/miniconda3/bin:$PATH"
source ~/.bashrc  # 或 ~/.zshrc

# 如果环境创建失败
conda clean --all  # 清理缓存
conda env create -f environment-dev.yml --force  # 强制重建

# 如果包冲突
conda config --set solver libmamba  # 使用更快的解决器
conda env create -f environment-dev.yml
```

**环境管理参考**:
详细的conda使用指南请参考：[CONDA_SETUP_GUIDE.md](./CONDA_SETUP_GUIDE.md)

---

### Step 1: WhiteNoise集成（30分钟）

```bash
# 1.1 验证依赖已安装
pip show whitenoise
# 如果未安装：pip install whitenoise==6.6.0

# 1.2 修改 api/index.py
# 在第173行附近找到CORS中间件配置
# 添加WhiteNoise包装（参考Technical Spec第1部分）

# 1.3 创建static目录（如果不存在）
mkdir -p static/css static/js static/images

# 1.4 测试压缩
python web_server.py &
curl -I http://localhost:8000/index.html | grep -i "content-encoding"
# 预期：Content-Encoding: gzip
```

---

### Step 2: Lighthouse CI集成（45分钟）

```bash
# 2.1 创建Lighthouse配置
cat > lighthouserc.json << 'EOF'
{
  "ci": {
    "collect": {
      "url": ["http://localhost:8000/", "http://localhost:8000/about"],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 1.0}]
      }
    }
  }
}
EOF

# 2.2 创建GitHub Actions workflow
mkdir -p .github/workflows
# 创建 .github/workflows/lighthouse-ci.yml（参考Technical Spec第2部分）

# 2.3 本地测试（需要Node.js）
npm install -g @lhci/cli
python web_server.py &
sleep 10
lhci autorun --config=lighthouserc.json

# 2.4 验证结果
# 检查是否有生成 .lighthouseci/ 目录
ls -la .lighthouseci/
```

---

### Step 3: 扩充城市数据（1小时）

```bash
# 3.1 备份现有数据
cp data/cities.json data/cities.json.backup

# 3.2 编辑 data/cities.json
# 添加45个新城市，参考Technical Spec第3部分的数据结构
# 确保每个城市包含：name, name_en, slug, description, popular_venues,
# priority, population, coordinates, keywords

# 3.3 验证JSON格式
python -c "import json; data=json.load(open('data/cities.json')); print(f'Cities: {len(data[\"cities\"])}')"
# 预期输出：Cities: 50

# 3.4 测试城市页面路由
python web_server.py &
curl http://localhost:8000/meetspot/chengdu | grep -i "成都"
curl http://localhost:8000/meetspot/wuhan | grep -i "武汉"
```

**城市列表建议**（50个）:

一线（4）: 北京、上海、深圳、广州
新一线（15）: 成都、重庆、杭州、西安、武汉、苏州、天津、南京、长沙、郑州、东莞、青岛、沈阳、宁波、昆明
二线（31）: 合肥、佛山、福州、厦门、哈尔滨、济南、温州、南宁、长春、泉州、石家庄、贵阳、南昌、金华、常州、惠州、无锡、嘉兴、太原、烟台、珠海、中山、台州、兰州、保定、镇江、扬州、临沂、洛阳、唐山、呼和浩特

---

### Step 4: 推荐导出页面SEO优化（1.5小时）

```bash
# 4.1 修改 app/tool/meetspot_recommender.py
# 在_generate_html_content()方法中添加SEO标签
# 参考Technical Spec第4部分的实现

# 4.2 扩展 api/services/seo_content.py
# 在generate_meta_tags()中添加'recommendation'类型
# 参考Technical Spec第4部分的SEO服务扩展

# 4.3 添加辅助方法
# _extract_city_from_locations()
# _load_cities()

# 4.4 测试生成
curl -X POST http://localhost:8000/api/find_meetspot \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}'

# 4.5 检查生成的HTML
ls -lt workspace/js_src/ | head -5
cat workspace/js_src/place_recommendation_*.html | grep -A 10 "<title>"
# 预期：包含完整SEO标签（title, description, og, schema）
```

---

### Step 5: 创建SEO验证脚本（1小时）

```bash
# 5.1 创建tests目录
mkdir -p tests

# 5.2 创建 tests/test_seo.py
# 参考Technical Spec第5部分的完整实现

# 5.3 安装依赖
pip install beautifulsoup4 requests

# 5.4 运行测试
python tests/test_seo.py http://localhost:8000

# 5.5 验证输出
# 预期：所有页面得分≥80分
```

---

### Step 6: Git状态清理（15分钟）

```bash
# 6.1 删除__pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +

# 6.2 删除已标记删除的文件
git rm -f SEO_DEPLOYMENT_CHECKLIST.md
git rm -f SEO_OPTIMIZATION_COMPLETE.md
git rm -f SEO_OPTIMIZATION_SUMMARY.md
git rm -f seo_optimization_meetspot-irq2_onrender_com_2025-11-08_134518.md
git rm -f public/google48ac1a797739b7b0.html

# 6.3 添加.gitignore（如果还没有）
cat >> .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.lighthouseci/
EOF

# 6.4 提交所有更改
git add .
git commit -m "feat: Phase 2 SEO优化 - 性能提升与监控集成

- 集成WhiteNoise静态文件压缩和gzip
- 添加Lighthouse CI自动化监控
- 扩充城市数据从5个到50个
- 优化推荐导出页面SEO标签
- 创建自动化SEO验证脚本
- 清理__pycache__和临时文件

Performance: 预期提升到90+
SEO Score: 保持100分
Cities: 50个主要城市覆盖"

# 6.5 验证状态
git status
# 预期：working tree clean
```

---

## Validation

### Validation Criteria

**功能验证**:
- [ ] WhiteNoise响应头包含`Content-Encoding: gzip`
- [ ] 静态文件响应头包含`Cache-Control`
- [ ] Lighthouse CI workflow在`.github/workflows/`中存在
- [ ] `lighthouserc.json`配置正确
- [ ] `data/cities.json`包含50个城市
- [ ] 所有50个城市页面可访问（/meetspot/{slug}）
- [ ] 推荐导出HTML包含完整SEO标签（title, meta, og, schema）
- [ ] `tests/test_seo.py`可执行且通过所有检查
- [ ] Git仓库干净，无未跟踪文件

**性能验证**:
```bash
# 本地Lighthouse测试
npm install -g lighthouse
python web_server.py &
lighthouse http://localhost:8000 --output=json --output-path=./report.json
cat report.json | jq '.categories.performance.score'
# 预期：≥0.9

cat report.json | jq '.categories.seo.score'
# 预期：1.0
```

**SEO验证**:
```bash
# 运行SEO验证脚本
python tests/test_seo.py http://localhost:8000
# 预期：Overall Score ≥ 80/100

# 检查城市页面
curl http://localhost:8000/meetspot/beijing | grep -o "<title>.*</title>"
# 预期：包含"北京聚会地点推荐"等关键词

# 检查推荐导出
curl -X POST http://localhost:8000/api/find_meetspot \
  -H "Content-Type: application/json" \
  -d '{"locations": ["北京大学", "清华大学"], "keywords": "咖啡馆"}' \
  | jq -r '.html_url' | xargs -I {} sh -c 'curl http://localhost:8000{} | grep -o "<title>.*</title>"'
# 预期：包含"北京咖啡馆推荐"等关键词
```

**回归验证**:
```bash
# 确保现有功能未被破坏
python -c "import app; print('App imports successfully')"

curl http://localhost:8000/health | jq
# 预期：{"status": "healthy"}

curl http://localhost:8000/ | grep -i "meetspot"
# 预期：主页正常渲染
```

---

## Edge Cases

### Edge Case 1: WhiteNoise与FastAPI兼容性

**问题**: WhiteNoise是WSGI中间件，FastAPI是ASGI应用

**解决方案**:
```python
# 使用a2wsgi包装器（如果遇到问题）
from a2wsgi import ASGIMiddleware

app.wsgi_app = WhiteNoise(
    ASGIMiddleware(app),
    root='static/'
)
```

**验证**:
```bash
# 测试ASGI兼容性
uvicorn api.index:app --reload
curl -I http://localhost:8000/static/test.css
```

---

### Edge Case 2: 城市数据加载失败

**问题**: `data/cities.json`文件不存在或格式错误

**解决方案**:
```python
# 在 api/routers/seo_pages.py 的 load_cities() 中添加错误处理
@lru_cache(maxsize=128)
def load_cities():
    try:
        with open('data/cities.json', 'r', encoding='utf-8') as f:
            return json.load(f)['cities']
    except FileNotFoundError:
        logger.warning("cities.json not found, using default cities")
        return DEFAULT_CITIES  # 定义默认城市列表
    except json.JSONDecodeError:
        logger.error("cities.json format error")
        return DEFAULT_CITIES
```

**验证**:
```bash
# 测试错误处理
mv data/cities.json data/cities.json.tmp
python web_server.py &
curl http://localhost:8000/  # 应该正常加载
mv data/cities.json.tmp data/cities.json
```

---

### Edge Case 3: Lighthouse CI在GitHub Actions中超时

**问题**: 服务器启动慢导致Lighthouse测试失败

**解决方案**:
```yaml
# 在 .github/workflows/lighthouse-ci.yml 中增加等待时间
- name: Start server
  run: |
    python web_server.py &
    for i in {1..30}; do
      if curl -s http://localhost:8000/health; then
        echo "Server started"
        break
      fi
      echo "Waiting for server... ($i/30)"
      sleep 2
    done
```

**验证**:
```bash
# 本地模拟CI环境
python web_server.py &
for i in {1..30}; do curl -s http://localhost:8000/health && break || sleep 2; done
```

---

### Edge Case 4: 推荐导出HTML中城市提取失败

**问题**: 地址不包含标准城市名

**解决方案**:
```python
def _extract_city_from_locations(self, locations: List[Dict]) -> str:
    """从地址列表中提取城市名 - 增强版"""
    cities_data = self._load_cities()

    for loc in locations:
        address = loc.get('address', '')

        # 尝试精确匹配
        for city in cities_data:
            if city['name'] in address:
                return city['name']

        # 尝试英文名匹配
        for city in cities_data:
            if city['name_en'].lower() in address.lower():
                return city['name']

        # 尝试模糊匹配（去掉"市"、"省"等）
        for city in cities_data:
            city_base = city['name'].replace('市', '')
            if city_base in address:
                return city['name']

    # 默认返回
    return "中国"  # 更通用的默认值
```

**验证**:
```bash
# 测试各种地址格式
curl -X POST http://localhost:8000/api/find_meetspot \
  -d '{"locations": ["Chengdu University", "成都高新区"], "keywords": "咖啡馆"}'
# 预期：能正确识别"成都"
```

---

## Notes / Next Steps After This Phase

完成Phase 2后，下一阶段工作（Phase 3）将聚焦：

1. **博客系统**：实现/blog路由，支持Markdown文章，每月发布2篇SEO优化内容
2. **用户案例**：创建/use-cases页面，展示真实使用场景和成功案例
3. **多语言完整实现**：完成英文版所有页面，实现hreflang标签
4. **外链建设**：准备对外API文档，吸引技术博客引用
5. **性能持续优化**：
   - 实现CDN集成（Cloudflare）
   - 添加Redis缓存层
   - 优化数据库查询（如有）

**监控指标（Phase 2完成后1周内观察）**:
- Google Search Console收录页面数：预期50+页面
- Lighthouse Performance分数：预期≥90
- 平均页面加载时间：预期<2秒
- Core Web Vitals：LCP<2.5s, FID<100ms, CLS<0.1

---

## Estimated Time

- **Step 0 (Conda环境)**: 15分钟
- **Step 1 (WhiteNoise)**: 30分钟
- **Step 2 (Lighthouse CI)**: 45分钟
- **Step 3 (城市数据)**: 1小时
- **Step 4 (推荐SEO)**: 1.5小时
- **Step 5 (验证脚本)**: 1小时
- **Step 6 (Git清理)**: 15分钟

**总计**: 约5.25小时（包含环境配置、测试和验证时间）

**注意**：如果conda环境已配置好，可跳过Step 0，总时间约5小时。

---

## Success Metrics

**Phase 2完成标准**:

| 指标 | 当前值 | 目标值 | 验证方法 |
|-----|--------|--------|---------|
| Lighthouse Performance | 未知 | ≥90 | `lighthouse http://localhost:8000` |
| Lighthouse SEO | 100 | 100（保持） | `lighthouse http://localhost:8000` |
| 城市页面数 | 5 | 50 | `curl http://localhost:8000/sitemap.xml \| grep -c meetspot` |
| 推荐页SEO标签 | 无 | 完整 | `curl推荐页 \| grep schema.org` |
| SEO验证得分 | N/A | ≥80 | `python tests/test_seo.py` |
| Git状态 | 混乱 | Clean | `git status` |
| 静态文件压缩 | 无 | Gzip | `curl -I \| grep gzip` |
| CI/CD监控 | 无 | Lighthouse CI | GitHub Actions绿色 |

---

**文档版本**: 2.0
**生成时间**: 2025-11-08
**执行方**: Codex
**审核方**: Claude Code
**预计完成时间**: 5小时
**优先级**: 高（P0）
