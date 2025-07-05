#!/bin/bash
# Vercel环境变量配置脚本

echo "📝 配置Vercel环境变量..."

# 检查是否安装了vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI未安装"
    echo "请先安装: npm i -g vercel"
    echo "或使用网页版: https://vercel.com/dashboard"
    exit 1
fi

echo "🔧 添加高德地图API密钥..."
vercel env add AMAP_API_KEY production <<< "041db813f69a2424f234fade1e3b3605"
vercel env add AMAP_API_KEY preview <<< "041db813f69a2424f234fade1e3b3605"
vercel env add AMAP_API_KEY development <<< "041db813f69a2424f234fade1e3b3605"

echo "🔧 添加硅基流动API密钥..."
vercel env add SILICON_API_KEY production <<< "sk-omysgcreevtaaengykwkmqkreqmukmolgzexkwfnainhwttb"
vercel env add SILICON_API_KEY preview <<< "sk-omysgcreevtaaengykwkmqkreqmukmolgzexkwfnainhwttb"
vercel env add SILICON_API_KEY development <<< "sk-omysgcreevtaaengykwkmqkreqmukmolgzexkwfnainhwttb"

echo "✅ 环境变量配置完成"
echo "🚀 正在触发重新部署..."
vercel --prod

echo "🎉 部署完成！"
