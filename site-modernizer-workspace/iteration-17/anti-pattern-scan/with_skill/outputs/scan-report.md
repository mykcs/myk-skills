# Anti-Pattern Scan Report

**Project:** mock-anti-pattern-site  
**Date:** 2026-05-15  
**Skill:** site-modernizer (SCAN workflow)

---

## Findings Summary

| # | File | Anti-Pattern | Severity | Status |
|---|------|--------------|----------|--------|
| 1 | `src/pages/index.astro:5` | `Astro.glob()` — deprecated, will be removed | HIGH | Fixed |
| 2 | `src/pages/index.astro:3,11` | `ViewTransitions` — renamed to `ClientRouter` | HIGH | Fixed |
| 3 | `src/components/Gallery.astro:7,8` | `<Image format="...">` — unnecessary in Astro 5+ | MED | Fixed |
| 4 | `src/pages/index.astro:17` | Implicit `any` type in `.map()` callback | LOW | Fixed |
| 5 | Repo root | Missing `.gitignore` for `node_modules/`, `dist/`, `.astro/` | LOW | Fixed |

---

## Detailed Changes

### 1. Migrated `Astro.glob` → Content Collections
- **Before:** `const posts = await Astro.glob('./posts/*.md');`
- **After:** `const posts = await getCollection('posts');`
- **New files:** `src/content/config.ts`, `src/content/posts/hello.md`
- **Why:** `Astro.glob` is deprecated and will be removed in a future major version. Content Collections provide type-safe schemas and better build performance.

### 2. Migrated `ViewTransitions` → `ClientRouter`
- **Before:** `import { ViewTransitions } from 'astro:transitions';` + `<ViewTransitions />`
- **After:** `import { ClientRouter } from 'astro:transitions';` + `<ClientRouter />`
- **Why:** `ViewTransitions` was renamed to `ClientRouter` in Astro 4+.

### 3. Removed explicit `format` from `<Image>`
- **Before:** `<Image src={hero} format="webp" ... />` and `format="avif"`
- **After:** `<Image src={hero} ... />` (no format prop)
- **Why:** Astro 5+ with Sharp auto-optimizes image formats. Explicit `format` overrides this and can prevent optimal format selection.

### 4. Added type annotation to `.map()` callback
- Added explicit type `{ slug: string; data: { title: string } }` to eliminate TS hint.

### 5. Added `.gitignore`
- Ignores `node_modules/`, `dist/`, `.astro/` to prevent accidental commits of generated files.

---

## Build Verification

- `npx astro check` — **0 errors, 0 warnings, 0 hints**
- `npm run build` — **Complete!** (1 page built)

---

## Commit

```
ef572a5 refactor(site): migrate deprecated Astro APIs to modern equivalents
```

**Files changed:** 6  
**Insertions:** 6,548  
**Deletions:** 6
