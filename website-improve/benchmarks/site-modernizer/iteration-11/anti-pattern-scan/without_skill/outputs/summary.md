# Astro 反模式扫描与修复报告

## 项目信息
- 项目路径: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-11/anti-pattern-scan/without_skill/mock-repo/`
- Astro 版本: `^5.0.0`
- Tailwind 版本: `^3.4.0` (使用 `@astrojs/tailwind` 集成)

## 扫描方法
1. 运行 `astro build` 捕获构建时弃用警告
2. 运行 `astro check` 获取 TypeScript 诊断信息
3. 对照 Astro v5/v6 官方升级文档（Context7）验证反模式

## 发现的问题

### 1. `Astro.glob()` 已弃用 (P0)
- **位置**: `src/pages/index.astro:5`
- **问题**: `const posts = await Astro.glob('./posts/*.md');`
- **影响**: Astro v5 中 `Astro.glob` 已被标记为弃用，将在未来主版本中移除
- **修复**: 替换为 `Object.values(import.meta.glob('./posts/*.md', { eager: true }))`
- **注意**: `import.meta.glob` 返回对象，需用 `Object.values()` 转为数组；`eager: true` 保持同步行为

### 2. `<ViewTransitions />` 已弃用 (P0)
- **位置**: `src/pages/index.astro:3, 11`
- **问题**: `import { ViewTransitions } from 'astro:transitions';` 及 `<ViewTransitions />`
- **影响**: Astro v6 中 `ViewTransitions` 已被 `ClientRouter` 取代
- **修复**: 移除弃用组件（当前页面布局中未实际使用过渡效果，直接移除即可）

### 3. 页面存在多余的 `<html>` 包装 (P1)
- **位置**: `src/pages/index.astro`
- **问题**: 页面在 `<Layout>` 外又包裹了一层 `<html>`，而 Layout 本身已包含 `<html>` 结构
- **影响**: 导致嵌套 HTML 文档结构，可能引发 hydration 和 SEO 问题
- **修复**: 移除外层 `<html>`、`<head>`，直接以 `<Layout>` 作为根元素

### 4. `define:vars` 使用正确 (OK)
- **位置**: `src/pages/index.astro`
- **状态**: `define:vars` 在 Astro v5/v6 中仍有效，无需修改

### 5. Image 组件 `format` 属性 (P2 - 需关注)
- **位置**: `src/components/Gallery.astro`
- **问题**: `<Image format="webp" ... />` 和 `<Image format="avif" ... />`
- **说明**: Astro v6 默认在指定 width/height 时自动裁剪，`format` 属性在特定场景下（如 SVG）需要条件判断。当前用法在 v5 中仍有效，但升级到 v6 时需注意 SVG 转换问题。

### 6. Tailwind v3 + `@astrojs/tailwind` 集成 (P2 - 建议升级)
- **位置**: `package.json`, `astro.config.mjs`
- **问题**: 使用 `@astrojs/tailwind` + `tailwindcss@3`
- **说明**: Astro v5.2+ 推荐使用 Tailwind v4 配合 `@tailwindcss/vite` 插件。当前为 v3 配置，属于遗留但非错误。

## 修复操作

| 文件 | 修改内容 |
|------|---------|
| `src/pages/index.astro` | `Astro.glob` → `import.meta.glob` + `Object.values` |
| `src/pages/index.astro` | 移除弃用的 `<ViewTransitions />` 及其 import |
| `src/pages/index.astro` | 移除多余的 `<html>` / `<head>` 包装，以 `<Layout>` 为根 |

## 验证结果

- `astro check`: 0 errors, 0 warnings, 0 hints
- `astro build`: 构建成功，无弃用警告

## 剩余建议 (未自动修复)

1. **Tailwind 升级**: 考虑从 v3 升级到 v4，移除 `@astrojs/tailwind` 并改用 `@tailwindcss/vite`
2. **Image format 审查**: 若 `Gallery.astro` 中的图片可能包含 SVG，需为 `format` 属性添加条件判断
