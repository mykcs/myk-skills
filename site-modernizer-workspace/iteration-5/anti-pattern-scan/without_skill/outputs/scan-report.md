# Astro 反模式扫描报告

> 项目：mock-anti-pattern-site
> 扫描日期：2026-05-14
> 扫描方式：无 Skill 基线测试（人工代码审查）
> Astro 版本：^5.0.0（package.json 声明）

---

## 执行摘要

| 类别 | 数量 | 风险等级 |
|------|------|----------|
| P0 - 必须修复（构建/运行时错误） | 2 | 高 |
| P1 - 强烈建议修复（性能/兼容性） | 3 | 中 |
| P2 - 建议优化（最佳实践） | 2 | 低 |

---

## P0 - 必须修复

### P0-1: `Astro.glob()` 已废弃 — 迁移到 `import.meta.glob()`

- **文件**：`src/pages/index.astro` 第 5 行
- **代码**：
  ```astro
  const posts = await Astro.glob('./posts/*.md');
  ```
- **问题**：`Astro.glob()` 在 Astro v3+ 中已标记为废弃，v5 中可能完全移除。
- **修复**：
  ```astro
  const posts = Object.values(await import.meta.glob('./posts/*.md', { eager: true }));
  ```
- **参考**：Astro 官方文档 — `Astro.glob` 迁移指南

### P0-2: `@astrojs/tailwind` v5 + Tailwind CSS v3 组合在 Astro v5 下不兼容

- **文件**：`package.json`
- **代码**：
  ```json
  "@astrojs/tailwind": "^5.1.0",
  "tailwindcss": "^3.4.0"
  ```
- **问题**：Astro v5 推荐使用 Tailwind CSS v4（内置 Vite 插件），`@astrojs/tailwind` 集成已废弃。
- **修复**：
  1. 移除 `@astrojs/tailwind` 依赖
  2. 升级 `tailwindcss` 到 `^4.0.0`
  3. 在 `astro.config.mjs` 中移除 `integrations: []` 中的 tailwind 集成
  4. 创建 `src/styles/global.css` 使用 `@import "tailwindcss"`
- **参考**：Tailwind CSS v4 官方迁移指南

---

## P1 - 强烈建议修复

### P1-1: `<ViewTransitions />` 组件导入路径已变更

- **文件**：`src/pages/index.astro` 第 3 行
- **代码**：
  ```astro
  import { ViewTransitions } from 'astro:transitions';
  ```
- **问题**：在 Astro v5 中，`ViewTransitions` 组件已更名为 `ClientRouter`，旧导入仍可用但已标记为 deprecated。
- **修复**：
  ```astro
  import { ClientRouter } from 'astro:transitions';
  ```
  并将 `<ViewTransitions />` 替换为 `<ClientRouter />`。

### P1-2: `<Image>` 组件 `format` 属性误用

- **文件**：`src/components/Gallery.astro` 第 7-8 行
- **代码**：
  ```astro
  <Image src={hero} format="webp" width={800} height={600} alt="Hero" />
  <Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
  ```
- **问题**：
  1. 同一图片源导出两种 `format` 不会生成两种格式，只会按最后一次调用缓存。
  2. `format` 属性在 Astro v5 的 `<Image>` 组件中行为有变化，推荐使用 `formats`（数组）或在 `astro.config.mjs` 中配置 `image.formats`。
- **修复**：
  ```astro
  <Image src={hero} width={800} height={600} alt="Hero" />
  <Image src={hero} width={400} height={300} alt="Thumb" />
  ```
  并在 `astro.config.mjs` 中添加：
  ```js
  image: {
    formats: ['avif', 'webp'],
  }
  ```

### P1-3: 页面组件包裹 `<html>` 导致重复根元素

- **文件**：`src/pages/index.astro` 第 9-19 行
- **代码**：
  ```astro
  <html>
    <head>
      <ViewTransitions />
    </head>
    <Layout>
      ...
    </Layout>
  </html>
  ```
- **问题**：`Layout.astro` 已经包含 `<!DOCTYPE html>` 和 `<html>` 根元素。页面再包一层 `<html>` 会导致 SSR 输出两个 `<html>` 标签，违反 HTML 规范，可能导致 hydration 错误。
- **修复**：移除页面中的 `<html>` / `<head>`，将所有内容放在 `Layout` 的 `<slot />` 内，或在 `Layout` 中处理 `<head>` 注入。
  ```astro
  ---
  import Layout from '../layouts/Layout.astro';
  import { ClientRouter } from 'astro:transitions';

  const posts = Object.values(await import.meta.glob('./posts/*.md', { eager: true }));
  const themeColor = '#3b82f6';
  ---

  <Layout>
    <ClientRouter />
    <h1>Old Site</h1>
    <ul>
      {posts.map(p => <li><a href={p.url}>{p.frontmatter.title}</a></li>)}
    </ul>
  </Layout>

  <style define:vars={{ themeColor }}>
    h1 { color: var(--themeColor); }
  </style>
  ```
  同时需要在 `Layout.astro` 的 `<head>` 中预留 `<slot name="head" />` 以支持 `ClientRouter` 注入。

---

## P2 - 建议优化

### P2-1: `define:vars` 在 scoped style 中已不推荐

- **文件**：`src/pages/index.astro` 第 21-23 行
- **代码**：
  ```astro
  <style define:vars={{ themeColor }}>
    h1 { color: var(--themeColor); }
  </style>
  ```
- **问题**：`define:vars` 在 Astro v5 中仍可用，但官方更推荐通过 CSS 自定义属性在 `:root` 或组件 props 中传递变量，避免运行时注入带来的 FOUC 风险。
- **修复方案（可选）**：
  ```astro
  <style>
    :root { --theme-color: #3b82f6; }
    h1 { color: var(--theme-color); }
  </style>
  ```
  或通过 `set:html` 在 `<head>` 中注入 `<style>`。

### P2-2: `astro.config.mjs` 缺少现代优化配置

- **文件**：`astro.config.mjs`
- **代码**：
  ```js
  export default defineConfig({
    output: 'static',
    integrations: [],
    i18n: { ... }
  });
  ```
- **问题**：缺少 `image` 服务配置、`vite` 优化选项、`site` / `base` 路径等现代 Astro 项目常用配置。
- **修复（建议）**：
  ```js
  export default defineConfig({
    output: 'static',
    site: 'https://example.com',
    image: {
      service: { entrypoint: 'astro/assets/services/sharp' },
      formats: ['avif', 'webp'],
    },
    i18n: {
      locales: ['en', 'zh'],
      defaultLocale: 'zh',
      prefixDefaultLocale: false,
    },
  });
  ```

---

## 迁移检查清单

- [ ] 替换所有 `Astro.glob()` 为 `import.meta.glob(..., { eager: true })`
- [ ] 升级 Tailwind CSS 到 v4，移除 `@astrojs/tailwind`
- [ ] 将 `ViewTransitions` 重命名为 `ClientRouter`
- [ ] 修复 `<html>` 重复包裹问题
- [ ] 统一 `<Image>` 的 `format` 配置到 `astro.config.mjs`
- [ ] 运行 `npm run build` 验证无报错
- [ ] 运行 `npm run preview` 验证页面渲染正常

---

## 备注

本次扫描基于 Astro v5 官方文档和常见反模式知识库完成，未使用自动化 Skill。所有发现均为静态代码分析结果，建议在实际迁移前在 staging 环境验证。
