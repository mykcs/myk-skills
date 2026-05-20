# Final Source Tree

```
src/
├── assets/
│   └── hero.png
├── components/
│   └── Gallery.astro
├── layouts/
│   └── Layout.astro
└── pages/
    └── index.astro
```

## `src/pages/index.astro`
```astro
---
import Layout from '../layouts/Layout.astro';
import { ClientRouter } from 'astro:transitions';
import Gallery from '../components/Gallery.astro';

interface Post {
  url: string;
  frontmatter: { title: string };
}

const posts: Post[] = [];
---

<Layout title="Mock Site">
  <Fragment slot="head">
    <ClientRouter />
  </Fragment>
  <h1>Old Site</h1>
  <ul>
    {posts.map(p => <li><a href={p.url}>{p.frontmatter.title}</a></li>)}
  </ul>
  <Gallery />
</Layout>

<style>
  :root {
    --theme-color: #3b82f6;
  }
  h1 { color: var(--theme-color); }
</style>
```

## `src/components/Gallery.astro`
```astro
---
import { Image } from 'astro:assets';
import hero from '../assets/hero.png';
---

<div class="gallery">
  <Image src={hero} width={800} height={600} alt="Hero" loading="eager" />
  <Image src={hero} width={400} height={300} alt="Thumb" loading="lazy" />
</div>
```

## `src/layouts/Layout.astro`
```astro
---
const { title = 'Mock Site' } = Astro.props;
const canonicalURL = new URL(Astro.url.pathname, Astro.site || 'https://example.com');
---
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="canonical" href={canonicalURL} />
  <meta property="og:title" content={title} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={canonicalURL} />
  <meta name="theme-color" content="#3b82f6" />
  <slot name="head" />
</head>
<body>
  <slot />
</body>
</html>
```
