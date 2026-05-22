# 最终文件状态

## 文件清单

```
src/
  components/
    Gallery.astro
  layouts/
    Layout.astro
  pages/
    index.astro
astro.config.mjs
package.json
```

---

## `src/pages/index.astro`

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

---

## `src/layouts/Layout.astro`

```astro
---
const { title = 'Mock Site' } = Astro.props;
---
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
<body>
  <slot />
</body>
</html>
```

---

## `src/components/Gallery.astro`

```astro
---
import { Image } from 'astro:assets';
import hero from '../assets/hero.png';
---

<div class="gallery">
  <Image src={hero} format="webp" width={800} height={600} alt="Hero" />
  <Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
</div>
```

---

## `astro.config.mjs`

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  integrations: [],
  i18n: {
    locales: ['en', 'zh'],
    defaultLocale: 'zh',
    prefixDefaultLocale: false,
  },
});
```

---

## `package.json`

```json
{
  "name": "mock-anti-pattern-site",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^5.0.0",
    "@astrojs/tailwind": "^5.1.0",
    "tailwindcss": "^3.4.0"
  }
}
```

---

## 构建状态

- **结果**: 成功
- **输出页数**: 1 页
- **输出目录**: `dist/`
- **错误**: 0
- **警告**: 0
