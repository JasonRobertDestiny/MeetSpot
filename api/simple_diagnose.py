#!/usr/bin/env python3
"""
极简Vercel诊断脚本
"""
import sys
import os
import json
import traceback
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

def handler(request):
    """Vercel处理函数"""
    try:
        # 收集基础信息
        result = {
            "status": "诊断中",
            "environment": {
                "python_version": sys.version,
                "working_dir": os.getcwd(),
                "python_path_length": len(sys.path),
                "env_vars": {
                    "AMAP_API_KEY": bool(os.getenv("AMAP_API_KEY")),
                    "SILICON_API_KEY": bool(os.getenv("SILICON_API_KEY"))
                }
            },
            "steps": []
        }
        
        # 检查关键文件
        key_files = ["web_server.py", "app", "config", "workspace", "requirements.txt"]
        file_status = {}
        for file in key_files:
            path = project_root / file
            file_status[file] = {
                "exists": path.exists(),
                "path": str(path)
            }
            if path.exists():
                result["steps"].append(f"✅ {file} 存在")
            else:
                result["steps"].append(f"❌ {file} 不存在")
                
        result["files"] = file_status
        
        # 尝试导入关键模块
        try:
            result["steps"].append("尝试导入FastAPI...")
            from fastapi import FastAPI
            result["steps"].append("✅ FastAPI导入成功")
        except Exception as e:
            result["steps"].append(f"❌ FastAPI导入失败: {e}")
            
        try:
            result["steps"].append("尝试导入web_server...")
            import web_server
            result["steps"].append("✅ web_server导入成功")
            
            if hasattr(web_server, 'app'):
                result["steps"].append("✅ web_server.app存在")
                result["status"] = "成功"
            else:
                result["steps"].append("❌ web_server.app不存在")
                result["status"] = "部分成功"
                
        except Exception as e:
            result["steps"].append(f"❌ web_server导入失败: {e}")
            result["import_error"] = str(e)
            result["import_traceback"] = traceback.format_exc()
            result["status"] = "失败"
        
        # 返回HTTP响应
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        # 完全失败的情况
        error_result = {
            "status": "严重错误",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "python_version": sys.version,
            "working_dir": os.getcwd()
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_result, ensure_ascii=False, indent=2)
        }
