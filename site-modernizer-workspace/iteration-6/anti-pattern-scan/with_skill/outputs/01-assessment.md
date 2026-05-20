# Site Modernizer Skill — ASSESS Phase Output

## Project Overview

| Property | Value |
|----------|-------|
| **Project** | mock-anti-pattern-site |
| **Astro Version** | 5.18.1 (installed), declared ^5.0.0 in package.json |
| **Tailwind Version** | 3.4.19 (installed), declared ^3.4.0 in package.json |
| **Output Mode** | static |
| **i18n Config** | locales: ['en', 'zh'], defaultLocale: 'zh', prefixDefaultLocale: false |
| **Integrations** | [] (none registered) |

## Files Scanned

- `astro.config.mjs`
- `package.json`
- `src/pages/index.astro`
- `src/layouts/Layout.astro`
- `src/components/Gallery.astro`

## Common Smells Detected

| Smell | File | Action Required |
|-------|------|-----------------|
| `Astro.glob()` usage | `src/pages/index.astro:5` | Replace with Content Collections |
| `<Image format="...">` | `src/components/Gallery.astro:7-8` | Remove format attr (Astro 6 auto-optimizes) |
| `ViewTransitions` import | `src/pages/index.astro:3,11` | Replace with `ClientRouter` (Astro 4+) |
| `define:vars` on `<style>` | `src/pages/index.astro:21` | Use CSS custom properties instead |
| `@astrojs/tailwind` integration | `package.json` | Upgrade to Tailwind v4 with `@tailwindcss/vite` |
| Missing Content Collections | N/A | Create `src/content/` for `Astro.glob` migration |
| Missing SEO tags | All pages | Add Open Graph, canonical, structured data |
| Missing i18n JSON | N/A | No i18n translation system detected |
| Missing sitemap | N/A | Add `@astrojs/sitemap` integration |
