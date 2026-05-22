# Site Modernizer Assessment Report

## Project Info
- **Path**: /tmp/site-modernizer-test-repo
- **Framework**: Astro 5.x
- **Build**: static output
- **i18n**: en, zh (default: zh, prefixDefaultLocale: false)
- **Tailwind**: v3.4 with @astrojs/tailwind

## Files Scanned
| File | Purpose |
|------|---------|
| astro.config.mjs | Framework config |
| package.json | Dependencies |
| src/components/Gallery.astro | Image gallery component |
| src/layouts/Layout.astro | Base layout |
| src/pages/index.astro | Homepage |

## Anti-Patterns Detected (Pre-Fix)

### P0 — Astro 6.x Convergence
1. **Astro.glob()** in `src/pages/index.astro` (line 5) — deprecated, should use Content Collections
2. **`<Image format="...">`** in `src/components/Gallery.astro` (lines 7-8) — `format="webp"` and `format="avif"` should be removed; Astro 6 / Sharp auto-optimizes
3. **`ViewTransitions`** import in `src/pages/index.astro` (line 3) — deprecated in Astro 4+, should use `ClientRouter`
4. **`define:vars` on `<style>`** in `src/pages/index.astro` (line 21) — should use CSS custom properties instead

### P1 — Routing & SEO
5. **Root `<html>` wrapper** in `src/pages/index.astro` (lines 9-19) — Layout already emits `<html>`, causing nested/duplicate `<html>` tags
6. **Missing SEO meta tags** — no `og:title`, `og:description`, canonical URL, or `theme-color`
7. **Layout lang hardcoded** to `zh` — should respect i18n locale

### P2 — Dependencies
8. **Tailwind v3 + @astrojs/tailwind** — should upgrade to Tailwind v4 with `@tailwindcss/vite`
