# Final Source Tree (Post-Fix)

```
/tmp/site-modernizer-test-repo/
├── astro.config.mjs
├── package.json
├── package-lock.json
├── scripts/
│   ├── build.sh
│   └── smart-autopush.sh
├── src/
│   ├── components/
│   │   └── Gallery.astro
│   ├── content/
│   │   ├── config.ts
│   │   └── posts/
│   │       └── hello.md
│   ├── layouts/
│   │   └── Layout.astro
│   └── pages/
│       └── index.astro
├── dist/
│   ├── index.html
│   └── _astro/
└── node_modules/
```

## File Contents (Post-Fix)

### astro.config.mjs
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

### package.json
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
    "@astrojs/tailwind": "^5.1.0",
    "astro": "^5.0.0",
    "tailwindcss": "^3.4.0"
  },
  "devDependencies": {
    "@astrojs/check": "^0.9.9",
    "typescript": "^5.9.3"
  }
}
```

### src/components/Gallery.astro
```astro
---
import { Image } from 'astro:assets';
import hero from '../assets/hero.png';
---

<div class="gallery">
  <Image src={hero} width={800} height={600} alt="Hero" />
  <Image src={hero} width={400} height={300} alt="Thumb" />
</div>
```

### src/layouts/Layout.astro
```astro
---
const { title = 'Mock Site', lang = 'zh' } = Astro.props;
---
<!DOCTYPE html>
<html lang={lang}>
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
<body>
  <slot />
</body>
</html>
```

### src/pages/index.astro
```astro
---
import Layout from '../layouts/Layout.astro';
import { ClientRouter } from 'astro:transitions';
import { getCollection } from 'astro:content';

const posts = await getCollection('posts');
---

<Layout title="Modern Site">
  <head>
    <ClientRouter />
    <meta name="theme-color" content="#3b82f6" />
    <link rel="canonical" href="https://example.com/" />
    <meta property="og:title" content="Modern Site" />
    <meta property="og:description" content="A modernized Astro site" />
    <meta property="og:url" content="https://example.com/" />
    <meta property="og:type" content="website" />
  </head>
  <h1>Modern Site</h1>
  <ul>
    {posts.map((p: { slug: string; data: { title: string } }) => <li><a href={`/posts/${p.slug}/`}>{p.data.title}</a></li>)}
  </ul>
</Layout>

<style>
  h1 { color: var(--theme-color); }
</style>
```

### src/content/config.ts
```ts
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  schema: z.object({
    title: z.string(),
  }),
});

export const collections = { posts };
```

### src/content/posts/hello.md
```md
---
title: "Hello World"
---
Hello from Content Collections.
```
