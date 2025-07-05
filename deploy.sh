#!/bin/bash

echo "===== MeetSpot Vercel 部署推送助手 ====="
echo

# 确定用户是否要推送到 GitHub
read -p "是否要推送更改到 GitHub? (y/n): " push_confirm
if [ "$push_confirm" != "y" ]; then
  echo "操作已取消"
  exit 0
fi

# 询问提交信息
read -p "请输入提交信息 [修复: Vercel部署配置更新]: " commit_message
if [ -z "$commit_message" ]; then
  commit_message="修复: Vercel部署配置更新"
fi

echo
echo "将推送以下关键文件:"
echo " - requirements.txt (依赖更新)"
echo " - vercel.json (部署配置)"
echo " - api/index.py (Vercel入口点)"
echo " - diagnose_vercel_deployment.py (部署诊断工具)"
echo " - verify_deployment.py (部署验证)"
echo " - VERCEL_DEPLOYMENT_CHECKLIST.md (部署清单)"
echo " - run_diagnostics.bat/sh (诊断脚本)"
echo

read -p "确认继续? (y/n): " final_confirm
if [ "$final_confirm" != "y" ]; then
  echo "操作已取消"
  exit 0
fi

echo
echo "正在添加文件..."
git add requirements.txt vercel.json api/index.py diagnose_vercel_deployment.py verify_deployment.py VERCEL_DEPLOYMENT_CHECKLIST.md run_diagnostics.bat run_diagnostics.sh

echo
echo "正在提交更改..."
git commit -m "$commit_message"

echo
echo "正在推送到GitHub..."
git push origin main

echo
echo "推送完成！请检查 Vercel 控制台确认部署状态。"
echo
