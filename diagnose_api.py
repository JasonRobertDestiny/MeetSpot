#!/usr/bin/env python3
"""
诊断 MeetSpot API 推荐接口问题
"""

import requests
import json
import time

BASE_URL = "https://meetspotagent.vercel.app"

def test_api_endpoints():
    print("🔍 诊断 MeetSpot API 接口")
    print("=" * 50)
    
    # 测试基础连接
    try:
        print(f"\n1️⃣ 测试基础连接: {BASE_URL}/")
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 前端页面正常")
        else:
            print("❌ 前端页面异常")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    # 测试API根路径
    try:
        print(f"\n2️⃣ 测试API根路径: {BASE_URL}/api/")
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        if response.text:
            print(f"响应内容: {response.text[:500]}")
    except Exception as e:
        print(f"❌ API根路径失败: {e}")
    
    # 测试推荐接口 - GET请求
    try:
        print(f"\n3️⃣ 测试推荐接口(GET): {BASE_URL}/api/find_meetspot")
        response = requests.get(f"{BASE_URL}/api/find_meetspot", timeout=15)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        if response.text:
            print(f"响应内容: {response.text[:500]}")
    except Exception as e:
        print(f"❌ GET请求失败: {e}")
    
    # 测试推荐接口 - POST请求（正常调用）
    try:
        print(f"\n4️⃣ 测试推荐接口(POST): {BASE_URL}/api/find_meetspot")
        
        # 构造测试数据
        test_data = {
            "locations": ["北京市朝阳区", "北京市海淀区"],
            "place_type": "咖啡厅",
            "additional_requirements": "安静，适合聊天"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/find_meetspot",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.text:
            try:
                result = response.json()
                print(f"JSON响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                print(f"非JSON响应: {response.text[:1000]}")
        else:
            print("空响应")
            
    except Exception as e:
        print(f"❌ POST请求失败: {e}")
    
    # 测试其他可能的路径
    test_paths = [
        "/api/health",
        "/api/status", 
        "/api/test",
        "/docs",
        "/openapi.json"
    ]
    
    print(f"\n5️⃣ 测试其他API路径:")
    for path in test_paths:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            print(f"{path}: {response.status_code} - {response.text[:100] if response.text else 'Empty'}")
        except Exception as e:
            print(f"{path}: 失败 - {e}")

def check_vercel_logs():
    print(f"\n6️⃣ 检查可能的问题:")
    print("- API 入口点是否正确加载 web_server.py")
    print("- 依赖是否完整安装")
    print("- 环境变量是否正确设置")
    print("- Python 路径和模块导入是否正常")
    print("- Vercel 函数是否超时或内存不足")
    
    print(f"\n📝 建议检查:")
    print("1. 查看 Vercel 部署日志")
    print("2. 检查 api/index.py 是否正确导入")
    print("3. 验证 requirements.txt 依赖")
    print("4. 确认环境变量设置")

if __name__ == "__main__":
    test_api_endpoints()
    check_vercel_logs()
