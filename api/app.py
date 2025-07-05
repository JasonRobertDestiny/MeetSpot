#!/usr/bin/env python3
"""
Vercel API入口点 - 直接导入web_server应用
"""
import sys
import os
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 直接导入你的web_server应用
from web_server import app

# 这就是全部 - Vercel会自动使用这个app
