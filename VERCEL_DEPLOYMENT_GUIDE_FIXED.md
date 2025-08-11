# MeetSpot Vercel部署指南 - 环境变量修复版

## 🚨 重要修复说明

**问题**: 之前的部署失败是因为在vercel.json中错误地引用了不存在的secret。

**解决方案**: 
1. 已从vercel.json中移除环境变量配置
2. 环境变量必须在Vercel仪表板中手动设置

## 1. 准备工作

### 1.1 文件结构确认（已优化）
```
MeetSpot/
├── api/
│   └── index.py          # ✅ Vercel入口文件（已优化兼容性）
├── app/                  # 应用核心代码
├── public/              # 静态文件
├── workspace/           # 工作区文件
├── vercel.json          # ✅ Vercel配置（已移除环境变量引用）
├── requirements_vercel.txt  # Vercel依赖
└── README.md
```

### 1.2 代码优化说明
- ✅ `api/index.py` 已优化为支持完全在线环境运行
- ✅ 自动检测环境变量并创建最小化配置
- ✅ 支持无配置文件的Vercel部署模式
- ✅ 自动创建必要的工作目录结构
- ✅ vercel.json 已清理，不再包含环境变量引用

## 2. 部署步骤

### 2.1 推送修复到GitHub
```bash
git add .
git commit -m "修复Vercel部署环境变量配置问题"
git push origin main
```

### 2.2 在Vercel中重新部署
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 找到你的MeetSpot项目
3. 如果是新项目，点击 "New Project" 导入GitHub仓库

### 2.3 ⚠️ 环境变量设置（关键步骤）

**重要提醒：环境变量必须在Vercel仪表板中设置，不能在代码中定义！**

#### 步骤详解：
1. 进入项目的设置页面（Settings）
2. 点击左侧菜单的 "Environment Variables"
3. 点击 "Add New" 按钮
4. 填写环境变量：
   - **Name**: `AMAP_API_KEY`
   - **Value**: 你的高德地图API密钥（完整密钥，不是引用）
   - **Environments**: ✅ Production ✅ Preview ✅ Development
5. 点击 "Save" 保存

**❌ 错误的做法（导致之前部署失败）：**
```json
// 不要在vercel.json中这样写
{
  "env": {
    "AMAP_API_KEY": "@amap_api_key"  // ❌ 这会引用不存在的secret
  }
}
```

**✅ 正确的做法：**
- 在Vercel仪表板中直接设置环境变量
- 使用实际的API密钥值，不使用任何引用符号

### 2.4 触发重新部署
设置环境变量后，必须重新部署：
1. 回到项目的 "Deployments" 页面
2. 找到最新的部署记录
3. 点击右侧的 "..." 菜单
4. 选择 "Redeploy"
5. 确认重新部署

## 3. 验证部署成功

### 3.1 检查健康状态
访问：`https://your-project.vercel.app/health`

**期望返回（环境变量配置正确）：**
```json
{
  "status": "healthy",
  "timestamp": 1699123456.789,
  "config": {
    "amap_configured": true,      // ✅ 应该为true
    "full_features": false,
    "minimal_mode": true
  }
}
```

### 3.2 测试API文档
访问：`https://your-project.vercel.app/docs`
应该能看到完整的API文档界面。

### 3.3 测试推荐功能
使用POST请求测试：
```bash
curl -X POST "https://your-project.vercel.app/find-meetspot" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": ["北京三里屯", "北京国贸"],
    "keywords": "咖啡馆",
    "user_requirements": "安静的环境，适合聊天"
  }'
```

## 4. 故障排查

### 4.1 环境变量相关错误

#### 错误1: `Environment Variable "AMAP_API_KEY" references Secret "amap_api_key", which does not exist`
**原因**: vercel.json中包含了错误的环境变量引用
**解决**: 
- ✅ 已修复：vercel.json中已移除env配置
- 确保在Vercel仪表板中设置了环境变量

#### 错误2: `高德地图API密钥未配置`
**原因**: 环境变量未正确设置
**解决**:
1. 检查Vercel仪表板中的Environment Variables
2. 确保AMAP_API_KEY值正确且没有额外的空格
3. 确保环境变量应用到了Production环境

### 4.2 其他常见问题

#### 构建失败
- 检查 `requirements_vercel.txt` 文件是否存在
- 查看构建日志中的详细错误信息

#### 404错误
- 确保访问的是正确的端点
- 检查路由配置是否正确

### 4.3 调试工具
- 使用 `/health` 端点检查配置状态
- 使用 `/config` 端点查看API密钥配置状态（不暴露实际密钥）
- 查看Vercel控制台的运行时日志

## 5. 快速部署检查清单

- [ ] vercel.json 不包含env配置（已修复）
- [ ] 在Vercel仪表板中设置了AMAP_API_KEY环境变量
- [ ] 环境变量应用到了Production环境
- [ ] 代码已推送到GitHub
- [ ] 在Vercel中触发了重新部署
- [ ] `/health` 端点返回 `amap_configured: true`
- [ ] `/docs` 页面可以正常访问

## 6. 技术特性

### 6.1 自适应配置
- 自动检测Vercel环境
- 无config.toml时创建最小化配置
- 支持仅环境变量的运行模式

### 6.2 容错机制
- 优雅处理模块导入失败
- 静态文件挂载失败时的回退方案
- 完整的错误日志记录

### 6.3 性能优化
- 最小化依赖加载
- 冷启动时间优化
- 内存使用优化

---

**部署成功标志**: 
✅ `/health` 返回 `amap_configured: true`
✅ `/find-meetspot` API可以正常返回推荐结果
✅ HTML推荐页面可以正常生成和访问
