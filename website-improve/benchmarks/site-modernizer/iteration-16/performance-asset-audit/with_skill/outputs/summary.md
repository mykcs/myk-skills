# Performance Audit Summary

## Issues Found & Fixed

### 1. Unused Dependencies (High Impact)
- **Removed**: `lodash`, `moment`, `jquery`
- **Why**: Zero imports in `src/`. These bloat bundle size and slow install time.
- **Result**: `package.json` now only contains `astro` and `@fontsource/inter`.

### 2. Google Fonts CDN (High Impact)
- **Before**: Layout loaded `fonts.googleapis.com` and `fonts.gstatic.com` via `<link>` tags.
- **After**: Replaced with local `@fontsource/inter` package (400/600/700 weights).
- **Why**: Eliminates external DNS + TLS + render-blocking font request chain.

### 3. Image Loading Strategy (Medium Impact)
- **Before**: All 4 images in `Gallery.astro` used `loading="eager"`.
- **After**: Only the hero image keeps `loading="eager"`; thumbnails switched to `loading="lazy" decoding="async"`.
- **Before**: Remote `<img>` in `index.astro` had no loading hints.
- **After**: Added `loading="lazy" decoding="async"`.
- **Why**: Prevents off-screen images from blocking initial page render.

### 4. Corrupt Asset (Build Blocker)
- **Found**: `src/assets/hero.png` was a 43-byte ASCII text file (placeholder), causing Astro image optimization to fail.
- **Fix**: Replaced with a valid 800x600 JPEG image.
- **Build result**: Astro successfully optimized it to WebP (49kB -> 35kB / 12kB).

## Build Verification

```
npm run build
```

- Status: **PASS** (0 errors, 1 page built, 2 images optimized)

## Files Modified

| File | Change |
|------|--------|
| `package.json` | Uninstalled `lodash`, `moment`, `jquery`; installed `@fontsource/inter` |
| `src/layouts/Layout.astro` | Removed Google Fonts `<link>` tags; added `@fontsource/inter` imports |
| `src/components/Gallery.astro` | Switched thumbnails to `loading="lazy" decoding="async"` |
| `src/pages/index.astro` | Added `loading="lazy" decoding="async"` to remote image |
| `src/assets/hero.png` | Replaced corrupt placeholder with valid image |
