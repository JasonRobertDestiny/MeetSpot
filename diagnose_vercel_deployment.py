#!/usr/bin/env python3
"""
MeetSpot Vercel 部署诊断工具
用于检查和诊断 Vercel 部署中的具体错误
"""

import os
import json
import sys
import requests
import time
from urllib.parse import urljoin
import traceback

# 默认 Vercel 部署 URL
DEFAULT_BASE_URL = "https://meetspotagent.vercel.app"

def print_section(title):
    """打印带格式的章节标题"""
    print("\n" + "=" * 50)
    print(f"📌 {title}")
    print("=" * 50)

def test_endpoint(base_url, endpoint, description, method="GET", data=None, timeout=10, verbose=True):
    """测试单个端点，返回响应对象和是否成功"""
    url = urljoin(base_url, endpoint)
    try:
        if verbose:
            print(f"\n🔍 测试 {description}")
            print(f"URL: {url}")
            print(f"方法: {method}")
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            if data and verbose:
                print(f"请求数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
            response = requests.post(url, json=data, timeout=timeout)
        else:
            if verbose:
                print(f"❌ 不支持的方法: {method}")
            return None, False
        
        if verbose:
            print(f"状态码: {response.status_code}")
        
        # 尝试解析为JSON
        response_data = None
        try:
            response_data = response.json()
            if verbose:
                print(f"JSON响应: {json.dumps(response_data, ensure_ascii=False, indent=2)[:300]}...")
        except:
            if verbose:
                print(f"非JSON响应，长度: {len(response.text)} 字符")
                if len(response.text) < 500:
                    print(f"响应内容: {response.text[:500]}")
        
        success = 200 <= response.status_code < 300
        if not success and verbose:
            print(f"❌ 请求失败: {response.status_code}")
        
        return response, success
    
    except Exception as e:
        if verbose:
            print(f"❌ 请求异常: {str(e)}")
            traceback.print_exc()
        return None, False

def test_find_meetspot_api(base_url):
    """测试会面点查找API"""
    endpoint = "/api/find_meetspot"
    data = {
        "locations": [
            {"name": "张三", "address": "北京市海淀区中关村"},
            {"name": "李四", "address": "北京市朝阳区国贸"}
        ],
        "preference": "咖啡厅"
    }
    
    print_section("测试会面点查找API")
    response, success = test_endpoint(base_url, endpoint, "会面点查找API", method="POST", data=data)
    
    if success:
        print("✅ 会面点查找API测试成功")
        
        # 分析响应结构
        try:
            data = response.json()
            if "recommendations" in data:
                print(f"✅ 找到 {len(data['recommendations'])} 个推荐结果")
                
                # 打印第一个推荐结果的详情
                if data["recommendations"]:
                    first = data["recommendations"][0]
                    print(f"📍 首个推荐: {first.get('name', 'N/A')}")
                    print(f"   地址: {first.get('address', 'N/A')}")
                    print(f"   评分: {first.get('rating', 'N/A')}")
            else:
                print("⚠️ 响应缺少 'recommendations' 字段")
        except Exception as e:
            print(f"❌ 解析响应失败: {str(e)}")
    else:
        print("❌ 会面点查找API测试失败")
        if response:
            print(f"状态码: {response.status_code}")
            try:
                print(f"错误详情: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            except:
                print(f"响应内容: {response.text[:500]}")

def diagnose_api_issues(base_url):
    """诊断API相关问题"""
    print_section("API诊断")
    
    # 1. 检查API基本状态
    _, status_success = test_endpoint(base_url, "/api/status", "API状态检查", verbose=False)
    
    if status_success:
        print("✅ API基本状态正常")
    else:
        print("❌ API基本状态异常，检查入口点配置")
    
    # 2. 诊断find_meetspot接口
    test_find_meetspot_api(base_url)

def diagnose_static_files(base_url):
    """诊断静态文件问题"""
    print_section("静态文件诊断")
    
    critical_files = [
        ("/", "首页"),
        ("/workspace/meetspot_finder.html", "会面点查找页面"),
        ("/docs/logo.png", "Logo图片")
    ]
    
    for path, desc in critical_files:
        _, success = test_endpoint(base_url, path, desc, verbose=False)
        print(f"{'✅' if success else '❌'} {desc}: {path}")

def run_complete_diagnostics(base_url=DEFAULT_BASE_URL):
    """运行完整诊断"""
    print_section("MeetSpot Vercel 部署诊断")
    print(f"🌐 目标URL: {base_url}")
    print(f"🕒 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 基本连接测试
    print_section("基本连接测试")
    response, success = test_endpoint(base_url, "/", "首页访问测试", verbose=False)
    
    if success:
        print("✅ 基本连接正常")
        print(f"状态码: {response.status_code}")
        print(f"响应大小: {len(response.text)} 字符")
    else:
        print("❌ 基本连接失败，部署可能有问题")
        if response:
            print(f"状态码: {response.status_code}")
        return
    
    # 2. 静态文件诊断
    diagnose_static_files(base_url)
    
    # 3. API诊断
    diagnose_api_issues(base_url)
    
    # 4. 综合评估
    print_section("诊断总结")
    print("以上诊断结果提供了部署状况的快照")
    print("如果发现错误，请检查：")
    print("1. Vercel环境变量是否正确配置")
    print("2. requirements.txt是否包含所有依赖")
    print("3. vercel.json中的路由和构建配置")
    print("4. api/index.py是否正确导入web_server.py")
    print("5. Vercel部署日志中的具体错误信息")

if __name__ == "__main__":
    base_url = DEFAULT_BASE_URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    run_complete_diagnostics(base_url)
