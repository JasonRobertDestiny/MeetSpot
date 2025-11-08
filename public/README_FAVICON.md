# Favicon 设置说明

## 当前状态
MeetSpot目前缺少favicon（网站图标）。

## 如何添加Favicon

### 方法1: 使用在线工具生成
1. 访问 https://realfavicongenerator.net/
2. 上传品牌Logo（推荐至少 512x512 px）
3. 自动生成多种尺寸的favicon
4. 下载并解压到 `public/` 目录

### 方法2: 手动创建
创建以下文件到 `public/` 目录：
- favicon.ico (16x16, 32x32)
- favicon-16x16.png
- favicon-32x32.png
- apple-touch-icon.png (180x180)
- android-chrome-192x192.png
- android-chrome-512x512.png

### 方法3: 使用SVG (推荐)
创建 `public/favicon.svg`，现代浏览器支持矢量图标。

## 在HTML中引用

添加到 `<head>` 标签中：

```html
<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

## 设计建议

推荐使用：
- 颜色：紫色渐变 (#667eea to #764ba2) 匹配品牌
- 图标：地图标记 + 人群图标
- 风格：简约、现代

