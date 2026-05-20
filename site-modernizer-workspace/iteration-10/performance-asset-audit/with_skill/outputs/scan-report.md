# Performance & Asset Audit Report

## Site: mock-perf-site (Astro 5.x)

### Initial Build Status
- `npm run build`: PASS (1 page, 2 optimized images)
- `npx astro check`: PASS (0 errors, 0 warnings, 0 hints)
- Build output size: 80KB (dist/)

### Lighthouse Scores (Before Fixes)

| Category | Score |
|----------|-------|
| Performance | 84 |
| Accessibility | 92 |
| Best Practices | 100 |
| SEO | 100 |

### Key Metrics (Before)

| Metric | Value | Score |
|--------|-------|-------|
| First Contentful Paint (FCP) | 2.3 s | 0.76 |
| Largest Contentful Paint (LCP) | 3.6 s | 0.61 |
| Speed Index | 5.1 s | 0.62 |
| Total Blocking Time (TBT) | 0 ms | 1.00 |
| Cumulative Layout Shift (CLS) | 0.001 | 1.00 |
| Time to Interactive (TTI) | 3.6 s | 0.91 |

### Identified Issues

#### P0 - Critical Performance
1. **Google Fonts CDN blocking render** — Layout.astro loads Inter from fonts.googleapis.com without `display=swap`, causing render-blocking and FCP/LCP delays.
2. **All Gallery images use `loading="eager"`** — 4 images (1x800x600 + 3x400x300) all eager-load, wasting bandwidth. Only the hero should be eager; thumbnails should lazy-load.
3. **Remote image without optimization** — index.astro uses `<img src="https://via.placeholder.com/800x600">` with no `loading`, `decoding`, or dimension attributes, hurting LCP.

#### P1 - Dependencies Bloat
4. **Unused dependencies in package.json** — `lodash`, `moment`, `jquery` are installed but never imported in `src/`. They bloat node_modules and risk accidental bundling.

#### P2 - Asset & Config
5. **Missing viewport meta tag** — Layout.astro lacks `<meta name="viewport">`, hurting mobile experience and Lighthouse mobile scores.
6. **Missing lang attribute diversity** — Only `lang="zh"` with no i18n routing configured.
7. **No sitemap integration** — SEO could benefit from `@astrojs/sitemap`.

### Anti-Pattern Scan (Astro 5/6 Checklist)

| Check | Status | Notes |
|-------|--------|-------|
| No `Astro.glob()` | PASS | Not used |
| No `<Image format="...">` | PASS | Astro auto-optimizes to webp |
| `ClientRouter` vs `ViewTransitions` | N/A | Not used |
| No `define:vars` on `<style>` | PASS | Not used |
| Fonts loaded locally | FAIL | Using Google Fonts CDN |
| Images use correct loading | FAIL | All eager, should be mixed |
| No unused dependencies | FAIL | lodash, moment, jquery unused |
| CSS `@theme` block | N/A | No Tailwind in this project |
| No hardcoded secrets | PASS | None found |
