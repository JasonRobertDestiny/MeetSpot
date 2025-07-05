#!/usr/bin/env python3
"""
超级简化的API入口点 - Vercel专用
"""
import os
import json

# 读取环境变量
amap_key = os.getenv("AMAP_API_KEY")
silicon_key = os.getenv("SILICON_API_KEY")

print(f"🔍 环境变量检查:")
print(f"  AMAP_API_KEY: {'已配置' if amap_key else '未配置'}")
print(f"  SILICON_API_KEY: {'已配置' if silicon_key else '未配置'}")

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="MeetSpot API", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"message": "MeetSpot API", "status": "online"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "amap": bool(amap_key), "silicon": bool(silicon_key)}
    
    @app.get("/api/status")
    async def api_status():
        return {
            "status": "online",
            "version": "1.0.0",
            "api_keys": {
                "amap": bool(amap_key),
                "silicon": bool(silicon_key)
            }
        }
    
    @app.post("/api/find_meetspot")
    async def find_meetspot(request: dict):
        """简化的推荐接口"""
        if not amap_key:
            return JSONResponse(
                status_code=503,
                content={"error": "API密钥未配置"}
            )
        
        # 返回模拟推荐
        return {
            "status": "success",
            "message": "找到推荐会面点",
            "recommendations": [
                {
                    "name": "星巴克咖啡",
                    "address": "北京市朝阳区建国门外大街1号",
                    "rating": "4.5",
                    "distance": "1.2公里"
                },
                {
                    "name": "Costa咖啡",
                    "address": "北京市海淀区中关村大街27号", 
                    "rating": "4.3",
                    "distance": "1.8公里"
                }
            ]
        }

except Exception as e:
    print(f"❌ FastAPI导入失败: {e}")
    
    # 最基本的ASGI应用
    async def app(scope, receive, send):
        if scope["type"] == "http":
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [[b'content-type', b'application/json']],
            })
            response = {
                "message": "MeetSpot API (基础模式)",
                "status": "online",
                "error": str(e),
                "env_check": {
                    "amap": bool(amap_key),
                    "silicon": bool(silicon_key)
                }
            }
            await send({
                'type': 'http.response.body',
                'body': json.dumps(response).encode(),
            })

# Vercel处理函数
def handler(event, context):
    return app
