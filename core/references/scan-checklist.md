# SCAN Checklist — Comprehensive Audit & Anti-Pattern Detection

Load this reference when the user asks for:
- Anti-pattern scan / 反模式扫描
- Site audit / 站点审计
- Modernization check / 现代化检查
- Build or type-safety issues

## 0. Pre-Scan Web Research — MANDATORY

> Run these lookups **before** applying any patterns flagged in this scan. Official docs are the source of truth; this skill file may be stale.

### Astro 6.x (framework patterns)
```
# Use Context7 for official docs — always prefer official over training data
mcp__context7__query_docs: "Astro 6 ClientRouter view-transition navigation auto"
mcp__context7__query_docs: "Astro 6 Content Collections latest patterns 2025"
mcp__context7__query_docs: "Astro 6 Tailwind CSS v4 integration best practices"
```

### Tailwind CSS v4 (theming, dark mode)
```
mcp__context7__query_docs: "Tailwind CSS v4 @theme dark mode best practices"
mcp__context7__query_docs: "Tailwind CSS v4 custom variants and Oklch colors"
```

### PWA (manifest, service worker, maskable icons)
```
mcp__context7__query_docs: "PWA manifest maskable icon safe area 2025"
WebSearch: "web app manifest maskable icon MDN 2025"
```

### @fontsource (local fonts)
```
mcp__context7__query_docs: "@fontsource local fonts Astro static site integration"
```

### Output
After each lookup, note 1-2 concrete findings (e.g., "ViewTransitions renamed to ClientRouter in Astro 4+", "Tailwind v4 uses @theme block not tailwind.config.mjs"). Use these to validate or override the patterns listed below.

## Workflow Reminder

**Scanning is not a read-only report — it is the first half of a fix workflow.**
After documenting findings, you MUST apply the fixes, verify the build, and commit the changes.
The full SCAN workflow is: scan → fix → build-verify → commit.

## 5.1 Build & Type Safety
- [ ] `npx astro check` passes (0 TS errors)
- [ ] `npm run build` passes (0 build errors)
- [ ] `dist/` output structure is correct (index.html, 404.html, locale routes)

## 5.2 Astro 6.x Convergence
- [ ] No `Astro.glob()` — use Content Collections (`getCollection`)
- [ ] No `<Image format="...">` — let Sharp decide
- [ ] `ClientRouter` not `ViewTransitions`
- [ ] No `define:vars` on `<style>` — use CSS custom properties
- [ ] `prefixDefaultLocale` configured correctly for i18n
- [ ] No inline `<script>` with complex logic — use `.js` imports
- [ ] Tailwind v4 uses `@tailwindcss/vite` not `@astrojs/tailwind`
- [ ] No `is:inline` script artifacts in `dist/`

## 5.3 Code Quality
- [ ] No unused imports or variables (check TS hints)
- [ ] No `any` type casts without comment
- [ ] No hardcoded bilingual text in components — must come from i18n JSON
- [ ] No duplicate event bindings or leaked listeners

## 5.4 Routing & Configuration
- [ ] `astro.config.mjs` i18n routing is correct (`defaultLocale`, `prefixDefaultLocale`)
- [ ] Root `index.astro` redirect doesn't conflict with i18n auto-redirect
- [ ] `getStaticPaths()` covers all declared locales
- [ ] 404 page supports i18n fallback

## 5.5 SEO & Structured Data
- [ ] Open Graph tags present: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- [ ] Twitter Card tags present (if applicable)
- [ ] Canonical URL (`link rel="canonical"`) on every page
- [ ] Schema.org `application/ld+json` for papers/projects (ScholarlyArticle)
- [ ] `theme-color` meta tag supports light/dark
- [ ] Sitemap generated (`@astrojs/sitemap`)

## 5.6 Performance & Assets
- [ ] Fonts loaded locally (`@fontsource/*`), not from CDN
  - **Fix**: Remove `<link href="https://fonts.googleapis.com/...">` from Layout.astro
  - **Fix**: `npm install @fontsource/inter` (or appropriate family)
  - **Fix**: Import font CSS in Layout.astro: `import '@fontsource/inter/400.css'`
- [ ] Images use `loading="eager"` only above fold, `loading="lazy"` below
  - **Fix**: First/hero image may stay `eager`; ALL others MUST be `loading="lazy"`
  - **Fix**: Also add `decoding="async"` to non-hero images
- [ ] No unused dependencies in `package.json`
  - **Fix**: `grep -r "from 'lodash'\|from 'moment'\|from 'jquery'" src/` — if no matches, `npm uninstall lodash moment jquery`
  - **Fix**: Remove any dependency not imported by any source file
- [ ] CSS uses `@theme` block (Tailwind v4), no legacy `tailwind.config.mjs`
- [ ] Font files exist where `@font-face` points (check `dist/` for `.woff2`)

## 5.7 i18n Synchronization
- [ ] `en.json` and `zh.json` have identical key sets
- [ ] No hardcoded captions/labels in components — all via `t()` or JSON
- [ ] Locale-specific content (dates, numbers) uses `Intl` helpers

## 5.8 Security
- [ ] No hardcoded secrets, API keys, or tokens
- [ ] No SQL/command injection vectors (static sites: check `server:` routes if any)
- [ ] No inline event handlers with user input (`onclick="..."`)

## After SCAN Fixes

After applying any fixes found during SCAN:

1. Re-run `npm run build` and `npx astro check` to confirm zero errors
2. Stage all changes: `git add -A`
3. **EXECUTE** the commit via `smart-autopush.sh` with a Conventional Commits message describing WHAT was audited/fixed and WHY
   - Example: `bash scripts/smart-autopush.sh . "refactor(site): migrate Astro.glob to Content Collections and upgrade Tailwind to v4" done`
4. **NEVER skip the commit step.** Even in test, mock, or evaluation repos, you MUST physically run the commit command. Do not assume the script is a no-op — execute it and report the result.
