#!/usr/bin/env python3
"""
简单的 Vercel 部署检测脚本
"""

import requests
import time

def check_vercel_deployment():
    """检查 Vercel 部署状态"""
    base_url = "https://meetspotagent.vercel.app"
    
    print("🔍 检查 Vercel 部署状态...")
    print(f"🌐 目标URL: {base_url}")
    
    # 等待部署完成
    print("⏳ 等待 60 秒，确保部署完成...")
    time.sleep(60)
    
    try:
        # 测试健康检查
        print("\n📡 测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ 健康检查成功: {response.status_code}")
            try:
                data = response.json()
                print(f"📊 响应数据: {data}")
            except:
                print("⚠️ 响应不是JSON格式")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
        
        # 测试API状态
        print("\n📡 测试API状态...")
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print(f"✅ API状态检查成功: {response.status_code}")
            try:
                data = response.json()
                print(f"📊 API响应: {data}")
            except:
                print("⚠️ API响应不是JSON格式")
        else:
            print(f"❌ API状态检查失败: {response.status_code}")
        
        # 测试会面点API
        print("\n📡 测试会面点查找API...")
        test_data = {
            "locations": [
                {"name": "张三", "address": "北京市海淀区中关村"},
                {"name": "李四", "address": "北京市朝阳区国贸"}
            ],
            "preference": "咖啡厅"
        }
        
        response = requests.post(f"{base_url}/api/find_meetspot", json=test_data, timeout=15)
        if response.status_code == 200:
            print(f"✅ 会面点API测试成功: {response.status_code}")
            try:
                data = response.json()
                if "recommendations" in data:
                    print(f"📍 找到 {len(data['recommendations'])} 个推荐结果")
                    for i, rec in enumerate(data["recommendations"][:2]):
                        print(f"  {i+1}. {rec.get('name', 'N/A')} - {rec.get('address', 'N/A')}")
                else:
                    print(f"📊 API响应: {data}")
            except Exception as e:
                print(f"⚠️ 解析响应失败: {e}")
                print(f"原始响应: {response.text[:200]}...")
        else:
            print(f"❌ 会面点API测试失败: {response.status_code}")
            print(f"错误响应: {response.text[:200]}...")
        
        print("\n" + "="*50)
        print("🎯 检测完成!")
        print(f"🌐 访问地址: {base_url}")
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")

if __name__ == "__main__":
    check_vercel_deployment()
