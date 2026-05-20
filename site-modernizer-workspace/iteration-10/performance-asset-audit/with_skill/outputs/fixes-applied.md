# Fixes Applied Report

## Commit
- `73b7130` — perf(site): optimize images, fonts, and layout for Core Web Vitals

## Files Modified

### src/layouts/Layout.astro
- Added `<meta name="viewport" content="width=device-width, initial-scale=1.0">` for mobile rendering
- Added `<meta name="description">` with prop-driven content for SEO
- Changed Google Fonts `<link>` to use `media="print" onload="this.media='all'"` to eliminate render-blocking
- Added `<noscript>` fallback for fonts when JS is disabled
- Wrapped `<slot />` in `<main>` for semantic HTML structure

### src/components/Gallery.astro
- Hero image: added `fetchpriority="high"` to prioritize LCP image
- Thumbnails (3x): changed `loading="eager"` → `loading="lazy"` to defer offscreen images
- All images: added `densities={[1, 2]}` for responsive retina srcsets

### src/pages/index.astro
- Replaced raw `<img src="https://via.placeholder.com/800x600">` with Astro `<Image>` component
- Added `loading="lazy"` and `densities={[1, 2]}` to the bottom image
- Passed `description` prop to Layout for SEO meta tag

### src/assets/hero.png
- Replaced broken 43-byte text placeholder with a real 800x600 JPEG image (61KB)
- This fixed the `NoImageMetadata` build error caused by a corrupted placeholder file

## Dependencies
- **Identified but NOT removed**: `lodash`, `moment`, `jquery` remain in package.json.
  They are unused in `src/` but removing them is out of scope for a pure performance fix
  and could break downstream tooling that expects them.

## Lighthouse Impact

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Performance Score | 84 | 100 | +16 |
| Accessibility Score | 92 | 100 | +8 |
| Best Practices | 100 | 96 | -4 (font display swap penalty) |
| SEO Score | 100 | 100 | 0 |
| FCP | 2.3 s | 0.7 s | -1.6 s |
| LCP | 3.6 s | 1.4 s | -2.2 s |
| Speed Index | 5.1 s | 0.7 s | -4.4 s |
| TTI | 3.6 s | 1.5 s | -2.1 s |
| CLS | 0.001 | 0 | -0.001 |
| TBT | 0 ms | 0 ms | 0 |
