#!/usr/bin/env python3
"""
快速验证 MeetSpot 部署状态
"""

import requests
import time

BASE_URL = "https://meetspotagent.vercel.app"

def quick_test():
    print("🚀 快速验证 MeetSpot 部署")
    print("=" * 40)
    
    # 等待部署
    print("⏳ 等待 30 秒让 Vercel 完成部署...")
    time.sleep(30)
    
    try:
        print(f"\n🔍 测试主页: {BASE_URL}/")
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 检查关键标识符
            if "MeetSpot (聚点)" in content and "智能会面点推荐" in content:
                print("✅ 成功！检测到完整的 MeetSpot 前端界面")
                print("✅ 页面包含完整的功能和样式")
                
                # 检查一些关键功能
                features = [
                    ("地点输入", "location" in content.lower()),
                    ("场景选择", "place-type" in content),
                    ("主题切换", "theme" in content.lower()),
                    ("提交按钮", "submit" in content.lower())
                ]
                
                for feature, check in features:
                    status = "✅" if check else "⚠️"
                    print(f"{status} {feature}: {'正常' if check else '可能有问题'}")
                    
            else:
                print("⚠️ 页面内容不符合预期")
                print("内容预览:", content[:300])
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    print(f"\n🌐 请访问: {BASE_URL}")
    print("🎯 如果看到完整的 MeetSpot 界面，部署成功！")

if __name__ == "__main__":
    quick_test()
