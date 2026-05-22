# Execution Plan: Strip mykcs.github.io to Redirect-Only

## Objective

Transform `mykcs.github.io` into a minimal redirect-only site that 301-redirects all traffic to `https://wangrui2025.github.io/`. Remove all remaining non-essential content, dependencies, and configuration.

## Current State Assessment

The repository at `/Users/myk/Repo/mykcs/mykcs.github.io` has already undergone a major stripping commit (`7f3e664`), but it still retains an Astro build pipeline that is overkill for a single redirect. Remaining tracked files:

| File | Purpose | Verdict |
|------|---------|---------|
| `.gitattributes` | Git line-ending rules | **Keep** |
| `.github/workflows/deploy.yml` | GitHub Pages CI/CD | **Keep** (needs simplification) |
| `CLAUDE.md` | Project conventions for Claude Code | **Delete** (no longer a real project) |
| `LICENSE` | MIT license | **Keep** |
| `README.md` | Redirect explanation | **Keep** (already accurate) |
| `astro/.gitignore` | Astro ignore rules | **Delete** (removing Astro) |
| `astro/astro.config.mjs` | Astro configuration | **Delete** (removing Astro) |
| `astro/package.json` | NPM dependencies | **Delete** (removing Astro) |
| `astro/package-lock.json` | NPM lockfile | **Delete** (removing Astro) |
| `astro/src/pages/index.astro` | 301 redirect page | **Replace** with static `index.html` |
| `node_modules/...` | Vite deps | **Delete** (should not be tracked) |
| `paper/.DS_Store` | macOS metadata | **Delete** (should not be tracked) |

## Target State

The final repository should contain exactly these files:

```
mykcs.github.io/
├── .gitattributes
├── .github/
│   └── workflows/
│       └── deploy.yml          # Simplified: deploy root directly, no build step
├── LICENSE
├── README.md
└── index.html                  # Single static file: <meta refresh> + JS redirect
```

## Execution Steps

### Step 1 — Create Static `index.html`

Create a root-level `index.html` with a robust cross-browser redirect. It must work even if JS is disabled (meta refresh fallback) and preserve path/query fragments where possible.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=https://wangrui2025.github.io/">
  <link rel="canonical" href="https://wangrui2025.github.io/">
  <title>Redirecting...</title>
  <script>
    window.location.replace('https://wangrui2025.github.io/' + window.location.pathname + window.location.search + window.location.hash);
  </script>
</head>
<body>
  <p>This page has moved to <a href="https://wangrui2025.github.io/">https://wangrui2025.github.io/</a>.</p>
</body>
</html>
```

### Step 2 — Simplify CI/CD

Replace `.github/workflows/deploy.yml` with a minimal workflow that deploys the repo root directly to GitHub Pages, eliminating the Node.js install/build steps.

```yaml
name: Deploy redirect to Pages

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

### Step 3 — Delete All Astro Artifacts

Remove the entire `astro/` directory and any stray tracked files that are no longer needed.

```bash
git rm -rf astro/
git rm -f CLAUDE.md
git rm -f node_modules/.vite/deps/_metadata.json
git rm -f node_modules/.vite/deps/package.json
git rm -f paper/.DS_Store
```

### Step 4 — Stage New Files

```bash
git add index.html
git add .github/workflows/deploy.yml
```

### Step 5 — Commit

Use `smart-autopush.sh` with a semantic message:

```bash
bash scripts/smart-autopush.sh . "refactor(site): replace Astro with static redirect-only index.html" done
```

*(Assumption: if `smart-autopush.sh` is unavailable in this repo, fall back to `git commit` + manual push with equivalent message.)*

### Step 6 — Verify

- [ ] `git ls-files` shows exactly: `.gitattributes`, `.github/workflows/deploy.yml`, `LICENSE`, `README.md`, `index.html`
- [ ] `index.html` contains valid HTML5, canonical link, meta refresh, and JS redirect
- [ ] Workflow file has no syntax errors (`yamllint` or visual inspection)
- [ ] No `node_modules`, `.DS_Store`, or Astro files remain tracked
- [ ] `git log --oneline -1` shows the new commit

## Risk & Rollback

| Risk | Mitigation |
|------|------------|
| GitHub Pages serves 404 before DNS/cache updates | `index.html` is at root; no sub-paths to break |
| Old bookmarks to `/paper/...` or `/images/...` | Those paths no longer exist; redirect lands on new homepage |
| Accidental deletion of `LICENSE` | Explicitly excluded from deletion list |

Rollback: `git revert HEAD` restores the Astro-based redirect if needed.

## Completion Criteria

1. Repository contains exactly 5 tracked files (plus `.git/`).
2. Pushing to `main` triggers GitHub Pages deployment without a build step.
3. Visiting `https://mykcs.github.io/` redirects to `https://wangrui2025.github.io/`.
