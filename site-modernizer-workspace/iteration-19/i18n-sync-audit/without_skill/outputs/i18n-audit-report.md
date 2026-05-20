# i18n Sync Audit Report

## Scan Scope
- Translation files: `src/content/i18n/en.json`, `src/content/i18n/zh.json`
- Components: `src/components/Hero.astro`, `src/components/Navbar.astro`
- Layouts: `src/layouts/Layout.astro`
- Pages: `src/pages/[lang]/index.astro`, `src/pages/index.astro`

## Issues Found & Fixes

### 1. Hero.astro — Hardcoded conditional rendering + hardcoded Chinese text
**Severity: HIGH**

| Line | Before | After |
|------|--------|-------|
| 5 | `lang === 'zh' ? '欢迎' : 'Welcome'` | `t.hero.title` |
| 6 | `这是一个演示网站` (hardcoded zh) | `t.hero.subtitle` |
| 7 | `立即开始` (hardcoded zh) | `t.hero.cta` |

**Fix**: Imported translation JSONs into Hero.astro and replaced all hardcoded strings with `t.hero.*` keys. The translation keys already existed in both `en.json` and `zh.json`.

### 2. zh.json — Missing key `extra_en_only`
**Severity: MED**

`en.json` contained `"extra_en_only": "This key is missing in zh"` but `zh.json` had no counterpart.

**Fix**: Added `"extra_en_only": "此键在英文中存在"` to `zh.json`.

### 3. Navbar.astro — Missing `contact` navigation link
**Severity: LOW**

Both `en.json` and `zh.json` already had `nav.contact` keys, but `Navbar.astro` only rendered `home` and `about` links.

**Fix**: Added `<a href="/contact/">{t.nav.contact}</a>` to the navbar.

## Verification
- Build command: `node node_modules/astro/dist/cli/index.js build`
- Result: PASS (exit 0)
- Output directories: `dist/en/`, `dist/zh/`, `dist/index.html`

## Modified Files
- `src/components/Hero.astro`
- `src/components/Navbar.astro`
- `src/content/i18n/zh.json`
