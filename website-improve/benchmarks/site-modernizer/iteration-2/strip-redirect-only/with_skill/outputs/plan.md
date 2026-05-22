# Plan: Strip mykcs.github.io to Redirect-Only

## Objective

Reduce the `mykcs.github.io` repository to the absolute minimum needed to serve a 301 redirect to `https://wangrui2025.github.io`. All other content (Astro source, assets, docs, CI workflows, etc.) must be removed.

## Current State (Post-Strip HEAD: `7f3e664`)

The repository has already been stripped in a previous batch operation (`[BATCH MODE] refactor(mykcs): strip mykcs.github.io to minimal redirect-only site`). The remaining tracked files are:

```
.gitattributes
.github/workflows/deploy.yml
astro/.gitignore
astro/astro.config.mjs
astro/package-lock.json
astro/package.json
astro/src/pages/index.astro
CLAUDE.md
LICENSE
node_modules/.vite/deps/_metadata.json
node_modules/.vite/deps/package.json
paper/.DS_Store
README.md
```

However, the current structure **still retains an unnecessary Astro build pipeline** (`astro.config.mjs`, `package.json`, `package-lock.json`, `node_modules/`, `.gitignore`) just to produce a single redirect page. This plan defines the final minimal state.

## Target State

The repository should contain **only** the files required for GitHub Pages to serve a redirect:

```
index.html          # Static redirect page (meta refresh + canonical)
README.md           # One-line explanation
LICENSE             # Keep existing license
.gitattributes      # Keep existing attributes
CNAME               # (Optional) if custom domain is used; omit for user site
```

The `index.html` content:

```html
<!doctype html>
<title>Redirecting to: https://wangrui2025.github.io/</title>
<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">
<meta name="robots" content="noindex">
<link rel="canonical" href="https://wangrui2025.github.io/">
<body>
  <a href="https://wangrui2025.github.io/">Redirecting from <code>/</code> to <code>https://wangrui2025.github.io/</code></a>
</body>
```

## Execution Steps

### Step 1: Backup Verification

Before any destructive changes, confirm the current working tree is clean and the latest commit is the expected strip commit.

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git status
git log --oneline -1
```

**Expected**: `HEAD` is `7f3e664`, working tree clean.

### Step 2: Remove Astro Build Pipeline

Delete all Astro-related files and directories. These are no longer needed because the redirect will be served as a static `index.html` at the repository root.

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io

# Remove Astro source and config
rm -rf astro/

# Remove leftover node_modules at root (if any)
rm -rf node_modules/

# Remove GitHub Actions workflow (no build step needed)
rm -rf .github/

# Remove project documentation that is now obsolete
rm -f CLAUDE.md

# Remove macOS detritus
rm -f paper/.DS_Store
rmdir paper 2>/dev/null || true
```

### Step 3: Stage Deletions

Stage all removals so Git tracks them.

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git add -A
```

**Check**: `git status` should show a large number of deletions and no untracked files.

### Step 4: Create Root `index.html`

Write the static redirect file to the repository root. This is the only file GitHub Pages needs to serve.

```bash
cat > /Users/myk/Repo/mykcs/mykcs.github.io/index.html << 'EOF'
<!doctype html>
<title>Redirecting to: https://wangrui2025.github.io/</title>
<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">
<meta name="robots" content="noindex">
<link rel="canonical" href="https://wangrui2025.github.io/">
<body>
	<a href="https://wangrui2025.github.io/">Redirecting from <code>/</code> to <code>https://wangrui2025.github.io/</code></a>
</body>
EOF
```

Stage it:

```bash
git add index.html
```

### Step 5: Update `README.md`

Ensure `README.md` clearly states the repository is a redirect-only placeholder.

Current content (acceptable, but can be tightened):

```markdown
# mykcs.github.io

This repository is a **301 redirect** to the active academic homepage:

**https://wangrui2025.github.io**

The site at `mykcs.github.io` automatically redirects all visitors to the new domain above. No content is hosted here.
```

If changes are made, stage them:

```bash
git add README.md
```

### Step 6: Commit

Use `smart-autopush.sh` with a semantic Conventional Commits message. Because this touches >10 files (mostly deletions), use `[BATCH MODE]`.

```bash
bash /Users/myk/Repo/mykcs/scripts/smart-autopush.sh /Users/myk/Repo/mykcs/mykcs.github.io "refactor(mykcs): strip to root-level static redirect, remove Astro pipeline [BATCH MODE]" done
```

**Message rationale**: `refactor` because we are restructuring without adding features; `mykcs` scope; description covers both the removal of the build pipeline and the addition of the root `index.html`.

### Step 7: Verify Final Tree

After commit, confirm the repository contains exactly the expected files.

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git ls-tree -r --name-only HEAD | sort
```

**Expected output**:

```
.gitattributes
LICENSE
README.md
index.html
```

### Step 8: Verify Redirect HTML

Open the generated `index.html` and confirm it contains:

- `<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">`
- `<link rel="canonical" href="https://wangrui2025.github.io/">`
- `<meta name="robots" content="noindex">`

### Step 9: GitHub Pages Deployment Check

Because this is a user/organization site (`mykcs.github.io`), GitHub Pages serves from the `master` (or `main`) branch root. With `index.html` at the root, no build step is required. Ensure the repository default branch is the one being pushed to.

```bash
git -C /Users/myk/Repo/mykcs/mykcs.github.io branch --show-current
```

**Expected**: `master` or `main`.

No `.github/workflows/deploy.yml` is needed because there is no build process.

## Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Accidental deletion of `LICENSE` or `README.md` | These are explicitly kept in the target state list. Step 7 verifies they remain. |
| `index.html` not served due to missing `CNAME` or branch mismatch | Verify branch in Step 9. `CNAME` is only needed for custom domains; `mykcs.github.io` is the default user domain. |
| SEO impact from removing content | The canonical tag and 301-meta-refresh preserve link equity. `robots noindex` prevents duplicate content penalties. |
| Old bookmarks to subpaths (e.g., `/paper/...`) break | Acceptable risk. The old site is superseded; no content is mirrored. Users hitting subpaths will see GitHub Pages 404, which is expected for a decommissioned site. |

## Rollback

If anything goes wrong, the previous state is preserved in Git:

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git reset --hard 7f3e664
```

## Summary Table

| Step | Action | Command Count | Verification |
|------|--------|---------------|--------------|
| 1 | Backup check | 2 | `git status` clean |
| 2 | Remove Astro pipeline | 5 | `ls` shows no `astro/`, `node_modules/`, `.github/` |
| 3 | Stage deletions | 1 | `git status` shows deletions |
| 4 | Create `index.html` | 2 | File exists at root, content correct |
| 5 | Update `README.md` | 0-1 | Content states redirect purpose |
| 6 | Commit via `smart-autopush.sh` | 1 | Commit succeeds, message passes quality gate |
| 7 | Verify final tree | 1 | Exactly 4 tracked files |
| 8 | Verify redirect HTML | 1 | Meta refresh + canonical + noindex present |
| 9 | Branch check | 1 | Default branch confirmed |
