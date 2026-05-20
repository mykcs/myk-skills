# Fixes Applied

## Fix 1: Replace `ViewTransitions` with `ClientRouter`
- **File**: src/pages/index.astro
- **Change**: `import { ViewTransitions } from 'astro:transitions'` → `import { ClientRouter } from 'astro:transitions'`
- **Change**: `<ViewTransitions />` → `<ClientRouter />`
- **Reason**: `ViewTransitions` is deprecated in Astro 4+; `ClientRouter` is the replacement

## Fix 2: Replace `Astro.glob()` with Content Collections
- **File**: src/pages/index.astro
- **Change**: `const posts = await Astro.glob('./posts/*.md')` → `const posts = await getCollection('posts')`
- **Change**: `p.frontmatter.title` → `p.data.title`, `p.url` → `/posts/${p.slug}/`
- **New File**: src/content/config.ts (Zod schema for posts collection)
- **Moved**: src/pages/posts/hello.md → src/content/posts/hello.md
- **Reason**: `Astro.glob` is deprecated and will be removed

## Fix 3: Remove explicit `format` from `<Image>`
- **File**: src/components/Gallery.astro
- **Change**: Removed `format="webp"` and `format="avif"` from `<Image>` components
- **Reason**: Astro 6 / Sharp auto-optimizes format; explicit format prevents optimization

## Fix 4: Replace `define:vars` on `<style>` with CSS custom property
- **File**: src/pages/index.astro
- **Change**: Removed `define:vars` from `<style>` tag
- **Change**: Added `<script is:inline define:vars={{ themeColor }}>` to set CSS custom property on `:root`
- **Reason**: `define:vars` on `<style>` is discouraged; CSS custom properties are preferred

## Fix 5: Fix duplicate `<html>` / `<head>` structure
- **File**: src/pages/index.astro
- **Change**: Removed outer `<html>` and `<head>` tags; page now uses `Layout` component directly as root
- **Reason**: Layout already renders `<html>`; duplicate tags are invalid HTML

## Fix 6: Create missing directories and placeholder asset
- **Created**: src/assets/hero.png (placeholder)
- **Created**: src/content/posts/ (Content Collections directory)
- **Reason**: Gallery.astro referenced non-existent asset; Content Collections require content directory

## Verification After Fixes
- `npx astro check`: 0 errors, 1 hint (implicit any in map callback — acceptable)
- `npm run build`: PASS (1 page built, 0 errors)
- No deprecation warnings remain
