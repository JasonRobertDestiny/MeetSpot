#!/usr/bin/env python3
"""
Vercel API入口点 - 使用ASGI包装器
"""
import sys
import os
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入主应用
try:
    from web_server import app as fastapi_app
    
    # 为Vercel创建ASGI应用包装器
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    # 直接使用原应用
    app = fastapi_app
    
except Exception as e:
    # 如果导入失败，创建fallback应用
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="MeetSpot Fallback")
    
    @app.get("/")
    async def fallback_root():
        return {"error": "主应用导入失败", "details": str(e)}
    
    @app.get("/health")
    async def fallback_health():
        return JSONResponse(status_code=503, content={"status": "error", "message": str(e)})
    
    @app.post("/api/find_meetspot")
    async def fallback_meetspot():
        return JSONResponse(status_code=503, content={"error": "服务暂时不可用"})

# 导出应用（Vercel会自动使用这个）
