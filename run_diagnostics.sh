#!/bin/bash

echo "===== MeetSpot Vercel 部署诊断工具 ====="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：未检测到Python安装。请安装Python后再运行此脚本。"
    exit 1
fi

# 检查诊断脚本是否存在
if [ ! -f "diagnose_vercel_deployment.py" ]; then
    echo "错误：未找到诊断脚本(diagnose_vercel_deployment.py)"
    exit 1
fi

# 询问用户Vercel部署URL
read -p "请输入Vercel部署URL [https://meetspotagent.vercel.app]: " vercel_url

# 如果用户未输入，使用默认URL
if [ -z "$vercel_url" ]; then
    vercel_url="https://meetspotagent.vercel.app"
fi

echo
echo "正在诊断 $vercel_url ..."
echo

# 运行诊断脚本
python3 diagnose_vercel_deployment.py "$vercel_url"

echo
echo "诊断完成！"
echo
