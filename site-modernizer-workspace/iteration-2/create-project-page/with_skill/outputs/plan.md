# OSA Project Page Creation Plan

## Overview
Create a bilingual (zh/en) project showcase page for CVPR 2026 paper "OSA" at `/osa/`, matching GDKVM quality. Stack: Astro 6 + Tailwind v4.

## Project Context
- **Working directory**: `/Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro`
- **Output**: Static site deployed to GitHub Pages at `https://wangrui2025.github.io/osa/`
- **Existing redirect**: `/Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro/public/OSA/index.html` currently redirects to `/osa/` (case fix)
- **Paper data**: Already exists in `src/content/papers/osa.json`
- **Assets**: Available in `public/academic/images/papers/cvpr2026-osa/`

## Architecture Analysis

### Astro Config (`astro.config.mjs`)
- `output: 'static'`
- `i18n.defaultLocale: 'zh'`, `locales: ['en', 'zh']`
- `routing.prefixDefaultLocale: false` (zh has no prefix, en is `/en/`)
- `site: 'https://wangrui2025.github.io'`
- Tailwind v4 via `@tailwindcss/vite`

### Existing Patterns
- Homepage uses `[lang]/index.astro` with `getStaticPaths()` returning `{ params: { lang: 'en' } }` and `{ params: { lang: 'zh' } }`
- `BaseLayout` provides SEO, theme toggle, KaTeX math, ClientRouter, structured data
- `Masthead` handles navigation + language switch via `getRelativeLocaleUrl`
- Content collections use `getEntry('papers', 'osa')` / `getCollection('papers')`
- Images use `astro:assets` `<Image>` component with build-time imports for vendor assets
- Dark mode: class-based via `html.dark`, initialized inline before paint

### Asset Inventory (OSA)
```
public/academic/images/papers/cvpr2026-osa/
  fig_osu_page-0001.jpg          # Teaser / main framework figure
  fig/
    osu/fig_osu.png              # OSU module diagram
    apfe/fig_apfe.png            # APFE module diagram
    Met/fig_overview.png         # Method overview
    first/fig_first.png          # First frame / initialization
    fail/fig_fail.png            # Failure case analysis
    challenge/image.png          # Challenge illustration
    landscape/fig_landscape.png  # 3D landscape visualization
    landscape_2d/image.png       # 2D landscape visualization
    abl/fig_abl.png              # Ablation study figure
    Exp/image.png                # Experiment figure
  tab/
    tab_abl.png                  # Ablation table
    tab_cap.png                  # Capability comparison table
```

## File Structure to Create

```
src/
  pages/
    osa/
      index.astro          # Redirect: /osa/ -> /osa/zh/
      [lang]/
        index.astro        # Main project page (en + zh)
  content/
    osa-page/
      zh.json              # Chinese page content
      en.json              # English page content
  components/
    osa/
      Hero.astro           # Title, authors, venue badge, teaser
      Abstract.astro       # Bilingual abstract text
      Method.astro         # Method figures + description
      Results.astro        # Quantitative tables + qualitative visuals
      BibTeX.astro         # Copy-ready citation block
      SectionHeading.astro # Reusable section heading
  layouts/
    ProjectLayout.astro    # Project-specific layout (extends BaseLayout)
```

## Step-by-Step Execution

### Phase 1: Content Data (Content Collection)

#### Step 1.1: Register `osa-page` collection in `src/content.config.ts`
```typescript
const osaPage = defineCollection({
  loader: glob({ base: './src/content/osa-page', pattern: '**/*.json' }),
  schema: z.object({
    // Hero
    title: z.string(),
    venue_badge: z.string(),
    venue_full: z.string(),
    authors: z.array(z.object({
      name: z.string(),
      affiliation: z.string().optional(),
      is_self: z.boolean().default(false),
      is_corresponding: z.boolean().default(false),
    })),
    // Abstract
    abstract: z.string(),
    // Method sections
    method_sections: z.array(z.object({
      heading: z.string(),
      description: z.string(),
      image_key: z.string().optional(),
    })),
    // Results
    results_intro: z.string(),
    // BibTeX
    bibtex: z.string(),
    // Links
    arxiv_url: z.string(),
    project_url: z.string(),
  }),
});
// Add to collections export: { ..., osaPage }
```

#### Step 1.2: Create `src/content/osa-page/zh.json`
```json
{
  "title": "OSA: 使用正交状态更新与解剖先验感知特征增强的超声心动图视频分割",
  "venue_badge": "CVPR 2026 Highlight",
  "venue_full": "IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) 2026",
  "authors": [
    { "name": "王锐", "affiliation": "深圳大学", "is_self": true },
    { "name": "吴惠思", "affiliation": "深圳大学", "is_corresponding": true },
    { "name": "秦璟", "affiliation": "深圳大学" }
  ],
  "abstract": "超声心动图视频分割对于心脏功能评估至关重要...",
  "method_sections": [
    { "heading": "概述", "description": "...", "image_key": "overview" },
    { "heading": "正交状态更新 (OSU)", "description": "...", "image_key": "osu" },
    { "heading": "解剖先验感知特征增强 (APFE)", "description": "...", "image_key": "apfe" }
  ],
  "results_intro": "我们在多个基准数据集上进行了全面评估...",
  "bibtex": "@inproceedings{wang2026osa,\\n  title={OSA: Echocardiography Video Segmentation via Orthogonalized State Update and Anatomical Prior-aware Feature Enhancement},\\n  author={Wang, Rui and Wu, Huisi and Qin, Jing},\\n  booktitle={CVPR},\\n  year={2026}\\n}",
  "arxiv_url": "https://arxiv.org/pdf/2603.26188",
  "project_url": "https://wangrui2025.github.io/osa/"
}
```

#### Step 1.3: Create `src/content/osa-page/en.json`
- Mirror structure with English content
- Author names in English: "Rui Wang", "Huisi Wu", "Jing Qin"

### Phase 2: Layout & Components

#### Step 2.1: Create `src/layouts/ProjectLayout.astro`
- Extends `BaseLayout`
- Props: `title`, `description`, `lang`, `ogImage` (teaser image)
- Sets `showNav: true`, `fixedFavicon: false`
- Adds `ScholarlyArticle` schema.org structured data in `<head>`
- No sidebar (project pages are single-column)
- Full-width content area (override `#main` max-width for hero)

#### Step 2.2: Create `src/components/osa/SectionHeading.astro`
```astro
---
interface Props { icon?: string; title: string; }
const { icon, title } = Astro.props;
---
<h2 class="section-heading font-medium text-[28px] leading-[1.2] flex items-center gap-2">
  {icon && <Icon name={icon} class="w-5 h-5 text-link-primary" />}
  {title}
</h2>
```

#### Step 2.3: Create `src/components/osa/Hero.astro`
- Full-width gradient background (warm editorial tone matching site theme)
- Paper title (large, serif font)
- Author list with affiliations, self bolded, corresponding marked with `*`
- Venue badge: "CVPR 2026 Highlight" with highlight styling
- Teaser image (`fig_osu_page-0001.jpg`) centered, max-width ~900px
- Action buttons: [arXiv] [Project] [Code] (if applicable)
- Quick links row below teaser

#### Step 2.4: Create `src/components/osa/Abstract.astro`
- `SectionHeading` with `tabler:file-text` icon
- Abstract text in readable width (~700px max)
- Collapsible " TL;DR " or key contribution bullets below

#### Step 2.5: Create `src/components/osa/Method.astro`
- `SectionHeading` with `tabler:settings` icon
- Iterate `method_sections` from content JSON
- Each section: heading + description + optional figure
- Figures use `<Image>` with lazy loading
- Grid layout for side-by-side comparisons if needed

#### Step 2.6: Create `src/components/osa/Results.astro`
- `SectionHeading` with `tabler:chart-bar` icon
- Quantitative results: use `tab/tab_abl.png` and `tab/tab_cap.png` as images
- Qualitative results: grid of figure images (challenge, fail, first, landscape)
- Each figure with caption below

#### Step 2.7: Create `src/components/osa/BibTeX.astro`
- `SectionHeading` with `tabler:quote` icon
- Pre-formatted BibTeX block in `<pre><code>`
- Copy-to-clipboard button (client-side JS, inline)
- Styled code block using expressive-code theme or custom

### Phase 3: Page Routes

#### Step 3.1: Create `src/pages/osa/index.astro`
```astro
---
return Astro.redirect('/osa/zh/', 302);
---
```
(Chinese default per site config)

#### Step 3.2: Create `src/pages/osa/[lang]/index.astro`
```astro
---
import ProjectLayout from '../../../layouts/ProjectLayout.astro';
import Hero from '../../../components/osa/Hero.astro';
import Abstract from '../../../components/osa/Abstract.astro';
import Method from '../../../components/osa/Method.astro';
import Results from '../../../components/osa/Results.astro';
import BibTeX from '../../../components/osa/BibTeX.astro';
import { getEntry } from 'astro:content';

export function getStaticPaths() {
  return [{ params: { lang: 'en' } }, { params: { lang: 'zh' } }];
}

const lang = Astro.params.lang as 'en' | 'zh';
const page = await getEntry('osa-page', lang);
if (!page) throw new Error(`osa-page entry "${lang}" not found`);
const data = page.data;
---

<ProjectLayout
  title={`${data.title} | ${data.venue_badge}`}
  description={data.abstract.slice(0, 160)}
  lang={lang}
>
  <Hero data={data} lang={lang} />
  <Abstract data={data} lang={lang} />
  <Method data={data} lang={lang} />
  <Results data={data} lang={lang} />
  <BibTeX data={data} lang={lang} />
</ProjectLayout>
```

### Phase 4: Image Handling

#### Step 4.1: Import teaser image in Hero component
```astro
---
import { Image } from 'astro:assets';
import teaserImage from '../../../../vendor/academic/images/papers/cvpr2026-osa/fig_osu_page-0001.jpg';
---
<Image src={teaserImage} alt="OSA Framework" width={900} height={450} />
```

#### Step 4.2: Method/Results figures
- For build-time optimization: import key figures as Astro assets
- For dynamic lists: use `<img src="/academic/images/papers/cvpr2026-osa/fig/..." />` with proper `alt` text

### Phase 5: Styling (Tailwind v4)

All styles use existing design tokens from `src/styles/global.css`:
- Background: `bg-bg-primary dark:bg-bg-dark`
- Text: `text-text-primary dark:text-text-dark`
- Accent: `text-paper-accent dark:text-paper-accent-dark`
- Cards: `bg-paper-bg dark:bg-paper-bg-dark border border-paper-border dark:border-paper-border-dark`
- Section headings: reuse `.section-heading` class

Hero-specific additions to `global.css` (if needed, < 50 lines):
```css
.project-hero {
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, rgb(250 249 245) 100%);
}
html.dark .project-hero {
  background: linear-gradient(135deg, var(--color-bg-dark) 0%, rgb(30 30 28) 100%);
}
```

### Phase 6: SEO & Structured Data

Add `ScholarlyArticle` schema in `ProjectLayout`:
```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "name": "OSA: ...",
  "author": [...],
  "datePublished": "2026",
  "isPartOf": { "@type": "PublicationEvent", "name": "CVPR 2026" }
}
```

### Phase 7: Verification

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro

# 1. TypeScript check
npx astro check

# 2. Build
npm run build

# 3. Verify routes exist in dist/
ls dist/osa/
ls dist/osa/zh/
ls dist/osa/en/

# 4. Verify no broken image references
grep -r "img src" dist/osa/ | head -20

# 5. Verify structured data
grep -r "ScholarlyArticle" dist/osa/

# 6. Start dev server and screenshot (optional)
npm run dev &
# Visit http://localhost:4321/osa/
```

### Phase 8: Cleanup

- Remove old redirect `public/OSA/index.html` (now handled by Astro routes)
- Or keep it as fallback: update to redirect to `/osa/zh/`

### Phase 9: Commit

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io
bash scripts/smart-autopush.sh . "feat(osa): add CVPR 2026 OSA bilingual project page with Hero/Abstract/Method/Results/BibTeX sections"
```

## Commands Summary

| Step | Command |
|------|---------|
| Register collection | Edit `src/content.config.ts` |
| Create content | Write `src/content/osa-page/zh.json` + `en.json` |
| Create layout | Write `src/layouts/ProjectLayout.astro` |
| Create components | Write 6 files in `src/components/osa/` |
| Create routes | Write `src/pages/osa/index.astro` + `src/pages/osa/[lang]/index.astro` |
| Type check | `npx astro check` |
| Build | `npm run build` |
| Verify | `ls dist/osa/` + grep checks |
| Commit | `bash scripts/smart-autopush.sh . "feat(osa): ..."` |

## Risk Notes
- `prefixDefaultLocale: false` means `/osa/` (no lang) must redirect to `/osa/zh/`, not `/zh/osa/`
- Image imports from `vendor/academic/` may fail if submodule not initialized; fallback to `public/academic/images/...`
- Ensure `getStaticPaths()` matches existing pattern used by `src/pages/[lang]/index.astro`
- Dark mode FOUC: verify `html.dark` class is set before any project-page paint
