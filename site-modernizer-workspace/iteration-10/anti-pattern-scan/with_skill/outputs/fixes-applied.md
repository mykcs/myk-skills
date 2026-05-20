# Fixes Applied Report

**Commit:** `1c34c09`  
**Message:** `refactor(site): fix Astro anti-patterns — migrate Astro.glob to Content Collections, replace ViewTransitions with ClientRouter, remove Image format props, eliminate define:vars, fix Layout nesting`

---

## Files Modified

### `src/pages/index.astro`
- Removed `Astro.glob('./posts/*.md')` → `getCollection('posts')`
- Removed `ViewTransitions` → `ClientRouter` (moved to Layout)
- Removed outer `<html>` / `<head>` / `<body>` tags (Layout now root)
- Removed unused `themeColor` constant
- Removed `<style define:vars>` block
- Added explicit `title` prop to `<Layout>`

### `src/components/Gallery.astro`
- Removed `format="webp"` from first `<Image>`
- Removed `format="avif"` from second `<Image>`

### `src/layouts/Layout.astro`
- Added `import { ClientRouter } from 'astro:transitions'`
- Added `<ClientRouter />` inside `<head>`
- Added `<meta name="viewport" content="width=device-width, initial-scale=1.0">`

---

## Files Created

### `src/content/config.ts`
Content collection schema using Zod:
```ts
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    pubDate: z.date().optional(),
    description: z.string().optional(),
  }),
});

export const collections = { posts };
```

### `src/content/posts/hello-world.md`
Sample post with frontmatter: title, pubDate, description.

### `src/content/posts/second-post.md`
Second sample post.

### `src/assets/hero.png`
Minimal valid 1x1 transparent PNG (created via Python) so `<Image>` component has a real asset to process.

---

## Verification

```
$ npx astro check
Result (3 files): 0 errors, 0 warnings, 1 hint

$ npm run build
[build] 1 page(s) built in 19.11s
[build] Complete!
```

All anti-patterns resolved. Build passes cleanly.
