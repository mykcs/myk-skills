# Final Source Tree

```
src/
├── assets/
│   └── hero.png
├── components/
│   └── Gallery.astro
├── content/
│   ├── config.ts
│   └── posts/
│       └── hello.md
├── layouts/
│   └── Layout.astro
└── pages/
    └── index.astro
```

## File Contents

### src/pages/index.astro
```astro
---
import Layout from '../layouts/Layout.astro';
import { ClientRouter } from 'astro:transitions';
import { getCollection } from 'astro:content';

const posts = await getCollection('posts');
const themeColor = '#3b82f6';
---

<Layout title="Mock Site">
  <ClientRouter />
  <h1>Old Site</h1>
  <ul>
    {posts.map(p => <li><a href={`/posts/${p.slug}/`}>{p.data.title}</a></li>)}
  </ul>
</Layout>

<style>
  h1 { color: var(--theme-color); }
</style>

<script is:inline define:vars={{ themeColor }}>
  document.documentElement.style.setProperty('--theme-color', themeColor);
</script>
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

### src/content/config.ts
```ts
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
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

Hello!
```
