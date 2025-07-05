#!/usr/bin/env python3
"""
Vercel调试入口点 - 用于诊断导入和环境问题
"""
import sys
import os
import traceback
from pathlib import Path

# 捕获所有输出到一个字符串
debug_info = []

try:
    debug_info.append(f"Python版本: {sys.version}")
    debug_info.append(f"Python路径: {sys.executable}")
    debug_info.append(f"当前工作目录: {os.getcwd()}")
    debug_info.append(f"__file__路径: {__file__}")
    
    # 项目根目录设置
    project_root = Path(__file__).parent.parent
    debug_info.append(f"项目根目录: {project_root}")
    debug_info.append(f"项目根目录绝对路径: {project_root.resolve()}")
    
    # 检查关键目录和文件
    key_paths = [
        "app",
        "config", 
        "workspace",
        "web_server.py",
        "requirements.txt",
        "vercel.json"
    ]
    
    for path in key_paths:
        full_path = project_root / path
        exists = full_path.exists()
        debug_info.append(f"路径 {path}: {'存在' if exists else '不存在'} ({full_path})")
        if exists and full_path.is_dir():
            try:
                contents = list(full_path.iterdir())[:5]  # 只显示前5个
                debug_info.append(f"  内容: {[p.name for p in contents]}")
            except Exception as e:
                debug_info.append(f"  无法列举内容: {e}")
    
    # 检查sys.path
    debug_info.append("Python sys.path:")
    for i, path in enumerate(sys.path[:10]):  # 只显示前10个
        debug_info.append(f"  {i}: {path}")
    
    # 尝试导入关键模块
    import_tests = [
        "fastapi",
        "pydantic", 
        "httpx",
        "app",
        "config",
        "web_server"
    ]
    
    debug_info.append("导入测试:")
    sys.path.insert(0, str(project_root))
    os.chdir(str(project_root))
    
    for module_name in import_tests:
        try:
            __import__(module_name)
            debug_info.append(f"  ✅ {module_name}: 成功")
        except Exception as e:
            debug_info.append(f"  ❌ {module_name}: {e}")
            # 显示详细错误
            debug_info.append(f"     详情: {traceback.format_exc().split('Traceback')[-1][:200]}...")

    # 环境变量检查
    debug_info.append("环境变量:")
    env_vars = ["OPENAI_API_KEY", "BING_SEARCH_API_KEY", "VERCEL", "VERCEL_ENV"]
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            debug_info.append(f"  {var}: {'***' if 'key' in var.lower() else value}")
        else:
            debug_info.append(f"  {var}: 未设置")

except Exception as e:
    debug_info.append(f"调试过程中出错: {e}")
    debug_info.append(f"完整错误: {traceback.format_exc()}")

# 现在创建一个简单的FastAPI应用返回调试信息
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, PlainTextResponse
    
    app = FastAPI(title="MeetSpot Debug")
    
    @app.get("/")
    async def debug_root():
        return PlainTextResponse("\n".join(debug_info))
    
    @app.get("/debug")
    async def debug_json():
        return {"debug_info": debug_info}
        
    @app.get("/api/")
    async def debug_api():
        return {"status": "debug_mode", "info": debug_info[:10]}  # 只返回前10条
        
except Exception as e:
    debug_info.append(f"创建FastAPI应用失败: {e}")
    # 最基本的WSGI应用
    def app(environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [("\n".join(debug_info)).encode()]

# Vercel 入口点
def handler(event, context):
    return app
