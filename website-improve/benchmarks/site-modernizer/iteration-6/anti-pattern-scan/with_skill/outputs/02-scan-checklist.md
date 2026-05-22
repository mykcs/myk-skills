# Site Modernizer Skill — SCAN Phase Checklist Output

## 5.1 Build & Type Safety

- [x] `npx astro check` — **4 hints** (0 errors, 0 warnings)
  - `ViewTransitions` is deprecated (src/pages/index.astro:3, 11)
  - `Astro.glob` signature is deprecated (src/pages/index.astro:5)
  - `glob` is deprecated (src/pages/index.astro:5)
- [ ] `npm run build` — **FAILS** with `AstroGlobNoMatch` error
  - `Astro.glob('./posts/*.md')` did not return any matching files
  - Pattern has no matching files in `src/pages/posts/`
- [ ] `dist/` output structure — build fails, cannot verify

## 5.2 Astro 6.x Convergence

- [ ] **No `Astro.glob()`** — FOUND: `src/pages/index.astro:5`
  - `const posts = await Astro.glob('./posts/*.md');`
  - Must migrate to Content Collections (`getCollection`)
- [ ] **No `<Image format="...">`** — FOUND: `src/components/Gallery.astro:7-8`
  - `<Image src={hero} format="webp" ... />`
  - `<Image src={hero} format="avif" ... />`
  - Must remove `format` attribute (let Sharp decide)
- [ ] **`ClientRouter` not `ViewTransitions`** — FOUND: `src/pages/index.astro:3,11`
  - `import { ViewTransitions } from 'astro:transitions';`
  - `<ViewTransitions />`
  - Must replace with `ClientRouter`
- [ ] **No `define:vars` on `<style>`** — FOUND: `src/pages/index.astro:21`
  - `<style define:vars={{ themeColor }}>`
  - Must use CSS custom properties
- [ ] **`prefixDefaultLocale` configured correctly** — ISSUE: `prefixDefaultLocale: false`
  - For Astro 6 i18n best practices, consider `true` for consistent URLs
- [x] **No inline `<script>` with complex logic** — OK
- [ ] **Tailwind v4 uses `@tailwindcss/vite`** — ISSUE: using `@astrojs/tailwind` v5.1.5
  - Must upgrade to Tailwind v4 + `@tailwindcss/vite`
- [x] **No `is:inline` script artifacts** — OK (none found)

## 5.3 Code Quality

- [x] **No unused imports or variables** — OK
- [x] **No `any` type casts** — OK
- [ ] **No hardcoded bilingual text** — ISSUE: `src/pages/index.astro:14` has `<h1>Old Site</h1>` hardcoded
- [x] **No duplicate event bindings or leaked listeners** — OK

## 5.4 Routing & Configuration

- [ ] **`astro.config.mjs` i18n routing** — ISSUE: `prefixDefaultLocale: false`
  - Root `index.astro` may conflict with i18n auto-redirect
- [ ] **Root `index.astro` redirect** — No redirect found
- [ ] **`getStaticPaths()` covers all locales** — No `getStaticPaths` found
- [ ] **404 page supports i18n fallback** — No 404 page found

## 5.5 SEO & Structured Data

- [ ] **Open Graph tags** — MISSING: no `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- [ ] **Twitter Card tags** — MISSING
- [ ] **Canonical URL** — MISSING: no `link rel="canonical"`
- [ ] **Schema.org structured data** — MISSING: no `application/ld+json`
- [ ] **`theme-color` meta tag** — MISSING
- [ ] **Sitemap generated** — MISSING: no `@astrojs/sitemap` integration

## 5.6 Performance & Assets

- [ ] **Fonts loaded locally** — No `@fontsource/*` packages found
- [ ] **Image loading attributes** — No `loading="eager"` or `loading="lazy"` found
- [ ] **No unused dependencies** — OK (minimal deps)
- [ ] **CSS uses `@theme` block** — ISSUE: Tailwind v3, no `@theme` block
- [ ] **Font files exist in dist** — N/A (no local fonts configured)

## 5.7 i18n Synchronization

- [ ] **`en.json` and `zh.json` identical keys** — No i18n JSON files found
- [ ] **No hardcoded captions/labels** — ISSUE: `<h1>Old Site</h1>` is hardcoded
- [ ] **Locale-specific content uses `Intl`** — No `Intl` usage found

## 5.8 Security

- [x] **No hardcoded secrets** — OK
- [x] **No SQL/command injection vectors** — OK (static site)
- [x] **No inline event handlers with user input** — OK
