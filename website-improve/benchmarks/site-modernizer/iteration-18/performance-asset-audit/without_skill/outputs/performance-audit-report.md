# Performance Audit Report

## Project
- **Path**: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-18/performance-asset-audit/without_skill/mock-repo`
- **Framework**: Astro v5 (Static)
- **Audit Date**: 2026-05-15

---

## Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Lighthouse Performance Score** | 0.96 | **1.00** | +0.04 |
| **First Contentful Paint (FCP)** | 1494.3 ms | **703.7 ms** | -52.9% |
| **Largest Contentful Paint (LCP)** | 1565.1 ms | **1052.4 ms** | -32.8% |
| **Speed Index** | 5026.6 ms | **1100.5 ms** | -78.1% |
| **LCP Element Render Delay** | 3068.2 ms | **37.4 ms** | -98.8% |
| **Total Blocking Time** | 0.0 ms | 4.0 ms | +4 ms (negligible) |
| **Cumulative Layout Shift** | 0.0 | 0.0 | no change |

---

## Issues Found & Fixed

### 1. Render-Blocking Google Fonts (HIGH)
- **Problem**: The Inter font stylesheet was loaded synchronously, blocking rendering for ~800ms.
- **Fix**: Changed to `rel="preload" as="style"` with `onload="this.rel='stylesheet'"` and added `<noscript>` fallback.
- **File**: `src/layouts/Layout.astro`

### 2. Massive LCP Element Render Delay (HIGH)
- **Problem**: The LCP image had a render delay of **3068ms** due to font blocking and lack of fetch priority.
- **Fix**: Added `fetchpriority="high"` to the hero image. Reduced render delay to **37ms**.
- **File**: `src/components/Gallery.astro`

### 3. All Gallery Images Loaded Eagerly (MED)
- **Problem**: All 4 images used `loading="eager"`, wasting bandwidth on below-the-fold thumbnails.
- **Fix**: Changed thumbnail images to `loading="lazy"`. Only the hero remains eager.
- **File**: `src/components/Gallery.astro`

### 4. Broken Remote Image + Missing Dimensions (MED)
- **Problem**: `via.placeholder.com` returned connection errors. The `<img>` had no `width`/`height`, causing layout shift risk.
- **Fix**: Replaced with `picsum.photos` and added explicit `width="800" height="600" loading="lazy"`.
- **File**: `src/pages/index.astro`

### 5. Missing Viewport Meta Tag (MED)
- **Problem**: No `<meta name="viewport">`, causing mobile rendering issues.
- **Fix**: Added `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
- **File**: `src/layouts/Layout.astro`

### 6. Missing Meta Description (LOW)
- **Problem**: No `<meta name="description">`.
- **Fix**: Added description meta tag.
- **File**: `src/layouts/Layout.astro`

### 7. Invalid Asset File (BUILD BLOCKER)
- **Problem**: `src/assets/hero.png` was a 43B ASCII text placeholder, causing Astro build to fail with `NoImageMetadata`.
- **Fix**: Replaced with a real 800x600 JPEG image (49KB).
- **File**: `src/assets/hero.png`

---

## Remaining Non-Critical Notes

| Issue | Severity | Note |
|-------|----------|------|
| `image-size-responsive` | Info | Lighthouse expects 1.5x DPR images (1200x900 for 800x600 display). Astro already generates optimized WebP; serving higher DPR is optional. |
| `cache-insight` | Info | Local dev server has no cache headers. Production hosting (Vercel/Netlify/GitHub Pages) will handle this. |
| `favicon.ico 404` | Info | Add a favicon to eliminate the console error. |
| `landmark-one-main` | Info | Wrap page content in `<main>` for accessibility. |

---

## Files Modified

1. `src/layouts/Layout.astro` — Font preload, viewport, meta description
2. `src/components/Gallery.astro` — fetchpriority, lazy loading
3. `src/pages/index.astro` — Fixed remote image URL + dimensions
4. `src/assets/hero.png` — Replaced fake placeholder with real image

---

## Verification

- Build passes: `npm run build` OK
- Lighthouse score: **1.00** (Performance)
- No console errors except favicon 404
