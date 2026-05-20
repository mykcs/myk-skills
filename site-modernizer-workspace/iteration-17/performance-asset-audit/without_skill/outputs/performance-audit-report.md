# 性能审计报告

## 项目信息
- **项目路径**: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-17/performance-asset-audit/without_skill/mock-repo`
- **框架**: Astro 5.x (Static)
- **审计日期**: 2026-05-15

## Lighthouse 评分（优化前）

| 指标 | 分数 |
|------|------|
| Performance | 95 |
| Accessibility | 94 |
| Best Practices | 88 |
| SEO | 91 |

## 发现的问题

### 1. 阻塞渲染的请求 (Render-blocking Requests)
- **问题**: Google Fonts CSS (`Inter`) 阻塞了首屏渲染，导致 LCP 延迟约 1390ms。
- **影响**: FCP 和 LCP 均达到 2.0s，Speed Index 4.5s。
- **修复**: 将字体 CSS 改为 `media="print" onload="this.media='all'"` 异步加载，并添加 `<noscript>` 回退。

### 2. 缺少 viewport meta 标签
- **问题**: `<head>` 中未声明 `viewport`，导致移动端缩放和布局异常，Lighthouse 扣分。
- **修复**: 在 `Layout.astro` 的 `<head>` 中添加了 `<meta name="viewport" content="width=device-width, initial-scale=1.0">`。

### 3. 缺少 meta description
- **问题**: 页面没有 `<meta name="description">`，影响 SEO 和社交分享。
- **修复**: 在 `Layout.astro` 中添加了 description meta 标签。

### 4. 图片缺少 width/height 属性
- **问题**: 远程图片 `<img src="https://via.placeholder.com/800x600">` 没有显式的 `width` 和 `height`，可能导致布局偏移 (CLS)。
- **修复**: 为该图片添加了 `width="800" height="600"` 以及 `loading="lazy" decoding="async"`。

### 5. 非首屏图片未懒加载
- **问题**: Gallery 组件中所有 4 张图片均使用 `loading="eager"`，其中 3 张缩略图不在首屏，却优先加载，浪费带宽。
- **修复**: 将 3 张缩略图的 `loading` 属性改为 `"lazy"`，仅保留 Hero 图为 `eager`。

### 6. 页面缺少 main 地标 (landmark)
- **问题**: 页面内容直接放在 `<body>` 下，没有 `<main>` 标签，影响可访问性 (Accessibility)。
- **修复**: 在 `Layout.astro` 中用 `<main>` 包裹 `<slot />`。

### 7. 冗余依赖
- **问题**: `package.json` 中声明了 `lodash`、`moment`、`jquery`，但源代码中并未使用它们。这些包会增加 `node_modules` 体积和潜在的构建时间。
- **建议**: 建议移除未使用的依赖以减小项目体积。

### 8. 图片比例异常 (Image Aspect Ratio)
- **问题**: Lighthouse 检测到图片显示比例与实际比例不符。这是因为 `hero.png` 是一个 1x1 的占位图，但代码中声明了 800x600 和 400x300 的尺寸。
- **说明**: 在实际项目中，请替换为真实的高分辨率图片，Astro 的 `<Image />` 组件会自动生成适配的 WebP 格式。

## 已执行的修改

| 文件 | 修改内容 |
|------|---------|
| `src/layouts/Layout.astro` | 添加 viewport、description、异步加载字体、`<main>` 包裹 |
| `src/pages/index.astro` | 为远程图片添加 width/height/lazy 属性 |
| `src/components/Gallery.astro` | 缩略图改为 `loading="lazy"` |

## 后续建议

1. **移除未使用的依赖**: 运行 `npm uninstall lodash moment jquery`。
2. **替换真实图片**: 将 `src/assets/hero.png` 替换为实际的高分辨率图片，Astro 会自动优化。
3. **启用资源缓存**: 部署时配置 CDN / Web 服务器的长期缓存策略（`Cache-Control: max-age=31536000, immutable`），因为当前 Lighthouse 报告本地资源的 cache lifetime 为 0ms。
4. **重新运行 Lighthouse**: 在应用上述修复后，建议重新运行 Lighthouse 验证性能提升。
