# MeetSpot Render 部署指南

## 快速部署步骤

### 1. 推送代码到 GitHub
```bash
git push origin main
```

### 2. 在 Render 上部署

1. 访问 [render.com](https://render.com) 并登录
2. 点击 **"New +"** → **"Web Service"**
3. 连接你的 GitHub 仓库：`JasonRobertDestiny/MeetSpot`
4. Render 会自动检测 `render.yaml` 配置文件
5. 在环境变量部分，添加：
   - **AMAP_API_KEY**: 你的高德地图 API 密钥（必需）

### 3. 点击 "Create Web Service"

部署完成后，你的应用将在以下地址可用：
```
https://meetspot.onrender.com
```

## 获取高德地图 API Key

如果还没有 API Key：
1. 访问 [lbs.amap.com](https://lbs.amap.com)
2. 注册/登录账号
3. 创建新应用
4. 获取 Web 服务 API Key

## 注意事项

- Render 免费套餐会在 15 分钟无活动后休眠
- 首次访问可能需要等待 30-50 秒启动
- 建议使用新加坡区域（已在 render.yaml 中配置）

## 故障排查

如果部署失败，检查：
1. AMAP_API_KEY 是否正确设置
2. 查看 Render 控制台的部署日志
3. 确保 GitHub 仓库是最新的

## 本地测试

部署前可以本地测试：
```bash
# 复制配置文件
cp config/config.toml.example config/config.toml

# 编辑 config.toml，添加你的 API Key

# 启动服务
python web_server.py
```

访问 http://localhost:8000 测试
