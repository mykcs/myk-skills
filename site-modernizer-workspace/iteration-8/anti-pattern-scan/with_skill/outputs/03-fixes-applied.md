# Fixes Applied

## Commit
- **Hash**: `947cdb6`
- **Message**: `refactor(site): fix Astro anti-patterns — remove format prop from Image, replace define:vars with CSS custom properties, type-safe posts array, add SEO meta tags`

## Files Modified

### 1. `src/pages/index.astro`
- **Anti-pattern**: `import.meta.glob()` with untyped result + `define:vars` on `<style>`
- **Fix**:
  - Replaced `import.meta.glob('./posts/*.md', { eager: true })` with typed `Post[]` array
  - Removed `define:vars={{ themeColor }}` from `<style>`
  - Added `:root { --theme-color: #3b82f6; }` CSS custom property
  - Wrapped `ClientRouter` in `<Fragment slot="head">` for Layout head injection
  - Removed unused `themeColor` variable

### 2. `src/components/Gallery.astro`
- **Anti-pattern**: `<Image format="webp">` and `<Image format="avif">`
- **Fix**:
  - Removed `format="webp"` from first `<Image>`
  - Removed `format="avif"` from second `<Image>`
  - Added `loading="eager"` to above-fold hero image
  - Added `loading="lazy"` to below-fold thumbnail

### 3. `src/layouts/Layout.astro`
- **Anti-pattern**: Missing SEO meta tags, no viewport, no canonical URL
- **Fix**:
  - Added `<meta name="viewport">`
  - Added `<link rel="canonical">` with `Astro.site` fallback
  - Added Open Graph tags: `og:title`, `og:type`, `og:url`
  - Added `<meta name="theme-color">`
  - Added `<slot name="head">` for page-level head injection

### 4. New files
- `.gitignore` — excludes `node_modules/`, `.astro/`, `dist/`, `.omc/`
- `src/assets/hero.png` — placeholder asset required by Gallery component

## Verification
- `npx astro check`: **0 errors, 0 warnings, 0 hints**
- `npm run build`: **PASS** (1 page, 2 optimized images)
