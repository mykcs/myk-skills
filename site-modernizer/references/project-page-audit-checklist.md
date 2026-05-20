# Project Page & Homepage Audit Checklist

Derived from real-world audits of academic project pages (GDKVM, OSA) and personal homepages.

## Pre-Audit Web Research

> **MANDATORY.** Validate current best practices before auditing.

```
mcp__context7__query_docs: "Astro academic personal homepage best practices 2025"
mcp__context7__query_docs: "PWA maskable icon manifest specification 2025"
mcp__context7__query_docs: "Open Graph image size recommendation Twitter LinkedIn 2025"
WebSearch: "academic personal homepage SEO best practices 2025"
```

## Homepage / Global Issues

| Priority | Issue | Impact |
|----------|-------|--------|
| P0 | `papers` → `publications`, `honors` → `awards` (including cross-repo `mykcs/academic` submodule) | Terminology inconsistency, tech debt |
| P1 | Missing `/en/cv/` English CV page | Conflicts with "global research community" goal |
| P1 | `manifest.json` fixes (maskable icons, dynamic `theme_color`) | PWA compliance, dark mode UX |
| P1 | Open Graph missing (`og:image`, `og:locale:alternate`) | Social sharing previews |
| P1 | CSS inline optimization (Critical CSS + font preloading) | First-contentful paint, bandwidth |

## Per-Project Page Issues (GDKVM / OSA pattern)

| Priority | Issue | Impact |
|----------|-------|--------|
| P1 | Create `CONTEXT.md` for domain glossary | Missing bounded-context terminology |
| P1 | Remove `website/` build artifacts from repo | Repository hygiene |
| P1 | Fix `CLAUDE.md` title errors (e.g. copied from another project) | Documentation accuracy |
| P2 | i18n architecture refactor (Content Collections → `src/i18n/`) | Maintenance cost |

## Detection Commands

```bash
# Check for outdated terminology
grep -rn "papers\|honors" src/ content/ --include="*.json" --include="*.ts" --include="*.astro"

# Check manifest.json health
cat public/manifest.json | jq '.icons[] | select(.purpose | contains("maskable") | not)'

# Check Open Graph
grep -rn 'og:image\|og:locale' src/layouts/ src/pages/

# Check for build artifacts that should not be in repo
ls website/ 2>/dev/null && echo "website/ dir exists — should be gitignored or removed"
```
