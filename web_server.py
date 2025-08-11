#!/usr/bin/env python3
"""
MeetSpot Local Development Server
=================================

This is the main entry point for local development.
It imports and runs the FastAPI application from api/index.py.

For production deployment on Vercel, the api/index.py file is used directly.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Main entry point for local development server"""
    try:
        # Import the FastAPI app from api/index.py
        from api.index import app
        import uvicorn
        
        print("🚀 启动 MeetSpot 本地开发服务器...")
        print("📍 服务地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("🔧 健康检查: http://localhost:8000/health")
        print("=" * 50)
        
        # Run the server
        uvicorn.run(
            "api.index:app", 
            host="0.0.0.0", 
            port=8000,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()