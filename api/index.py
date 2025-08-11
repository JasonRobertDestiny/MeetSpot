import sys
import os
import time
import asyncio
import re
import json
from typing import List, Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 导入应用模块
try:
    from app.config import config
    from app.tool.meetspot_recommender import CafeRecommender
    from app.logger import logger
    print("✅ 成功导入所有必要模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    config = None

# 请求模型定义
class LocationRequest(BaseModel):
    locations: List[str]
    venue_types: Optional[List[str]] = ["咖啡馆"]
    user_requirements: Optional[str] = ""

class MeetSpotRequest(BaseModel):
    locations: List[str] 
    keywords: Optional[str] = "咖啡馆"
    place_type: Optional[str] = ""
    user_requirements: Optional[str] = ""

# 环境变量配置（用于 Vercel）
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
AMAP_SECURITY_JS_CODE = os.getenv("AMAP_SECURITY_JS_CODE", "")

# 创建 FastAPI 应用
app = FastAPI(
    title="MeetSpot", 
    description="MeetSpot会面点推荐服务 - 完整功能版",
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

# 挂载静态文件（如果目录存在）
try:
    # Vercel环境下创建必要的目录结构
    workspace_dir = "workspace"
    js_src_dir = os.path.join(workspace_dir, "js_src")
    os.makedirs(js_src_dir, exist_ok=True)
    
    if os.path.exists(workspace_dir):
        app.mount("/workspace", StaticFiles(directory=workspace_dir), name="workspace")
        print("✅ 挂载 /workspace 静态文件")
    
    if os.path.exists("public"):
        app.mount("/public", StaticFiles(directory="public"), name="public")
        print("✅ 挂载 /public 静态文件")
        
    if os.path.exists("docs"):
        app.mount("/docs-static", StaticFiles(directory="docs"), name="docs-static")
        print("✅ 挂载 /docs 静态文件")
except Exception as e:
    print(f"⚠️ 静态文件挂载失败: {e}")
    # 在Vercel环境下，静态文件挂载可能失败，这是正常的

@app.get("/")
async def read_root():
    """根路径 - 返回主页"""
    try:
        # 尝试返回实际的HTML页面
        html_file = "public/index.html"
        if os.path.exists(html_file):
            return FileResponse(html_file)
        
        # 否则返回简单的欢迎页面
        return {
            "message": "🎯 MeetSpot API - 智能会面地点推荐服务",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "timestamp": time.time()
        }
    except Exception as e:
        return {"message": "MeetSpot API", "error": str(e)}

@app.get("/health")
async def health_check():
    """健康检查和配置状态"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "config": {
            "amap_configured": bool(AMAP_API_KEY or (config and config.amap.api_key)),
            "full_features": bool(config)
        }
    }

@app.get("/config")
async def get_config():
    """获取当前配置状态（不暴露敏感信息）"""
    amap_key = ""
    if config:
        amap_key = config.amap.api_key
    else:
        amap_key = AMAP_API_KEY
        
    return {
        "amap_api_key_configured": bool(amap_key),
        "amap_api_key_length": len(amap_key) if amap_key else 0,
        "config_loaded": bool(config),
        "full_features_available": bool(config)
    }

@app.post("/api/find_meetspot")
async def find_meetspot(request: MeetSpotRequest):
    """完整的会面地点推荐功能"""
    start_time = time.time()
    
    try:
        print(f"📝 收到请求: {request.model_dump()}")
        
        # 检查配置
        if config:
            api_key = config.amap.api_key
            print(f"✅ 使用配置文件中的API密钥: {api_key[:10]}...")
        else:
            api_key = AMAP_API_KEY
            print(f"✅ 使用环境变量中的API密钥: {api_key[:10]}...")
            
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="高德地图API密钥未配置，请设置AMAP_API_KEY环境变量或配置config.toml文件"
            )
        
        # 使用推荐工具
        if config:
            print("🔧 开始初始化推荐工具...")
            recommender = CafeRecommender()
            
            print("🚀 开始执行推荐...")
            # 调用推荐工具
            result = await recommender.execute(
                locations=request.locations,
                keywords=request.keywords,
                place_type=request.place_type,
                user_requirements=request.user_requirements
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️  推荐完成，耗时: {processing_time:.2f}秒")
            
            # 解析工具输出，提取HTML文件路径
            output_text = result.output
            html_url = None
            
            print(f"📄 工具输出预览: {output_text[:200]}...")
            
            # 从输出中提取HTML文件路径 - 修复的正则表达式
            html_match = re.search(r'HTML页面:\s*([^\s\n]+\.html)', output_text)
            if html_match:
                html_filename = html_match.group(1)
                print(f"🔍 找到HTML文件名: {html_filename}")
                html_url = f"/workspace/js_src/{html_filename}"
                print(f"🌐 转换为URL: {html_url}")
            else:
                print("❌ 未找到'HTML页面:'模式，尝试其他模式...")
                # 尝试匹配生成的推荐页面格式
                html_match2 = re.search(r'生成的推荐页面：\s*([^\s\n]+\.html)', output_text)
                if html_match2:
                    html_path = html_match2.group(1)
                    if html_path.startswith('workspace/'):
                        html_url = f"/{html_path}"
                    else:
                        html_url = f"/workspace/{html_path}"
                    print(f"🔍 备用匹配1找到: {html_url}")
                else:
                    # 尝试匹配任何place_recommendation格式的文件名
                    html_match3 = re.search(r'(place_recommendation_\d{14}_[a-f0-9]+\.html)', output_text)
                    if html_match3:
                        html_filename = html_match3.group(1)
                        html_url = f"/workspace/js_src/{html_filename}"
                        print(f"🔍 备用匹配2找到: {html_url}")
                    else:
                        print("❌ 所有匹配模式都失败了")
                        html_url = None
            
            # 返回前端期望的格式
            response_data = {
                "success": True,
                "html_url": html_url,
                "locations_count": len(request.locations),
                "processing_time": processing_time,
                "message": "推荐生成成功",
                "output": output_text
            }
            
            print(f"📤 返回响应: success={response_data['success']}, html_url={response_data['html_url']}")
            return response_data
            
        else:
            # Fallback：如果无法加载完整模块，返回错误
            print("❌ 配置未加载")
            raise HTTPException(
                status_code=500,
                detail="服务配置错误：无法加载推荐模块，请确保在本地环境运行或正确配置Vercel环境变量"
            )
            
    except Exception as e:
        print(f"💥 异常发生: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        traceback.print_exc()
        
        processing_time = time.time() - start_time
        
        # 返回错误响应，但保持前端期望的格式
        error_response = {
            "success": False,
            "error": str(e),
            "processing_time": processing_time,
            "message": f"推荐失败: {str(e)}"
        }
        
        print(f"📤 返回错误响应: {error_response['message']}")
        return error_response

@app.post("/recommend")
async def get_recommendations(request: LocationRequest):
    """兼容性API端点 - 统一响应格式"""
    # 转换请求格式
    meetspot_request = MeetSpotRequest(
        locations=request.locations,
        keywords=request.venue_types[0] if request.venue_types else "咖啡馆",
        user_requirements=request.user_requirements
    )
    
    # 直接调用主端点并返回相同格式
    return await find_meetspot(meetspot_request)

@app.get("/api/status")
async def api_status():
    """API状态检查"""
    return {
        "status": "healthy",
        "service": "MeetSpot",
        "version": "1.0.0",
        "platform": "Multi-platform",
        "features": "Complete" if config else "Limited",
        "timestamp": time.time()
    }

# Vercel 处理函数
app_instance = app

# 如果直接运行此文件（本地测试）
if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 MeetSpot 完整功能服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000)