# Astro Build Report

**Project:** mock-repo (anti-pattern-scan/without_skill)
**Date:** 2026-05-17
**Working Directory:** `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-20/anti-pattern-scan/without_skill/mock-repo`

## Build Status: PASSED

### npm install
- Added 1 package
- 168 packages looking for funding
- Duration: ~4s

### npm run build
- Astro v5 build successful
- Output: static mode
- Duration: 1.25s
- Pages built: 2
  - `/index.html`
  - `/posts/hello/index.html`

### Output Artifacts
| File | Size | Gzip |
|------|------|------|
| `ClientRouter.astro_astro_type_script_index_0_lang.CDGfc0hd.js` | 15.36 kB | 5.31 kB |

## Anti-pattern Analysis

### FOUC Check
**Result: NO FOUC RISK**
- CSS is inlined in `<head>` via Astro's scoped styles
- No external stylesheet links that could cause flash
- `<h1>` styling is inlined: `h1[data-astro-cid-j7pv25f6]{color:#3b82f6}`

### Layout Issues
**Result: NONE DETECTED**
- Simple static site structure
- No complex grid/flex layouts that could cause cross-browser issues
- View transitions enabled via `<ClientRouter />` (optional progressive enhancement)

## Commit Status
**No changes to commit** - build artifacts match expected output, no source files modified.

## Summary

| Check | Status |
|-------|--------|
| Build | PASSED |
| FOUC Risk | LOW (inline CSS) |
| Layout Issues | NONE |
| Changes to Commit | NO |