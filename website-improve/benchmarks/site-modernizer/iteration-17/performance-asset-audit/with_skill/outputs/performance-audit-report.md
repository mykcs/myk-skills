# Performance & Asset Audit Report

**Project**: mock-perf-site  
**Date**: 2026-05-15  
**Skill**: site-modernizer (SCAN phase)

---

## Findings Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | Google Fonts CDN blocking render | HIGH | Fixed |
| 2 | Below-the-fold images eager-loaded | HIGH | Fixed |
| 3 | Unused dependencies (lodash, moment, jquery) | MED | Fixed |
| 4 | Corrupt hero.png placeholder broke image optimization | MED | Fixed |

---

## 1. Google Fonts CDN → Local Fontsource

**Problem**: Layout loaded Inter from `fonts.googleapis.com` via `<link>`. This adds DNS lookup + TLS handshake + render-blocking request on every cold load.

**Fix**: Installed `@fontsource/inter` and imported weights 400/600/700 directly in `Layout.astro` frontmatter. Removed all `<link rel="preconnect">` and Google Fonts tags.

**Impact**: Eliminates external font latency; fonts are now self-hosted and cacheable.

---

## 2. Image Lazy Loading

**Problem**: Gallery thumbnails and the remote placeholder `<img>` all loaded with `loading="eager"` (or no attribute), competing for bandwidth during initial paint.

**Fix**:
- Hero image kept `loading="eager"` (above-the-fold).
- Gallery thumbnails switched to `loading="lazy" decoding="async"`.
- Remote `<img>` on index page got `loading="lazy" decoding="async"`.

**Impact**: Reduces initial payload and improves LCP.

---

## 3. Unused Dependencies

**Problem**: `package.json` listed `lodash`, `moment`, `jquery` but zero imports existed in `src/`.

**Fix**: `npm uninstall lodash moment jquery`.

**Impact**: Shrinks `node_modules` and eliminates potential security surface area from unmaintained packages (especially moment, which is legacy).

---

## 4. Corrupt Placeholder Image

**Problem**: `src/assets/hero.png` was a text file (`# Placeholder image file for build testing`), causing Astro image optimization to fail with `NoImageMetadata`.

**Fix**: Replaced with a real 800x600 JPEG image so `astro:assets` can generate WebP variants.

**Impact**: Build passes; Astro correctly emits optimized WebP (23 kB / 7 kB vs 35 kB original).

---

## Build Verification

```
> astro build
✓ 1 page(s) built in 1.60s
✓ generating optimized images (2 WebP variants)
```

No errors.

---

## Commit

```
216adad perf(site): replace Google Fonts CDN with @fontsource/inter, add lazy loading, remove unused deps
```
