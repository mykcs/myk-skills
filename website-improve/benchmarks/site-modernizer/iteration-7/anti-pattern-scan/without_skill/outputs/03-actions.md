# 已执行的修复操作

## 修复 1: `src/pages/index.astro` — 三合一修复

### 变更前
```astro
---
import Layout from '../layouts/Layout.astro';
import { ViewTransitions } from 'astro:transitions';

const posts = await Astro.glob('./posts/*.md');
const themeColor = '#3b82f6';
---

<html>
  <head>
    <ViewTransitions />
  </head>
  <Layout>
    <h1>Old Site</h1>
    <ul>
      {posts.map(p => <li><a href={p.url}>{p.frontmatter.title}</a></li>)}
    </ul>
  </Layout>
</html>

<style define:vars={{ themeColor }}>
  h1 { color: var(--themeColor); }
</style>
```

### 变更后
```astro
---
import Layout from '../layouts/Layout.astro';
import { ClientRouter } from 'astro:transitions';

const posts = Object.values(import.meta.glob('./posts/*.md', { eager: true }));
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

### 修复说明
1. `ViewTransitions` → `ClientRouter`（Astro 6 兼容性）
2. `Astro.glob()` → `import.meta.glob(..., { eager: true })` + `Object.values()`（废弃 API 替换）
3. 移除页面中的 `<html>`/`<head>`，让 `<Layout>` 作为根包裹元素（修正嵌套 html 反模式）

## 未修复项（本次未执行）

| 问题 | 原因 |
|------|------|
| Gallery.astro 的 `format` prop | 该组件未被任何页面引用，当前构建不报错；修复需删除 `format="webp"` 和 `format="avif"` |
| Tailwind v3 → v4 升级 | 涉及 package.json 依赖变更、可能需调整 tailwind 配置文件，属于较大变更 |
| 缺失的 `src/assets/hero.png` | 需用户提供图片资源或修改组件逻辑 |

## 验证结果

- `npm run build` 执行成功，输出 `1 page(s) built in 415ms`
- 无报错、无警告
