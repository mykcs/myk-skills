# Dedup CV Page Plan (No Skill)

## Current State
- `src/pages/cv.astro` — pure Chinese CV page (hardcoded `lang = 'zh'`)
- `src/pages/[lang]/cv.astro` — bilingual CV page (supports `en` and `zh` via `getStaticPaths`)
- `src/components/CvContent.astro` — shared component rendering Chinese/English based on `lang` prop
- `astro.config.mjs` — i18n configured with `defaultLocale: 'zh'`, `prefixDefaultLocale: false`

## Problem
Duplicate CV pages exist. Users can access both `/cv` and `/zh/cv`, but `/cv` is redundant.

## Solution
1. Delete `src/pages/cv.astro` (the duplicate pure-Chinese page).
2. Create `src/pages/cv/index.astro` that redirects to `/zh/cv/`.
   - Use Astro's `<meta http-equiv="refresh">` redirect for static output compatibility.
3. Verify no other files reference the old `cv.astro` page directly.

## Why Not Modify `[lang]/cv.astro`?
It already correctly handles both languages; no changes needed there.

## Verification Steps
- Build the project (`astro build`) and confirm no errors.
- Check that `/cv` redirects to `/zh/cv/`.
