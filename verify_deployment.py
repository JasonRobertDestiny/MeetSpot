#!/usr/bin/env python3
"""
Vercel 部署验证脚本
检查 MeetSpot 在 Vercel 上的部署状态
"""

import requests
import time
import json
import sys
from urllib.parse import urljoin

# 默认 Vercel 部署 URL
DEFAULT_BASE_URL = "https://meetspotagent.vercel.app"

def test_endpoint(base_url, endpoint, description, method="GET", data=None, timeout=10):
    """测试单个端点"""
    url = urljoin(base_url, endpoint)
    try:
        print(f"\n🔍 测试 {description}")
        print(f"URL: {url}")
        print(f"方法: {method}")
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            if data:
                print(f"请求数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
            response = requests.post(url, json=data, timeout=timeout)
        else:
            print(f"❌ 不支持的方法: {method}")
            return
        
        print(f"状态码: {response.status_code}")
        
        # 尝试解析为JSON
        try:
            data = response.json()
            print(f"JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
            return data
        except ValueError:
            # 非JSON响应
            content = response.text[:300]
            print(f"内容预览: {content}...")
            
            # 检查是否为HTML
            if "<html" in content.lower():
                print("✅ 返回HTML内容")
                
                # 检查是否包含MeetSpot关键词
                if "MeetSpot" in response.text or "会面点" in response.text:
                    print("✅ 包含关键词: MeetSpot/会面点")
                else:
                    print("⚠️ 不包含关键词: MeetSpot/会面点")
            
            return response.text
            
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    
    return None

def test_find_meetspot_api(base_url):
    """测试会面点查找API"""
    print("\n🚀 测试会面点查找API (/api/find_meetspot)")
    
    # 测试数据
    test_data = {
        "locations": ["北京市朝阳区", "北京市海淀区"],
        "keywords": "咖啡馆",
        "user_requirements": "安静的地方，有插座",
        "theme": "默认"
    }
    
    start_time = time.time()
    result = test_endpoint(
        base_url, 
        "/api/find_meetspot", 
        "会面点查找API", 
        method="POST", 
        data=test_data,
        timeout=60  # 查找可能需要较长时间
    )
    duration = time.time() - start_time
    
    print(f"处理耗时: {duration:.2f}秒")
    
    # 分析结果
    if result:
        if isinstance(result, dict):
            # 检查是否包含预期字段
            if "status" in result:
                print(f"API状态: {result.get('status')}")
            
            # 检查是否包含链接
            if "html_url" in result:
                print(f"结果页面URL: {result.get('html_url')}")
                # 尝试访问结果页面
                try:
                    result_url = urljoin(base_url, result.get('html_url'))
                    print(f"尝试访问结果页面: {result_url}")
                    response = requests.get(result_url, timeout=10)
                    print(f"结果页面状态码: {response.status_code}")
                except Exception as e:
                    print(f"访问结果页面失败: {e}")
    
    return result

def main():
    """主函数"""
    # 使用命令行参数或默认URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = DEFAULT_BASE_URL
    
    # 确保base_url没有尾斜杠
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    
    print(f"🚀 MeetSpot Vercel 部署验证 ({base_url})")
    
    # 1. 测试健康检查
    test_endpoint(base_url, "/health", "健康检查")
    
    # 2. 测试首页
    test_endpoint(base_url, "/", "首页")
    
    # 3. 测试静态资源 - meetspot_finder.html
    test_endpoint(base_url, "/workspace/meetspot_finder.html", "会面点查找页面")
    
    # 4. 测试静态资源 - 图片
    test_endpoint(base_url, "/docs/logo.png", "Logo图片")
    
    # 5. 测试API状态
    test_endpoint(base_url, "/api/status", "API状态")
    
    # 6. 测试会面点查找API
    test_find_meetspot_api(base_url)
    
    print("\n" + "=" * 50)
    print("🎯 部署验证完成!")
    print(f"🌐 访问地址: {base_url}")

if __name__ == "__main__":
    main()
    
    # 1. 测试健康检查
    test_endpoint(base_url, "/health", "健康检查")
    
    # 2. 测试首页
    test_endpoint(base_url, "/", "首页")
    
    # 3. 测试静态资源 - meetspot_finder.html
    test_endpoint(base_url, "/workspace/meetspot_finder.html", "会面点查找页面")
    
    # 4. 测试静态资源 - 图片
    test_endpoint(base_url, "/docs/logo.png", "Logo图片")
    
    # 5. 测试API状态
    test_endpoint(base_url, "/api/status", "API状态")
    
    # 6. 测试会面点查找API
    test_find_meetspot_api(base_url)

if __name__ == "__main__":
    base_url = DEFAULT_BASE_URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    main()
    print("=" * 50)
    
    # 等待部署完成
    print("⏳ 等待 30 秒，确保部署完成...")
    time.sleep(30)
    
    # 测试各个端点
    endpoints = [
        ("/", "主页"),
        ("/health", "健康检查"),
        ("/api/status", "API状态"),
        ("/workspace/meetspot_finder.html", "前端页面")
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(base_url, endpoint, description)
    
    print("\n" + "=" * 50)
    print("🎯 部署验证完成!")
    print(f"🌐 访问地址: {base_url}")
