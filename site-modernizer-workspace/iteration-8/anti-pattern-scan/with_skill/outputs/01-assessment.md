# Site Modernizer Assessment

## Project Info
- **Path**: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-8/anti-pattern-scan/mock-repo`
- **Framework**: Astro 5.x
- **Output**: Static
- **Integrations**: None
- **i18n**: Configured (`en`, `zh`, default `zh`, `prefixDefaultLocale: false`)

## Files Scanned
- `src/pages/index.astro`
- `src/layouts/Layout.astro`
- `src/components/Gallery.astro`
- `astro.config.mjs`
- `package.json`

## Findings Summary
| # | Issue | Severity | Category |
|---|-------|----------|----------|
| 1 | `import.meta.glob()` used instead of Content Collections | HIGH | Astro 6 Convergence |
| 2 | `<Image format="...">` (webp, avif) — Astro 6 auto-optimizes | MED | Astro 6 Convergence |
| 3 | `define:vars` on `<style>` — deprecated pattern | MED | Astro 6 Convergence |
| 4 | `astro check` fails with TS errors (`unknown` type on glob result) | HIGH | Type Safety |
| 5 | Missing `posts/` directory referenced by glob | MED | Build Integrity |
| 6 | No Open Graph / SEO meta tags | LOW | SEO |
| 7 | No canonical URL | LOW | SEO |
| 8 | No sitemap integration | LOW | SEO |
| 9 | `@astrojs/tailwind` v5 + Tailwind v3 — should upgrade to v4 | LOW | Dependencies |

## Build Status
- `npm run build`: PASS (after clean install)
- `npx astro check`: FAIL (2 TS errors)
