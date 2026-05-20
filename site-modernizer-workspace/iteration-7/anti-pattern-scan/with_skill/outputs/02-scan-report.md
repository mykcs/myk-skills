# Anti-Pattern Scan Report

## Scan Methodology
Following the site-modernizer skill SCAN checklist (sections 5.1–5.8), all source files were audited against Astro 6.x convergence criteria.

## Findings Summary

| # | Category | File | Anti-Pattern | Severity | Status |
|---|----------|------|--------------|----------|--------|
| 1 | Astro 6.x | `src/pages/index.astro` | `Astro.glob()` — deprecated, no matching files | P0 | Fixed |
| 2 | Astro 6.x | `src/components/Gallery.astro` | `<Image format="webp">` and `<Image format="avif">` — Sharp auto-optimizes | P0 | Fixed |
| 3 | Astro 6.x | `src/pages/index.astro` | `ViewTransitions` import — replaced by `ClientRouter` in Astro 4+ | P0 | Fixed |
| 4 | Astro 6.x | `src/pages/index.astro` | `define:vars` on `<style>` — use CSS custom properties instead | P0 | Fixed |
| 5 | Routing | `src/pages/index.astro` | Duplicate `<html>` wrapper (Layout already emits `<html>`) | P1 | Fixed |
| 6 | SEO | `src/pages/index.astro` | Missing `og:title`, `og:description`, canonical, `theme-color` | P1 | Fixed |
| 7 | i18n | `src/layouts/Layout.astro` | `lang="zh"` hardcoded — should accept locale prop | P1 | Fixed |
| 8 | Type Safety | `src/pages/index.astro` | Implicit `any` on `posts.map(p => ...)` | P2 | Fixed |

## New Files Created
| File | Purpose |
|------|---------|
| `src/content/config.ts` | Content Collections schema definition |
| `src/content/posts/hello.md` | Sample post for Content Collections |

## Verification Results
- `npm run build`: PASS (0 errors)
- `npx astro check`: PASS (0 errors, 0 warnings, 0 hints)
