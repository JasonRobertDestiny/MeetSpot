#!/usr/bin/env python3
"""
测试完整的推荐功能 - 模拟前端表单提交
"""
import requests
import json
import time

BASE_URL = "https://meetspotagent.vercel.app"

def test_recommendation():
    print("🎯 测试 MeetSpot 完整推荐功能")
    print("=" * 50)
    
    # 模拟前端发送的推荐请求
    test_data = {
        "locations": [
            "北京市朝阳区",
            "北京市海淀区"
        ],
        "keywords": "咖啡厅",
        "user_requirements": "安静，适合聊天，有WiFi",
        "theme": "coffee"
    }
    
    try:
        print(f"🌐 调用推荐API: {BASE_URL}/api/find_meetspot")
        print(f"📋 请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/find_meetspot",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ 请求耗时: {processing_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 推荐成功!")
            print(f"📄 响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 检查是否包含html_url
            if "html_url" in result:
                html_url = result["html_url"]
                full_url = f"{BASE_URL}{html_url}"
                print(f"🌐 推荐结果页面: {full_url}")
                
                # 尝试访问结果页面
                try:
                    page_response = requests.get(full_url, timeout=10)
                    if page_response.status_code == 200:
                        print(f"✅ 推荐结果页面可正常访问")
                        if "MeetSpot" in page_response.text:
                            print(f"✅ 页面内容正常")
                        else:
                            print(f"⚠️ 页面内容可能有问题")
                    else:
                        print(f"❌ 推荐结果页面无法访问: {page_response.status_code}")
                except Exception as e:
                    print(f"❌ 访问推荐结果页面失败: {e}")
            else:
                print(f"⚠️ 响应中缺少 html_url 字段")
                
        else:
            print(f"❌ 推荐失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ 错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ 错误响应: {response.text}")
                
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（超过30秒）")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_recommendation()
