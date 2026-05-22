# Performance Audit Report

**Project:** mock-perf-site  
**Date:** 2026-05-15  
**Auditor:** Claude Code Agent  

---

## Summary

| Category | Issues Found | Fixed |
|----------|-------------|-------|
| Unused Dependencies | 3 | 3 |
| Render-blocking Resources | 1 | 1 |
| Images without Lazy Loading | 0 | 0 |
| Broken/Corrupt Assets | 0 | 0 |

---

## Findings & Fixes

### 1. Unused Dependencies (HIGH)

**Issue:** `package.json` declared three heavy dependencies that were never imported or used anywhere in `src/`:

- `lodash` (~70 kB minified)
- `moment` (~290 kB minified, legacy)
- `jquery` (~87 kB minified)

**Impact:** Bloated `node_modules`, slower installs, larger lockfile, potential security surface area.

**Fix:** Removed all three from `dependencies`.

**File:** `package.json`

---

### 2. Render-blocking Google Fonts (MEDIUM)

**Issue:** The Google Fonts CSS link was loaded synchronously in `<head>`, blocking first paint until the font stylesheet downloaded.

```html
<!-- BEFORE -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
```

**Fix:** Applied the `media="print"` + `onload="this.media='all'"` async loading pattern with a `<noscript>` fallback. This is the standard web-performance technique for non-critical third-party CSS.

```html
<!-- AFTER -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet"></noscript>
```

**File:** `src/layouts/Layout.astro`

---

### 3. Images without Lazy Loading (NONE)

**Status:** No issues found.

- Gallery images use Astro `<Image />`, which automatically injects `loading="lazy"`, `decoding="async"`, and generates responsive WebP variants.
- The remote `<img>` on `index.astro` already had `loading="lazy"`.

---

### 4. Broken/Corrupt Asset Files (NONE)

**Status:** No issues found.

- `src/assets/hero.png` validated as valid PNG (800x600, 8-bit RGB, non-interlaced).
- Build image optimization completed successfully.

---

## Build Verification

```
> astro build
[build] 1 page(s) built in ~1.6s
[build] Complete!
```

- Build passes with zero errors.
- Generated `dist/index.html` correctly contains the async font loading markup.

---

## Committed Changes

```
9d44070 perf: remove unused deps (lodash, moment, jquery); async-load Google Fonts
 2 files changed, 3 insertions(+), 5 deletions(-)
```

**Files modified:**
- `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-19/performance-asset-audit/without_skill/mock-repo/package.json`
- `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-19/performance-asset-audit/without_skill/mock-repo/src/layouts/Layout.astro`
