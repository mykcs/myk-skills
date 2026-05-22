# Astro Anti-Pattern Scan & Fix Report

**Project**: mock-anti-pattern-site  
**Date**: 2026-05-15  
**Skill**: site-modernizer (SCAN workflow: scan → fix → build-verify → commit)

---

## Findings Summary

| # | Anti-Pattern | File | Severity | Status |
|---|--------------|------|----------|--------|
| 1 | `Astro.glob()` — deprecated content discovery | `src/pages/index.astro` | HIGH | Fixed |
| 2 | `ViewTransitions` import — renamed in Astro 4+ | `src/pages/index.astro` | HIGH | Fixed |
| 3 | `<Image format="...">` — `format` prop deprecated in Astro 6 | `src/components/Gallery.astro` | MED | Fixed |
| 4 | Duplicate `<html>`/`<head>`/`<body>` nesting | `src/pages/index.astro` | HIGH | Fixed |
| 5 | Missing viewport meta tag | `src/layouts/Layout.astro` | MED | Fixed |
| 6 | `define:vars` CSS custom property (legacy pattern) | `src/pages/index.astro` | LOW | Fixed |

---

## Detailed Fixes

### 1. `Astro.glob()` → Content Collections

**Before**:
```astro
const posts = Astro.glob('./posts/*.md');
// ...
{posts.map(p => <li>{p.frontmatter.title}</li>)}
```

**After**:
```astro
import { getCollection } from 'astro:content';
const posts = await getCollection('posts');
// ...
{posts.map(p => <li>{p.data.title}</li>)}
```

**Added**: `src/content/config.ts` with `posts` collection schema.
**Added**: `src/pages/posts/hello.md` as sample content for the collection.

### 2. `ViewTransitions` → `ClientRouter`

**Before**:
```astro
import { ViewTransitions } from 'astro:transitions';
<ViewTransitions />
```

**After**:
```astro
import { ClientRouter } from 'astro:transitions';
<ClientRouter />
```

### 3. Removed `<Image format="...">` props

**Before**:
```astro
<Image src={hero} format="webp" width={800} height={600} alt="Hero" />
<Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
```

**After**:
```astro
<Image src={hero} width={800} height={600} alt="Hero" />
<Image src={hero} width={400} height={300} alt="Thumb" />
```

Astro 6 auto-optimizes image formats; explicit `format` is unnecessary and deprecated.

### 4. Fixed Layout nesting (duplicate HTML structure)

**Before**: `index.astro` wrapped itself in a full `<html>` document and then placed `<Layout>` inside the body, causing nested `<html>`/`<head>`/`<body>` tags.

**After**: `index.astro` uses `<Layout>` as the root element. Layout owns the `<html>`/`<head>`/`<body>` structure.

### 5. Added viewport meta tag

**Before**:
```astro
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
```

**After**:
```astro
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
```

### 6. Simplified `define:vars` → static CSS

**Before**:
```astro
<style define:vars={{ themeColor }}>
  h1 { color: var(--themeColor); }
</style>
```

**After**:
```astro
<style>
  h1 { color: #3b82f6; }
</style>
```

The dynamic CSS custom property was unnecessary since the value was static.

---

## Build Verification

```
> astro build
[content] Synced content
[build] output: "static"
[build] 1 page(s) built in 392ms
[build] Complete!
```

Build passed with 0 errors.

---

## Commits

| Commit | Message |
|--------|---------|
| `bdb9b95` | `refactor(site): modernize Astro anti-patterns (Astro.glob→Content Collections, ViewTransitions→ClientRouter, remove Image format prop, fix Layout nesting)` |
| `3bf28c2` | `chore(git): add .gitignore to exclude node_modules and build artifacts` |

---

## Files Modified

- `src/pages/index.astro`
- `src/components/Gallery.astro`
- `src/layouts/Layout.astro`

## Files Created

- `src/content/config.ts`
- `src/pages/posts/hello.md`
- `.gitignore`
