# Fixes Applied

## 1. `src/pages/index.astro` — Full Rewrite

### Before
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

### After
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

## 2. `src/components/Gallery.astro` — Remove `format` Attributes

### Before
```astro
<Image src={hero} format="webp" width={800} height={600} alt="Hero" />
<Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
```

### After
```astro
<Image src={hero} width={800} height={600} alt="Hero" />
<Image src={hero} width={400} height={300} alt="Thumb" />
```

## 3. `src/layouts/Layout.astro` — Accept `lang` Prop

### Before
```astro
const { title = 'Mock Site' } = Astro.props;
---
<html lang="zh">
```

### After
```astro
const { title = 'Mock Site', lang = 'zh' } = Astro.props;
---
<html lang={lang}>
```

## 4. New Files

### `src/content/config.ts`
```ts
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  schema: z.object({
    title: z.string(),
  }),
});

export const collections = { posts };
```

### `src/content/posts/hello.md`
```md
---
title: "Hello World"
---
Hello from Content Collections.
```
