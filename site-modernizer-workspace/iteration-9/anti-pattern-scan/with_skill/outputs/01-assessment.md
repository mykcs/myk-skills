# Site Modernizer Assessment

## Project Info
- **Path**: /Users/myk/.claude/skills/site-modernizer-workspace/iteration-9/anti-pattern-scan/mock-repo
- **Framework**: Astro 5.x (detected from package.json)
- **Build Output**: static
- **Styling**: Tailwind CSS v3 (via @astrojs/tailwind)

## Files Scanned
- astro.config.mjs
- package.json
- src/pages/index.astro
- src/layouts/Layout.astro
- src/components/Gallery.astro
- scripts/smart-autopush.sh

## Identified Anti-Patterns & Modernization Items

### 1. Deprecated `ViewTransitions` import
- **Location**: src/pages/index.astro:3, src/pages/index.astro:11
- **Issue**: `ViewTransitions` is deprecated in Astro 4+; replaced by `ClientRouter`
- **Severity**: HIGH

### 2. Deprecated `Astro.glob()` usage
- **Location**: src/pages/index.astro:5
- **Issue**: `Astro.glob` is deprecated and will be removed in a future major version
- **Severity**: HIGH

### 3. `<Image format="...">` anti-pattern
- **Location**: src/components/Gallery.astro:7-8
- **Issue**: Explicit `format="webp"` and `format="avif"` on `<Image>` prevents Astro/Sharp from auto-optimizing
- **Severity**: MEDIUM

### 4. `define:vars` on `<style>` anti-pattern
- **Location**: src/pages/index.astro:21
- **Issue**: `define:vars` on `<style>` is discouraged; use CSS custom properties instead
- **Severity**: MEDIUM

### 5. Tailwind v3 with `@astrojs/tailwind`
- **Location**: package.json dependencies
- **Issue**: Astro 6 + Tailwind v4 prefers `@tailwindcss/vite` instead of `@astrojs/tailwind`
- **Severity**: LOW (Astro 5.x still supports v3)

### 6. Missing i18n routing files
- **Location**: src/pages/
- **Issue**: No `[lang]/` route structure; only root `index.astro` exists
- **Severity**: LOW

### 7. Missing assets referenced by Gallery
- **Location**: src/components/Gallery.astro imports `../assets/hero.png`
- **Issue**: `src/assets/` directory does not exist
- **Severity**: MEDIUM

### 8. Duplicate `<html>` / `<head>` tags
- **Location**: src/pages/index.astro
- **Issue**: Page has its own `<html>` and `<head>` wrapping `<Layout>`, which also renders `<html>`
- **Severity**: HIGH
