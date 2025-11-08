# MeetSpot Conda环境配置指南

## 为什么使用Conda？

**相比pip的优势**:
1. **跨平台一致性**：Windows/Linux/Mac环境统一
2. **Python版本管理**：锁定Python 3.11，避免版本冲突
3. **系统级依赖**：自动处理C库依赖（如numpy、pandas）
4. **环境隔离**：完全独立的Python环境，不污染系统Python
5. **快速环境复制**：一键创建相同开发环境

---

## 快速开始

### 1. 安装Conda

**选择1：Miniconda（推荐，轻量级）**
```bash
# Linux/Mac
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Windows
# 下载：https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
# 双击安装
```

**选择2：Anaconda（完整版，包含数据科学工具）**
```bash
# 下载：https://www.anaconda.com/download
```

**验证安装**:
```bash
conda --version
# 输出：conda 24.1.0 或更高版本
```

---

### 2. 创建MeetSpot环境

#### 生产环境（最小依赖）
```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate meetspot

# 验证
python --version  # Python 3.11.x
pip list          # 查看已安装包
```

#### 开发环境（包含测试、linting工具）
```bash
# 创建开发环境
conda env create -f environment-dev.yml

# 激活环境
conda activate meetspot-dev

# 验证开发工具
pytest --version
black --version
ruff --version
```

---

### 3. 日常使用

#### 激活环境
```bash
# 每次打开新终端都需要激活
conda activate meetspot

# 或开发环境
conda activate meetspot-dev
```

#### 运行项目
```bash
# 确保已激活环境
(meetspot) $ python web_server.py

# 或使用uvicorn
(meetspot) $ uvicorn api.index:app --reload
```

#### 运行测试
```bash
(meetspot-dev) $ pytest tests/

# 带覆盖率
(meetspot-dev) $ pytest --cov=app tests/
```

#### 代码格式化
```bash
(meetspot-dev) $ black .
(meetspot-dev) $ ruff check .
```

---

## 环境管理命令

### 查看环境列表
```bash
conda env list
# 输出示例：
# meetspot                /home/user/miniconda3/envs/meetspot
# meetspot-dev            /home/user/miniconda3/envs/meetspot-dev
```

### 更新环境
```bash
# 当environment.yml有变化时
conda env update -f environment.yml --prune

# --prune会移除不再需要的包
```

### 导出当前环境
```bash
# 导出conda环境
conda env export > environment-frozen.yml

# 导出pip格式（兼容性）
pip freeze > requirements-frozen.txt
```

### 删除环境
```bash
# 删除开发环境
conda deactivate  # 先退出环境
conda env remove -n meetspot-dev
```

### 克隆环境
```bash
# 基于生产环境创建测试环境
conda create --name meetspot-test --clone meetspot
```

---

## 在不同场景下的使用

### 场景1：新成员加入项目
```bash
# 1. 克隆仓库
git clone https://github.com/YourOrg/MeetSpot.git
cd MeetSpot

# 2. 创建conda环境
conda env create -f environment-dev.yml

# 3. 激活环境
conda activate meetspot-dev

# 4. 配置环境变量
cp config/config.toml.example config/config.toml
# 编辑config.toml，添加AMAP_API_KEY

# 5. 运行项目
python web_server.py

# 6. 运行测试
pytest tests/

# ✅ 开发环境就绪！
```

### 场景2：生产部署（Docker）
```dockerfile
# Dockerfile中使用conda
FROM continuumio/miniconda3:latest

WORKDIR /app
COPY environment.yml .

# 创建环境
RUN conda env create -f environment.yml

# 激活环境
SHELL ["conda", "run", "-n", "meetspot", "/bin/bash", "-c"]

COPY . .

# 运行应用
CMD ["conda", "run", "-n", "meetspot", "python", "web_server.py"]
```

### 场景3：CI/CD集成（GitHub Actions）
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - uses: conda-incubator/setup-miniconda@v2
      with:
        environment-file: environment-dev.yml
        activate-environment: meetspot-dev
        python-version: 3.11

    - name: Run tests
      shell: bash -l {0}  # 激活conda环境
      run: |
        pytest tests/ --cov=app
```

### 场景4：多Python版本测试
```bash
# 创建Python 3.12测试环境
conda create -n meetspot-py312 python=3.12
conda activate meetspot-py312
pip install -r requirements.txt

# 运行测试
pytest tests/
```

---

## 与现有工具集成

### VSCode集成
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "/home/user/miniconda3/envs/meetspot-dev/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm集成
1. File → Settings → Project: MeetSpot → Python Interpreter
2. Add Interpreter → Conda Environment
3. 选择 `meetspot-dev` 环境
4. Apply → OK

### Jupyter Notebook支持
```bash
# 在开发环境中安装ipykernel
conda activate meetspot-dev
conda install ipykernel

# 注册kernel
python -m ipykernel install --user --name=meetspot-dev --display-name="MeetSpot Dev"

# 启动Jupyter
jupyter notebook
```

---

## 故障排除

### 问题1：conda命令找不到
```bash
# 检查conda是否在PATH中
echo $PATH | grep conda

# 如果没有，手动添加
export PATH="/home/user/miniconda3/bin:$PATH"

# 永久添加到 ~/.bashrc 或 ~/.zshrc
echo 'export PATH="/home/user/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 问题2：环境创建失败
```bash
# 清除conda缓存
conda clean --all

# 更新conda自身
conda update -n base conda

# 重试创建环境
conda env create -f environment.yml --force
```

### 问题3：包冲突
```bash
# 使用conda解决器
conda config --set solver libmamba

# 或使用mamba（更快的conda）
conda install mamba -n base -c conda-forge
mamba env create -f environment.yml
```

### 问题4：pip包在conda环境中安装失败
```bash
# 确保使用conda环境的pip
conda activate meetspot
which pip
# 输出：/home/user/miniconda3/envs/meetspot/bin/pip

# 如果还有问题，重新安装pip
conda install pip --force-reinstall
```

### 问题5：Windows下激活环境失败
```powershell
# PowerShell需要初始化conda
conda init powershell

# 重启PowerShell，然后激活
conda activate meetspot
```

---

## 性能优化

### 使用Mamba加速
```bash
# 安装mamba（conda的C++重写版，快10倍）
conda install mamba -n base -c conda-forge

# 使用mamba创建环境
mamba env create -f environment.yml

# 使用mamba安装包
mamba install numpy pandas
```

### 配置国内镜像（中国用户）
```bash
# 清华源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --set show_channel_urls yes

# 验证配置
conda config --show channels
```

---

## 最佳实践

### 1. 环境命名规范
```bash
# 生产环境：项目名
meetspot

# 开发环境：项目名-dev
meetspot-dev

# 测试环境：项目名-test
meetspot-test

# 特定版本：项目名-版本号
meetspot-v2.0
```

### 2. 定期更新依赖
```bash
# 每月更新一次依赖
conda activate meetspot-dev
conda update --all

# 导出新的环境文件
conda env export > environment-dev-$(date +%Y%m%d).yml
```

### 3. 锁定环境以确保可重现性
```bash
# 生成完全锁定的环境文件（包含所有依赖的精确版本）
conda env export --no-builds > environment-lock.yml

# 或使用conda-lock工具（推荐）
conda install conda-lock -c conda-forge
conda-lock -f environment.yml -p linux-64 -p osx-64 -p win-64
```

### 4. 自动激活环境
```bash
# 在项目根目录创建 .envrc（需要direnv）
echo 'conda activate meetspot-dev' > .envrc

# 安装direnv
# Linux: sudo apt install direnv
# Mac: brew install direnv

# 允许自动激活
direnv allow
```

---

## Conda vs Docker vs Venv

| 特性 | Conda | Docker | Venv |
|-----|-------|--------|------|
| 环境隔离 | ✅ 强 | ✅ 完全 | ⚠️ 仅Python |
| 跨平台 | ✅ 优秀 | ✅ 优秀 | ⚠️ 一般 |
| Python版本管理 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| 系统依赖 | ✅ 自动处理 | ✅ 自动处理 | ❌ 手动 |
| 启动速度 | ✅ 快 | ⚠️ 慢 | ✅ 快 |
| 资源占用 | ⚠️ 中等 | ❌ 高 | ✅ 低 |
| 学习曲线 | ⚠️ 中等 | ❌ 陡峭 | ✅ 简单 |
| 适用场景 | 数据科学、开发 | 生产部署 | 简单Python项目 |

**推荐组合**：
- **本地开发**：Conda（环境管理）
- **CI/CD**：Conda + Docker（测试+部署）
- **生产环境**：Docker（容器化部署）

---

## 快速参考

### 常用命令
```bash
# 环境管理
conda env list                    # 列出所有环境
conda activate <env>              # 激活环境
conda deactivate                  # 退出环境
conda env remove -n <env>         # 删除环境

# 包管理
conda list                        # 列出已安装包
conda install <package>           # 安装包
conda update <package>            # 更新包
conda remove <package>            # 移除包
conda search <package>            # 搜索包

# 环境导入导出
conda env create -f env.yml       # 从文件创建环境
conda env export > env.yml        # 导出环境
conda env update -f env.yml       # 更新环境

# 清理
conda clean --all                 # 清理缓存
conda clean --packages            # 清理未使用的包
```

---

## 更多资源

- **官方文档**：https://docs.conda.io/
- **Conda Cheat Sheet**：https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html
- **Mamba文档**：https://mamba.readthedocs.io/
- **环境管理最佳实践**：https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

---

**文档版本**: 1.0
**最后更新**: 2025-11-08
**维护者**: MeetSpot Team
