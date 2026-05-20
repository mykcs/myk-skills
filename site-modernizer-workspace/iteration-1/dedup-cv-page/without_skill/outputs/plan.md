# Plan: Deduplicate CV Pages and Redirect `/cv/` to `/zh/cv/`

## Context

- Astro v6 project with static output (`output: 'static'`)
- i18n routing configured with `prefixDefaultLocale: false`
- Duplicate CV pages exist:
  - `src/pages/cv.astro` — standalone Chinese-only CV page (serves `/cv/`)
  - `src/pages/[lang]/cv.astro` — bilingual CV page (serves `/en/cv/` and `/zh/cv/`)
- Goal: remove the duplicate standalone page and ensure `/cv/` redirects to `/zh/cv/`

---

## Step 1: Delete the Standalone Duplicate Page

**File to delete:**
```
src/pages/cv.astro
```

**Rationale:** This file creates a standalone `/cv/` route that duplicates the content served by `src/pages/[lang]/cv.astro` under `/zh/cv/`. Removing it eliminates the duplication.

**Command:**
```bash
rm src/pages/cv.astro
```

---

## Step 2: Create a Redirect for `/cv/` to `/zh/cv/`

Since the project uses `output: 'static'`, Astro's server-side redirects (`redirects` config) do not apply at runtime. Instead, we use one of the following static-friendly approaches.

### Option A: HTML Meta Refresh (Recommended for Static Sites)

Create a lightweight redirect page at the old URL.

**File to create:** `src/pages/cv.astro`

Wait — this would recreate the file we just deleted. Instead, create a redirect page that does not duplicate content.

**Correct approach:** Create `src/pages/cv.astro` as a redirect-only page:

```astro
---
// src/pages/cv.astro
// Redirects /cv/ -> /zh/cv/
---

<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>Redirecting...</title>
    <meta http-equiv="refresh" content="0;url=/zh/cv/" />
    <link rel="canonical" href="/zh/cv/" />
  </head>
  <body>
    <p>Redirecting to <a href="/zh/cv/">/zh/cv/</a>...</p>
  </body>
</html>
```

**Why this works:**
- Astro static build generates `/cv/index.html` from this file.
- Browsers follow the `<meta http-equiv="refresh">` tag immediately.
- The `<link rel="canonical">` helps search engines understand the canonical URL.
- No content duplication occurs because this page contains only the redirect logic.

### Option B: Astro Config Redirect (Build-Time Only)

If you prefer to keep `src/pages/cv.astro` fully deleted, add a redirect in `astro.config.mjs`:

```js
export default defineConfig({
  // ... existing config
  redirects: {
    '/cv': '/zh/cv',
    '/cv/': '/zh/cv/',
  },
});
```

**Important caveat:** With `output: 'static'`, Astro redirects generate HTML files with meta refreshes at build time. This is functionally equivalent to Option A but keeps the redirect logic in config rather than a page file. However, Astro v6 static redirect behavior may vary; verify the generated `dist/cv/index.html` exists after build.

**Recommendation:** Use **Option A** (explicit redirect page) for predictability and full control over the generated HTML.

---

## Step 3: Verify `[lang]/cv.astro` Handles Chinese Correctly

**File to inspect:** `src/pages/[lang]/cv.astro`

Ensure the `[lang]` dynamic route correctly renders Chinese content when `lang === 'zh'`.

Typical pattern:

```astro
---
// src/pages/[lang]/cv.astro
export function getStaticPaths() {
  return [
    { params: { lang: 'en' } },
    { params: { lang: 'zh' } },
  ];
}

const { lang } = Astro.params;
---

<Layout lang={lang}>
  <!-- CV content rendered based on lang -->
</Layout>
```

If `getStaticPaths()` is missing or does not include `'zh'`, add it.

---

## Step 4: Update Internal Links (If Any)

Search the codebase for hardcoded links to `/cv` or `/cv/` and update them to `/zh/cv/` where appropriate.

**Command:**
```bash
grep -r "href=\"/cv\"" src/ || true
grep -r "href=\"/cv/\"" src/ || true
grep -r "'/cv'" src/ || true
grep -r '"/cv"' src/ || true
```

Update any navigation, footer, or index page links that pointed to the old standalone page.

---

## Step 5: Configuration Changes

No changes to `astro.config.mjs` are strictly required if using Option A (redirect page).

If using Option B (config redirect), add the `redirects` object as shown in Step 2.

**Do NOT change:**
- `prefixDefaultLocale: false` — keep as-is; this setting means the default locale (`zh`) does not get a URL prefix automatically, but since we explicitly want `/zh/cv/`, the `[lang]` route handles it.

---

## Step 6: Build Verification Steps

1. **Build the project:**
   ```bash
   npm run build
   ```

2. **Verify the redirect file exists:**
   ```bash
   cat dist/cv/index.html
   ```
   Expected: contains `<meta http-equiv="refresh" content="0;url=/zh/cv/" />`

3. **Verify the Chinese CV exists:**
   ```bash
   ls dist/zh/cv/index.html
   ```
   Expected: file exists.

4. **Verify the English CV exists:**
   ```bash
   ls dist/en/cv/index.html
   ```
   Expected: file exists.

5. **Verify no standalone `/cv/` content duplication:**
   ```bash
   # Ensure dist/cv/index.html is small (just redirect markup)
   wc -c dist/cv/index.html
   ```
   Expected: very small file size (< 500 bytes).

6. **(Optional) Serve locally and test:**
   ```bash
   npx astro preview
   ```
   - Visit `http://localhost:4321/cv/` → should redirect to `/zh/cv/`
   - Visit `http://localhost:4321/zh/cv/` → should show Chinese CV
   - Visit `http://localhost:4321/en/cv/` → should show English CV

---

## Step 7: Commit

**Suggested commit message:**

```
refactor(cv): deduplicate cv page and redirect /cv/ to /zh/cv/

- Remove standalone src/pages/cv.astro (duplicate of /zh/cv/)
- Add meta-refresh redirect page at /cv/ -> /zh/cv/
- Update internal links to point to /zh/cv/ where needed
- Verify dist output: /cv/ is redirect-only, /zh/cv/ and /en/cv/ remain intact
```

**Command:**
```bash
bash scripts/smart-autopush.sh . "refactor(cv): deduplicate cv page and redirect /cv/ to /zh/cv/" done
```

---

## Summary Table

| Step | Action | File(s) |
|------|--------|---------|
| 1 | Delete duplicate standalone CV | `src/pages/cv.astro` |
| 2 | Create redirect page | `src/pages/cv.astro` (new, redirect-only) |
| 3 | Verify `[lang]/cv.astro` has `getStaticPaths()` | `src/pages/[lang]/cv.astro` |
| 4 | Update internal links | Various `src/**/*.astro` |
| 5 | Config changes | None (or `astro.config.mjs` if using Option B) |
| 6 | Build + verify | `dist/cv/index.html`, `dist/zh/cv/index.html`, `dist/en/cv/index.html` |
| 7 | Commit | `smart-autopush.sh` |

---

## Risk Statement

- **SEO:** The meta-refresh redirect is acceptable for static sites, but a true HTTP 301/302 redirect requires server-level configuration (e.g., `_redirects` for Netlify, `.htaccess` for Apache). If this site is deployed to GitHub Pages, meta-refresh is the standard approach.
- **Link rot:** Any external bookmarks to `/cv/` will still work but incur a client-side redirect.
- **Build output:** Ensure `dist/cv/index.html` is generated correctly; if Astro's i18n routing interferes, verify `getStaticPaths()` in `[lang]/cv.astro` explicitly includes both `en` and `zh`.
