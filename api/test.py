from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        result = {
            "message": "MeetSpot 测试成功",
            "status": "working",
            "method": "GET"
        }
        
        self.wfile.write(json.dumps(result).encode())
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        result = {
            "message": "MeetSpot POST 测试成功",
            "status": "working",
            "method": "POST"
        }
        
        self.wfile.write(json.dumps(result).encode())
