# Execution Plan: Deduplicate CV Pages

## Task Summary
Remove the duplicate standalone CV page (`src/pages/cv.astro`) and set up a redirect so that requests to `/cv/` automatically go to `/zh/cv/`.

## Current State Analysis
- `src/pages/cv.astro`: Standalone Chinese-only CV page (hardcodes `lang = 'zh'`).
- `src/pages/[lang]/cv.astro`: Bilingual CV page supporting both `/en/cv/` and `/zh/cv/` via `getStaticPaths()`.
- `astro.config.mjs`: Configured for static output (`output: 'static'`), with i18n default locale `zh` and `prefixDefaultLocale: false`.

## Execution Steps

### Step 1: Delete Duplicate Page
- **Action**: Remove `src/pages/cv.astro`.
- **Rationale**: It is functionally a subset of `src/pages/[lang]/cv.astro` (only the `zh` variant). Keeping it creates a duplicate route and maintenance burden.

### Step 2: Add Redirect for `/cv/` → `/zh/cv/`
- **Action**: Modify `astro.config.mjs` to add a redirect entry.
- **Rationale**: Astro's static build supports `redirects` in `astro.config.mjs`, which generates HTML meta-refresh files for static hosts (like GitHub Pages).
- **Expected config addition**:
  ```js
  export default defineConfig({
    // ... existing config ...
    redirects: {
      '/cv': '/zh/cv',
      '/cv/': '/zh/cv/',
    },
  });
  ```
  Note: Astro handles trailing slashes based on the `trailingSlash` config. Since none is set, adding both variants ensures coverage.

### Step 3: Verify No Broken Internal Links
- **Action**: Search the entire `src/` directory for any hardcoded links to `/cv` or `/cv/`.
- **Rationale**: Ensure no navigation components or other pages point to the soon-to-be-removed standalone page.
- **Current finding**: No internal links found in the mock repo.

### Step 4: Build Verification
- **Action**: Run `npm run build`.
- **Rationale**: Confirm that:
  1. `src/pages/cv.astro` is no longer emitted.
  2. `dist/cv/index.html` (or `dist/cv.html`) is generated as a redirect file.
  3. `dist/zh/cv/index.html` still exists and is valid.

## Risk Assessment
- **Low Risk**: This is a straightforward deletion + config change in a small, well-understood mock repo.
- **Edge Case**: If the production site has external links pointing to `/cv/`, the redirect will handle them gracefully.
