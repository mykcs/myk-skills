# Execution Plan: Strip mykcs.github.io to Redirect-Only

## Objective
Convert the `mykcs/mykcs.github.io` repository into a minimal redirect-only site that permanently redirects all traffic to `https://wangrui2025.github.io`. All existing content must be removed.

## Current State Analysis

### Repository: `mykcs/mykcs.github.io`
- **Default branch:** `main`
- **Visibility:** private
- **Current files (recursive):**
  - `.DS_Store`
  - `.omc/` (OMC state, sessions, HUD state)
  - `assets/css/tailwind-custom.css`
  - `cc_switch_20260407`
  - `CLAUDE.md`
  - `gdkvm`
  - `gs_data_shieldsio.json`
  - `mykcs.github.io/` (nested directory containing an Astro project)
    - `.gitattributes`
    - `.github/workflows/deploy.yml`
    - `astro/` (Astro source, config, package files)
    - `CLAUDE.md`
    - `LICENSE`
    - `node_modules/`
    - `paper/`
    - `README.md`
  - `szu_ktbg_20260417`

### Target Domain
- `https://wangrui2025.github.io`

## Execution Plan

### Phase 1: Backup & Safety
1. **Clone the repository locally** to a temporary workspace.
2. **Create a backup branch** `backup/pre-redirect` from `main` to preserve all current content.
3. Verify the backup branch exists and points to the current `main` HEAD.

### Phase 2: Strip All Content
1. **Delete all files and directories** from the `main` branch working tree, **except** `.git`.
2. Specifically remove:
   - `.DS_Store`
   - `.omc/` (entire directory)
   - `assets/` (entire directory)
   - `cc_switch_20260407`
   - `CLAUDE.md`
   - `gdkvm`
   - `gs_data_shieldsio.json`
   - `mykcs.github.io/` (entire nested directory)
   - `szu_ktbg_20260417`
3. Stage all deletions with `git add -A`.

### Phase 3: Create Redirect Files
Create a minimal set of files to handle all redirect scenarios on GitHub Pages:

#### 3.1 `index.html` (root redirect)
- Must redirect **all** paths to `https://wangrui2025.github.io`.
- Use JavaScript `location.replace()` for a clean redirect (preserves back button behavior better than `location.href`).
- Include `<meta http-equiv="refresh">` as a no-JS fallback.
- Include basic SEO meta tags (title, description) to avoid blank search results.

#### 3.2 `404.html` (catch-all redirect)
- GitHub Pages serves `404.html` for any unmatched path.
- Must contain the **same redirect logic** as `index.html` so that deep links (e.g., `mykcs.github.io/old-page`) also redirect.
- The redirect target should be `https://wangrui2025.github.io` (root), not attempt to mirror the path, since the old content no longer exists.

#### 3.3 `.nojekyll` (optional but recommended)
- If the repository previously used Jekyll (or if GitHub Pages might try to process it), include an empty `.nojekyll` file to disable Jekyll processing and ensure files are served as-is.
- **Decision:** Include it defensively; it has no negative impact.

### Phase 4: Commit & Push
1. Stage the new files (`index.html`, `404.html`, `.nojekyll`).
2. Commit with a clear, semantic message:
   ```
   feat: replace entire site with redirect to wangrui2025.github.io
   ```
3. Push to `main` using `smart-autopush.sh` (per project rules).
4. Verify the push succeeded and GitHub Pages deployment triggered.

### Phase 5: Verification
1. **Wait for GitHub Pages deployment** (typically under 1 minute for simple HTML).
2. **Test the root URL:** `https://mykcs.github.io` → should redirect to `https://wangrui2025.github.io`.
3. **Test a deep URL:** `https://mykcs.github.io/nonexistent-path` → should also redirect (via `404.html`).
4. **Test with curl:**
   ```bash
   curl -I -L https://mykcs.github.io
   ```
   Expect a chain ending at `https://wangrui2025.github.io`.
5. **Test with JavaScript disabled** in browser to confirm `<meta refresh>` fallback works.

## Redirect File Specifications

### `index.html` / `404.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0; url=https://wangrui2025.github.io">
  <title>Redirecting...</title>
  <link rel="canonical" href="https://wangrui2025.github.io">
</head>
<body>
  <p>Redirecting to <a href="https://wangrui2025.github.io">wangrui2025.github.io</a>...</p>
  <script>
    window.location.replace('https://wangrui2025.github.io');
  </script>
</body>
</html>
```

### `.nojekyll`
Empty file.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Accidental data loss | Low | High | Backup branch `backup/pre-redirect` created before any destructive action. |
| Redirect loop | Very Low | High | Target domain is different (`wangrui2025.github.io` vs `mykcs.github.io`). |
| SEO / search engine confusion | Low | Medium | `rel="canonical"` tag signals the new domain. Old URLs will 404 then redirect. |
| GitHub Pages cache delay | Medium | Low | Verify after a few minutes; cache invalidates automatically. |
| Nested `mykcs.github.io/` directory was the actual site root | Medium | High | The redirect files are placed at the repo root, which GitHub Pages serves for user sites. The nested directory will be deleted. |

## Rollback Plan
If anything goes wrong:
1. Reset `main` to the backup branch:
   ```bash
   git checkout main
   git reset --hard backup/pre-redirect
   git push --force-with-lease origin main
   ```
2. GitHub Pages will revert to the previous site within minutes.

## Acceptance Criteria
- [ ] `mykcs.github.io` repository `main` branch contains exactly 3 files: `index.html`, `404.html`, `.nojekyll`.
- [ ] All previous content is removed from `main` (preserved on `backup/pre-redirect`).
- [ ] Visiting `https://mykcs.github.io` redirects to `https://wangrui2025.github.io`.
- [ ] Visiting any deep path on `mykcs.github.io` also redirects.
- [ ] Redirect works with JavaScript disabled (meta refresh fallback).
- [ ] Push was performed via `smart-autopush.sh` with a semantic commit message.
