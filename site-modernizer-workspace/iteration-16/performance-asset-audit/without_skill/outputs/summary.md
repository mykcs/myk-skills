# Performance Audit Summary (without skill)

## Issues Found

1. **Unused heavy dependencies** — `package.json` included `lodash`, `moment`, and `jquery` which are never imported by the site. These bloat install size and can slow CI / cold starts.
2. **No image lazy-loading** — All `<Image>` components in `Gallery.astro` used `loading="eager"`, forcing the browser to download every image immediately even though most are below the fold.
3. **Remote `<img>` without lazy-loading or dimensions** — `index.astro` used a bare `<img>` tag with no `loading="lazy"`, `width`, or `height`, causing layout shift and unnecessary early network requests.
4. **Render-blocking Google Fonts** — The font stylesheet was loaded synchronously in `<head>`, blocking first paint.
5. **Corrupt placeholder image** — `src/assets/hero.png` was a text file, causing Astro image optimization to fail at build time.

## Fixes Applied

| File | Change |
|------|--------|
| `package.json` | Removed `lodash`, `moment`, `jquery` |
| `src/components/Gallery.astro` | Changed 3 thumbnail `<Image>` tags from `loading="eager"` to `loading="lazy"` |
| `src/pages/index.astro` | Added `loading="lazy" width="800" height="600"` to remote `<img>` |
| `src/layouts/Layout.astro` | Converted Google Fonts `<link>` to `rel="preload"` + `onload` trick with `<noscript>` fallback |
| `src/assets/hero.png` | Replaced text placeholder with a valid 800×600 PNG |

## Verification

- `npm run build` passes successfully.
- Astro optimized the hero image to WebP (0 kB output due to solid color).
