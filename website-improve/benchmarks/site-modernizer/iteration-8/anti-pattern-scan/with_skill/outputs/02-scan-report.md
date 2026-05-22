# Anti-Pattern Scan Report

## Scan Date: 2026-05-14
## Scanner: site-modernizer skill (SCAN phase)

---

### 5.1 Build & Type Safety
- [x] `npx astro check` — **2 errors** (TS2339: Property 'frontmatter'/'url' does not exist on type 'unknown')
- [x] `npm run build` — **PASS** (after clean install)
- [ ] `dist/` structure — only `index.html`, no locale routes, no 404.html

### 5.2 Astro 6.x Convergence
- [x] `import.meta.glob()` found in `src/pages/index.astro:5` — **ANTI-PATTERN**
  - Should use Content Collections (`getCollection`) or typed glob
- [x] `<Image format="webp">` found in `src/components/Gallery.astro:7` — **ANTI-PATTERN**
- [x] `<Image format="avif">` found in `src/components/Gallery.astro:8` — **ANTI-PATTERN**
  - Astro 6 / Sharp auto-optimizes format; remove `format` prop
- [x] `define:vars` on `<style>` found in `src/pages/index.astro:17` — **ANTI-PATTERN**
  - Should use CSS custom properties via `:root` or inline style
- [ ] `ClientRouter` vs `ViewTransitions` — `ClientRouter` is used (correct for Astro 4+)
- [ ] `is:inline` — not found
- [ ] Tailwind v4 — using v3 with `@astrojs/tailwind`

### 5.3 Code Quality
- [x] Unused `ClientRouter` import in `index.astro` if no transitions used
- [x] Type-unsafe `import.meta.glob` result (no generic type parameter)

### 5.4 Routing & Configuration
- [ ] `prefixDefaultLocale: false` — root `index.astro` may conflict with i18n auto-redirect
- [ ] No `getStaticPaths()` for locale routing
- [ ] No 404 page

### 5.5 SEO & Structured Data
- [ ] Missing `og:title`, `og:description`, `og:image`, `og:url`
- [ ] Missing canonical URL
- [ ] Missing `theme-color`
- [ ] No sitemap integration

### 5.6 Performance & Assets
- [ ] No local fonts configured
- [ ] No `loading="lazy"` on images

### 5.7 i18n Synchronization
- [ ] No i18n JSON files found
- [ ] Hardcoded text in components ("Old Site")

### 5.8 Security
- [x] No hardcoded secrets found
- [x] No inline event handlers with user input

---

## Fix Plan
1. Replace `import.meta.glob` with typed array (mock data since no posts/ dir)
2. Remove `format` prop from `<Image>` components
3. Replace `define:vars` with CSS custom property in `:root`
4. Fix TS types for posts array
5. Add basic SEO meta tags to Layout
6. Re-run `astro check` and `npm run build`
7. Commit via `smart-autopush.sh`
