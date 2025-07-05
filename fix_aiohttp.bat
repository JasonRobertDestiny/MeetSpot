@echo off
chcp 65001 >nul
echo ===== MeetSpot aiohttp 修复推送助手 =====
echo.

REM 确定用户是否要推送到 GitHub
set /p push_confirm="是否要推送 aiohttp 修复到 GitHub? (y/n): "
if /i "%push_confirm%" NEQ "y" (
  echo 操作已取消
  goto :end
)

REM 询问提交信息
set /p commit_message="请输入提交信息 [修复: 移除 aiohttp 依赖解决 Python 3.12 兼容性问题]: "
if "%commit_message%"=="" set commit_message=修复: 移除 aiohttp 依赖解决 Python 3.12 兼容性问题

echo.
echo 将推送以下修复文件:
echo  - requirements.txt (移除 aiohttp 和 folium)
echo  - app/tool/meetspot_recommender.py (使用 httpx 替代 aiohttp)
echo  - app/tool/bing_search.py (使用 httpx 替代 aiohttp)
echo.

set /p final_confirm="确认继续? (y/n): "
if /i "%final_confirm%" NEQ "y" (
  echo 操作已取消
  goto :end
)

echo.
echo 正在添加文件...
git add requirements.txt app/tool/meetspot_recommender.py app/tool/bing_search.py

echo.
echo 正在提交更改...
git commit -m "%commit_message%"

echo.
echo 正在推送到GitHub...
git push origin main

echo.
echo 推送完成！请检查 Vercel 控制台确认部署状态。
echo 注意：这次移除了 aiohttp 依赖以解决 Python 3.12 编译问题。
echo.

:end
pause
