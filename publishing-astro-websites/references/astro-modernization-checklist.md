# Astro v6 Modernization Checklist

Use this checklist when upgrading from Astro 4/5 to Astro 6, or when modernizing an older Astro codebase. Run through all sections in order.

---

## Pre-Upgrade Web Research

> **MANDATORY.** Fetch the latest Astro v6 upgrade guide via Context7 before starting.

```
mcp__context7__query_docs: "Astro 6 migration guide from v5 breaking changes 2025"
mcp__context7__query_docs: "Astro 6 Tailwind CSS v4 upgrade path"
mcp__context7__query_docs: "Astro 6 ViewTransitions ClientRouter migration"
```

Also search for any recently deprecated packages:
```
WebSearch: "Astro 6 deprecated packages migration 2025"
```

## Pre-Upgrade

- [ ] Pin current working state: `git log --oneline -1` (note the commit hash)
- [ ] Ensure clean working tree: `git status` should show no uncommitted changes
- [ ] Run current build: `npm run build` — must pass before any changes
- [ ] Note current versions: `npm list astro @astrojs/tailwind tailwindcss`

---

## Dependency Upgrade

### Core packages
```bash
npm install astro@latest @astrojs/tailwind@latest
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
```

### Check integration compatibility
- [ ] All `@astrojs/*` integrations updated to latest
- [ ] Third-party integrations (e.g., `astro-icon`, `astro-compress`) support Astro 6
- [ ] No peer dependency warnings after upgrade

### Remove deprecated packages
- [ ] Remove `@astrojs/image` if present (built-in `astro:assets` replaces it)
- [ ] Remove manual `sharp` installation if using built-in image optimization

**Detection**: `npm ls` should show no deprecated or extraneous packages

---

## Configuration Migration

### astro.config.mjs
- [ ] `output: 'static'` is set (or `output: 'server'` / `hybrid` as needed)
- [ ] `site` is set for production URL (needed for `astro:assets` and sitemap)
- [ ] Image configuration uses new Astro 6 format if customized:
  ```js
  image: {
    domains: ['example.com'],
    remotePatterns: [{ protocol: 'https' }],
  }
  ```

### TypeScript
- [ ] `tsconfig.json` uses `"moduleResolution": "bundler"`
- [ ] `tsconfig.json` includes `"strict": true` recommended
- [ ] No `@ts-ignore` suppressions for Astro types

---

## Code Migration

### Images (Critical)
Astro 6 has built-in image optimization via `astro:assets`.

- [ ] Replace `@astrojs/image` imports with `astro:assets`
  ```astro
  --- before ---
  import { Image } from '@astrojs/image/components';
  --- after ---
  import { Image } from 'astro:assets';
  ```
- [ ] Remove `format="webp"` from `<Image>` tags (Astro 6 auto-selects best format)
- [ ] Ensure all local images have valid paths (relative or aliased)
- [ ] External images must be whitelisted in `astro.config.mjs` `image.domains` or `image.remotePatterns`

### ViewTransitions → ClientRouter
- [ ] Replace all `ViewTransitions` with `ClientRouter`
  ```astro
  --- before ---
  import { ViewTransitions } from 'astro:transitions';
  --- after ---
  import { ClientRouter } from 'astro:transitions';
  ```

### Content Collections
- [ ] Replace `Astro.glob()` with `getCollection()` where applicable
- [ ] Ensure `src/content/config.ts` defines collections with `z.object()` schemas
- [ ] Update dynamic routes to use `getStaticPaths` with `getCollection`

**Example migration:**
```astro
--- before ---
const posts = await Astro.glob('../content/blog/*.md');
--- after ---
import { getCollection } from 'astro:content';
const posts = await getCollection('blog');
```

### Tailwind CSS v3 → v4
If upgrading Tailwind from v3 to v4:
- [ ] Replace `tailwind.config.js` with inline config in CSS (v4 uses CSS-based config)
- [ ] Update `@tailwind` directives to `@import 'tailwindcss'`
- [ ] Migrate custom theme values from `tailwind.config.js` to `@theme` in CSS
- [ ] Remove `postcss.config.js` if using Vite integration (Tailwind v4 has built-in Vite plugin)

**v3 → v4 CSS migration:**
```css
/* before */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* after */
@import 'tailwindcss';
@theme {
  --color-primary: oklch(55% 0.15 255);
  --font-sans: 'Inter', ui-sans-serif, system-ui;
}
```

---

## Post-Upgrade Verification

### Build check
```bash
npm run build
```
- [ ] Zero build errors
- [ ] No warnings about deprecated APIs

### Type check
```bash
npx astro check
```
- [ ] Zero TypeScript errors

### Runtime check
```bash
npm run preview
```
- [ ] Homepage loads correctly
- [ ] All internal links work
- [ ] Images load and are optimized
- [ ] No console errors

### Visual regression
- [ ] No layout shifts compared to pre-upgrade
- [ ] Fonts load correctly
- [ ] Dark/light mode (if applicable) works
- [ ] Mobile viewport renders correctly

---

## Rollback Plan

If the upgrade fails catastrophically:

```bash
git stash  # stash any WIP changes
git checkout <pre-upgrade-commit-hash>  # return to known-good state
npm install  # reinstall old dependencies
npm run build  # verify old state still builds
```

---

## Common Upgrade Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find module 'astro:assets'` | Astro not upgraded to v6 | `npm install astro@latest` |
| `Image format must not be specified` | Astro 6 rejects explicit `format` | Remove `format` prop from `<Image>` |
| `getStaticPaths()` required | Dynamic route without params | Add `getStaticPaths` with `getCollection` |
| `ViewTransitions is not exported` | Old import name | Change to `ClientRouter` |
| Tailwind classes not applied | v3 → v4 config mismatch | Migrate config to `@theme` in CSS |
| `sharp` installation error | Missing native dependency | `npm install sharp` or use `npm config set sharp_binary_host` |
