# Performance Audit Summary

## Task
Audit and optimize a mock Astro site for performance issues using the `site-modernizer` skill.

## Workflow Followed
1. **ASSESS** — Explored codebase (package.json, astro.config.mjs, src/pages, src/layouts, src/components, src/assets)
2. **SCAN** — Ran anti-pattern checks per `references/scan-checklist.md`
3. **FIX** — Applied performance optimizations
4. **VERIFY** — Built, type-checked, and ran Lighthouse before/after
5. **COMMIT** — Committed changes with Conventional Commits message

## Key Findings

### Issues Found
1. **Render-blocking Google Fonts** — Layout.astro loaded Inter via `<link>` without deferred loading, blocking FCP/LCP.
2. **All images eager-loaded** — Gallery component marked 4 images as `loading="eager"`, wasting bandwidth on below-fold thumbnails.
3. **Unoptimized remote image** — index.astro used a raw `<img>` tag pointing to an external placeholder with no lazy loading or srcset.
4. **Missing viewport meta** — No mobile viewport configuration.
5. **Broken placeholder image** — `src/assets/hero.png` was a 43-byte text file, causing `NoImageMetadata` build errors.
6. **Unused dependencies** — `lodash`, `moment`, `jquery` installed but never imported (noted, not removed to avoid downstream breakage).

### Fixes Applied
- Deferred Google Fonts with `media="print" onload="this.media='all'"` + noscript fallback
- Added `viewport` and `description` meta tags
- Set hero `fetchpriority="high"`, thumbnails `loading="lazy"`
- Added `densities={[1, 2]}` to all Astro Image components for retina srcsets
- Replaced raw `<img>` with Astro `<Image>` component
- Replaced broken placeholder with a real image

## Verification Results

### Build
- `npm run build`: PASS (1 page, 3 optimized images)
- `npx astro check`: PASS (0 errors, 0 warnings, 0 hints)

### Lighthouse (Mobile)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Performance | 84 | 100 | +16 |
| Accessibility | 92 | 100 | +8 |
| SEO | 100 | 100 | — |
| FCP | 2.3 s | 0.7 s | -70% |
| LCP | 3.6 s | 1.4 s | -61% |
| Speed Index | 5.1 s | 0.7 s | -86% |
| TTI | 3.6 s | 1.5 s | -58% |
| CLS | 0.001 | 0 | -100% |

## Files Changed
- `src/layouts/Layout.astro`
- `src/components/Gallery.astro`
- `src/pages/index.astro`
- `src/assets/hero.png`

## Commit
`73b7130` — perf(site): optimize images, fonts, and layout for Core Web Vitals

## Outputs Saved
- `scan-report.md` — Full audit findings
- `fixes-applied.md` — Detailed fix list with Lighthouse deltas
- `build-output.txt` — Build and type-check logs
- `git-log.txt` — Commit history
- `lighthouse-before.json` — Raw Lighthouse data (before)
- `lighthouse-after.json` — Raw Lighthouse data (after)
