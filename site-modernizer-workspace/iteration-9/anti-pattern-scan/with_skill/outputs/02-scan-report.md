# Anti-Pattern Scan Report

## Build & Type Safety
- [x] `npx astro check` passes (0 TS errors) — YES, 0 errors, 4 deprecation hints
- [x] `npm run build` passes (0 build errors) — YES (after adding placeholder posts)
- [ ] `dist/` output structure is correct — PARTIAL (only root index + posts)

## Astro 5.x/6.x Convergence
- [ ] No `Astro.glob()` — **FOUND** in src/pages/index.astro:5
- [ ] No `<Image format="...">` — **FOUND** in src/components/Gallery.astro:7-8
- [ ] `ClientRouter` not `ViewTransitions` — **FOUND** deprecated import in src/pages/index.astro
- [ ] No `define:vars` on `<style>` — **FOUND** in src/pages/index.astro:21
- [ ] `prefixDefaultLocale` configured correctly — PARTIAL (set to false, no `[lang]` routes)
- [ ] No inline `<script>` with complex logic — OK
- [ ] Tailwind v4 uses `@tailwindcss/vite` — NOT APPLICABLE (still on v3)
- [ ] No `is:inline` script artifacts — OK

## Code Quality
- [ ] No unused imports — OK
- [ ] No `any` type casts — OK
- [ ] No hardcoded bilingual text — N/A (single language)
- [ ] No duplicate event bindings — OK

## Routing & Configuration
- [ ] `astro.config.mjs` i18n routing correct — PARTIAL
- [ ] Root `index.astro` redirect doesn't conflict — N/A
- [ ] `getStaticPaths()` covers locales — MISSING
- [ ] 404 page supports i18n fallback — MISSING

## SEO & Structured Data
- [ ] Open Graph tags present — MISSING
- [ ] Twitter Card tags — MISSING
- [ ] Canonical URL — MISSING
- [ ] Schema.org JSON-LD — MISSING
- [ ] `theme-color` meta — MISSING
- [ ] Sitemap generated — MISSING

## Performance & Assets
- [ ] Fonts loaded locally — N/A
- [ ] Image loading attributes — MISSING
- [ ] No unused dependencies — OK
- [ ] CSS uses `@theme` — N/A (Tailwind v3)
- [ ] Font files exist — N/A

## i18n Synchronization
- [ ] `en.json` and `zh.json` identical keys — MISSING
- [ ] No hardcoded captions — N/A
- [ ] `Intl` helpers — N/A

## Security
- [ ] No hardcoded secrets — OK
- [ ] No injection vectors — OK
- [ ] No inline event handlers — OK

## Summary
| Category | Issues | Severity |
|----------|--------|----------|
| Astro 5.x/6.x Convergence | 4 | HIGH |
| Routing & Configuration | 3 | MEDIUM |
| SEO & Structured Data | 6 | LOW |
| Performance & Assets | 2 | LOW |
| i18n | 3 | LOW |
| Security | 0 | — |
