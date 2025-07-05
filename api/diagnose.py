#!/usr/bin/env python3
"""
Vercel诊断脚本 - 检查具体错误
"""
import sys
import os
import traceback
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="MeetSpot Debug")
    
    @app.get("/")
    async def debug_root():
        try:
            # 尝试逐步导入并报告状态
            result = {
                "status": "检查中",
                "steps": [],
                "environment": {
                    "python_version": sys.version,
                    "working_dir": os.getcwd(),
                    "python_path": sys.path[:5],  # 只显示前5个
                    "env_vars": {
                        "AMAP_API_KEY": bool(os.getenv("AMAP_API_KEY")),
                        "SILICON_API_KEY": bool(os.getenv("SILICON_API_KEY"))
                    }
                }
            }
            
            # 检查关键文件
            key_files = ["web_server.py", "app", "config", "workspace"]
            file_status = {}
            for file in key_files:
                path = project_root / file
                file_status[file] = {
                    "exists": path.exists(),
                    "path": str(path)
                }
            result["files"] = file_status
            
            # 尝试导入web_server
            try:
                result["steps"].append("尝试导入web_server...")
                import web_server
                result["steps"].append("✅ web_server导入成功")
                
                # 检查app属性
                if hasattr(web_server, 'app'):
                    result["steps"].append("✅ web_server.app存在")
                    result["status"] = "成功"
                    result["message"] = "web_server.app可正常使用"
                else:
                    result["steps"].append("❌ web_server.app不存在")
                    result["status"] = "部分成功"
                    
            except Exception as e:
                result["steps"].append(f"❌ 导入web_server失败: {e}")
                result["import_error"] = str(e)
                result["import_traceback"] = traceback.format_exc()
                result["status"] = "失败"
                
            return result
            
        except Exception as e:
            return {
                "status": "严重错误",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    @app.get("/health")
    async def debug_health():
        return {"status": "debug_mode", "message": "诊断模式"}
    
    @app.post("/api/find_meetspot")
    async def debug_meetspot(request: dict):
        return JSONResponse(
            status_code=503,
            content={
                "error": "诊断模式",
                "message": "请访问根路径获取详细诊断信息",
                "request_received": request
            }
        )

except Exception as e:
    # 如果连FastAPI都无法导入
    async def debug_app(scope, receive, send):
        import json
        
        response = {
            "error": "FastAPI导入失败",
            "details": str(e),
            "traceback": traceback.format_exc()
        }
        
        await send({
            'type': 'http.response.start',
            'status': 500,
            'headers': [[b'content-type', b'application/json']],
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps(response).encode(),
        })
    
    app = debug_app

# Vercel处理函数
def handler(event, context):
    return app
