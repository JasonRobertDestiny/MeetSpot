import os
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 请求模型定义
class LocationRequest(BaseModel):
    locations: List[str]
    venue_types: Optional[List[str]] = ["咖啡馆"]
    user_requirements: Optional[str] = ""

# 环境变量配置
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
AMAP_SECURITY_JS_CODE = os.getenv("AMAP_SECURITY_JS_CODE", "")

# 创建 FastAPI 应用
app = FastAPI(
    title="MeetSpot", 
    description="MeetSpot会面点推荐服务 - Vercel部署版",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """根路径"""
    return {
        "message": "🎯 MeetSpot API - 智能会面地点推荐服务",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "config": {
            "amap_configured": bool(AMAP_API_KEY),
            "amap_security_configured": bool(AMAP_SECURITY_JS_CODE)
        }
    }

@app.get("/config")
async def get_config():
    """获取当前配置状态（不暴露敏感信息）"""
    return {
        "amap_api_key_configured": bool(AMAP_API_KEY),
        "amap_api_key_length": len(AMAP_API_KEY) if AMAP_API_KEY else 0,
        "amap_security_configured": bool(AMAP_SECURITY_JS_CODE)
    }

@app.post("/recommend")
async def get_recommendations(request: LocationRequest):
    """获取会面地点推荐（简化版）"""
    try:
        # 检查API密钥配置
        if not AMAP_API_KEY:
            raise HTTPException(
                status_code=500, 
                detail="高德地图API密钥未配置，请设置AMAP_API_KEY环境变量"
            )
            
        # 返回简化的推荐结果
        return {
            "status": "success",
            "message": "MeetSpot 推荐服务运行中",
            "data": {
                "locations": request.locations,
                "venue_types": request.venue_types,
                "user_requirements": request.user_requirements,
                "recommendations": [
                    {
                        "name": "星巴克咖啡(示例)",
                        "type": "咖啡馆",
                        "address": "示例地址",
                        "rating": 4.5,
                        "distance": "500m",
                        "note": "这是一个示例推荐"
                    },
                    {
                        "name": "肯德基(示例)",
                        "type": "餐厅",
                        "address": "示例地址2",
                        "rating": 4.0,
                        "distance": "800m",
                        "note": "这是另一个示例推荐"
                    }
                ],
                "center_point": {
                    "lat": 39.9042,
                    "lng": 116.4074,
                    "name": "计算的中心点"
                },
                "note": "这是简化版API，完整功能需要集成高德地图POI搜索"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/api/status")
async def api_status():
    """API状态检查"""
    return {
        "status": "healthy",
        "service": "MeetSpot",
        "version": "1.0.0",
        "platform": "Vercel",
        "timestamp": time.time()
    }

# Vercel 处理函数
def handler(request, response):
    """Vercel serverless 函数入口点"""
    return app

# 如果直接运行此文件（本地测试）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
