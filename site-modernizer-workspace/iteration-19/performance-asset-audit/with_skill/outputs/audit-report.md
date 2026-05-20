# Performance & Asset Audit Report

**Project:** mock-perf-site  
**Date:** 2026-05-15  
**Auditor:** site-modernizer skill (SCAN phase)  

---

## 1. Findings Summary

| Category | Finding | Severity | Status |
|----------|---------|----------|--------|
| Assets | Corrupt `hero.png` (26B ASCII text) | HIGH | Fixed |
| Fonts | Google Fonts CDN links blocking render | HIGH | Fixed |
| Dependencies | `lodash`, `moment`, `jquery` unused in `src/` | MED | Fixed |
| Images | Remote `<img>` missing `decoding="async"` | LOW | Fixed |

---

## 2. Detailed Findings

### 2.1 Corrupt Image Asset (HIGH)
- **File:** `src/assets/hero.png`
- **Issue:** File was 26 bytes of ASCII text (`corrupt image placeholder`), not a valid PNG. Astro build failed with `NoImageMetadata` / `pngload_buffer: invalid scanline filter`.
- **Fix:** Replaced with a valid 800x600 PNG generated via Python.

### 2.2 Google Fonts CDN Render-Blocking (HIGH)
- **File:** `src/layouts/Layout.astro`
- **Issue:** Three `<link>` tags to `fonts.googleapis.com` / `fonts.gstatic.com` caused external DNS + TLS + download on every cold load, blocking first paint.
- **Fix:**
  1. Installed `@fontsource/inter`.
  2. Removed all Google Fonts `<link>` tags.
  3. Added local CSS imports inside `<script>`:
     ```astro
     <script>
       import '@fontsource/inter/400.css';
       import '@fontsource/inter/600.css';
       import '@fontsource/inter/700.css';
     </script>
     ```
  4. Build now self-hosts only the needed font subsets (~7 kB CSS + woff2).

### 2.3 Unused Dependencies (MED)
- **File:** `package.json`
- **Issue:** `lodash`, `moment`, `jquery` listed in `dependencies` but zero imports in `src/`.
- **Fix:** `npm uninstall lodash moment jquery`.
- **Impact:** Faster install, smaller `node_modules`, reduced attack surface.

### 2.4 Missing Image Decoding Hint (LOW)
- **File:** `src/pages/index.astro`
- **Issue:** Remote `<img>` had `loading="lazy"` but no `decoding="async"`.
- **Fix:** Added `decoding="async"` to the remote image tag.

---

## 3. Build Verification

```
$ npm run build
> astro build
[build] 1 page(s) built in ~530 ms
[build] Complete!
```

- Zero errors.
- Image optimization produced WebP variants.
- Font subsets emitted to `dist/_astro/`.

---

## 4. Files Modified

1. `src/assets/hero.png` — regenerated valid PNG
2. `src/layouts/Layout.astro` — replaced Google Fonts CDN with `@fontsource/inter`
3. `src/pages/index.astro` — added `decoding="async"` to remote image
4. `package.json` — removed `lodash`, `moment`, `jquery`
5. `package-lock.json` — updated after dependency changes

---

## 5. Recommendations (Not Addressed)

| Item | Why |
|------|-----|
| Add `astro check` to CI | Catches TypeScript / Astro errors early |
| Subset `@fontsource/inter` further | Only Latin + Latin-Ext needed for zh site; saves ~100 kB of unused Cyrillic/Greek woff2 |
| Add `width`/`height` to Astro `<Image>` | Prevents layout shift (already present) |
| Consider `fetchpriority="high"` on hero | If LCP is the hero image |
