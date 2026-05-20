---
name: site-modernizer
description: >
  Audit, clean up, and modernize static site architectures (Astro, Jekyll, etc.).
  Use this skill whenever the user mentions:
  - "cleanup / clean up / 清理" a website, old pages, deprecated projects, or duplicate content
  - "modernize / 升级 / 重构" a site (Astro 6, Tailwind v4, build pipeline, etc.)
  - "project page / 项目页" for a paper (e.g. CVPR/ICCV project showcase pages)
  - "redirect / 重定向" after moving or renaming pages/sites
  - "anti-pattern scan / 反模式扫描" or "architecture decision / ADR / CONTEXT.md"
  - "build pipeline / 构建脚本" consolidation or simplification
  - "duplicate pages / 重复页面" or "merge scripts"
  - Any request involving multiple steps of site maintenance, refactoring, or new project-page creation.
---

# Site Modernizer

A workflow skill for maintaining and upgrading static academic/personal websites.
Covers cleanup, architecture decisions, build pipeline unification, anti-pattern scanning, and professional project-page creation.

## Workflow Overview

```
0. DOCS LOOKUP → Fetch latest Astro/Tailwind/PWA docs via Context7 + WebSearch
1. ASSESS      → Explore codebase, identify problems, list cleanup/modernization items
2. DECIDE      → If decisions are unclear, use grill-with-docs (CONTEXT.md + ADR)
3. CLEAN       → Remove duplicates, deprecated files, stale assets, unused dependencies
4. BUILD       → Unify build scripts into Astro Integration or single pipeline
5. SCAN        → Run anti-pattern checks (Astro.glob, Image format, ViewTransitions, etc.)
6. PAGE        → Create/refactor bilingual project pages (if requested)
7. REDIRECT    → Set up 301/meta-refresh/JS redirects for moved content
8. VERIFY      → Build passes, no broken links, no FOUC, responsive viewport check, zh/en content parity check
```

## Non-Negotiable Rules

These rules apply to **every** task, regardless of scope:

1. **Commit is mandatory.** Every task that modifies files MUST end with `git add -A` followed by `smart-autopush.sh`. If `smart-autopush.sh` does not exist, use `git add -A && git commit -m "<type>(<scope>): <description>" && git push`. No exceptions. A task without a commit is incomplete.
2. **Build must pass before commit.** Run `npm run build` after all changes. If it fails, fix the errors first. Do not commit a broken build.
3. **Verify before declaring done.** Before saying the task is complete, run `git log --oneline -1` to confirm the commit exists.
4. **Benchmark garbage cleanup.** If benchmarking creates `mock-repo/` or `outputs/dist/` directories, clean them up immediately after the iteration completes. See `site-modernizer-workspace` SKILL.md for the cleanup command. Do not leave rebuildable artifacts on disk.

## 0.5 AESTHETIC — Design Quality Standards: Modern · Clean · Elegant

Every site audit must apply this three-axis quality bar. These are not cosmetic preferences — they are functional indicators of site health and professionalism.

### Axis 1 — Modern（现代）

**Definition**: The site does not look like it was built with 2015-era tooling.

| Check | Pass | Fail |
|-------|------|------|
| Font stack | `@fontsource` self-hosted, no Google Fonts CDN `<link>` | `<link>` to `fonts.googleapis.com` or `fonts.gstatic.com` |
| Color syntax | All colors in `oklch()` or `oklch()` derived from design tokens in `@theme` | Raw `hex(#fff)`, `rgb()`, `hsl()` in components or inline styles |
| Dark mode | Class-based (`.dark`) via Tailwind `@custom-variant`, not `prefers-color-scheme` only | JS media-query listener toggling `<html class>` without Tailwind variant |
| Framework | Astro v6 + Tailwind v4 (`@tailwindcss/vite`), or current stable | Astro v4/v5 + `@astrojs/tailwind`, or raw CSS without Tailwind |
| View transitions | `<ClientRouter />` (Astro 4+) | `<ViewTransitions />` (deprecated Astro 3 API) |
| Build output | Static HTML — zero server-side runtime | SSR or hydration overhead |

**Detection:**
```bash
# CDN fonts
grep -r "fonts.googleapis.com\|fonts.gstatic.com" src/ public/ && echo "FAIL: CDN fonts"

# Color syntax (flag raw hex/rgb/hsl not inside @theme)
grep -rn "#[0-9a-fA-F]\{3,8\}\|rgb\|hsl" src/ --include="*.astro" --include="*.css" | grep -v "@theme\|oklch\|node_modules" | head -10

# Deprecated ViewTransitions
grep -rn "ViewTransitions" src/ --include="*.astro" && echo "FAIL: deprecated ViewTransitions"
```

### Axis 2 — Clean（干净）

**Definition**: No visual noise, no dead UI, no layout overflow, no broken redirects.

| Check | Pass | Fail |
|-------|------|------|
| Redirects | Every `_redirects` entry + every physical HTML redirect resolves to HTTP 200 | 404 destination, case-mismatch redirect without physical file |
| Console errors | Zero Error-level at all viewports (Playwright check) | Any `Uncaught` error, 404 resource, failed fetch |
| Horizontal overflow | `document.body.scrollWidth <= window.innerWidth` at all viewports | Scrollbar appears at 375px mobile width |
| Asset hygiene | Zero orphaned build artifacts (`dist/` not in `src/`), zero committed `node_modules` | `public/dist/`, `.DS_Store`, `Thumbs.db` in repo |
| Dead UI | Every `<a>`, `<button>`, interactive element has a working handler or valid `href` | Ghost buttons, empty `onclick`, `#` links that do nothing |
| Accessibility | All images have `alt`, all inputs have `<label>`, keyboard focus ring visible | Missing `alt="..."`, unlabeled inputs, `:focus-visible { outline: none }` |

**Detection:**
```bash
# Horizontal overflow (run in Playwright)
page.evaluate(() => document.body.scrollWidth > window.innerWidth)

# Orphaned artifacts
find src/ -name "dist" -o -name "node_modules" -o -name ".DS_Store" && echo "FAIL: orphaned artifacts"

# Redirect health — run per-site curl checks (see Redirect Health Checklist in Section 5)
```

### Axis 3 — Elegant（优雅）

**Definition**: Typography, spacing, and motion feel deliberate — not "defaults" or "auto-generated."

| Check | Pass | Fail |
|-------|------|------|
| Font pairing | Intentional heading/body font combination, min 2 weights loaded per family | Single weight, no hierarchy, no CJK fallback chain |
| Spacing | Consistent spacing scale (Tailwind `space-*` or CSS custom properties), no magic numbers | `margin: 7px`, `padding: 23px` scattered in components |
| Motion | CSS `transition` or `animation` present; `prefers-reduced-motion` respected | Animations that trigger layout shift, `setTimeout`-based effects, no reduced-motion guard |
| Visual depth | Subtle shadows, gradients, or texture on interactive/surface elements; no flat solid blocks unless intentional | Everything same `background: white`, no shadow hierarchy, no hover feedback |
| Dark mode polish | Dark palette uses soft contrast (`oklch` L > 15 for bg), not inverted colors | `background: #000` with `color: #fff` (harsh, not elegant) |

**Detection:**
```bash
# Magic number spacing (flag px values not in 4px grid)
grep -rn "px\b" src/ --include="*.astro" | grep -v "node_modules\|0px\|4px\|8px\|12px\|16px\|24px\|32px\|48px\|64px" | head -10

# Missing reduced-motion guard
grep -rn "@media (prefers-reduced-motion" src/ --include="*.css" --include="*.astro" || echo "WARN: no reduced-motion guard"
```

### Scoring

After audit, report a 3-axis scorecard:

| Site | Modern | Clean | Elegant | Overall |
|------|--------|-------|---------|---------|
| wangrui2025.github.io | ✓ | ✓ | ✓ | PASS |
| OSA | ✓ | ✓ | ✓ | PASS |
| GDKVM | ✓ | ✓ | ✓ | PASS |

**Overall = PASS only if all three axes pass.** Any single FAIL blocks the site from being considered "production quality."

---

## 0. DOCS LOOKUP — Always-On Web Research

**This step is MANDATORY for every invocation.** Before touching any code, fetch the latest official documentation to validate that your planned approach is current.

### When to Run
- Every time you open this skill (at the start of every session)
- Before applying any framework-specific fix (Astro, Tailwind, PWA, etc.)
- When a scan finding mentions a migration or deprecated API

### How to Run

**Astro (framework, integrations, ViewTransitions, Content Collections):**
Use the `docs-lookup` skill or the `context7` MCP server:
```
Skill: docs-lookup
Query: Astro 6 ClientRouter view-transition best practices 2025
```
Or directly:
```
mcp__context7__query_docs: "Astro 6 ClientRouter transition animation best practices"
mcp__context7__query_docs: "Astro 6 ViewTransitions migration guide"
mcp__context7__query_docs: "Astro Content Collections latest patterns"
```

**Tailwind CSS v4:**
```
mcp__context7__query_docs: "Tailwind CSS v4 best practices dark mode 2025"
mcp__context7__query_docs: "Tailwind CSS v4 @theme CSS variables"
```

**PWA (manifest, service worker, maskable icons):**
```
mcp__context7__query_docs: "PWA manifest maskable icons best practices 2025"
WebSearch: "web app manifest maskable icon safe area 2025"
```

**@fontsource (local fonts):**
```
mcp__context7__query_docs: "@fontsource local fonts Astro integration"
```

### Output
After running the lookups, note 2-3 key findings in your context. These inform which patterns to apply in SCAN/ASSESS and which anti-patterns to flag.

### Why This Is Non-Negotiable
The web evolves faster than skill files. Patterns marked as "current best practice" in this document may be superseded by newer APIs. The only reliable source is the official docs, fetched fresh each session.

---

## 1. ASSESS — Exploration Checklist

Read these files in order (skip if absent):
- `CLAUDE.md`, `AGENTS.md` — project-specific conventions
- `astro.config.mjs` / `astro.config.ts` — framework version, integrations, i18n
- `package.json` — dependencies (look for deprecated packages)
- `src/pages/` — duplicate pages? (e.g. `/cv.astro` vs `/[lang]/cv.astro`)
- `src/integrations/` or `scripts/` — scattered build scripts?
- `docs/adr/`, `docs/` — existing architecture docs?
- `.github/workflows/` — CI health
- Root-level orphaned files — old favicons, paper PDFs, image dumps

### When Source Files Are Missing
If the user describes a scenario (e.g. "duplicate CV pages exist") but the corresponding files are **not present** in the working directory:
1. **Do not refuse outright.** Instead, produce a **hypothetical plan** based on the user's description.
2. **Label every assumption clearly** with `(Assumption: file described by user)`.
3. Proceed through the rest of the workflow (DECIDE → CLEAN → REDIRECT → VERIFY) as if the files existed.
4. This fallback ensures the skill remains useful when the repo has already been partially cleaned or when the user is describing a target state.

### Package Manager & CI Lock-File Hygiene

A common source of "works on my machine" failures is package manager mismatch between local and CI.

**Detection routine** (run before any dependency change):
1. Check which lock file exists: `pnpm-lock.yaml`, `package-lock.json`, or `yarn.lock`
2. Check `.github/workflows/*.yml` for the install command (`npm ci`, `pnpm install`, `yarn install`)
3. Check `.npmrc` exists if the CI uses pnpm

**Fix rules**:
- If CI uses **pnpm** but `package-lock.json` exists: delete `package-lock.json`, run `pnpm install` to regenerate `pnpm-lock.yaml`
- If `.npmrc` is missing and CI uses pnpm: check if pnpm-specific config (e.g., `shamefully-hoist=true`) is required by the project
- Never leave stale lock files from a different package manager in the repo

**Why**: GitHub Actions fails when it expects pnpm but finds an outdated npm lock file, or when `.npmrc` with pnpm-specific settings is missing.

### Common Smells
| Smell | Action |
|-------|--------|
| Multiple `*.sh` / `*.mjs` build scripts | Unify into single Astro Integration |
| `Astro.glob()` in `.astro` files | Replace with Content Collections |
| `<Image format="webp">` | Remove `format` (Astro 6 auto-optimizes) |
| `ViewTransitions` import | Replace with `ClientRouter` (Astro 4+) |
| Duplicate CV/homepage pages | Delete one, add `Astro.redirect()` |
| Jekyll/Hugo remnants in Astro project | Remove; migrate content if needed |
| Old project sites still deployed | Strip to redirect-only if superseded |
| Hardcoded image paths in templates | Use `data-im="key"` + `image-map.json` pattern |
| Stale lock file from wrong package manager | Remove `package-lock.json` if CI uses pnpm (check `.github/workflows/`), keep only one lock file |
| Missing `.npmrc` with pnpm-specific config | Restore `.npmrc` with `shamefully-hoist=true` when pnpm is the package manager |

## 2. DECIDE — Architecture Documentation

If the cleanup touches URL structure, i18n routing, or page organization:
- Use the `grill-with-docs` skill (or equivalent domain interview)
- Create/update `CONTEXT.md` for glossary and bounded contexts
- Create ADR in `docs/adr/` if the decision is hard to reverse, surprising, or involves real trade-offs

ADR naming: `docs/adr/000N-short-kebab-description.md`

## 3. CLEAN — Deletion Rules

**Before deleting anything:**
1. Check if content exists in the newer/primary site (diff text, compare images)
2. Verify no external links point to the file (search `grep -r "filename" src/ public/`)
3. For Git-tracked files: `git rm` (not `rm`) so deletions are staged properly

**Batch deletion (>10 files):**
- Use `[BATCH MODE]` in commit message
- After push: `git log --oneline` + `git diff --stat` per project rules

**After every CLEAN step:**
- Stage deletions: `git add -A` (or `git rm` for individual files)
- Commit via `smart-autopush.sh` with a Conventional Commits message describing WHAT was cleaned and WHY
- Example: `bash scripts/smart-autopush.sh . "refactor(site): remove duplicate cv.astro and add redirect to /zh/cv/" done`

## 4. BUILD — Pipeline Unification

Prefer a single Astro Integration over multiple shell scripts.

Template:
```js
// src/integrations/build-pipeline.mjs
export default function buildPipeline() {
  return {
    name: 'build-pipeline',
    hooks: {
      'astro:server:setup': async () => { /* dev prep */ },
      'astro:build:start': async () => { /* pre-build copy/sync */ },
      'astro:build:done': ({ dir }) => { /* post-build inline/restore */ },
    },
  };
}
```

Register in `astro.config.mjs`:
```js
import buildPipeline from './src/integrations/build-pipeline.mjs';
export default defineConfig({ integrations: [buildPipeline()] });
```

## 5. SCAN — Comprehensive Audit & Anti-Pattern Checklist (Astro 6)

> **Before running scans:** Run Context7 lookups to validate the current best practices for any patterns you plan to flag. See `## 0. DOCS LOOKUP` above.

When auditing or scanning a site, load `references/scan-checklist.md` and run through all categories. **Scanning is not a read-only report — it is the first half of a fix workflow.** After documenting findings, you MUST apply the fixes, verify the build, and commit the changes. Do not stop at the report stage. The full SCAN workflow is: scan → fix → build-verify → commit.

After applying fixes: re-run `npm run build` + `npx astro check`. If either fails, fix the errors first — **do not commit a broken build**.

Once the build is green, execute the mandatory final steps in order:
1. Stage all changes: `git add -A`
2. **EXECUTE** commit via `smart-autopush.sh` with a semantic Conventional Commits message. If `smart-autopush.sh` is unavailable, run `git add -A && git commit -m "<type>(<scope>): <description>" && git push`
3. Run `git log --oneline -3` to confirm the commit landed
4. Only after confirming the commit exists, declare the task complete

**Build-fail exception:** If build fails due to pre-existing issues (not caused by your changes), fix what you can, stage and commit the changes you DID make. An uncommitted fix is a wasted fix.

### i18n Anti-Patterns — Mandatory Fix Rules

When scanning for i18n issues, these are NOT optional cleanups — they MUST be fixed:

1. **Conditional bilingual rendering is forbidden.** Any pattern like `{lang === 'zh' ? '中文' : 'English'}` must be replaced with a single `t('key')` call and the strings moved to both `en.json` and `zh.json`.
   - **Detection**: Run `grep -rn "lang ===" src/` and `grep -rn "lang===" src/`. 
     - **EXCLUDE dictionary selection**: `const t = lang === 'zh' ? zh : en` (or similar `const x = lang === ...`) is NOT an anti-pattern — it is the canonical way to choose a translation dictionary.
     - **ELIMINATE conditional rendering**: Any ternary that directly renders different text based on `lang` inside JSX/HTML (e.g. `{lang === 'zh' ? '中文' : 'English'}`) MUST be replaced.
   - **Fix procedure** (do not skip steps):
     - Step 1: For each file with conditional rendering matches, extract BOTH branches of every ternary into new i18n keys.
     - Step 2: Add those keys to **ALL** locale JSON files (en.json, zh.json, and any others).
     - Step 3: If no `t()` helper exists in the project, create a minimal one in `src/lib/i18n.ts` (or `src/i18n/translator.ts`) that imports the JSON files and returns the string for the current locale. Example:
       ```ts
       import en from '../content/i18n/en.json';
       import zh from '../content/i18n/zh.json';
       const dicts = { en, zh };
       export function t(key: string, lang: string = 'zh') {
         const parts = key.split('.');
         let val: any = dicts[lang as keyof typeof dicts] || dicts.zh;
         for (const p of parts) val = val?.[p];
         return val || key;
       }
       ```
     - Step 4: Replace the ternary with `t('new.key')` in the component, passing `lang` if needed.
     - Step 5: Re-run `grep -rn "lang ===" src/` to confirm zero conditional rendering matches remain (dictionary selection patterns are allowed).
     - Step 6: Run `npm run build`. If it fails, fix errors before proceeding.
     - Step 7: **Commit is MANDATORY.** Run `git add -A` then `smart-autopush.sh` with a semantic message. Run `git log --oneline -1` to confirm. Do not stop after build passes — commit is the final step.
   - **Why**: Conditionals in components scatter translations across source files, making updates error-prone and breaking key-set synchronization. A single remaining conditional rendering ternary is a failure.

2. **All hardcoded UI text must use `t()`.** Labels, buttons, alt text, aria-labels, meta descriptions — if it is human-readable text inside a component, it must come from JSON.

3. **`en.json` and `zh.json` must have identical key sets.** After any change, diff the top-level keys. If one locale is missing a key, copy the other locale's value as a placeholder and mark it for translation review.

### Performance & Asset Anti-Patterns — Mandatory Fix Rules

These three fixes are mechanically verifiable and MUST be applied when the conditions are met:

1. **CDN font links must be removed and replaced with `@fontsource/*`.**
   - Detection: `grep -r "fonts.googleapis.com\|fonts.gstatic.com" src/ public/`
   - Fix procedure (do not skip steps):
     - Step 1: `npm install @fontsource/inter` (or appropriate family). **This is the FIRST and ONLY step you perform before touching any code.**
     - Step 1a: Verify the install succeeded by running `ls node_modules/@fontsource/inter/package.json`. If this file does not exist, the install failed — fix it before proceeding.
     - Step 2: Only after verification, remove all `<link>` tags pointing to Google Fonts from Layout.
     - Step 3: Add `import '@fontsource/inter/400.css'` to Layout.
     - Step 4: Run `npm run build` immediately to verify the import resolves.
     - Step 5: **Commit.** Run `git add -A` then `smart-autopush.sh` (or `git commit -m "perf(fonts): replace Google Fonts CDN with @fontsource/inter" && git push`). Then run `git log --oneline -1` to confirm.
   - **Why**: Adding the import without installing the package breaks the build. The verification step (1a) prevents the common failure mode where agents claim to have installed a package but actually did not.

2. **All below-the-fold images MUST have `loading="lazy"` and `decoding="async"`.**
   - Detection: Run `grep -rn "<img" src/ --include="*.astro"` to list all images. Identify the hero/above-fold image (usually the first/largest on the page) and exclude it. Every other `<img>` tag MUST have `loading="lazy" decoding="async"`.
   - Fix procedure (do not skip steps):
     - Step 1: Run the grep command above to get the full list of `<img>` tags.
     - Step 2: For each image that is NOT the hero/above-fold image, add `loading="lazy" decoding="async"` to the tag.
     - Step 3: Re-run the grep. Any `<img>` without `loading="lazy"` (except hero) is a failure.
     - Step 4: Run `npm run build` to verify nothing breaks.

3. **Unused dependencies MUST be uninstalled.**
   - Detection: Check `package.json` dependencies against actual imports in `src/`:
     ```bash
     for pkg in lodash moment jquery; do
       grep -r "from ['\"]$pkg['\"]" src/ || echo "$pkg unused"
     done
     ```
   - Fix: `npm uninstall <unused-pkg>` for any dependency with zero imports. Also check `devDependencies`.

4. **After all three fixes above are applied and build passes, commit.**
   - Run `git add -A` then `smart-autopush.sh` (or `git commit -m "perf(site): remove unused deps, replace Google Fonts, add lazy loading" && git push`).
   - Run `git log --oneline -1` to confirm. These are NOT optional — they are part of the SCAN fix contract.

### Project Page & Homepage Health Checklist

When auditing existing project pages (e.g. `/gdkvm/`, `/osa/`) or the homepage, also check:

- **Terminology consistency**: `papers` → `publications`, `honors` → `awards` (including `mykcs/academic` submodule)
- **Missing English CV** at `/en/cv/` if the site targets a global audience
- **PWA hygiene**: `manifest.json` with maskable icons, dynamic `theme_color`
- **Social sharing**: Open Graph tags (`og:image`, `og:locale:alternate`)
- **Performance**: Critical CSS inlining, font preloading
- **Repository cleanliness**: No `website/` build artifacts committed
- **Documentation accuracy**: `CLAUDE.md` titles match the actual project, `CONTEXT.md` exists for domain glossary

Full checklist with detection commands: `references/project-page-audit-checklist.md`

### Redirect Health Checklist — Mandatory Scan (Astro + GitHub Pages)

This is a **mandatory scan** for every site audit. Redirects silently break when HTML redirect files are deleted or `_redirects` entries point to non-existent destinations.

#### Why `_redirects` Alone Is Insufficient

GitHub Pages `_redirects` file only works for **Netlify**-style redirects. For Astro static sites deployed to **GitHub Pages**, a `_redirects` entry pointing to a non-existent path will silently return 404. The only reliable redirect techniques on GitHub Pages are:
- Physical HTML files with `<meta http-equiv="refresh">` or `<script>location.replace()</script>`
- Astro `.astro` files with `Astro.redirect()` (for same-domain routing)

#### Scan Procedure

**Step 1: Inventory all redirect sources**
```bash
# List all _redirects entries
cat astro/public/_redirects

# List all physical HTML redirect files
find astro/public -name "index.html" -path "*/\*" -exec grep -l "location.replace\|http-equiv=\"refresh\"" {} \;

# List all Astro redirect pages
grep -rn "Astro.redirect" astro/src/pages/ --include="*.astro"
```

**Step 2: For each `_redirects` entry, verify destination exists**
```bash
# Read _redirects, extract destination paths, check each
# Example for /gdkvm → /GDKVM/:
curl -sI https://<site>.github.io/GDKVM/ | head -1
# Must return 200. If 404, the redirect is broken.
```

**Step 3: For each case-change redirect, verify physical HTML file exists**
```bash
# Example: /OSA/ → /osa/ (uppercase to lowercase)
ls astro/public/OSA/index.html
# If missing, create it:
# <!DOCTYPE html><html><head>
# <meta charset="utf-8">
# <script>location.replace('/osa/' + location.hash)</script>
# <link rel="canonical" href="/osa/">
# <title>Redirecting...</title></head><body></body></html>
```

**Step 4: Check for orphan redirect HTML files with no destination**
```bash
# Find all HTML redirect files, extract their target, verify target exists
for f in $(find astro/public -name "index.html" -exec grep -l "location.replace\|refresh" {} \;); do
  target=$(grep -oP "location\.replace\(['\"]/\K[^'\"]+" "$f" | head -1)
  if [ -n "$target" ]; then
    status=$(curl -sI "https://<site>.github.io$target" | head -1)
    echo "$f → /$target: $status"
  fi
done
```

#### Common Failure Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| `_redirects` entry points to 404 | `curl -I /source` → 302 → 404 | Replace with physical HTML redirect file |
| Case change without physical file | `/OSA/` → 404 | Create `public/OSA/index.html` with JS redirect |
| Trailing-slash redirect | `/cv` → 301 → `/cv/` → 200 (works by accident) | Not a bug, but verify destination is intentional |
| Project moved but old path not preserved | External links to `/gdkvm/` return 404 | Create physical redirect at `public/gdkvm/index.html` |

#### Fix Rules

1. **Case-change redirects must be physical HTML files** (GitHub Pages `_redirects` is case-sensitive and unreliable for this)
2. **`_redirects` entries that point to 404 must be replaced** with physical HTML redirect files
3. **After adding any HTML redirect file**, commit immediately — do not wait for a build

#### Acceptance Criteria
- [ ] Every `_redirects` entry resolves to 200
- [ ] Every case-change redirect (`/OSA/` → `/osa/`) has a physical HTML file
- [ ] Every project page with an old URL has a physical redirect file
- [ ] No redirect chain longer than 1 hop (source → destination, not source → intermediate → destination)

## 6. PAGE — Bilingual Project Page Creation

For new paper project pages (e.g. `/osa/`, `/gdkvm/`):

### Stack
- Astro 6.x + Tailwind CSS v4
- Local fonts (`@fontsource/inter`) — zero CDN dependency
- **oklch color space — MANDATORY** — All theme color variables MUST use `oklch()` syntax in `@theme`. Do NOT use hex, rgb, or hsl in new/modernized code. When documenting the color scheme in the plan, list colors as oklch values (e.g. `oklch(55% 0.15 255)`), not hex strings.
  ```css
  @theme {
    --color-primary: oklch(55% 0.15 255);
    --color-accent: oklch(65% 0.18 30);
    --color-bg: oklch(96% 0.01 95);
  }
  ```
- Static output (`output: 'static'`)

### Pattern Reference — gdkvm
When creating a new project page, **always inspect an existing high-quality page first** (e.g. `/gdkvm/` if it exists, or the most recent project page). Mirror its:
- Layout structure and section ordering
- i18n helper patterns (`createTranslator`, locale routing)
- Animation conventions (e.g. `highlight-title` scroll reveal)
- Component hierarchy (Layout → Page → Sections)
- SEO/structuredData.ts approach

If no existing project page exists, state this explicitly and define a standalone standard.

### URL Structure
```
/osa/          → redirect to /osa/en/ (or /osa/zh/ if Chinese default)
/osa/en/       → English project page
/osa/zh/       → Chinese project page
```

If `prefixDefaultLocale: true`, add root `index.astro`:
```astro
---
return Astro.redirect('/osa/en/', 302);
---
```

### Content Sections (standard order)
1. **Hero** — title, authors, venue badge, teaser image
2. **Abstract** — bilingual
3. **Motivation** — why this problem matters
4. **Method** — architecture diagram + key formulas
5. **Results** — quantitative table + qualitative visuals
6. **BibTeX** — copy-paste ready citation
7. **Links** — arXiv, code, project (if applicable)

### Asset Source Rules
- Images: `vendor/academic/` or `mykcs/academic` submodule
- Papers: arXiv metadata via `arxiv.org/abs/XXXX.XXXXX`
- Author list: **always verify with user** — do not hallucinate co-authors

### After PAGE Creation
- Stage all new/modified files: `git add -A`
- Commit via `smart-autopush.sh` with a Conventional Commits message describing WHAT the page adds and WHY
- Example: `bash scripts/smart-autopush.sh . "feat(osa): add CVPR 2026 OSA bilingual project page with Hero/Abstract/Method/Results/BibTeX" done`
- Even in hypothetical plans or mock repos, include the commit command as a required step

## 7. REDIRECT — Compatibility Patterns

When renaming a page/site:

| Scenario | Technique |
|----------|-----------|
| Same domain, Astro page moved | `Astro.redirect('/new/', 301)` in old route |
| Cross-domain (old → new) | Meta refresh + canonical in static HTML |
| Case change (`/OSA/` → `/osa/`) | JS `location.replace('/osa/')` in old path (faster than meta) |
| Old external bookmarks | Keep old path alive as redirect page for 6+ months |

**After every REDIRECT step:**
- Stage changes: `git add -A`
- Commit via `smart-autopush.sh` with a Conventional Commits message
- Example: `bash scripts/smart-autopush.sh . "refactor(site): add 301 redirect from /cv/ to /zh/cv/" done`

## 8. VERIFY — Pre-Push Checklist

- [ ] `npm run build` passes (0 errors)
- [ ] `astro check` passes (0 TS errors)
- [ ] Redirect target loads correctly
- [ ] No `.DS_Store` or `node_modules` staged
- [ ] **Every file change is committed** with a Conventional Commits message (type(scope): imperative description)
- [ ] **Commit message describes WHY, not just filenames** — e.g. `refactor(cv): remove duplicate page and redirect /cv/ to /zh/cv/` not `update cv.astro`
- [ ] Push via `smart-autopush.sh` (never `git push` directly)
- [ ] After push: monitor GitHub Actions, fix CI failures before declaring done
- [ ] CI green: `git log --oneline -3` to confirm final commit landed

### Mandatory "Done" Verification Protocol

**Before declaring any task complete**, run the following in order and paste output:

1. **Diff audit**: `git diff --stat HEAD~1..HEAD` (or `git diff --stat` if uncommitted) — confirm only intended files changed
2. **Build re-verify**: `npm run build 2>&1 | tail -5` — confirm 0 errors
3. **Commit confirmation**: `git log --oneline -3` — confirm commit exists with semantic message
4. **CI status** (if pushed): Report GitHub Actions run conclusion

**If any step fails, the task is NOT done.** Fix and re-run the protocol.

**Why**: 52 'wrong_approach' friction events in usage data traced to incomplete fixes and misdiagnosed root causes cascading into new bugs. A forced verification gate catches these before declaration.

### 8.1 Device Window Display Check (Responsive Verification)

After build, verify the site renders correctly across key viewport sizes. Use Playwright to launch a browser and check for layout regressions.

**Required viewports:**
| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 812px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

**Procedure** (run after `npm run build`):
1. Start preview server: `npm run preview -- --port 4321 &` (background)
2. Wait for server: `sleep 3`
3. For each viewport, use Playwright to:
   - Navigate to `http://localhost:4321/`
   - Resize browser to viewport dimensions
   - Take a snapshot / check for console errors
   - Navigate to key pages (home, project pages, zh/ and en/ variants)
4. Report any layout overflow, overlapping elements, or console errors per viewport.
5. Shut down preview server: `pkill -f "astro preview"` (or `kill $PID`)

**Acceptance criteria:**
- Zero console errors (Error level) at all viewports
- No horizontal overflow (`document.body.scrollWidth > window.innerWidth`)
- No elements clipped or hidden at mobile (375px) width

**Why**: CSS changes can introduce viewport-specific regressions (e.g. horizontal scroll on mobile, collapsed nav menus, overflowing text). Build passing does not guarantee visual correctness at all sizes.

### 8.2 Chinese / English Content Parity Check

Verify that every visible text element on the Chinese version has a corresponding entry on the English version, and vice versa. This catches untranslated strings, missing i18n keys, and hardcoded strings.

**Scope**: All pages under `src/pages/` and all `.astro` components.

**Procedure:**
1. **i18n key parity**: Diff `en.json` and `zh.json` top-level keys. Every key present in one must be present in the other. Missing keys are a FAIL.
   ```bash
   # Get key counts — must match exactly
   node -e "console.log(Object.keys(require('./src/content/i18n/en.json')).sort().join('\n'))" > /tmp/en_keys.txt
   node -e "console.log(Object.keys(require('./src/content/i18n/zh.json')).sort().join('\n'))" > /tmp/zh_keys.txt
   diff /tmp/en_keys.txt /tmp/zh_keys.txt && echo "KEYS_MATCH" || echo "KEY_MISMATCH"
   ```
2. **Hardcoded string scan**: Scan `.astro` and `.ts` files for visible text not routed through `t()`.
   ```bash
   # Flag hardcoded Chinese or English text in source
   grep -rn "[一-鿿]" src/ --include="*.astro" --include="*.ts" | grep -v "import.*from" | grep -v "t(" | head -20
   grep -rn "[A-Z][a-z].{20,50}" src/ --include="*.astro" | grep -v "t(" | grep -v "import" | head -20
   ```
   Any result here is a potential hardcoded string that should use `t()`.
3. **Page-level snapshot parity** (optional, if Playwright is available):
   - Navigate to `/zh/` and `/en/` pages at desktop viewport
   - Compare visible text nodes — untranslated strings will appear as Chinese in the English shell or vice versa

**Acceptance criteria:**
- `en.json` and `zh.json` have identical key sets (diff returns empty)
- Zero hardcoded Chinese/English strings found in grep scan
- No untranslated text visible switching between zh/ and en/ routes

**Why**: Bilingual sites decay when new strings are added to only one locale, or when developers hardcode UI text instead of using `t()`. This check catches both failure modes at verification time.

### 8.3 GitHub Actions CI Failure Protocol

**This is a MANDATORY step after every push.** Do NOT assume the build passed just because `npm run build` succeeded locally. CI runs in a different environment and will surface different failures.

**Procedure:**
1. After push, monitor the GitHub Actions run at `https://github.com/<owner>/<repo>/actions`
2. If the workflow fails:
   - **Do not ignore or defer.** The failure is real and must be fixed.
   - Read the failure log carefully — CI failures often reveal missing dependencies, wrong Node version, pnpm vs npm lock file mismatch, or missing environment variables.
3. Common CI failure causes and fixes:
   | Cause | Fix |
   |-------|-----|
   | `pnpm-lock.yaml` out of sync with `package.json` | Re-run `pnpm install` locally, commit and push |
   | `@fontsource/*` installed but `node_modules` not regenerated | Delete `node_modules`, run `pnpm install`, commit + push |
   | CI uses `npm ci` but `package-lock.json` exists | Delete `package-lock.json`, use pnpm consistently |
   | Missing `.npmrc` with pnpm config | Add `.npmrc` with required settings, commit + push |
   | Build script uses `npm run build` but deps differ | Ensure `npm run build` works identically locally |
   | Type errors only on CI (not locally) | Run `npx astro check` locally, fix all errors |
4. After fixing: push again, re-monitor CI.
5. **Loop until CI is green.** Do not stop at "it works locally."
6. Once CI passes, run `git log --oneline -3` to confirm the final commit.

**Why**: CI is the source of truth for deployment. A passing local build with a failing CI means the site will not deploy. Common causes: lock file drift, Node version mismatch, different shell environments.

### Iteration-20 (2026-05-15) — Production Ready ✓

| Metric | with_skill | without_skill | Delta |
|--------|------------|----------------|-------|
| Pass Rate | **100%** (mean 1.0) | 93.3% (mean 0.93) | **+7%** |
| Time (s) | 148.9 ± 17.5 | 154.9 ± 21.6 | -6.0s |
| Tokens | 44,918 ± 1,082 | 39,374 ± 2,143 | +5,544 |

**Per-eval breakdown (eval_id 0/1/2 = anti-pattern/i18n/performance):**

| Eval | Config | Pass Rate | Time | Tokens |
|------|--------|-----------|------|--------|
| anti-pattern | with_skill | **5/5** | 141.9s | 44,490 |
| anti-pattern | without_skill | 4/5 | 131.0s | 37,536 |
| i18n | with_skill | **5/5** | 168.7s | 46,031 |
| i18n | without_skill | 5/5 | 170.7s | 41,731 |
| performance | with_skill | **5/5** | 136.1s | 44,232 |
| performance | without_skill | 5/5 | 162.9s | 38,855 |

**Key fixes that achieved 100% with_skill pass rate:**
- i18n: explicit `npm run build` + `git commit` steps in fix procedure (iter-19 had commit failures)
- performance: corrected `loading="lazy"` grep pattern + hero.png PNG/JPEG format acceptance

**Historical trend:**

| Iteration | with_skill | without_skill | Delta | Key Change |
|-----------|-----------|----------------|-------|------------|
| iter-18 | 93.3% | 73.3% | +20% | Fixed parallel cp contamination, agent cwd |
| iter-19 | 86.7% | 66.7% | +20% | — |
| iter-20 | **100%** | 93.3% | **+7%** | Commit embedded in fix procedure |

**Note:** Iteration-18 through -20 fixed the infrastructure issues from iteration-17 (parallel `cp` cross-contamination, agent working directory inheritance). The commit-embedding requirement from iteration-17 is now enforced via mandatory `smart-autopush.sh` in every fix workflow step.

## Bundled Resources

### references/astro-modernization-checklist.md
Full Astro v6 migration checklist — pre-upgrade state, dependency upgrade path (Astro 4/5 → 6), code migration (images, ViewTransitions→ClientRouter, Content Collections, Tailwind v3→v4), post-upgrade verification, and rollback plan. Use for large version upgrades.

### references/project-page-template.astro
Starter template for a bilingual project page with Hero/Abstract/Method/Results/BibTeX/Links sections. Copy to `src/pages/<project>/[lang]/index.astro` and replace paper metadata. Covers `createTranslator`, `oklch()` theme colors, and copy-to-clipboard BibTeX.

### references/scan-checklist.md
Comprehensive anti-pattern audit checklist — i18n, performance, asset, and framework patterns with detection commands and fix procedures.

### references/project-page-audit-checklist.md
Extended health checklist for existing project pages and homepages — PWA, SEO, terminology, repository hygiene.
