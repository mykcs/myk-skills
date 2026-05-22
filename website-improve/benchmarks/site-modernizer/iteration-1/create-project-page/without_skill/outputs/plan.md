# Execution Plan: OSA Project Showcase Page

## Project Context
- **Repository**: `mykcs.github.io/astro/`
- **Stack**: Astro 6.1.8 + Tailwind CSS 4.2.2 + `@tailwindcss/vite`
- **Fonts**: `@fontsource/inter` (local), `@fontsource/noto-serif-sc`, `@fontsource/source-serif-4`
- **Color Space**: oklch
- **Output**: Static (`output: 'static'`)
- **Deployment**: GitHub Pages (`https://wangrui2025.github.io`)
- **Bilingual**: English + Chinese (`prefixDefaultLocale: true`)
- **Paper**: OSA: Orthogonalized State Update..., CVPR 2026, arXiv: 2603.26188
- **Authors**: 王锐, 吴惠思 (corresponding), 秦璟

---

## 1. File Structure

```
mykcs.github.io/astro/
├── astro.config.mjs              (updated: add i18n routing)
├── src/
│   ├── layouts/
│   │   └── ProjectLayout.astro   (new: project-specific layout)
│   ├── pages/
│   │   ├── index.astro           (existing: redirect)
│   │   └── osa/
│   │       ├── index.astro       (new: EN project page)
│   │       └── zh/
│   │           └── index.astro   (new: ZH project page)
│   ├── components/
│   │   ├── osa/
│   │   │   ├── HeroSection.astro
│   │   │   ├── AbstractSection.astro
│   │   │   ├── MethodSection.astro
│   │   │   ├── ResultsSection.astro
│   │   │   ├── BibtexSection.astro
│   │   │   └── FooterSection.astro
│   │   └── ui/
│   │       ├── LanguageSwitch.astro
│   │       └── AuthorList.astro
│   ├── content/
│   │   └── osa/
│   │       ├── en.json           (EN content strings)
│   │       └── zh.json           (ZH content strings
│   └── styles/
│       └── global.css            (updated: add project theme vars)
└── public/
    └── osa/
        ├── teaser.jpg            (teaser image)
        ├── method.png            (method figure)
        └── results/              (result images)
```

---

## 2. URL Routing Setup

### 2.1 Astro Config Update (`astro.config.mjs`)

Add i18n configuration for bilingual routing:

```javascript
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://wangrui2025.github.io',
  integrations: [sitemap()],
  output: 'static',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh'],
    routing: {
      prefixDefaultLocale: true,
    },
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true,
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
```

### 2.2 Routing Table

| URL | Locale | File |
|-----|--------|------|
| `/osa/` | EN (default) | `src/pages/osa/index.astro` |
| `/osa/zh/` | ZH | `src/pages/osa/zh/index.astro` |

### 2.3 Language Switch Logic

Use `Astro.currentLocale` to detect current language and generate switch links:

```astro
---
const currentLocale = Astro.currentLocale || 'en';
const switchLocale = currentLocale === 'en' ? 'zh' : 'en';
const switchPath = currentLocale === 'en' ? '/osa/zh/' : '/osa/';
---
<a href={switchPath} class="language-switch">
  {switchLocale === 'zh' ? '中文' : 'English'}
</a>
```

---

## 3. Section-by-Section Content Plan

### 3.1 HeroSection

**Purpose**: Immediate visual impact, paper identity, quick links.

**Content**:
- **Title**: "OSA: Orthogonalized State Update for Efficient Neural Network Training"
- **Venue Badge**: "CVPR 2026" (styled badge)
- **arXiv Badge**: Link to `2603.26188`
- **Authors**: 王锐, 吴惠思*, 秦璟 (* = corresponding)
- **Institution**: Shenzhen University (深大)
- **Teaser Image**: Full-width hero image (16:9 aspect ratio)
- **Quick Links**: [Paper] [arXiv] [Code] [BibTeX]

**Design Spec**:
- Background: `oklch(15% 0.02 260)` (deep navy, dark mode first)
- Text: `oklch(95% 0 0)` (off-white)
- Accent: `oklch(65% 0.18 250)` (vibrant blue)
- Teaser image: `object-fit: cover`, max-height `60vh`
- Responsive: Stack vertically on mobile, side-by-side on desktop (teaser below title)

**Tailwind Classes**:
```
bg-[oklch(15%_0.02_260)] text-[oklch(95%_0_0)]
```

---

### 3.2 AbstractSection

**Purpose**: Concise paper summary in both languages.

**Content** (EN):
> We propose OSA, a novel optimization method that orthogonalizes state updates in adaptive optimizers. By decoupling the first and second moment estimates through orthogonal projection, OSA reduces gradient variance while maintaining computational efficiency. Our method achieves faster convergence and improved generalization across vision and language tasks...

**Content** (ZH):
> 我们提出 OSA，一种通过正交化状态更新来改进自适应优化器的新方法。通过对一阶和二阶矩估计进行正交投影解耦，OSA 在保持计算效率的同时降低了梯度方差。我们的方法在视觉和语言任务上实现了更快的收敛速度和更好的泛化性能...

**Design Spec**:
- Max-width: `768px` centered
- Font: `font-serif` for abstract body (academic feel)
- Language toggle: Tab switch or stacked display
- Background: Subtle gradient `oklch(20% 0.01 260)` to `oklch(18% 0.01 260)`

---

### 3.3 MethodSection

**Purpose**: Explain the core technical contribution with figures.

**Content**:
- **Heading**: "Method" / "方法"
- **Subsections**:
  1. Motivation: Why orthogonalization matters
  2. OSA Update Rule: Mathematical formulation
  3. Algorithm: Pseudo-code or flow diagram
- **Figure**: Method overview diagram (`method.png`)

**Design Spec**:
- Two-column layout on desktop (text left, figure right)
- Math: Use KaTeX (already configured in project via CDN or local)
- Figure: `rounded-xl shadow-lg`, `border border-oklch(30% 0.02 260)`
- Code/Algorithm: Shiki-highlighted block

**KaTeX Integration** (add to layout head):
```astro
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
```

---

### 3.4 ResultsSection

**Purpose**: Showcase quantitative and qualitative results.

**Content**:
- **Heading**: "Experiments" / "实验"
- **Subsections**:
  1. Main Results: Comparison tables (ImageNet, COCO, etc.)
  2. Ablations: Key hyperparameter studies
  3. Visualizations: Qualitative comparisons
- **Tables**: Styled HTML tables with Tailwind
- **Gallery**: Grid of result images

**Design Spec**:
- Tables: `w-full`, alternating row backgrounds, sticky header
- Gallery: CSS Grid `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`, gap-4
- Images: `rounded-lg`, hover `scale-105` transition
- Captions: `text-sm text-oklch(70% 0 0)`

---

### 3.5 BibtexSection

**Purpose**: Easy citation copy.

**Content**:
```bibtex
@inproceedings{wang2026osa,
  title={OSA: Orthogonalized State Update for Efficient Neural Network Training},
  author={Wang, Rui and Wu, Huisi and Qin, Jing},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year={2026}
}
```

**Design Spec**:
- Monospace font (`font-mono`)
- Copy button with clipboard API
- Dark code block background: `oklch(12% 0.01 260)`
- Syntax highlighting for BibTeX (use Shiki or simple color tokens)

---

### 3.6 FooterSection

**Purpose**: Credits, links, copyright.

**Content**:
- Copyright 2026
- Link to personal homepage
- Acknowledgments (if any)

**Design Spec**:
- Minimal, centered
- Border-top separator
- `text-sm text-oklch(60% 0 0)`

---

## 4. Code Snippets for Key Components

### 4.1 ProjectLayout.astro

```astro
---
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

interface Props {
  title: string;
  description: string;
  locale: string;
}

const { title, description, locale } = Astro.props;
const switchLocale = locale === 'en' ? 'zh' : 'en';
const switchPath = locale === 'en' ? '/osa/zh/' : '/osa/';
const switchLabel = locale === 'en' ? '中文' : 'English';
---

<!DOCTYPE html>
<html lang={locale} class="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <meta name="description" content={description} />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
      onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
  </head>
  <body class="bg-[oklch(15%_0.02_260)] text-[oklch(95%_0_0)] font-sans antialiased">
    <nav class="fixed top-0 w-full z-50 bg-[oklch(15%_0.02_260)]/80 backdrop-blur-md border-b border-[oklch(25%_0.02_260)]">
      <div class="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <a href="/" class="font-semibold text-lg">Rui Wang</a>
        <div class="flex items-center gap-4">
          <a href={switchPath} class="text-sm hover:text-[oklch(65%_0.18_250)] transition-colors">
            {switchLabel}
          </a>
        </div>
      </div>
    </nav>
    <main class="pt-14">
      <slot />
    </main>
  </body>
</html>
```

### 4.2 HeroSection.astro

```astro
---
interface Props {
  title: string;
  subtitle: string;
  venue: string;
  arxivId: string;
  authors: Array<{name: string; url?: string; isCorresponding?: boolean}>;
  institution: string;
  teaserImage: string;
}

const { title, subtitle, venue, arxivId, authors, institution, teaserImage } = Astro.props;
---

<section class="relative min-h-[80vh] flex flex-col items-center justify-center px-4 py-20">
  <div class="max-w-5xl mx-auto text-center space-y-6">
    <div class="flex items-center justify-center gap-3">
      <span class="px-3 py-1 rounded-full bg-[oklch(65%_0.18_250)]/10 text-[oklch(65%_0.18_250)] text-sm font-medium border border-[oklch(65%_0.18_250)]/20">
        {venue}
      </span>
      <a href={`https://arxiv.org/abs/${arxivId}`} target="_blank" rel="noopener"
         class="px-3 py-1 rounded-full bg-[oklch(60%_0.15_30)]/10 text-[oklch(70%_0.15_30)] text-sm font-medium border border-[oklch(60%_0.15_30)]/20 hover:bg-[oklch(60%_0.15_30)]/20 transition-colors">
        arXiv:{arxivId}
      </a>
    </div>

    <h1 class="text-4xl md:text-6xl font-bold tracking-tight leading-tight">
      {title}
    </h1>
    <p class="text-xl md:text-2xl text-[oklch(75%_0_0)] font-light">
      {subtitle}
    </p>

    <div class="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-lg">
      {authors.map((author, i) => (
        <span class="flex items-center gap-1">
          {author.url ? (
            <a href={author.url} class="hover:text-[oklch(65%_0.18_250)] transition-colors">{author.name}</a>
          ) : (
            <span>{author.name}</span>
          )}
          {author.isCorresponding && <span class="text-[oklch(65%_0.18_250)]">*</span>}
          {i < authors.length - 1 && <span class="text-[oklch(50%_0_0)]">,</span>}
        </span>
      ))}
    </div>

    <p class="text-[oklch(70%_0_0)]">{institution}</p>

    <div class="flex items-center justify-center gap-4 pt-4">
      <a href={`https://arxiv.org/pdf/${arxivId}.pdf`} target="_blank" rel="noopener"
         class="px-6 py-2.5 rounded-lg bg-[oklch(65%_0.18_250)] text-white font-medium hover:bg-[oklch(60%_0.18_250)] transition-colors">
        Paper
      </a>
      <a href={`https://arxiv.org/abs/${arxivId}`} target="_blank" rel="noopener"
         class="px-6 py-2.5 rounded-lg bg-[oklch(25%_0.02_260)] text-[oklch(95%_0_0)] font-medium border border-[oklch(35%_0.02_260)] hover:bg-[oklch(30%_0.02_260)] transition-colors">
        arXiv
      </a>
      <button disabled
         class="px-6 py-2.5 rounded-lg bg-[oklch(20%_0.02_260)] text-[oklch(60%_0_0)] font-medium border border-[oklch(25%_0.02_260)] cursor-not-allowed">
        Code (Coming Soon)
      </button>
    </div>
  </div>

  <div class="max-w-5xl mx-auto mt-12 w-full">
    <img src={teaserImage} alt="OSA Teaser" class="w-full rounded-xl shadow-2xl border border-[oklch(25%_0.02_260)]" />
  </div>
</section>
```

### 4.3 AbstractSection.astro

```astro
---
interface Props {
  abstractEn: string;
  abstractZh: string;
  locale: string;
}

const { abstractEn, abstractZh, locale } = Astro.props;
---

<section class="py-20 px-4 bg-gradient-to-b from-[oklch(18%_0.01_260)] to-[oklch(15%_0.02_260)]">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl font-bold mb-8 text-center">{locale === 'zh' ? '摘要' : 'Abstract'}</h2>
    <div class="space-y-6">
      <p class="text-lg leading-relaxed text-[oklch(85%_0_0)] font-serif">
        {locale === 'zh' ? abstractZh : abstractEn}
      </p>
      {locale === 'en' && abstractZh && (
        <div class="pt-6 border-t border-[oklch(25%_0.02_260)]">
          <p class="text-base leading-relaxed text-[oklch(65%_0_0)] font-serif">
            {abstractZh}
          </p>
        </div>
      )}
    </div>
  </div>
</section>
```

### 4.4 BibtexSection.astro

```astro
---
interface Props {
  bibtex: string;
}

const { bibtex } = Astro.props;
---

<section class="py-20 px-4">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl font-bold mb-8 text-center">Citation</h2>
    <div class="relative group">
      <pre class="bg-[oklch(12%_0.01_260)] border border-[oklch(22%_0.01_260)] rounded-xl p-6 overflow-x-auto"><code class="text-sm font-mono text-[oklch(80%_0_0)]">{bibtex}</code></pre>
      <button
        onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000);"
        class="absolute top-4 right-4 px-3 py-1.5 rounded-md bg-[oklch(25%_0.02_260)] text-xs font-medium text-[oklch(80%_0_0)] border border-[oklch(35%_0.02_260)] opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[oklch(30%_0.02_260)]"
      >
        Copy
      </button>
    </div>
  </div>
</section>
```

### 4.5 src/pages/osa/index.astro (English)

```astro
---
import ProjectLayout from '../../layouts/ProjectLayout.astro';
import HeroSection from '../../components/osa/HeroSection.astro';
import AbstractSection from '../../components/osa/AbstractSection.astro';
import MethodSection from '../../components/osa/MethodSection.astro';
import ResultsSection from '../../components/osa/ResultsSection.astro';
import BibtexSection from '../../components/osa/BibtexSection.astro';
import FooterSection from '../../components/osa/FooterSection.astro';

const locale = 'en';
const content = await import(`../../content/osa/${locale}.json`);
---

<ProjectLayout
  title={`${content.title} | CVPR 2026`}
  description={content.abstract}
  locale={locale}
>
  <HeroSection
    title={content.title}
    subtitle={content.subtitle}
    venue={content.venue}
    arxivId={content.arxivId}
    authors={content.authors}
    institution={content.institution}
    teaserImage={content.teaserImage}
  />
  <AbstractSection
    abstractEn={content.abstract}
    abstractZh={content.abstractZh}
    locale={locale}
  />
  <MethodSection
    sections={content.methodSections}
    figure={content.methodFigure}
    locale={locale}
  />
  <ResultsSection
    tables={content.resultTables}
    figures={content.resultFigures}
    locale={locale}
  />
  <BibtexSection bibtex={content.bibtex} />
  <FooterSection content={content.footer} />
</ProjectLayout>
```

### 4.6 src/content/osa/en.json

```json
{
  "title": "OSA: Orthogonalized State Update for Efficient Neural Network Training",
  "subtitle": "A novel optimization method that decouples moment estimates via orthogonal projection",
  "venue": "CVPR 2026",
  "arxivId": "2603.26188",
  "authors": [
    {"name": "Rui Wang", "url": "https://wangrui2025.github.io"},
    {"name": "Huisi Wu", "isCorresponding": true},
    {"name": "Jing Qin"}
  ],
  "institution": "Shenzhen University",
  "teaserImage": "/osa/teaser.jpg",
  "abstract": "We propose OSA, a novel optimization method that orthogonalizes state updates in adaptive optimizers. By decoupling the first and second moment estimates through orthogonal projection, OSA reduces gradient variance while maintaining computational efficiency. Our method achieves faster convergence and improved generalization across vision and language tasks.",
  "abstractZh": "我们提出 OSA，一种通过正交化状态更新来改进自适应优化器的新方法。通过对一阶和二阶矩估计进行正交投影解耦，OSA 在保持计算效率的同时降低了梯度方差。",
  "methodSections": [...],
  "methodFigure": "/osa/method.png",
  "resultTables": [...],
  "resultFigures": [...],
  "bibtex": "@inproceedings{wang2026osa,\\n  title={OSA: Orthogonalized State Update for Efficient Neural Network Training},\\n  author={Wang, Rui and Wu, Huisi and Qin, Jing},\\n  booktitle={CVPR},\\n  year={2026}\\n}",
  "footer": {
    "copyright": "2026 Rui Wang. All rights reserved.",
    "homepageLink": "https://wangrui2025.github.io"
  }
}
```

---

## 5. Global Styles Update (`src/styles/global.css`)

```css
@import "tailwindcss";

@theme {
  --color-osa-bg: oklch(15% 0.02 260);
  --color-osa-surface: oklch(20% 0.02 260);
  --color-osa-surface-raised: oklch(25% 0.02 260);
  --color-osa-border: oklch(30% 0.02 260);
  --color-osa-text: oklch(95% 0 0);
  --color-osa-text-muted: oklch(70% 0 0);
  --color-osa-accent: oklch(65% 0.18 250);
  --color-osa-accent-hover: oklch(60% 0.18 250);
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-serif: 'Noto Serif SC', 'Source Serif 4', Georgia, serif;
}

html {
  scroll-behavior: smooth;
}

body {
  background-color: var(--color-osa-bg);
  color: var(--color-osa-text);
}

/* KaTeX overrides for dark theme */
.katex { color: var(--color-osa-text); }
```

---

## 6. Build Verification Steps

### 6.1 Pre-build Checklist

```bash
cd /Users/myk/Repo/mykcs/.claude/worktrees/agent-ae640095eafdad0e0/mykcs.github.io/astro

# 1. Verify file structure
ls -la src/pages/osa/
ls -la src/components/osa/
ls -la src/content/osa/
ls -la public/osa/

# 2. Validate JSON content
node -e "JSON.parse(require('fs').readFileSync('src/content/osa/en.json'))"
node -e "JSON.parse(require('fs').readFileSync('src/content/osa/zh.json'))"

# 3. Check Astro config syntax
npx astro check
```

### 6.2 Build & Verify

```bash
# 4. Install dependencies (if needed)
npm install

# 5. Build the site
npm run build

# 6. Verify output structure
ls -la dist/osa/
ls -la dist/osa/zh/

# 7. Check for 404s or missing assets
grep -r "404" dist/ || echo "No 404 references found"

# 8. Preview locally (optional)
npm run preview
```

### 6.3 Post-build Validation

| Check | Command | Expected Result |
|-------|---------|-----------------|
| HTML exists | `test -f dist/osa/index.html` | Pass |
| ZH HTML exists | `test -f dist/osa/zh/index.html` | Pass |
| Assets copied | `test -f dist/osa/teaser.jpg` | Pass |
| No broken links | `grep -r 'href="#"' dist/osa/` | Empty |
| CSS loaded | `grep 'global.css' dist/osa/index.html` | Match found |

---

## 7. Quality Checklist

- [ ] Dark theme by default (oklch color space)
- [ ] Responsive design (mobile-first Tailwind)
- [ ] Bilingual support (EN/ZH with language switch)
- [ ] KaTeX math rendering
- [ ] Copy-to-clipboard for BibTeX
- [ ] Semantic HTML (section, article, nav)
- [ ] Open Graph meta tags
- [ ] Alt text for all images
- [ ] Smooth scroll behavior
- [ ] Hover/focus states for accessibility
- [ ] No console errors
- [ ] Lighthouse score > 90 (Performance, Accessibility, Best Practices, SEO)

---

## 8. Risk Statement

- **No existing `/gdkvm/` reference**: The task references matching `/gdkvm/` quality, but no such page exists in the current worktree. This plan defines a standalone high-quality academic project page standard.
- **Image assets**: Teaser and method figures must be provided separately; placeholders should be used during development.
- **KaTeX CDN dependency**: If offline builds are required, switch to local KaTeX npm package.
- **Tailwind v4 syntax**: Uses `@theme` and CSS-first configuration; verify compatibility with `@tailwindcss/vite` 4.2.2.
