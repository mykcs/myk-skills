# Plan: Strip mykcs.github.io to Redirect-Only

## Objective
Reduce the `mykcs.github.io` repository to a single static redirect page pointing to `https://wangrui2025.github.io/`, removing all other content, build pipelines, and dependencies.

## Current State
- Repository: `mykcs/mykcs.github.io`
- Local path: `/Users/myk/Repo/mykcs/mykcs.github.io`
- The site is currently an Astro project with a CI build pipeline that deploys `astro/dist` to GitHub Pages.
- `astro/src/pages/index.astro` already contains `Astro.redirect('https://wangrui2025.github.io/', 301)`.
- However, the repository still contains the entire Astro toolchain, source code, `node_modules`, and a GitHub Actions workflow.

## Target State
- Repository contains **only** a root-level `index.html` that performs an HTML meta-redirect.
- No build step required; GitHub Pages serves `index.html` directly from the repository root.
- All historical content, build configs, and dependencies removed from the working tree (preserved in Git history).

---

## Step 1: Pre-Execution Checks

1.1. Verify the current branch is `main` and the working tree is clean.
```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git status
```

1.2. Confirm the list of tracked files to be deleted.
```bash
git ls-tree -r HEAD --name-only
```
Expected tracked files (all to be removed except as noted):
- `.gitattributes`
- `.github/workflows/deploy.yml`
- `CLAUDE.md`
- `LICENSE`
- `README.md`
- `astro/.gitignore`
- `astro/astro.config.mjs`
- `astro/package-lock.json`
- `astro/package.json`
- `astro/src/pages/index.astro`
- `node_modules/.vite/deps/_metadata.json`
- `node_modules/.vite/deps/package.json`
- `paper/.DS_Store`

## Step 2: Remove All Tracked Files

Delete every tracked file and directory from the working tree. This leaves only untracked files (which should also be cleaned afterward).

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
# Remove tracked files and directories
git rm -rf .gitattributes
# .github/workflows/deploy.yml will be removed when .github/ is deleted
# astro/ will be removed recursively
# node_modules/ will be removed recursively
# paper/ will be removed recursively
# CLAUDE.md, LICENSE, README.md will be removed
```

Simpler approach: delete everything then recreate `index.html`.
```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
# Remove all tracked content
git rm -rf .
```

## Step 3: Create Root-Level Redirect Page

Create `/Users/myk/Repo/mykcs/mykcs.github.io/index.html` with the following content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redirecting to https://wangrui2025.github.io/</title>
  <meta http-equiv="refresh" content="0; url=https://wangrui2025.github.io/">
  <link rel="canonical" href="https://wangrui2025.github.io/">
  <meta name="robots" content="noindex">
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: #f5f5f5;
      color: #333;
    }
    a { color: #0366d6; }
  </style>
</head>
<body>
  <p>Redirecting to <a href="https://wangrui2025.github.io/">https://wangrui2025.github.io/</a>...</p>
</body>
</html>
```

Add the new file to Git:
```bash
git add index.html
```

## Step 4: Update README.md (Optional but Recommended)

If keeping `README.md`, recreate it with minimal content:

```markdown
# mykcs.github.io

This repository hosts a static redirect from `mykcs.github.io` to the active homepage at **https://wangrui2025.github.io**.
```

If the user prefers absolute minimalism, `README.md` can also be omitted. The plan defaults to **keeping** it for repository clarity.

```bash
git add README.md
```

## Step 5: Commit Changes

Use `smart-autopush.sh` with a semantic commit message.

```bash
bash /Users/myk/Repo/mykcs/scripts/smart-autopush.sh /Users/myk/Repo/mykcs/mykcs.github.io "refactor(site): strip to root-level redirect-only page" done
```

Alternative manual commit (if script unavailable):
```bash
git commit -m "refactor(site): strip to root-level redirect-only page

- Remove entire Astro build pipeline, source code, and dependencies
- Remove GitHub Actions workflow
- Add root index.html with meta-refresh redirect to wangrui2025.github.io
- Preserve repository purpose in README.md"
```

## Step 6: Update GitHub Pages Source Setting

Because the repository previously deployed via **GitHub Actions**, the Pages source must be switched to deploy directly from the `main` branch root.

6.1. Open the repository settings page:
`https://github.com/mykcs/mykcs.github.io/settings/pages`

6.2. Under "Build and deployment" > "Source", select:
- **Deploy from a branch**
- Branch: `main`
- Folder: `/ (root)`

6.3. Click **Save**.

6.4. Wait for the Pages deployment to complete (check the Actions tab for the "pages build and deployment" workflow that GitHub auto-triggers on branch-source changes).

## Step 7: Post-Deployment Verification

7.1. Verify the GitHub Pages deployment succeeds.
```bash
# Check repository status
cd /Users/myk/Repo/mykcs/mykcs.github.io
git status
```

7.2. Verify the live site responds with the redirect page.
```bash
curl -s -o /dev/null -w "%{http_code}" https://mykcs.github.io/
# Expected: 200 (the HTML page itself returns 200; the meta-refresh performs client-side redirect)
```

7.3. Verify the redirect destination is correct by checking the response body.
```bash
curl -s https://mykcs.github.io/ | grep -o 'https://wangrui2025.github.io/'
```

7.4. Verify the canonical link is present.
```bash
curl -s https://mykcs.github.io/ | grep 'rel="canonical"'
```

## Step 8: Cleanup Untracked Artifacts (Optional)

Remove any remaining untracked files/directories that were previously ignored (e.g., `.DS_Store`, `.omc/`, `node_modules/` remnants if not fully removed by `git rm`).

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git clean -fdx
```

> **Warning**: `git clean -fdx` deletes all untracked and ignored files. Confirm no important untracked files exist before running.

---

## Rollback Plan

If anything goes wrong, the full historical site is preserved in Git history and can be restored:

```bash
# Restore the last Astro-based commit to a new branch
git checkout -b restore-astro-site HEAD~1
# Or revert the strip commit on main
git revert HEAD
```

## Summary Table

| Step | Action | Status |
|------|--------|--------|
| 1 | Pre-execution checks (git status, ls-tree) | Pending |
| 2 | Remove all tracked files (`git rm -rf .`) | Pending |
| 3 | Create root `index.html` redirect page | Pending |
| 4 | Update/recreate `README.md` | Pending |
| 5 | Commit with semantic message | Pending |
| 6 | Switch GitHub Pages source to branch/root | Pending |
| 7 | Verify live deployment | Pending |
| 8 | Clean untracked artifacts | Pending |
