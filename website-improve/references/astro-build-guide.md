# Astro Build Guide

> 从零开始创建 Astro 静态站点的完整指南。
> 与 `astro-modernization-checklist.md`（升级现有项目）互补使用。

---

## 1. 项目初始化

```bash
# 创建新项目
npm create astro@latest

# 选项建议
#   - Template: Choose "Empty" or "Blog" as needed
#   - TypeScript: Yes (strict)
#   - Dependencies: Yes (install now)
#   - Git: Yes
```

**初始化后验证：**
```bash
cd <project-dir>
npm run dev    # http://localhost:4321
npm run build  # 必须成功
```

---

## 2. 项目结构

```
/
├── astro.config.mjs      # 站点配置
├── tsconfig.json         # TypeScript 配置
├── package.json
├── public/               # 静态资源（直接复制到 dist/）
│   └── favicon.svg
├── src/
│   ├── layouts/          # 布局组件
│   │   └── BaseLayout.astro
│   ├── pages/            # 路由页面
│   │   ├── index.astro
│   │   └── 404.astro
│   ├── components/       # UI 组件
│   │   └── Header.astro
│   ├── content/          # Content Collections（可选）
│   │   └── config.ts
│   ├── styles/           # 全局样式
│   │   └── global.css
│   └── scripts/          # 客户端脚本
│       └── main.ts
└── .github/
    └── workflows/
        └── deploy.yml    # CI/CD（GitHub Pages）
```

---

## 3. Tailwind CSS v4 集成

```bash
npm install -D @tailwindcss/vite
```

**astro.config.mjs：**
```js
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
});
```

**src/styles/global.css：**
```css
@import 'tailwindcss';

@theme {
  --font-sans: 'Inter', ui-sans-serif, system-ui;
  --color-primary: oklch(55% 0.15 255);
}
```

**注意：** Tailwind v4 不使用 `tailwind.config.mjs`，主题配置写在 `@theme` 块中。

---

## 4. Content Collections

**src/content/config.ts：**
```ts
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.date(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

**使用：**
```astro
---
import { getCollection } from 'astro:content';
const posts = await getCollection('blog');
---
```

---

## 5. i18n 路由

**astro.config.mjs：**
```js
export default defineConfig({
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh'],
    routing: {
      prefixDefaultLocale: false,
      redirectToDefaultLocale: true,  // 显式设置，Astro v6 默认 false
    },
  },
});
```

**目录结构：**
```
src/pages/
├── index.astro           # 自动重定向到 /en/ 或 /zh/
├── [lang]/
│   ├── index.astro       # 双语首页
│   └── about.astro       # 双语关于页
```

**获取当前 locale：**
```astro
---
const { lang } = Astro.params;
---
```

---

## 6. 布局组件

**src/layouts/BaseLayout.astro：**
```astro
---
interface Props {
  title: string;
  lang?: string;
}
const { title, lang = 'en' } = Astro.props;
---

<html lang={lang}>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>{title}</title>
    <link rel="stylesheet" href="/styles/global.css" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

**使用：**
```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="Home">
  <h1>Hello World</h1>
</BaseLayout>
```

---

## 7. 组件开发

**Props：**
```astro
---
interface Props {
  href: string;
  variant?: 'primary' | 'secondary';
}
const { href, variant = 'primary' } = Astro.props;
---

<a href={href} class:list={['btn', variant]}>
  <slot />
</a>
```

**Slots：**
```astro
---
// Card.astro
---

<div class="card">
  <div class="card-header">
    <slot name="header" />
  </div>
  <div class="card-body">
    <slot />
  </div>
</div>
```

---

## 8. 图片与资源

**本地图片（推荐）：**
```astro
---
import { Image } from 'astro:assets';
import myImage from '../assets/photo.jpg';
---

<Image src={myImage} alt="Description" loading="lazy" />
```

**public/ 目录图片：**
```astro
<img src="/images/logo.png" alt="Logo" loading="eager" />
```

**注意：**
- `astro:assets` 的 `<Image />` 会自动优化、生成 srcset
- 外部图片需在 `astro.config.mjs` 中配置 `image.domains` 或 `image.remotePatterns`

---

## 9. 客户端脚本

**Island 架构：**
```astro
---
// 服务端渲染，无 JS
---

<Counter client:load />  <!-- 页面加载时 hydrate -->
<Counter client:idle />  <!-- 浏览器 idle 时 hydrate -->
<Counter client:visible /> <!-- 进入视口时 hydrate -->
```

**纯脚本（非组件）：**
```astro
<script src="../scripts/main.ts"></script>
```

---

## 10. SEO 基础

**每个布局必须包含：**
```astro
<meta name="description" content={description} />
<link rel="canonical" href={canonicalUrl} />

<!-- Open Graph -->
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={ogImage} />
<meta property="og:url" content={canonicalUrl} />
<meta property="og:type" content="website" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />

<!-- Structured Data -->
<script type="application/ld+json" set:html={JSON.stringify(jsonLd)} />
```

---

## 11. 构建与部署

### 本地构建
```bash
npm run build      # 输出到 dist/
npm run preview    # 本地预览生产构建
```

### GitHub Pages 部署

**.github/workflows/deploy.yml：**
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
```

**astro.config.mjs（GitHub Pages）：**
```js
export default defineConfig({
  site: 'https://username.github.io',
  base: '/repo-name',  // 如果是项目站点（非用户站点）
});
```

---

## 12. 新建项目验收清单

项目创建完成后，用以下清单验收：

- [ ] `npm run build` 通过，0 errors
- [ ] `npm run preview` 首页正常加载
- [ ] 所有内部链接可点击
- [ ] 图片正常显示
- [ ] 移动端 viewport 无溢出
- [ ] `dist/` 输出结构正确
- [ ] GitHub Actions 部署成功
