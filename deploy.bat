@echo off
echo ===== MeetSpot Vercel 部署推送助手 =====
echo.

REM 确定用户是否要推送到 GitHub
set /p push_confirm="是否要推送更改到 GitHub? (y/n): "
if /i "%push_confirm%" NEQ "y" (
  echo 操作已取消
  goto :end
)

REM 询问提交信息
set /p commit_message="请输入提交信息 [修复: Vercel部署配置更新]: "
if "%commit_message%"=="" set commit_message=修复: Vercel部署配置更新

echo.
echo 将推送以下关键文件:
echo  - requirements.txt (依赖更新)
echo  - vercel.json (部署配置)
echo  - api/index.py (Vercel入口点)
echo  - diagnose_vercel_deployment.py (部署诊断工具)
echo  - verify_deployment.py (部署验证)
echo  - VERCEL_DEPLOYMENT_CHECKLIST.md (部署清单)
echo  - run_diagnostics.bat/sh (诊断脚本)
echo.

set /p final_confirm="确认继续? (y/n): "
if /i "%final_confirm%" NEQ "y" (
  echo 操作已取消
  goto :end
)

echo.
echo 正在添加文件...
git add requirements.txt vercel.json api/index.py diagnose_vercel_deployment.py verify_deployment.py VERCEL_DEPLOYMENT_CHECKLIST.md run_diagnostics.bat run_diagnostics.sh

echo.
echo 正在提交更改...
git commit -m "%commit_message%"

echo.
echo 正在推送到GitHub...
git push origin main

echo.
echo 推送完成！请检查 Vercel 控制台确认部署状态。
echo.

:end
pause
