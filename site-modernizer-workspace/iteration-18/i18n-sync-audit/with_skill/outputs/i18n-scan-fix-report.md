# i18n Sync Audit Report

## Scan Date: 2026-05-15

## Issues Found & Fixed

| Issue | File | Fix |
|-------|------|-----|
| Hardcoded Chinese "当前语言" | `Navbar.astro` | Added `navbar.currentLang` key |
| Hardcoded Chinese footer | `[lang]/index.astro` | Use `t.footer.copyright` |
| Conditional title `lang === 'zh' ? '演示站点' : 'Demo Site'` | `[lang]/index.astro` | Use `t.page.title` from JSON |
| Hardcoded title in Layout | `Layout.astro` | Use `t.page.title` from JSON |
| Missing keys in en.json | `en.json` | Added `page.title`, `navbar.currentLang`, `cta` |

## Changes Made

### Added to en.json and zh.json
```json
"page": { "title": "..." },
"navbar": { "currentLang": "..." }
```

### Modified Components
- `Navbar.astro`: Use `t.nav.home`, `t.nav.about`, `t.navbar.currentLang`
- `Layout.astro`: Use `t.page.title` for title
- `[lang]/index.astro`: Remove conditional title, use footer from `t()`

## Verification
- Build: PASS
- `grep "lang ==="` (conditional text): ZERO matches
- Commit: `8ad93f7 fix(i18n): eliminate hardcoded text and conditional title rendering`

## Key Sync Rule
All user-facing text must use `t('key')` - no inline conditionals like `{lang === 'zh' ? '中文' : 'English'}`.
