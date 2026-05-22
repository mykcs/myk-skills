# i18n Sync Audit Report

## Project
- Path: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-10/i18n-sync-audit/mock-repo/`
- Framework: Astro v5 (static output)
- Languages: en, zh

## Audit Methodology
1. Flatten both JSON translation files and compare key sets.
2. Compare nested structure and value types.
3. Scan all `.astro` components for `t.*` key references.
4. Cross-reference JSON keys against component usage.

## Findings

### 1. Key Completeness: PASS
- Both `en.json` and `zh.json` contain exactly the same 10 keys.
- No missing keys in either language file.

### 2. Structure Consistency: PASS
- Identical nesting structure across both files.
- All value types match (strings within objects).

### 3. Usage vs. Definition Mismatch: 2 issues

#### Issue A: Unused keys in JSON (dead translations)
- `nav.contact` — present in both EN/ZH but never referenced in any `.astro` component.
- `footer.backToTop` — present in both EN/ZH but never referenced in any `.astro` component.

**Impact:** These translations are orphaned. They bloat the bundle slightly and may mislead future maintainers into thinking a "Contact" link or "Back to Top" feature exists.

#### Issue B: Missing page/route for `nav.about`
- `Navbar.astro` references `t.nav.about` and links to `/about/`.
- No `src/pages/[lang]/about.astro` (or equivalent) exists.
- No `src/pages/about/` directory exists.
- Clicking "About" will result in a 404.

**Impact:** Broken navigation link.

### 4. Astro i18n Config vs. Implementation Mismatch: 1 issue

#### Issue C: `prefixDefaultLocale: false` with manual `[lang]` routing
- `astro.config.mjs` sets `prefixDefaultLocale: false` and defines `locales: ['en', 'zh']`.
- However, pages are manually implemented under `src/pages/[lang]/index.astro`.
- The root `src/pages/index.astro` hard-redirects to `/zh/`.
- This creates an architectural inconsistency: Astro's built-in i18n helpers expect the default locale at the root when `prefixDefaultLocale: false`, but the root is occupied by a redirect page.

## Recommendations
1. Remove `nav.contact` and `footer.backToTop` from both JSON files if they are not planned for use.
2. Create `src/pages/[lang]/about.astro` to fix the broken `/about/` link, OR remove the About link from `Navbar.astro`.
3. (Optional) Align `astro.config.mjs` i18n settings with the manual `[lang]` routing strategy.

## Action Taken
- No translation text mismatches were found.
- The EN and ZH strings are semantically aligned.
- Issues identified are structural (unused keys, missing route) rather than translation-sync issues.
