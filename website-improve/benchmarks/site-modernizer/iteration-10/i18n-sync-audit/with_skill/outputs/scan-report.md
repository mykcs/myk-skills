# i18n Sync Audit Report

## Scan Methodology
- Compared `src/content/i18n/en.json` and `src/content/i18n/zh.json` key-by-key.
- Checked components (`Hero.astro`, `Navbar.astro`, `Layout.astro`, `[lang]/index.astro`) for hardcoded Chinese strings that should be i18n-driven.
- Checked for missing translations, extra keys, and hardcoded fallback strings.

## Findings

### 1. Key Mismatches Between JSON Files

| Key | en.json | zh.json | Issue |
|-----|---------|---------|-------|
| `nav.contact` | MISSING | "联系我们" | Key exists only in zh |
| `hero.cta` | MISSING | "立即开始" | Key exists only in zh |
| `footer.backToTop` | MISSING | "返回顶部" | Key exists only in zh |

### 2. Hardcoded Chinese Strings in Components (Anti-Pattern)

| File | Line | Hardcoded String | Should Use Key |
|------|------|------------------|----------------|
| `Hero.astro` | 5 | `'欢迎'` / `'Welcome'` (inline ternary) | `hero.title` |
| `Hero.astro` | 6 | `'这是一个演示网站'` | `hero.subtitle` |
| `Hero.astro` | 7 | `'立即开始'` | `hero.cta` |
| `Navbar.astro` | 5 | `'首页'` | `nav.home` |
| `Navbar.astro` | 6 | `'关于我们'` | `nav.about` |
| `Navbar.astro` | 7 | `'当前语言: {lang}'` | `nav.currentLang` or similar |
| `Layout.astro` | 5 | `lang="zh"` (fixed) | Should reflect page locale |
| `[lang]/index.astro` | 12 | `'演示站点'` / `'Demo Site'` (inline ternary) | `site.title` |
| `[lang]/index.astro` | 15 | `'保留所有权利 © 2024'` | `footer.copyright` |

### 3. Missing English Translations to Add
- `nav.contact`: "Contact"
- `hero.cta`: "Get Started"
- `footer.backToTop`: "Back to Top"

### 4. Missing Chinese Translations to Add
- None (zh.json is the superset).

## Summary
- **3 keys** missing from `en.json`.
- **8 hardcoded strings** across 4 files that should be driven by i18n JSON.
- **1 layout issue**: `<html lang="zh">` is fixed regardless of locale.
