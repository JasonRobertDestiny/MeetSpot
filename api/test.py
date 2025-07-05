from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 简单的环境检查
        result = {
            "message": "MeetSpot Vercel 诊断成功",
            "status": "working",
            "environment": {
                "amap_key": "configured" if os.getenv("AMAP_API_KEY") else "missing",
                "silicon_key": "configured" if os.getenv("SILICON_API_KEY") else "missing"
            },
            "method": "GET"
        }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        result = {
            "message": "MeetSpot POST 接口可用",
            "status": "working",
            "method": "POST",
            "note": "推荐功能正在修复中"
        }
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
