#!/usr/bin/env python3
"""
Vercel API入口点 - 优先使用完整的web_server.app
"""
import sys
import os
import traceback
from pathlib import Path

# 设置项目根目录和Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

# 检查环境变量
amap_key = os.getenv("AMAP_API_KEY")
silicon_key = os.getenv("SILICON_API_KEY")

print(f"🔍 Vercel环境检查:")
print(f"Python版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")
print(f"项目根目录: {project_root}")
print(f"AMAP_API_KEY: {'✅已配置' if amap_key else '❌未配置'}")
print(f"SILICON_API_KEY: {'✅已配置' if silicon_key else '❌未配置'}")

# 检查关键文件是否存在
key_files = ["web_server.py", "app", "config", "workspace"]
for file in key_files:
    path = project_root / file
    exists = path.exists()
    print(f"  {file}: {'✅存在' if exists else '❌缺失'}")

try:
    # 强制导入完整的 web_server 应用
    print("🔄 尝试导入 web_server...")
    import web_server
    app = web_server.app
    print("✅ 成功导入完整的 web_server.app")
    print("✅ MeetSpot API 完整功能已加载")
    
except Exception as e:
    print(f"❌ 导入 web_server 失败: {e}")
    print(f"📋 错误详情:")
    traceback.print_exc()
    
    # 如果完整版本无法导入，创建错误报告应用
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="MeetSpot API - Error Mode")
    
    @app.get("/")
    async def error_root():
        return {
            "error": "MeetSpot API 导入失败",
            "details": str(e),
            "mode": "error_fallback",
            "environment_check": {
                "amap_configured": bool(amap_key),
                "silicon_configured": bool(silicon_key)
            },
            "missing_files": [f for f in key_files if not (project_root / f).exists()],
            "suggestion": "请检查所有依赖是否正确安装"
        }
    
    @app.get("/health")
    async def error_health():
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "应用初始化失败",
                "details": str(e)
            }
        )
    
    @app.post("/api/find_meetspot")
    async def error_meetspot(request: dict):
        return JSONResponse(
            status_code=503,
            content={
                "error": "MeetSpot 推荐服务不可用",
                "reason": "web_server.py 导入失败",
                "details": str(e),
                "note": "请检查环境变量和依赖安装"
            }
        )

# Vercel处理函数
def handler(event, context):
    return app
