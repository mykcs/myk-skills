# Astro Anti-Pattern Scan Report

**Project:** mock-anti-pattern-site  
**Date:** 2026-05-14  
**Skill:** site-modernizer (SCAN phase)  
**Reference:** `references/scan-checklist.md`

---

## Findings Summary

| # | File | Anti-Pattern | Severity | Status |
|---|------|-------------|----------|--------|
| 1 | `src/pages/index.astro` | `Astro.glob('./posts/*.md')` — deprecated, use Content Collections | HIGH | Fixed |
| 2 | `src/pages/index.astro` | `ViewTransitions` import from `astro:transitions` — renamed to `ClientRouter` in Astro 4+ | HIGH | Fixed |
| 3 | `src/components/Gallery.astro` | `<Image format="...">` — explicit format props conflict with Sharp auto-optimization | MED | Fixed |
| 4 | `src/pages/index.astro` | `define:vars` on `<style>` — discouraged, use CSS custom properties or scoped styles | MED | Fixed |
| 5 | `src/pages/index.astro` | Duplicate `<html>` / `<head>` tags wrapping Layout component | MED | Fixed |
| 6 | `src/layouts/Layout.astro` | Missing `ClientRouter` in layout head | LOW | Fixed |
| 7 | `src/layouts/Layout.astro` | Missing viewport meta tag | LOW | Fixed |
| 8 | `src/content/` | Content collection config and posts missing — `getCollection('posts')` returned empty | HIGH | Fixed |

---

## Detailed Findings

### 1. `Astro.glob()` Usage (HIGH)
**Location:** `src/pages/index.astro`
**Issue:** `Astro.glob()` is deprecated in favor of Content Collections (`getCollection`). It lacks type safety, schema validation, and automatic slug generation.
**Fix:** Migrated to `getCollection('posts')` with a proper `src/content/config.ts` schema.

### 2. `ViewTransitions` Import (HIGH)
**Location:** `src/pages/index.astro`
**Issue:** `ViewTransitions` was renamed to `ClientRouter` in Astro 4. The old import still works in Astro 5 but is legacy.
**Fix:** Replaced `import { ViewTransitions } from 'astro:transitions'` with `import { ClientRouter } from 'astro:transitions'`.

### 3. `<Image format="...">` Props (MED)
**Location:** `src/components/Gallery.astro`
**Issue:** Explicit `format="webp"` and `format="avif"` props on `<Image>` override Sharp's auto-format selection, which can serve suboptimal formats to browsers that don't support them.
**Fix:** Removed `format` props entirely. Sharp now auto-selects the best format.

### 4. `define:vars` on `<style>` (MED)
**Location:** `src/pages/index.astro`
**Issue:** `define:vars` injects CSS variables via inline styles, which is less maintainable than native CSS custom properties and can cause specificity issues.
**Fix:** Removed `define:vars` and the associated `<style>` block. The theme color is now static or can be set via a global CSS file.

### 5. Duplicate HTML/Head Tags (MED)
**Location:** `src/pages/index.astro`
**Issue:** The page wrapped `<Layout>` inside its own `<html>` and `<head>` tags. `Layout.astro` already provides these, causing invalid nested HTML structure.
**Fix:** Removed outer `<html>`/`<head>`/`<body>` tags. `Layout` is now the root element.

### 6. Missing `ClientRouter` in Layout (LOW)
**Location:** `src/layouts/Layout.astro`
**Issue:** `ClientRouter` was placed in the page's own `<head>` instead of the shared Layout, meaning other pages wouldn't benefit from view transitions.
**Fix:** Moved `<ClientRouter />` into `Layout.astro`'s `<head>`.

### 7. Missing Viewport Meta Tag (LOW)
**Location:** `src/layouts/Layout.astro`
**Issue:** No `<meta name="viewport">` tag, causing poor mobile rendering.
**Fix:** Added `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.

### 8. Missing Content Collection (HIGH)
**Location:** `src/content/`
**Issue:** `getCollection('posts')` was called but no content collection config or posts existed. Build warned: "The collection 'posts' does not exist or is empty."
**Fix:** Created `src/content/config.ts` with Zod schema and two sample posts.

---

## Build Verification

- `npx astro check`: 0 errors, 0 warnings, 1 hint (implicit `any` on `p` in map — acceptable for mock)
- `npm run build`: Complete, 1 page built, no errors

---

## Remaining Items (Not Addressed)

| Item | Reason |
|------|--------|
| Tailwind v3 → v4 migration | Out of scope for anti-pattern scan; requires dependency upgrade and config rewrite |
| `prefixDefaultLocale` i18n routing | Config already correct; no anti-pattern detected |
| SEO meta tags (OG, canonical, schema) | Enhancement, not anti-pattern |
| Sitemap generation | Enhancement, not anti-pattern |
