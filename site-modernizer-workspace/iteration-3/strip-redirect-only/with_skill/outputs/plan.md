# Plan: Strip mykcs.github.io to Redirect-Only Site

## Objective

Transform `mykcs.github.io` into a minimal redirect-only repository that performs a **301 redirect** to the active homepage `https://wangrui2025.github.io`. All other content, pages, assets, and build infrastructure are to be removed.

---

## Context

- **Source repository**: `/Users/myk/Repo/mykcs/mykcs.github.io`
- **Target branch**: `main`
- **Current state**: The repository has already been stripped down in commit `7f3e664` to a minimal Astro-based redirect. It currently contains:
  - An Astro project under `astro/` with a single `src/pages/index.astro` that returns `Astro.redirect('https://wangrui2025.github.io/', 301)`
  - GitHub Actions workflow `.github/workflows/deploy.yml` to build and deploy `astro/dist` to GitHub Pages
  - `README.md` documenting the redirect purpose
  - `CLAUDE.md`, `LICENSE`, `.gitattributes`
  - `node_modules/` and `paper/.DS_Store` (untracked artifacts)
- **Desired end state**: A **zero-build** redirect site. No Astro, no `npm install`, no build step. Just a static `index.html` at the repo root containing a `<meta http-equiv="refresh">` redirect, plus essential repo files.

---

## Execution Steps

### Step 1: Remove All Non-Essential Files and Directories

Delete the following from the repository root (`/Users/myk/Repo/mykcs/mykcs.github.io/`):

```bash
# Remove the entire Astro project directory
rm -rf astro/

# Remove untracked artifacts
rm -rf node_modules/
rm -f paper/.DS_Store
rm -rf paper/

# Remove legacy documentation that is no longer relevant to a redirect site
rm -f CLAUDE.md
```

**Verification command:**
```bash
git -C /Users/myk/Repo/mykcs/mykcs.github.io status
```
Expected: `astro/`, `node_modules/`, `paper/`, `CLAUDE.md` shown as deleted.

---

### Step 2: Create Root-Level `index.html`

Create `/Users/myk/Repo/mykcs/mykcs.github.io/index.html` with the following content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=https://wangrui2025.github.io/">
  <link rel="canonical" href="https://wangrui2025.github.io/">
  <title>Redirecting...</title>
</head>
<body>
  <p>This page has moved to <a href="https://wangrui2025.github.io/">https://wangrui2025.github.io/</a>.</p>
</body>
</html>
```

**Rationale:**
- `http-equiv="refresh"` provides the redirect without any server-side configuration (required for GitHub Pages static hosting).
- `rel="canonical"` helps search engines understand the new canonical URL.
- A visible `<a>` link serves as a fallback for browsers that do not honor the meta refresh.

---

### Step 3: Update `.github/workflows/deploy.yml`

Since there is no longer a build step, replace the existing Astro build workflow with a simple "deploy static files" workflow.

**New file content** for `/Users/myk/Repo/mykcs/mykcs.github.io/.github/workflows/deploy.yml`:

```yaml
name: Deploy static redirect to Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: .

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Rationale:**
- `path: .` uploads the repository root directly (which now only contains `index.html`, `README.md`, `LICENSE`, etc.).
- No Node.js setup, no `npm install`, no build step.

---

### Step 4: Update `README.md`

Ensure `/Users/myk/Repo/mykcs/mykcs.github.io/README.md` accurately reflects the new zero-build state.

**Content:**

```markdown
# mykcs.github.io

This repository is a **301 redirect** to the active academic homepage:

**https://wangrui2025.github.io**

The site at `mykcs.github.io` automatically redirects all visitors to the new domain above.
No content is hosted here; the redirect is performed by a static `index.html`.
```

---

### Step 5: Update `.gitattributes`

Ensure `/Users/myk/Repo/mykcs/mykcs.github.io/.gitattributes` remains minimal. Current content (`* text=auto`) is acceptable. No change required unless specific line-ending rules are needed.

---

### Step 6: Commit Changes

Stage all changes and commit with a semantic message.

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io

git add -A

git commit -m "refactor(site): replace Astro build with static HTML redirect

- Remove astro/ project, node_modules/, paper/, CLAUDE.md
- Add root index.html with meta refresh to wangrui2025.github.io
- Simplify deploy.yml to upload static files directly
- Update README to reflect zero-build redirect site"
```

**Verification commands:**
```bash
git -C /Users/myk/Repo/mykcs/mykcs.github.io log --oneline -3
git -C /Users/myk/Repo/mykcs/mykcs.github.io ls-tree -r --name-only HEAD
```

Expected file list after commit:
```
.gitattributes
.github/workflows/deploy.yml
LICENSE
README.md
index.html
```

---

### Step 7: Push to Remote

Push the `main` branch to `origin` using `smart-autopush.sh` (per project rules).

```bash
bash /Users/myk/Repo/mykcs/scripts/smart-autopush.sh /Users/myk/Repo/mykcs/mykcs.github.io \
  "refactor(site): replace Astro build with static HTML redirect"
```

**Verification:**
```bash
git -C /Users/myk/Repo/mykcs/mykcs.github.io log --oneline --graph --all -5
```

---

### Step 8: Post-Deploy Verification (Manual)

After GitHub Actions completes:

1. Visit `https://mykcs.github.io` in a browser.
2. Confirm it redirects to `https://wangrui2025.github.io/`.
3. Check browser DevTools Network tab for a `200 OK` on `index.html` followed by navigation to the target.
4. Verify no 404 errors for previously existing paths (they will 404, which is expected since content was removed).

---

## Rollback Plan

If the redirect fails after deployment:

1. Revert the commit:
   ```bash
   git -C /Users/myk/Repo/mykcs/mykcs.github.io revert HEAD --no-edit
   git -C /Users/myk/Repo/mykcs/mykcs.github.io push origin main
   ```
2. The previous Astro-based redirect will be restored.

---

## Files to Be Modified / Created / Deleted Summary

| Action | Path | Note |
|--------|------|------|
| **DELETE** | `astro/` | Entire Astro project directory |
| **DELETE** | `node_modules/` | Untracked artifacts |
| **DELETE** | `paper/` | Empty/untracked directory with `.DS_Store` |
| **DELETE** | `CLAUDE.md` | Legacy project guidance |
| **CREATE** | `index.html` | Root-level static redirect page |
| **UPDATE** | `.github/workflows/deploy.yml` | Replace build workflow with static deploy |
| **UPDATE** | `README.md` | Clarify zero-build redirect |
| **KEEP** | `.gitattributes` | Already minimal |
| **KEEP** | `LICENSE` | Unchanged |

---

## Acceptance Criteria

- [ ] `astro/`, `node_modules/`, `paper/`, `CLAUDE.md` are removed from the working tree and index.
- [ ] `index.html` exists at the repository root and contains a valid meta refresh redirect to `https://wangrui2025.github.io/`.
- [ ] `.github/workflows/deploy.yml` deploys the repository root directly without any build steps.
- [ ] `git status` shows a clean working tree after commit.
- [ ] `git ls-tree -r --name-only HEAD` lists exactly: `.gitattributes`, `.github/workflows/deploy.yml`, `LICENSE`, `README.md`, `index.html`.
- [ ] Changes are pushed to `origin/main`.
- [ ] (Post-deploy) `https://mykcs.github.io` successfully redirects to `https://wangrui2025.github.io/`.
