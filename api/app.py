#!/usr/bin/env python3
"""
Vercel API入口点 - 直接使用web_server应用
"""
import sys
import os
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

# 直接导入主应用
from web_server import app

# Vercel需要的处理函数
def handler(event, context):
    """Vercel Lambda处理函数"""
    return app

# 导出应用
__all__ = ['app', 'handler']
