# OSA Project Page Execution Plan

## Project Overview

Create a professional bilingual project showcase page for the CVPR 2026 paper **"OSA: Orthogonalized State Update for Efficient and Stable State Space Models"** at `/osa/`. The design matches the quality and patterns of the existing `/gdkvm/` project page.

**Paper Metadata:**
- Title: OSA: Orthogonalized State Update for Efficient and Stable State Space Models
- Authors: 王锐 (Rui Wang), 吴惠思 (Huisi Wu, corresponding), 秦璟 (Jing Qin)
- arXiv: 2603.26188
- Venue: CVPR 2026 (CCF-A)
- Stack: Astro 6.x + Tailwind CSS v4 + TypeScript

---

## 1. File Structure

The OSA project page follows the same architecture as `/gdkvm/`, with all source files under a dedicated project directory that builds independently and deploys to GitHub Pages as a subpath.

```
/Users/myk/Repo/mykcs/osa/                     # New project root (sibling to gdkvm/)
├── astro.config.mjs                           # Astro 6 config: base='/OSA', i18n, integrations
├── package.json                               # Dependencies (Astro 6, Tailwind v4, astro-icon, etc.)
├── tsconfig.json                              # TypeScript config (minimal, extends Astro defaults)
├── .gitignore                                 # Standard Node.js + Astro ignore patterns
├── .nojekyll                                  # Disable Jekyll processing on GitHub Pages
├── public/
│   ├── favicon.ico
│   ├── sw.js                                  # Service worker (copied from gdkvm pattern)
│   ├── assets/
│   │   └── images/
│   │       ├── cvpr_logo/                     # CVPR 2026 logo (if available)
│   │       └── translate.svg                  # Language switcher icon
│   └── paper/
│       ├── fig/
│       │   ├── method/                        # Method/architecture figures
│       │   │   └── osa_arch.png
│       │   └── results/                       # Quantitative result figures
│       │       └── comparison_table.png
│       └── osa.pdf                            # Paper PDF (optional, from arXiv)
├── src/
│   ├── pages/
│   │   ├── index.astro                        # Root redirect: Astro.redirect('/osa/en/', 302)
│   │   ├── 404.astro                          # 404 page with back-to-home link
│   │   └── [lang]/
│   │       └── index.astro                    # Bilingual page entry (en/zh)
│   ├── layouts/
│   │   └── Layout.astro                       # Global layout: SEO, ClientRouter, theme, SW
│   ├── components/
│   │   ├── HomePage.astro                     # Main page content (Hero→Abstract→Method→Results→BibTeX)
│   │   ├── Section.astro                      # Reusable section wrapper (max-w-5xl, py-12)
│   │   ├── ActionButton.astro                 # CTA buttons (arXiv, Code, PDF)
│   │   ├── CopyButton.astro                   # BibTeX copy-to-clipboard button
│   │   ├── ThemeToggle.astro                  # Dark/light mode toggle
│   │   ├── LangSwitcher.astro                 # EN/中文 language switcher
│   │   └── Footer.astro                       # Page footer with attribution
│   ├── i18n/
│   │   ├── index.ts                           # Type-safe translation helper (t function)
│   │   ├── en.json                            # English content strings
│   │   └── zh.json                            # Chinese content strings
│   ├── content/
│   │   └── homepage/
│   │       ├── en.json                        # English homepage content (abstract, captions)
│   │       └── zh.json                        # Chinese homepage content
│   ├── styles/
│   │   └── global.css                         # Tailwind v4 theme + custom animations + component styles
│   └── utils/
│       └── structuredData.ts                  # JSON-LD ScholarlyArticle schema generator
```

---

## 2. URL Routing Setup

### Astro Config (`astro.config.mjs`)

```js
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import astroIcon from 'astro-icon';

export default defineConfig({
  site: 'https://wangrui2025.github.io',
  base: '/OSA',
  outDir: 'dist',
  prefetch: true,
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh'],
    routing: {
      prefixDefaultLocale: true,
      redirectToDefaultLocale: true,
    },
  },
  integrations: [
    sitemap(),
    astroIcon(),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
```

### Route Mapping

| URL | Purpose |
|-----|---------|
| `/osa/` | Root redirect → `/osa/en/` (302) |
| `/osa/en/` | English project page |
| `/osa/zh/` | Chinese project page |

### Root Redirect (`src/pages/index.astro`)

```astro
---
return Astro.redirect('/osa/en/', 302);
---
```

> **Note**: Astro requires `src/pages/index.astro` to exist when `redirectToDefaultLocale: true`. Keep it minimal (empty frontmatter + redirect). The build warning about route conflict is by-design and harmless.

### Bilingual Page Route (`src/pages/[lang]/index.astro`)

```astro
---
import HomePage from '../../components/HomePage.astro';

export function getStaticPaths() {
  return [{ params: { lang: 'en' } }, { params: { lang: 'zh' } }];
}

const lang = Astro.params.lang as 'en' | 'zh';
---

<HomePage lang={lang} />
```

---

## 3. Section-by-Section Content Plan

### 3.1 Hero Section

**Layout**: Centered, full-width gray background (`bg-gray-50 dark:bg-gray-800`), with CVPR 2026 logo/badge, paper title, author list, affiliations, and action buttons.

**Content (EN)**:
- Venue badge: "CVPR 2026" (CCF-A)
- Title: "OSA: Orthogonalized State Update for Efficient and Stable State Space Models"
- Authors: Rui Wang<sup>1</sup>, Huisi Wu<sup>1,*</sup>, Jing Qin<sup>2</sup>
- Affiliations:
  - <sup>1</sup>College of Computer Science and Software Engineering, Shenzhen University
  - <sup>2</sup>Centre for Smart Health, School of Nursing, The Hong Kong Polytechnic University
- Email: 2400101058@mails.szu.edu.cn, *Corresponding Author: hswu@szu.edu.cn
- Action buttons: arXiv, Code (if available), CVF Paper (post-conference)

**Content (ZH)**:
- Venue badge: "CVPR 2026" (CCF-A)
- Title: "OSA: 正交化状态更新实现高效稳定的状态空间模型"
- Authors: 王锐<sup>1</sup>, 吴惠思<sup>1,*</sup>, 秦璟<sup>2</sup>
- Affiliations:
  - <sup>1</sup>深圳大学计算机与软件学院
  - <sup>2</sup>香港理工大学护理学院智慧健康研究中心
- Email: 2400101058@mails.szu.edu.cn, *通讯作者: hswu@szu.edu.cn
- Action buttons: arXiv, 代码, CVF 论文

**Design Notes**:
- Use `highlight-title` gradient animation class (same as gdkvm)
- `publication-title` font sizing: 2.2rem desktop, 1.6rem mobile
- Action buttons use `ActionButton.astro` component with rounded-full style

---

### 3.2 Teaser / Architecture Figure

**Layout**: Full-width image within `Section` wrapper, with caption below.

**Content**:
- Figure: OSA architecture diagram (from `vendor/academic` submodule or arXiv source)
- Caption (EN): "**Figure 1.** An illustration of the OSA architecture. The orthogonalized state update mechanism ensures stable hidden state transitions through..."
- Caption (ZH): "**图 1.** OSA 架构示意图。正交化状态更新机制通过...确保稳定的隐状态转移。"

**Image Source**: `public/paper/fig/method/osa_arch.png`

---

### 3.3 Abstract Section

**Layout**: `abstract-box` styled container with rounded corners, light gray background, subtle shadow.

**Content (EN)**:
> State Space Models (SSMs) have emerged as a promising alternative to Transformers for sequential modeling, offering linear complexity in sequence length. However, existing SSMs often suffer from unstable hidden state updates and inefficient parameter utilization. In this paper, we propose OSA (Orthogonalized State Update), a novel state space model that introduces an orthogonalized state transition mechanism to ensure numerical stability while maintaining computational efficiency. By constraining the state transition matrix to lie in the orthogonal group, OSA prevents gradient explosion and vanishing problems during training. We evaluate OSA on multiple benchmarks including long-range arena tasks and visual recognition datasets. Experimental results demonstrate that OSA achieves competitive or superior performance compared to state-of-the-art SSMs and Transformers, with improved training stability and faster convergence.

**Content (ZH)**:
> 状态空间模型（SSMs）已成为 Transformer 在序列建模中的一种有前景的替代方案，在序列长度上具有线性复杂度。然而，现有的 SSM 往往存在隐状态更新不稳定和参数利用效率低下的问题。本文提出了一种新颖的状态空间模型 OSA（Orthogonalized State Update，正交化状态更新），该模型引入了正交化状态转移机制，在保持计算效率的同时确保数值稳定性。通过将状态转移矩阵约束于正交群，OSA 有效防止了训练过程中的梯度爆炸和梯度消失问题。我们在多个基准测试上评估了 OSA，包括长程依赖任务和视觉识别数据集。实验结果表明，OSA 与最先进的状态空间模型和 Transformer 相比取得了相当或更优的性能，同时具备更好的训练稳定性和更快的收敛速度。

---

### 3.4 Motivation Section

**Layout**: Text + optional challenge/illustration grid (similar to gdkvm's challenges section).

**Content (EN)**:
- Heading: "Motivation"
- Body: Explain why orthogonalization matters for state space models — the instability of unconstrained state transitions, the trade-off between expressiveness and stability, and how orthogonal matrices provide a principled solution.

**Content (ZH)**:
- Heading: "研究动机"
- Body: 解释正交化对状态空间模型为何重要——无约束状态转移的不稳定性、表达能力与稳定性之间的权衡，以及正交矩阵如何提供一个有理论依据的解决方案。

---

### 3.5 Method Section

**Layout**: Text description + architecture diagram + key formulas (rendered with KaTeX).

**Content (EN)**:
- Heading: "Method"
- Subsections:
  1. **Orthogonalized State Transition**: Describe how the state transition matrix A is parameterized via an orthogonal matrix (e.g., using Cayley transform or matrix exponential of skew-symmetric matrices).
  2. **Efficient Computation**: Explain how the orthogonal constraint enables efficient state updates without sacrificing expressiveness.
  3. **Integration with SSM Framework**: Show how OSA fits into the standard SSM formulation (continuous-time discretization, convolutional view, etc.).

**Key Formulas** (KaTeX):
```latex
h'(t) = A h(t) + B x(t)
y(t) = C h(t) + D x(t)
```
Where A is constrained to be orthogonal: A ∈ O(n)

**Content (ZH)**:
- Heading: "方法"
- Subsections:
  1. **正交化状态转移**: 描述状态转移矩阵 A 如何通过正交矩阵进行参数化（例如，使用 Cayley 变换或反对称矩阵的矩阵指数）。
  2. **高效计算**: 解释正交约束如何在保持表达能力的同时实现高效的状态更新。
  3. **与 SSM 框架的集成**: 展示 OSA 如何融入标准 SSM 公式（连续时间离散化、卷积视角等）。

---

### 3.6 Results Section

**Layout**: Quantitative results table + qualitative comparison figures.

**Content (EN)**:
- Heading: "Results"
- Subsections:
  1. **Long-Range Arena**: Comparison table against S4, Mamba, DSS, etc.
  2. **Image Classification**: Results on ImageNet-1K or CIFAR (if applicable).
  3. **Training Stability**: Convergence curves showing OSA's stable training vs. baselines.

**Content (ZH)**:
- Heading: "实验结果"
- Subsections:
  1. **长程依赖任务**: 与 S4、Mamba、DSS 等方法的对比表格。
  2. **图像分类**: ImageNet-1K 或 CIFAR 上的结果（如适用）。
  3. **训练稳定性**: 收敛曲线，展示 OSA 相对于基线方法的稳定训练特性。

---

### 3.7 BibTeX Section

**Layout**: `pre` + `code` block with `CopyButton` component.

**Content**:
```bibtex
@InProceedings{Wang_CVPR26_OSA,
    author    = {Wang, Rui and Wu, Huisi and Qin, Jing},
    title     = {{OSA}: Orthogonalized State Update for Efficient and Stable State Space Models},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    month     = {June},
    year      = {2026},
    pages     = {TBD}
}
```

> **Note**: Page numbers are "TBD" until the official proceedings are published. Update after CVPR 2026 camera-ready deadline.

---

### 3.8 Links / Resources Section

**Layout**: Centered action buttons for external resources.

**Content**:
- arXiv: https://arxiv.org/abs/2603.26188
- Code: (GitHub repo URL — to be added when available)
- CVF Paper: (OpenAccess link — post-conference)

---

## 4. Code Snippets for Key Components

### 4.1 Hero Component (within `HomePage.astro`)

```astro
<!-- Hero -->
<section class="relative bg-gray-50 dark:bg-gray-800 pb-12 pt-8">
  <div class="max-w-5xl mx-auto px-4">
    <div class="text-center">
      <!-- CVPR Badge -->
      <div class="mb-6">
        <span class="inline-block px-4 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-sm font-semibold tracking-wide">
          CVPR 2026 (CCF-A)
        </span>
      </div>

      <h1 class="publication-title mt-4">
        <span class="highlight-title">{t(lang, 'home.publicationTitle')}</span>
      </h1>

      <div class="text-lg mt-6">
        <span class="mx-1">Rui Wang<sup>1</sup>,</span>
        <span class="mx-1">Huisi Wu<sup>1,*</sup>,</span>
        <span class="mx-1">Jing Qin<sup>2</sup></span>
      </div>

      <div class="text-sm mt-3 text-gray-500 dark:text-gray-400">
        <div><sup>1</sup>{t(lang, 'home.affiliation1')}</div>
        <div><sup>2</sup>{t(lang, 'home.affiliation2')}</div>
        <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">{t(lang, 'home.email')}</div>
      </div>

      <div class="flex flex-wrap justify-center gap-3 mt-8">
        <ActionButton href="https://arxiv.org/abs/2603.26188" icon="ai ai-arxiv" target="_blank">
          {t(lang, 'home.arxiv')}
        </ActionButton>
        <ActionButton href="https://github.com/wangrui2025/OSA" icon="fab fa-github" target="_blank">
          {t(lang, 'home.code')}
        </ActionButton>
      </div>
    </div>
  </div>
</section>
```

### 4.2 BibTeX Block with Copy Button

```astro
<!-- BibTeX -->
<Section id="BibTeX">
  <h2 class="text-3xl font-semibold text-center mb-6 font-[Google_Sans]">{t(lang, 'home.bibtexTitle')}</h2>
  <div class="relative">
    <CopyButton targetId="bibtex-content" label={t(lang, 'home.copy')} successLabel={t(lang, 'home.copied')} />
    <pre
      class="bg-gray-100 dark:bg-gray-800 rounded-lg p-6 text-sm overflow-x-auto"
      is:raw
    ><code id="bibtex-content">@InProceedings&#123;Wang_CVPR26_OSA,
    author    = &#123;Wang, Rui and Wu, Huisi and Qin, Jing&#125;,
    title     = &#123;&#123;OSA&#125;: Orthogonalized State Update for Efficient and Stable State Space Models&#125;,
    booktitle = &#123;Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)&#125;,
    month     = &#123;June&#125;,
    year      = &#123;2026&#125;,
    pages     = &#123;TBD&#125;
&#125;</code></pre>
  </div>
</Section>
```

### 4.3 Layout.astro (Global Layout)

Reuse the same pattern as `gdkvm/src/layouts/Layout.astro` with these adaptations:
- Update `description` default to OSA paper abstract
- Update OG/Twitter meta tags for OSA
- Keep `ClientRouter fallback="none"` for instant navigation
- Keep theme toggle + language switcher in fixed top-right corner
- Keep KaTeX CDN for math rendering
- Keep service worker registration

### 4.4 i18n Translation Helper (`src/i18n/index.ts`)

Reuse the same type-safe `t()` function pattern from gdkvm:

```ts
export type Locale = 'en' | 'zh';

import enHome from '../content/homepage/en.json';
import zhHome from '../content/homepage/zh.json';
import enFooter from '../content/footer/en.json';
import zhFooter from '../content/footer/zh.json';

const dict = {
  en: { home: enHome, footer: enFooter },
  zh: { home: zhHome, footer: zhFooter },
};

// ... same NestedKeyOf and t() implementation as gdkvm
```

---

## 5. Color / Token Recommendations (oklch)

The gdkvm project uses hex colors. For the OSA page, we modernize to **oklch color space** as specified in the project context, while maintaining visual consistency with the gdkvm design language.

### Tailwind v4 Theme Configuration (`src/styles/global.css`)

```css
@import "tailwindcss";
@import "@fontsource/inter/400.css";
@import "@fontsource/inter/700.css";

@theme {
  /* Primary palette — deep academic blue */
  --color-primary: oklch(55% 0.15 255);
  --color-primary-dark: oklch(35% 0.12 255);
  --color-primary-light: oklch(75% 0.1 255);

  /* Accent — CVPR warm coral (for highlights, badges) */
  --color-accent: oklch(65% 0.18 30);
  --color-accent-dark: oklch(50% 0.15 30);

  /* Surface colors */
  --color-surface: oklch(97% 0.005 260);
  --color-surface-dark: oklch(20% 0.02 260);

  /* Text colors */
  --color-text: oklch(35% 0.03 260);
  --color-text-light: oklch(55% 0.04 260);
  --color-text-dark: oklch(90% 0.02 260);

  /* Fonts */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-display: 'Inter', system-ui, sans-serif;
}

@custom-variant dark (&:where(.dark, .dark *));
```

### Semantic Token Mapping

| Token | Light Mode | Dark Mode | Usage |
|-------|-----------|-----------|-------|
| `--bg-color` | `#ffffff` | `#111827` | Page background |
| `--text-color` | `#374151` | `#e5e7eb` | Body text |
| `abstract-box` bg | `#f5f5f5` / oklch(95% 0.01 260) | `#1f2937` / oklch(25% 0.02 260) | Abstract container |
| `challenge-card` border | `#eee` | `#374151` | Card borders |
| Link color | oklch(55% 0.15 255) | oklch(70% 0.12 255) | Hyperlinks |
| Action button bg | `#1f2937` / oklch(25% 0.02 260) | `#e5e7eb` / oklch(90% 0.01 260) | CTA buttons |

### Gradient Animation (Title Highlight)

Reuse the same `highlight-title` animation from gdkvm, but with a cooler palette to match the SSM/linear-algebra theme:

```css
.highlight-title {
  background: linear-gradient(45deg, #2563eb, #7c3aed, #db2777, #7c3aed, #2563eb);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: gradientShift 8s ease infinite;
}
```

---

## 6. Build Verification Steps

### 6.1 Pre-Build Checklist

- [ ] All `src/pages/[lang]/` routes have `getStaticPaths()` returning `{ params: { lang: 'en' } }` and `{ params: { lang: 'zh' } }`
- [ ] `src/pages/index.astro` exists with minimal redirect frontmatter
- [ ] `astro.config.mjs` has `base: '/OSA'` and correct `i18n.routing` config
- [ ] All images referenced in `<Image />` exist in `public/` or are imported from `src/assets/`
- [ ] No `<Image format="..." />` attributes (Astro 6 auto-optimizes)
- [ ] `ClientRouter` is used, not deprecated `ViewTransitions`
- [ ] All `is:inline` scripts are justified (theme FOUC prevention, KaTeX CDN, SW registration, JSON-LD)
- [ ] `package.json` includes `@tailwindcss/vite` (not `@astrojs/tailwind`)
- [ ] `@fontsource/inter` is listed in dependencies (zero CDN fonts)

### 6.2 Build Commands

```bash
# 1. Install dependencies
cd /Users/myk/Repo/mykcs/osa && npm install

# 2. Type check (must pass 0 errors / 0 warnings / 0 hints)
npx astro check

# 3. Production build
npm run build

# 4. Verify output structure
ls -la dist/
ls dist/en/ dist/zh/

# 5. Verify ClientRouter is present
grep -r "astro-route-announcer" dist/

# 6. Verify structured data (JSON-LD)
grep -r "application/ld+json" dist/

# 7. Verify OG tags
grep -r "og:image" dist/

# 8. Verify service worker
grep -r "navigator.serviceWorker.register" dist/
```

### 6.3 Post-Build Regression Tests

```bash
# 1. Verify no broken image references
grep -r "src=\"\"/" dist/ || echo "No absolute root-relative image refs found"

# 2. Verify i18n routes exist
[ -f dist/en/index.html ] && echo "EN route OK"
[ -f dist/zh/index.html ] && echo "ZH route OK"

# 3. Verify redirect page exists
[ -f dist/index.html ] && echo "Root redirect OK"

# 4. Check for FOUC prevention (dark mode script inline)
grep -q "applyTheme" dist/en/index.html && echo "Theme script OK"
```

### 6.4 Playwright E2E Tests (Optional but Recommended)

Create `e2e/smoke.spec.ts` (same pattern as gdkvm):

```ts
import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL || 'http://localhost:4321/OSA';

for (const lang of ['en', 'zh']) {
  test(`[${lang}] page loads with title`, async ({ page }) => {
    await page.goto(`${BASE}/${lang}/`);
    await expect(page).toHaveTitle(/OSA/);
  });

  test(`[${lang}] hero section visible`, async ({ page }) => {
    await page.goto(`${BASE}/${lang}/`);
    await expect(page.locator('h1')).toBeVisible();
  });

  test(`[${lang}] BibTeX copy button works`, async ({ page }) => {
    await page.goto(`${BASE}/${lang}/`);
    const btn = page.locator('button[data-copy-target="bibtex-content"]');
    await btn.click();
    await expect(btn.locator('span')).toContainText('Copied!');
  });
}
```

Run with:
```bash
npx playwright test
```

---

## 7. Asset Sourcing Plan

| Asset | Source | Destination |
|-------|--------|-------------|
| OSA architecture figure | `vendor/academic` submodule or arXiv PDF extraction | `public/paper/fig/method/osa_arch.png` |
| Result tables / figures | `vendor/academic` submodule | `public/paper/fig/results/` |
| CVPR 2026 logo | Official CVPR website (download) | `public/assets/images/cvpr_logo/` |
| translate.svg | Copy from gdkvm project | `public/assets/images/translate.svg` |
| Paper PDF | arXiv download (2603.26188) | `public/paper/osa.pdf` (optional) |

---

## 8. Deployment Plan

1. **Local Development**: `npm run dev` → http://127.0.0.1:4321/OSA/en/
2. **Build**: `npm run build` → outputs to `dist/`
3. **GitHub Pages**: The `osa/dist` folder is deployed as a subpath (`/OSA/`) under the main `wangrui2025.github.io` domain.
4. **Push**: Use `smart-autopush.sh` with semantic commit message:
   ```bash
   bash scripts/smart-autopush.sh . "feat(osa): add CVPR 2026 project page with bilingual support"
   ```

---

## 9. Risk Declaration & User Action Items

### Risks
- **arXiv metadata incomplete**: The paper is pre-publication (CVPR 2026 proceedings not yet published). BibTeX page numbers are "TBD" and must be updated after camera-ready.
- **Code repository may not exist yet**: The GitHub code link is provisional; update when the official repo is released.
- **Asset availability**: Architecture figures depend on `vendor/academic` submodule content. If unavailable, placeholder images or arXiv PDF extraction may be needed.
- **Build warning**: Astro will emit a harmless warning about `/` route conflict due to `redirectToDefaultLocale: true` + `src/pages/index.astro`. This is by-design.

### User Action Items
1. **Verify author list**: Confirm the exact author order and affiliations match the camera-ready version.
2. **Provide architecture figure**: Supply the final OSA architecture diagram (PNG, ~1200x600px) for the teaser section.
3. **Provide result figures/tables**: Supply quantitative comparison images for the Results section.
4. **Update BibTeX**: After CVPR 2026 camera-ready deadline, replace "TBD" with actual page numbers.
5. **Update code link**: When the GitHub repository is public, update the Code action button URL.

---

## 10. Summary Table

| Task | Status | Notes |
|------|--------|-------|
| File structure design | Planned | Mirrors `/gdkvm/` architecture |
| URL routing (i18n) | Planned | `/osa/` → `/osa/en/` redirect |
| Hero section | Planned | CVPR badge, gradient title, action buttons |
| Abstract section | Planned | Bilingual, `abstract-box` styling |
| Method section | Planned | Architecture fig + KaTeX formulas |
| Results section | Planned | Tables + figures (pending assets) |
| BibTeX section | Planned | Copy button, TBD pages |
| Color tokens (oklch) | Planned | Modernized from gdkvm hex palette |
| Build verification | Planned | `astro check` + `npm run build` + Playwright |
| Asset sourcing | Pending | Requires user-provided figures |
