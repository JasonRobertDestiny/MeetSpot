# MeetSpot Vercel 部署检查清单

## 部署前准备

1. 检查 `requirements.txt` 是否包含所有必要依赖
2. 确保 `vercel.json` 配置正确
   - 包含所有必要的静态资源目录
   - 路由配置正确
   - 入口点设置为 `api/index.py`
3. 确保 `api/index.py` 能正确导入 `web_server.py`

## Vercel 环境变量配置

请确保在 Vercel 控制台中设置了以下环境变量：

- `AMAP_KEY` - 高德地图 API 密钥
- `MANUS_API_KEY` - Manus API 密钥 (如果使用)
- `DEBUG` - 设置为 `true` 以启用调试模式

## 部署步骤

1. 确保所有更改已提交到 Git 仓库
   ```
   git add .
   git commit -m "准备 Vercel 部署"
   ```

2. 推送到 GitHub
   ```
   git push origin main
   ```

3. 登录 Vercel 并导入项目（如果尚未导入）

4. 配置环境变量

5. 重新部署项目
   - 在 Vercel 控制台中点击 "Redeploy"
   - 或进行小改动后再次推送

## 部署后验证

1. 运行诊断脚本
   ```
   # Windows
   run_diagnostics.bat

   # Linux/Mac
   ./run_diagnostics.sh
   ```

2. 检查以下端点是否正常：
   - 首页：`/`
   - 健康检查：`/health`
   - API 状态：`/api/status`
   - 会面点查找页面：`/workspace/meetspot_finder.html`
   - 会面点查找 API：`/api/find_meetspot`

## 常见问题

### 1. API 报 500 错误

- 检查 Vercel 日志中的详细错误信息
- 确认环境变量是否正确设置
- 检查依赖是否完整

### 2. 静态资源找不到

- 确认 `vercel.json` 中的静态资源目录和路由配置
- 检查文件是否存在于正确的目录中

### 3. 应用无法启动

- 检查 `api/index.py` 中的导入逻辑
- 确认 `web_server.py` 文件存在且无语法错误
- 查看 Vercel 构建日志寻找线索

## 重要链接

- [Vercel 控制台](https://vercel.com/dashboard)
- [Vercel Python 文档](https://vercel.com/docs/functions/runtimes/python)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
