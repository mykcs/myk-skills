# Astro 反模式扫描与修复报告

## 项目信息
- **项目路径**: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-15/anti-pattern-scan/without_skill/mock-repo`
- **Astro 版本**: `^5.0.0`
- **扫描日期**: 2026-05-15

## 扫描范围
- `src/pages/index.astro`
- `src/layouts/Layout.astro`
- `src/components/Gallery.astro`
- `astro.config.mjs`
- `package.json`

## 发现的问题与修复

### 1. `index.astro` — `Astro.glob()` 已弃用（P0）
- **问题**: `Astro.glob()` 在 Astro 5.x 中已被标记为弃用，推荐使用 `import.meta.glob()` 替代。
- **修复**: 将 `Astro.glob('./posts/*.md')` 替换为 `Object.values(await import.meta.glob('./posts/*.md', { eager: true }))`。

### 2. `index.astro` — `<ViewTransitions />` 导入路径过时（P0）
- **问题**: `import { ViewTransitions } from 'astro:transitions'` 是旧写法。Astro 5.x 中推荐使用 `ClientRouter`（或保持 `ViewTransitions` 但需注意其已重命名为 `ClientRouter`）。
- **修复**: 将导入改为 `import { ClientRouter } from 'astro:transitions'` 并将组件标签改为 `<ClientRouter />`。

### 3. `index.astro` — `define:vars` 与 `<html>` 根元素嵌套问题（P1）
- **问题**: 页面中直接书写了 `<html>` 根元素，且 `<Layout>` 被嵌套在 `<html>` 内部，导致最终输出出现嵌套的 `<html>` 标签（Layout 本身已包含 `<html>`）。
- **修复**: 移除页面中的 `<html>`、`<head>` 标签，让 `Layout.astro` 作为唯一根元素包裹内容。

### 4. `Layout.astro` — 缺少 `<meta name="viewport">`（P1）
- **问题**: 现代网站必须在 `<head>` 中包含 viewport meta 标签，否则移动端显示异常。
- **修复**: 在 `<head>` 中添加 `<meta name="viewport" content="width=device-width, initial-scale=1.0">`。

### 5. `Gallery.astro` — `format` prop 已弃用（P1）
- **问题**: `<Image />` 组件上的 `format` prop 在 Astro 5.x 中已弃用，推荐使用 `formats`（在 `astro.config.mjs` 中配置）或 ` Picture` 组件来提供多格式回退。
- **修复**: 移除 `format="webp"` 和 `format="avif"`，改为在 `astro.config.mjs` 中统一配置图片格式策略。同时修正了第二处 `Image` 的 `alt` 描述。

### 6. `astro.config.mjs` — 图片格式策略缺失（P1）
- **问题**: 未在配置中声明图片输出格式，导致无法利用 Astro 的自动格式优化。
- **修复**: 在 `defineConfig` 中添加 `image: { formats: ['webp', 'avif'] }`。

## 修改文件清单
| 文件 | 修改类型 |
|------|---------|
| `src/pages/index.astro` | 重写：移除嵌套 `<html>`，替换 `Astro.glob`，替换 `ViewTransitions` |
| `src/layouts/Layout.astro` | 编辑：添加 viewport meta |
| `src/components/Gallery.astro` | 编辑：移除 `format` prop |
| `astro.config.mjs` | 编辑：添加 `image.formats` 配置 |

## 构建验证
- **命令**: `npm run build`
- **结果**: 成功（1 page built, 2 optimized images generated）

## 备注
- 未发现 `@astrojs/tailwind` 配置异常，当前使用 Tailwind CSS v3，若需升级至 v4 可另行处理。
- 未发现其他明显过时语法（如旧版 `getStaticPaths` 用法、已移除的 `Astro.canonicalURL` 等）。
