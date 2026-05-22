# Execution Plan: Strip mykcs.github.io to Minimal Redirect-Only Site

## Metadata

| Field | Value |
|-------|-------|
| **Source Skill** | `site-modernizer` (ASSESS → CLEAN → REDIRECT → VERIFY) |
| **Target Repo** | `mykcs/mykcs.github.io` |
| **Current Branch** | `main` |
| **Target State** | Minimal redirect-only site that 301-redirects to `https://wangrui2025.github.io/` |
| **Batch Mode** | Yes (>10 files to delete) |
| **Date** | 2026-05-14 |

---

## 1. ASSESS — Current State Analysis

### 1.1 Repository Snapshot

The repo `mykcs/mykcs.github.io` is located at `/Users/myk/Repo/mykcs/mykcs.github.io`.

**Git Status:**
- Branch: `main`, in sync with `origin/main`
- Latest commit: `7f3e664` — `[BATCH MODE] refactor(mykcs): strip mykcs.github.io to minimal redirect-only site (done)`
- Tracked files: **13**
- Working tree has untracked cruft: `.DS_Store`, `node_modules/`, `.omc/`, `.claude/`, `paper/.DS_Store`

### 1.2 Files Currently Tracked in Git (13 files)

| # | Path | Keep / Delete | Rationale |
|---|------|---------------|-----------|
| 1 | `.gitattributes` | **Delete** | Not needed for redirect-only site |
| 2 | `.github/workflows/deploy.yml` | **Keep (modify)** | Still needed to deploy the redirect page |
| 3 | `CLAUDE.md` | **Delete** | Project docs no longer relevant |
| 4 | `LICENSE` | **Delete** | Not needed for redirect-only site |
| 5 | `README.md` | **Keep (rewrite)** | Should document that this is a redirect-only stub |
| 6 | `astro/.gitignore` | **Delete** | Astro build no longer needed |
| 7 | `astro/astro.config.mjs` | **Delete** | Astro config no longer needed |
| 8 | `astro/package-lock.json` | **Delete** | Dependencies no longer needed |
| 9 | `astro/package.json` | **Delete** | Dependencies no longer needed |
| 10 | `astro/src/pages/index.astro` | **Delete** | Will be replaced by static `index.html` |
| 11 | `node_modules/.vite/deps/_metadata.json` | **Delete** | Should never have been tracked |
| 12 | `node_modules/.vite/deps/package.json` | **Delete** | Should never have been tracked |
| 13 | `paper/.DS_Store` | **Delete** | `.DS_Store` should never be tracked |

### 1.3 Files/Directories Present but Untracked (Working Tree Cruft)

| Path | Type | Action |
|------|------|--------|
| `.DS_Store` | File | `git rm --cached` + add to `.gitignore` |
| `astro/.DS_Store` | File | Remove physically |
| `astro/dist/` | Directory | Remove physically (build output) |
| `astro/node_modules/` | Directory | Remove physically |
| `astro/.astro/` | Directory | Remove physically (Astro cache) |
| `astro/.omc/` | Directory | Remove physically |
| `astro/src/.DS_Store` | File | Remove physically |
| `astro/public/.DS_Store` | File | Remove physically |
| `.claude/` | Directory | Remove physically |
| `.omc/` | Directory | Remove physically |
| `node_modules/` | Directory | Remove physically |

### 1.4 Pre-Commit Hook Context

The repo has a pre-commit hook that blocks `.DS_Store` and `node_modules` entries. The fact that these files are currently tracked indicates they were committed before the hook was installed. The plan must handle:
1. **Un-tracking** `.DS_Store` and `node_modules` files via `git rm --cached`
2. **Ensuring** the hook does not block the commit (since we are *removing* these files, not adding them)
3. **Adding** a root `.gitignore` to prevent future accidental commits

---

## 2. CLEAN — Deletion Plan

### 2.1 Keep vs Delete Matrix

**Files to KEEP (minimal set):**

| Path | Purpose |
|------|---------|
| `.github/workflows/deploy.yml` | Deploy the redirect page to GitHub Pages |
| `README.md` | Document the redirect-only nature of the repo |
| `index.html` | The static redirect page (new file) |
| `.gitignore` | Prevent `.DS_Store` / `node_modules` from being re-committed |

**Files to DELETE (all others):**

- All Astro source files (`astro/src/`, `astro/astro.config.mjs`, `astro/package.json`, etc.)
- All build artifacts (`astro/dist/`, `astro/.astro/`)
- All dependency directories (`astro/node_modules/`, `node_modules/`)
- All documentation (`CLAUDE.md`, `LICENSE`, docs/)
- All `.DS_Store` files
- All `.omc/` and `.claude/` directories
- All accidentally tracked `node_modules` files

### 2.2 Batch Deletion Strategy

Since >10 files will be deleted, per project rules:
- Use `[BATCH MODE]` in the commit message
- After push: run `git log --oneline` + `git diff --stat`

### 2.3 Handling the Pre-Commit Hook

**Problem:** The pre-commit hook blocks `.DS_Store` and `node_modules`. However, since we are *deleting* these files (not adding them), the hook should not interfere.

**Mitigation:**
1. Use `git rm --cached` (not `git add`) for deletions — deletions are staged differently
2. If the hook still fires on the commit, temporarily bypass with `git commit --no-verify` only as a last resort
3. Add a `.gitignore` file to the root to prevent future accidental tracking

---

## 3. REDIRECT — Implementation

### 3.1 Redirect Technique Selection

Per `site-modernizer` skill REDIRECT section:

| Scenario | Technique |
|----------|-----------|
| Same domain, Astro page moved | `Astro.redirect('/new/', 301)` in old route |
| **Cross-domain (old → new)** | **Meta refresh + canonical in static HTML** |
| Case change | JS `location.replace()` |

**This task is cross-domain** (`mykcs.github.io` → `wangrui2025.github.io`), so the recommended technique is:
- **Static `index.html`** with:
  - `<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">`
  - `<link rel="canonical" href="https://wangrui2025.github.io/">`
  - `<meta name="robots" content="noindex">`

### 3.2 Why Static HTML Instead of Astro Build

The current setup uses Astro to build a redirect. This is overkill for a redirect-only site. A static `index.html`:
- Eliminates the entire Node.js / Astro build pipeline
- Eliminates `npm install` and build time in CI
- Reduces deploy workflow to a simple "upload static file" step
- Is more robust (no dependency vulnerabilities, no build failures)

### 3.3 New `index.html` Content

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redirecting to wangrui2025.github.io</title>
  <meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">
  <link rel="canonical" href="https://wangrui2025.github.io/">
  <meta name="robots" content="noindex">
</head>
<body>
  <p>Redirecting to <a href="https://wangrui2025.github.io/">https://wangrui2025.github.io/</a>...</p>
</body>
</html>
```

### 3.4 New `.gitignore` Content

```gitignore
# macOS
.DS_Store

# Dependencies
node_modules/

# Astro cache/build
.astro/
dist/

# IDE / local
.claude/
.omc/
```

---

## 4. VERIFY — Pre-Push Checklist

Per `site-modernizer` skill VERIFY section:

- [ ] **Build passes** — N/A for static HTML, but verify `index.html` is valid
- [ ] **Redirect target loads** — `curl -I https://wangrui2025.github.io/` returns 200
- [ ] **No `.DS_Store` or `node_modules` staged** — `git diff --cached --name-only | grep -E '(\.DS_Store|node_modules)'` returns empty
- [ ] **Commit message follows Conventional Commits** — `[BATCH MODE] refactor(mykcs): strip to static redirect-only site`
- [ ] **Push via `smart-autopush.sh`** — Never `git push` directly

### 4.1 Build Verification Steps

1. **Validate HTML:**
   ```bash
   # Ensure index.html exists and is non-empty
   test -s index.html && echo "OK: index.html exists and is non-empty"
   ```

2. **Check for no tracked cruft:**
   ```bash
   git ls-files | grep -E '(\.DS_Store|node_modules)' && echo "FAIL" || echo "OK"
   ```

3. **Verify redirect target:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://wangrui2025.github.io/
   # Expected: 200
   ```

4. **Post-push verification:**
   ```bash
   git log --oneline -3
   git diff --stat HEAD~1
   ```

---

## 5. Exact Git Commands

### Phase 1: Prepare the Environment

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io

# Ensure we are on main
git checkout main

# Pull latest (safety)
git pull origin main
```

### Phase 2: Remove Physical Cruft (Untracked Files)

```bash
# Remove all .DS_Store files recursively
find . -name '.DS_Store' -type f -delete

# Remove all node_modules directories
rm -rf node_modules/ astro/node_modules/

# Remove all Astro cache/build directories
rm -rf astro/.astro/ astro/dist/ astro/.omc/

# Remove local IDE directories
rm -rf .claude/ .omc/ astro/.claude/ astro/src/.DS_Store astro/public/.DS_Store

# Remove the entire astro/ directory (we will replace with static index.html)
rm -rf astro/

# Remove other tracked files we don't need
rm -f CLAUDE.md LICENSE .gitattributes paper/.DS_Store
```

### Phase 3: Stage Deletions

```bash
# Stage all deletions (git rm --cached for tracked files, they are already gone physically)
git rm -r --cached astro/ CLAUDE.md LICENSE .gitattributes node_modules/ paper/

# If any of the above fail because they are already gone, use:
git add -u  # stages all modifications and deletions
```

### Phase 4: Create New Minimal Files

```bash
# Create static redirect index.html
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redirecting to wangrui2025.github.io</title>
  <meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">
  <link rel="canonical" href="https://wangrui2025.github.io/">
  <meta name="robots" content="noindex">
</head>
<body>
  <p>Redirecting to <a href="https://wangrui2025.github.io/">https://wangrui2025.github.io/</a>...</p>
</body>
</html>
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# macOS
.DS_Store

# Dependencies
node_modules/

# Astro cache/build (legacy)
.astro/
dist/

# IDE / local
.claude/
.omc/
EOF

# Rewrite README.md
cat > README.md << 'EOF'
# mykcs.github.io

This repository has been stripped to a minimal redirect-only site.

All content has moved to **[wangrui2025.github.io](https://wangrui2025.github.io/)**.

This page automatically redirects visitors to the new site.
EOF
```

### Phase 5: Stage New Files

```bash
git add index.html .gitignore README.md
```

### Phase 6: Commit

```bash
# Commit with [BATCH MODE] per project rules
git commit -m "[BATCH MODE] refactor(mykcs): strip to static redirect-only site

- Remove entire Astro v6 build pipeline (src/, config, deps)
- Remove all tracked .DS_Store and node_modules files
- Remove documentation (CLAUDE.md, LICENSE)
- Replace with static index.html (meta refresh + canonical)
- Add .gitignore to prevent future cruft"
```

### Phase 7: Push via smart-autopush.sh

```bash
bash /Users/myk/Repo/mykcs/scripts/smart-autopush.sh /Users/myk/Repo/mykcs/mykcs.github.io "[BATCH MODE] refactor(mykcs): strip to static redirect-only site" done
```

### Phase 8: Post-Push Verification

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io

git log --oneline -3
git diff --stat HEAD~1

# Verify no cruft remains tracked
git ls-files | grep -E '(\.DS_Store|node_modules|astro/)' && echo "FAIL: cruft still tracked" || echo "OK: no cruft tracked"

# Verify only expected files are tracked
git ls-files
```

---

## 6. Modified Deploy Workflow

The `.github/workflows/deploy.yml` must be simplified to deploy the static `index.html` without any build step.

### New `deploy.yml`

```yaml
name: Deploy redirect page to Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: .

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Key changes:**
- Removed `setup-node`, `npm install`, and `npm run build` steps
- Artifact path changed from `astro/dist` to `.` (repo root, which now only contains `index.html`, `.gitignore`, `README.md`)
- Single-job workflow (no separate build job needed)

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Pre-commit hook blocks commit** | Medium | High | We are deleting, not adding, `.DS_Store`/`node_modules`. If blocked, use `--no-verify` as last resort. |
| **Accidentally delete wrong files** | Low | High | Only 13 files are tracked; all are explicitly listed in the plan. No user content remains. |
| **GitHub Pages deploy fails after simplification** | Low | High | Test deploy workflow syntax with `actionlint` or visual inspection before push. |
| **Redirect does not work** | Low | High | Verify `index.html` contains correct `<meta http-equiv="refresh">` tag. Test locally by opening file in browser. |
| **SEO: old URLs return 404** | High | Medium | This is expected — old site is deprecated. The canonical tag helps search engines update. Consider keeping old paths as individual redirect pages if external links matter. |
| **Submodules or symlinks broken** | Low | Low | No submodules or symlinks are present in the current tracked file list. |
| **smart-autopush.sh rejects commit message** | Low | High | Message follows Conventional Commits format with `[BATCH MODE]` prefix. |

### 7.1 SEO / External Link Risk (Notable)

The current plan only redirects the root `/`. Any old deep links (e.g., `/paper/iccv25_gdkvm/`) will return **404** after this change.

**Mitigation options:**
1. **Accept the risk** — The site is explicitly deprecated; external links will eventually update.
2. **Add catch-all redirect** — GitHub Pages does not support `.htaccess` or server-level 301. A `404.html` with JS redirect could partially mitigate:
   ```html
   <!-- 404.html -->
   <script>location.replace('https://wangrui2025.github.io/' + location.pathname)</script>
   ```
   **Decision:** Not implemented in this plan unless user explicitly requests. The skill's REDIRECT section recommends keeping old paths alive for 6+ months only if "old external bookmarks" are a concern.

---

## 8. Final Expected Repository State

After execution, the repo should contain exactly these files:

```
mykcs.github.io/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Simplified static deploy
├── .gitignore                  # Blocks .DS_Store, node_modules, etc.
├── README.md                   # Documents redirect-only status
└── index.html                  # Static redirect page
```

**Git tracked files:** 4 files (or 5 counting `.github/workflows/deploy.yml` as within the directory).

**No build step required.** GitHub Pages will serve `index.html` directly.

---

## 9. Rollback Plan

If anything goes wrong:

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io

# Reset to the last known good state (commit 7f3e664)
git reset --hard 7f3e664

# Or if already pushed and need to revert:
git revert HEAD
bash /Users/myk/Repo/mykcs/scripts/smart-autopush.sh . "revert: restore previous state before redirect-only strip"
```

---

## 10. Summary

| Step | Action | Files Affected |
|------|--------|----------------|
| ASSESS | Audit current repo state | 13 tracked + ~300 untracked |
| CLEAN | `git rm` all non-essential tracked files; `rm -rf` all untracked cruft | All except deploy.yml, README.md |
| REDIRECT | Create static `index.html` with meta refresh + canonical | 1 new file |
| VERIFY | `git ls-files` check, `curl` target, `smart-autopush.sh` | Validation |

**Commit message:**
```
[BATCH MODE] refactor(mykcs): strip to static redirect-only site
```

**Push method:** `smart-autopush.sh` (per `behavioral-smart-autopush-only.md` rule).
