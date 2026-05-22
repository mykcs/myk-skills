# Site Modernizer Skill — Fix Plan (DECIDE + CLEAN + BUILD + SCAN)

## Phase 1: DECIDE — Architecture Decisions

### ADR-001: Migrate from Astro.glob to Content Collections
- **Context**: `Astro.glob()` is deprecated and build-breaking
- **Decision**: Create `src/content/posts/` collection with `src/content/config.ts`
- **Consequence**: All markdown content moves to `src/content/`

### ADR-002: Upgrade Tailwind from v3 to v4
- **Context**: `@astrojs/tailwind` is legacy; Tailwind v4 uses `@tailwindcss/vite`
- **Decision**: Remove `@astrojs/tailwind`, install `tailwindcss@^4` + `@tailwindcss/vite`
- **Consequence**: May need to migrate `tailwind.config.mjs` to CSS-based config

### ADR-003: Adopt ClientRouter for View Transitions
- **Context**: `ViewTransitions` component deprecated in Astro 4+
- **Decision**: Replace with `ClientRouter`
- **Consequence**: No behavior change, just API update

## Phase 2: CLEAN — Immediate Fixes

### Step 2.1: Fix Build-Breaking Anti-Patterns

```bash
# Fix 1: Replace ViewTransitions with ClientRouter
# In src/pages/index.astro:
# - Change: import { ViewTransitions } from 'astro:transitions';
# + Change: import { ClientRouter } from 'astro:transitions';
# - Change: <ViewTransitions />
# + Change: <ClientRouter />

# Fix 2: Remove Image format attributes
# In src/components/Gallery.astro:
# - Change: format="webp"
# - Change: format="avif"

# Fix 3: Remove define:vars, use CSS custom properties
# In src/pages/index.astro:
# - Change: <style define:vars={{ themeColor }}>
# + Change: Move to global CSS or inline style
```

### Step 2.2: Create Content Collections

```bash
mkdir -p src/content/posts
```

Create `src/content/config.ts`:
```typescript
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.date(),
  }),
});

export const collections = { posts };
```

Update `src/pages/index.astro`:
```astro
---
import { getCollection } from 'astro:content';
const posts = await getCollection('posts');
---
```

### Step 2.3: Commit Changes

```bash
bash scripts/smart-autopush.sh . "refactor(site): migrate Astro.glob to Content Collections, replace ViewTransitions with ClientRouter, remove Image format attrs" done
```

## Phase 3: BUILD — Pipeline Unification

No scattered build scripts detected. Current pipeline is unified via `package.json` scripts.

If build scripts grow, consider `src/integrations/build-pipeline.mjs` per skill template.

## Phase 4: SCAN — Re-verify After Fixes

After applying fixes, re-run:

```bash
npm run build
npx astro check
```

Expected results:
- [ ] `npm run build` passes (0 errors)
- [ ] `npx astro check` passes (0 hints)
- [ ] No `Astro.glob` references remain
- [ ] No `ViewTransitions` references remain
- [ ] No `format="..."` on `<Image>` remains
- [ ] No `define:vars` on `<style>` remains

## Phase 5: REDIRECT — N/A

No page moves or renames detected. No redirects needed.

## Phase 6: VERIFY — Pre-Push Checklist

- [ ] `npm run build` passes (0 errors)
- [ ] `astro check` passes (0 TS errors)
- [ ] No `.DS_Store` or `node_modules` staged
- [ ] Every file change committed with Conventional Commits message
- [ ] Commit message describes WHY, not just filenames
- [ ] Push via `smart-autopush.sh`
