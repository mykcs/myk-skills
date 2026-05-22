# Site Modernizer Skill — Prioritized Findings

## P0 (Critical — Build-Breaking or Deprecated API)

### 1. Astro.glob() Deprecated + Build Failure
- **File**: `src/pages/index.astro:5`
- **Issue**: `const posts = await Astro.glob('./posts/*.md');`
- **Impact**: Build fails with `AstroGlobNoMatch` — no matching files in `./posts/*.md`
- **Fix**: Migrate to Content Collections (`src/content/posts/`) + `getCollection('posts')`
- **Skill Reference**: Section 5.2 — "No Astro.glob() — use Content Collections"

### 2. ViewTransitions Deprecated
- **File**: `src/pages/index.astro:3, 11`
- **Issue**: `import { ViewTransitions } from 'astro:transitions';` + `<ViewTransitions />`
- **Impact**: TypeScript hints flag as deprecated; will be removed in future Astro major
- **Fix**: Replace with `import { ClientRouter } from 'astro:transitions';` + `<ClientRouter />`
- **Skill Reference**: Section 5.2 — "ClientRouter not ViewTransitions"

### 3. Image format="..." Anti-Pattern
- **File**: `src/components/Gallery.astro:7-8`
- **Issue**: `<Image src={hero} format="webp" ... />` and `format="avif"`
- **Impact**: Astro 6 auto-optimizes; manual format forces suboptimal encoding
- **Fix**: Remove `format` attribute, let Sharp decide best format
- **Skill Reference**: Section 5.2 — "No <Image format=\"...\">"

### 4. define:vars on <style> Anti-Pattern
- **File**: `src/pages/index.astro:21`
- **Issue**: `<style define:vars={{ themeColor }}>`
- **Impact**: Deprecated pattern; use CSS custom properties instead
- **Fix**: Move theme color to `:root { --theme-color: #3b82f6; }` in global CSS
- **Skill Reference**: Section 5.2 — "No define:vars on <style>"

## P1 (High — Modernization Blockers)

### 5. Tailwind v3 + @astrojs/tailwind Legacy
- **File**: `package.json`
- **Issue**: `@astrojs/tailwind@5.1.5` + `tailwindcss@3.4.19`
- **Impact**: Not on Tailwind v4; `@astrojs/tailwind` is legacy integration
- **Fix**: Upgrade to `tailwindcss@^4.0.0` + `@tailwindcss/vite`
- **Skill Reference**: Section 5.2 — "Tailwind v4 uses @tailwindcss/vite"

### 6. Missing Content Collections
- **File**: N/A (directory missing)
- **Issue**: No `src/content/` directory; `Astro.glob` has no migration target
- **Impact**: Cannot modernize content queries without Content Collections setup
- **Fix**: Create `src/content/config.ts` + `src/content/posts/` collection
- **Skill Reference**: Section 5.2 — "No Astro.glob() — use Content Collections"

### 7. prefixDefaultLocale: false
- **File**: `astro.config.mjs:9`
- **Issue**: `prefixDefaultLocale: false`
- **Impact**: Root `/` serves Chinese directly; inconsistent with `/en/` pattern
- **Fix**: Consider `prefixDefaultLocale: true` for URL consistency
- **Skill Reference**: Section 5.4 — "astro.config.mjs i18n routing is correct"

## P2 (Medium — SEO / Quality of Life)

### 8. Missing SEO Tags
- **Files**: All pages
- **Issue**: No Open Graph, canonical, structured data, or theme-color
- **Impact**: Poor social sharing, SEO, and accessibility
- **Fix**: Add `<meta property="og:*">`, `<link rel="canonical">`, Schema.org JSON-LD
- **Skill Reference**: Section 5.5

### 9. Missing Sitemap
- **File**: `astro.config.mjs`
- **Issue**: No `@astrojs/sitemap` integration
- **Impact**: Search engines cannot discover all pages
- **Fix**: `npm i @astrojs/sitemap` + add to integrations array
- **Skill Reference**: Section 5.5 — "Sitemap generated"

### 10. Hardcoded Text
- **File**: `src/pages/index.astro:14`
- **Issue**: `<h1>Old Site</h1>` hardcoded English
- **Impact**: Not i18n-ready
- **Fix**: Use `t('site.title')` with i18n JSON files
- **Skill Reference**: Section 5.7 — "No hardcoded captions/labels"

### 11. Missing 404 Page
- **File**: N/A
- **Issue**: No `src/pages/404.astro`
- **Impact**: Default Astro 404, no i18n fallback
- **Fix**: Create bilingual 404 page
- **Skill Reference**: Section 5.4 — "404 page supports i18n fallback"

### 12. No Local Fonts
- **File**: N/A
- **Issue**: No `@fontsource/*` packages
- **Impact**: Potential FOUC if loading from CDN
- **Fix**: Install `@fontsource/inter` or preferred font
- **Skill Reference**: Section 5.6 — "Fonts loaded locally"
