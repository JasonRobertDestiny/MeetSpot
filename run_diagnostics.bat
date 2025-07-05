@echo off
echo ===== MeetSpot Vercel 部署诊断工具 =====
echo.

REM 检查Python是否安装
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo 错误：未检测到Python安装。请安装Python后再运行此脚本。
  exit /b 1
)

REM 检查诊断脚本是否存在
if not exist diagnose_vercel_deployment.py (
  echo 错误：未找到诊断脚本(diagnose_vercel_deployment.py)
  exit /b 1
)

REM 询问用户Vercel部署URL
set /p vercel_url="请输入Vercel部署URL [https://meetspotagent.vercel.app]: "

REM 如果用户未输入，使用默认URL
if "%vercel_url%"=="" set vercel_url=https://meetspotagent.vercel.app

echo.
echo 正在诊断 %vercel_url% ...
echo.

REM 运行诊断脚本
python diagnose_vercel_deployment.py %vercel_url%

echo.
echo 诊断完成！
echo.

pause
