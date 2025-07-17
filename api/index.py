#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vercel API 入口点
用于在 Vercel 无服务器环境中运行 FastAPI 应用
"""

import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    # 导入主 FastAPI 应用
    from web_server import app
    print("✅ Successfully imported FastAPI app from web_server")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    # 存储错误信息供端点使用
    import_error_msg = str(e)
    
    # 创建一个简单的备用应用
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="MeetSpot API", description="智能会面点推荐系统")
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "message": "MeetSpot API 正在运行",
            "status": "online",
            "mode": "fallback",
            "error": import_error_msg
        })
    
    @app.get("/health")
    async def health():
        return JSONResponse({
            "status": "healthy",
            "service": "MeetSpot",
            "mode": "fallback",
            "error": import_error_msg
        })
    
    @app.post("/api/find_meetspot")
    async def find_meetspot_fallback():
        return JSONResponse({
            "error": "Service temporarily unavailable",
            "message": "推荐服务暂时不可用，请稍后重试",
            "details": import_error_msg
        }, status_code=503)

# 确保应用可以被 Vercel 访问
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)