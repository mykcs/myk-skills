# i18n Sync Audit Summary

## Issues Found

### 1. Key Set Mismatch Between Locales
- `zh.json` had keys missing from `en.json`:
  - `nav.contact`
  - `hero.cta`
  - `footer.backToTop`
- Both files lacked shared keys for newly extracted UI text:
  - `meta.siteTitle`
  - `navbar.homeLabel`
  - `navbar.aboutLabel`
  - `navbar.currentLang`

### 2. Conditional Bilingual Rendering (Anti-Pattern)
- `Hero.astro`: `{lang === 'zh' ? '欢迎' : 'Welcome'}`
- `[lang]/index.astro`: `{lang === 'zh' ? '演示站点' : 'Demo Site'}`

### 3. Hardcoded Chinese Text in Components
- `Hero.astro`: subtitle and button text
- `Navbar.astro`: nav links and language label
- `[lang]/index.astro`: footer copyright text

### 4. Static HTML Lang Attribute
- `Layout.astro` hardcoded `lang="zh"` instead of reflecting the active locale.

## Fixes Applied

| File | Change |
|------|--------|
| `src/lib/i18n.ts` | **Created** — minimal `t(key, lang)` helper with dot-path lookup |
| `src/content/i18n/en.json` | Added missing keys so key set matches `zh.json` |
| `src/content/i18n/zh.json` | Added `meta.siteTitle` and `navbar.*` keys |
| `src/components/Hero.astro` | Replaced conditional + hardcoded text with `t()` calls |
| `src/components/Navbar.astro` | Replaced hardcoded Chinese text with `t()` calls |
| `src/pages/[lang]/index.astro` | Replaced conditional + hardcoded text with `t()` calls; passed `lang` to `Layout` |
| `src/layouts/Layout.astro` | Made `html lang` dynamic via `lang` prop |

## Verification

- `grep -rn "lang ===" src/` → **zero matches** (no conditional bilingual rendering remains)
- `npm run build` → **passes** (3 pages built successfully)
- `git log --oneline -1` → commit `1c7cfe9` confirmed

## Key Modified Files (Saved to Outputs)

- `en.json`
- `zh.json`
- `Hero.astro`
- `Navbar.astro`
- `lang_index.astro`
- `Layout.astro`
- `i18n.ts`
