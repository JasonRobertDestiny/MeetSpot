#!/bin/bash

echo "===== MeetSpot Vercel 优化部署推送助手 ====="
echo

# 确定用户是否要推送到 GitHub
read -p "是否要推送更改到 GitHub? (y/n): " push_confirm
if [ "$push_confirm" != "y" ]; then
  echo "操作已取消"
  exit 0
fi

# 询问提交信息
read -p "请输入提交信息 [优化: Vercel 部署包大小优化]: " commit_message
if [ -z "$commit_message" ]; then
  commit_message="优化: Vercel 部署包大小优化"
fi

echo
echo "将推送以下关键文件:"
echo " - requirements.txt (精简依赖)"
echo " - vercel.json (优化构建配置)"
echo " - api/index.py (优化入口点)"
echo " - .vercelignore (更新忽略文件)"
echo

read -p "确认继续? (y/n): " final_confirm
if [ "$final_confirm" != "y" ]; then
  echo "操作已取消"
  exit 0
fi

echo
echo "正在添加文件..."
git add requirements.txt vercel.json api/index.py .vercelignore

echo
echo "正在提交更改..."
git commit -m "$commit_message"

echo
echo "正在推送到GitHub..."
git push origin main

echo
echo "推送完成！请检查 Vercel 控制台确认部署状态。"
echo
