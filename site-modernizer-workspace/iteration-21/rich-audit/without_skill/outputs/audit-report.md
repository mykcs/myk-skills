# Rich Audit Report - mock-repo

**Repo:** mock-anti-pattern-site  
**Date:** 2026-05-17  
**Audit Type:** Full Anti-Pattern & Security Scan  
**Status:** Fixes applied and committed

---

## Summary

| Issue | Category | Severity | Location | Status |
|-------|----------|----------|----------|--------|
| Unused dependencies (@astrojs/tailwind, tailwindcss) | Performance | MEDIUM | package.json | Fixed |
| Missing viewport meta tag | Performance/Accessibility | MEDIUM | src/layouts/Layout.astro | Fixed |
| git commit || true swallows errors | Security | MEDIUM | scripts/smart-autopush.sh | Fixed |

---

## Fixes Applied

### 1. Remove Unused Dependencies (MEDIUM)

**File:** `package.json`

**Issue:** Project was declaring `@astrojs/tailwind` and `tailwindcss` as dependencies but `astro.config.mjs` shows no integrations configured and source files use plain CSS. This adds ~2MB unnecessary download/install overhead.

**Before:**
```json
"dependencies": {
  "astro": "^5.0.0",
  "@astrojs/tailwind": "^5.1.0",
  "tailwindcss": "^3.4.0"
}
```

**After:**
```json
"dependencies": {
  "astro": "^5.0.0"
}
```

**Rationale:** Reduces install time and bundle size. Tailwind can be added later if needed.

---

### 2. Add Viewport Meta Tag (MEDIUM)

**File:** `src/layouts/Layout.astro`

**Issue:** Missing `<meta name="viewport">` tag causes improper mobile rendering. All modern sites require this.

**Before:**
```html
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
```

**After:**
```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
```

**Rationale:** Viewport meta is essential for responsive design and proper mobile rendering.

---

### 3. Fix Git Commit Error Swallowing (MEDIUM)

**File:** `scripts/smart-autopush.sh`

**Issue:** `git commit || true` silently ignores all commit failures, including authentication errors, which could mask security issues.

**Before:**
```bash
git add -A
git commit -m "$MESSAGE" || true
```

**After:**
```bash
git add -A
if git diff --staged --quiet; then
  echo "[mock] No changes to commit"
else
  git commit -m "$MESSAGE"
fi
```

**Rationale:** Proper error handling distinguishes between "nothing to commit" and actual failures.

---

## Commits

| Commit | Message |
|--------|---------|
| `e3484fa` | fix(security): remove unused deps, add viewport meta, fix commit script |

---

## Verification

```bash
$ git log --oneline -3
e3484fa fix(security): remove unused deps, add viewport meta, fix commit script
f5c7be4 docs(audit): add astro anti-pattern audit report to outputs/
66537fa refactor(site): replace Astro.glob with import.meta.glob...
```