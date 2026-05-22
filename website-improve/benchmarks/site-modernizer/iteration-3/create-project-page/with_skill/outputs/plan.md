# OSA Project Page — 执行计划

> **目标**：为 CVPR 2026 OSA 论文创建项目展示页，路径 `/osa/`，对标 GDKVM 质量。
> **技术栈**：Astro 6 + Tailwind v4
> **语言**：中英文双语
> **区块**：Hero、Abstract、Method、Results、BibTeX

---

## 1. 项目现状分析

### 1.1 现有架构

| 维度 | 现状 |
|------|------|
| 框架 | Astro 6.1.8 (`output: 'static'`) |
| CSS | Tailwind v4 (`@tailwindcss/vite`) |
| i18n | `prefixDefaultLocale: false`，默认中文 |
| 路由 | `/[lang]/` 动态路由，`/` 重定向到 `/zh/` |
| 内容 | Content Collections (`papers`, `homepage`, `scholar`, `education`, `honors`) |
| 字体 | `@fontsource/inter` + `@fontsource/plus-jakarta-sans` |
| 主题 | Light/Dark class 切换，CSS 变量在 `@theme` 中定义 |
| 布局 | `BaseLayout.astro` → `HomepageLayout.astro` / `CVLayout.astro` |

### 1.2 关键文件映射

```
astro/
├── astro.config.mjs          # i18n 配置、redirects
├── src/
│   ├── content.config.ts      # Content Collections schema
│   ├── content/
│   │   └── papers/osa.json    # OSA 论文元数据（已存在）
│   ├── layouts/
│   │   ├── BaseLayout.astro   # 根布局（SEO、主题、导航）
│   │   └── HomepageLayout.astro
│   ├── components/
│   │   ├── Masthead.astro     # 顶部导航
│   │   ├── Footer.astro       # 页脚
│   │   ├── PaperCard.astro    # 论文卡片（可复用）
│   │   └── ThemeToggle.astro  # 主题切换
│   ├── pages/
│   │   ├── index.astro        # 根重定向到 /zh/
│   │   └── [lang]/            # 动态语言路由
│   │       ├── index.astro    # 首页
│   │       ├── cv.astro       # CV 页
│   │       └── slides.astro   # Slides 页
│   ├── utils/
│   │   ├── constants.ts       # 站点常量
│   │   ├── i18n.ts            # createTranslator 辅助函数
│   │   └── structuredData.ts  # Schema.org 结构化数据
│   └── styles/global.css      # Tailwind v4 @theme + 全局样式
└── public/
    ├── academic/images/papers/cvpr2026-osa/   # OSA 图片资源（已存在）
    └── OSA/index.html                          # 旧重定向页（需清理）
```

### 1.3 OSA 现有资产

- **论文数据**：`src/content/papers/osa.json`（标题、作者、venue、arxiv、project URL 等）
- **图片资源**：`public/academic/images/papers/cvpr2026-osa/` 下已有
  - `fig_osu_page-0001.jpg` — 论文框架图
  - `fig/Met/fig_overview.png` — 方法 overview
  - `fig/osu/fig_osu.png` — OSU 模块图
  - `fig/apfe/fig_apfe.png` — APFE 模块图
  - `fig/challenge/image.png` — 挑战示意图
  - `fig/landscape/fig_landscape.png` — 领域 landscape
  - `fig/Exp/image.png` — 实验结果
  - `fig/abl/fig_abl.png` — 消融实验
  - `tab/tab_cap.png` — 能力对比表
  - `tab/tab_abl.png` — 消融实验表
- **旧重定向**：`public/OSA/index.html` 重定向到 `/osa/`（大小写问题，需清理）

---

## 2. 执行计划

### Phase 1: 内容准备（数据层）

#### Step 1.1 — 创建 OSA 项目页内容集合

创建 `src/content/osa/` 目录，存放双语项目页内容。

```bash
mkdir -p /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro/src/content/osa
```

创建 `src/content/osa/en.json`：

```json
{
  "title": "OSA: Orthogonalized State Update and Anatomical Prior-aware Feature Enhancement",
  "venue": "CVPR 2026",
  "venue_badge": "Highlight",
  "authors": [
    { "name": "Rui Wang", "is_self": true, "affiliation": "Shenzhen University" },
    { "name": "Huisi Wu", "is_self": false, "affiliation": "Shenzhen University", "is_corresponding": true },
    { "name": "Jing Qin", "is_self": false, "affiliation": "The Hong Kong Polytechnic University" }
  ],
  "affiliations": [
    "College of Computer Science and Software Engineering, Shenzhen University",
    "Department of Computing, The Hong Kong Polytechnic University"
  ],
  "links": {
    "arxiv": "https://arxiv.org/pdf/2603.26188",
    "project": "https://wangrui2025.github.io/osa/",
    "code": null,
    "video": null,
    "poster": null
  },
  "hero": {
    "teaser": "/academic/images/papers/cvpr2026-osa/fig_osu_page-0001.jpg",
    "teaser_alt": "OSA framework overview"
  },
  "abstract": "Echocardiography video segmentation is critical for cardiac function assessment...",
  "motivation": {
    "heading": "Motivation",
    "content": "Existing methods struggle with temporal consistency and anatomical plausibility...",
    "image": "/academic/images/papers/cvpr2026-osa/fig/challenge/image.png"
  },
  "method": {
    "heading": "Method",
    "overview": "We propose OSA, a novel framework that...",
    "sections": [
      {
        "title": "Orthogonalized State Update (OSU)",
        "content": "The OSU module ensures state transitions remain orthogonal...",
        "image": "/academic/images/papers/cvpr2026-osa/fig/osu/fig_osu.png"
      },
      {
        "title": "Anatomical Prior-aware Feature Enhancement (APFE)",
        "content": "APFE injects anatomical constraints into feature learning...",
        "image": "/academic/images/papers/cvpr2026-osa/fig/apfe/fig_apfe.png"
      }
    ]
  },
  "results": {
    "heading": "Results",
    "overview": "OSA achieves state-of-the-art performance on...",
    "images": [
      { "src": "/academic/images/papers/cvpr2026-osa/fig/Exp/image.png", "caption": "Quantitative comparison with SOTA methods" },
      { "src": "/academic/images/papers/cvpr2026-osa/tab/tab_cap.png", "caption": "Capability comparison table" },
      { "src": "/academic/images/papers/cvpr2026-osa/fig/abl/fig_abl.png", "caption": "Ablation study results" }
    ]
  },
  "bibtex": "@inproceedings{wang2026osa,\\n  title={OSA: Orthogonalized State Update and Anatomical Prior-aware Feature Enhancement for Echocardiography Video Segmentation},\\n  author={Wang, Rui and Wu, Huisi and Qin, Jing},\\n  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},\\n  year={2026}\\n}"
}
```

创建 `src/content/osa/zh.json`（中文镜像，内容翻译）。

#### Step 1.2 — 注册 Content Collection

在 `src/content.config.ts` 中新增 `osa` collection：

```typescript
const osa = defineCollection({
  loader: glob({ base: './src/content/osa', pattern: '**/*.json' }),
  schema: z.object({
    title: z.string(),
    venue: z.string(),
    venue_badge: z.string().optional(),
    authors: z.array(z.object({
      name: z.string(),
      is_self: z.boolean().default(false),
      is_corresponding: z.boolean().default(false),
      affiliation: z.string(),
    })),
    affiliations: z.array(z.string()),
    links: z.object({
      arxiv: z.string().url().optional(),
      project: z.string().url().optional(),
      code: z.string().url().optional(),
      video: z.string().url().optional(),
      poster: z.string().url().optional(),
    }),
    hero: z.object({
      teaser: z.string(),
      teaser_alt: z.string(),
    }),
    abstract: z.string(),
    motivation: z.object({
      heading: z.string(),
      content: z.string(),
      image: z.string().optional(),
    }),
    method: z.object({
      heading: z.string(),
      overview: z.string(),
      sections: z.array(z.object({
        title: z.string(),
        content: z.string(),
        image: z.string().optional(),
      })),
    }),
    results: z.object({
      heading: z.string(),
      overview: z.string(),
      images: z.array(z.object({
        src: z.string(),
        caption: z.string(),
      })),
    }),
    bibtex: z.string(),
  }),
});

export const collections = { papers, scholar, homepage, education, honors, osa };
```

---

### Phase 2: 页面开发（视图层）

#### Step 2.1 — 创建 OSA 专属布局

创建 `src/layouts/ProjectLayout.astro`：

- 继承 `BaseLayout.astro`
- 移除侧边栏（项目页不需要 AuthorProfile）
- 添加项目页专用 SEO（ScholarlyArticle Schema.org）
- 保留主题切换和导航

```astro
---
import BaseLayout from './BaseLayout.astro';

interface Props {
  title: string;
  description: string;
  lang: 'en' | 'zh';
  ogImage?: string;
}

const { title, description, lang, ogImage } = Astro.props;
---

<BaseLayout
  title={title}
  description={description}
  lang={lang}
  ogTitle={title}
  ogDescription={description}
  ogImage={ogImage}
  showNav={true}
>
  <div class="max-w-[960px] mx-auto px-4 py-8" slot="hero">
    <slot />
  </div>
</BaseLayout>
```

#### Step 2.2 — 创建 OSA 页面组件

创建 `src/pages/osa.astro`（根路径重定向）：

```astro
---
return Astro.redirect('/osa/zh/', 302);
---
```

创建 `src/pages/osa/[lang].astro`（双语页面）：

```astro
---
import ProjectLayout from '../../layouts/ProjectLayout.astro';
import { getEntry } from 'astro:content';
import { Image } from 'astro:assets';

export function getStaticPaths() {
  return [{ params: { lang: 'en' } }, { params: { lang: 'zh' } }];
}

const lang = Astro.params.lang as 'en' | 'zh';
const data = await getEntry('osa', lang);
if (!data) throw new Error(`OSA content for ${lang} not found`);
const p = data.data;

// Import teaser image
import teaserImage from '../../../vendor/academic/images/papers/cvpr2026-osa/fig_osu_page-0001.jpg';
---

<ProjectLayout
  title={`${p.title} | ${p.venue}`}
  description={p.abstract.slice(0, 160)}
  lang={lang}
  ogImage={p.hero.teaser}
>
  <!-- Hero Section -->
  <section class="text-center mb-12">
    <div class="inline-block px-3 py-1 mb-4 text-sm font-medium rounded-full bg-paper-accent/10 text-paper-accent dark:bg-paper-accent-dark/10 dark:text-paper-accent-dark">
      {p.venue} {p.venue_badge && <span class="ml-1">· {p.venue_badge}</span>}
    </div>
    <h1 class="font-serif text-4xl md:text-5xl font-semibold leading-tight mb-6 text-heading-primary dark:text-heading-dark">
      {p.title}
    </h1>
    <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 mb-4 text-sm text-text-secondary dark:text-text-secondary-dark">
      {p.authors.map((author) => (
        <span class={author.is_self ? 'font-semibold text-text-primary dark:text-text-dark' : ''}>
          {author.name}{author.is_corresponding ? '*' : ''}
          <sup class="text-xs text-text-secondary dark:text-text-secondary-dark">{p.affiliations.indexOf(author.affiliation) + 1}</sup>
        </span>
      ))}
    </div>
    <div class="text-xs text-text-secondary dark:text-text-secondary-dark mb-6 space-y-1">
      {p.affiliations.map((aff, i) => (
        <div><sup>{i + 1}</sup>{aff}</div>
      ))}
    </div>
    <div class="flex justify-center gap-4 mb-8">
      {p.links.arxiv && <a href={p.links.arxiv} target="_blank" class="px-4 py-2 rounded-lg bg-paper-accent text-white text-sm font-medium hover:opacity-90 transition-opacity">arXiv</a>}
      {p.links.code && <a href={p.links.code} target="_blank" class="px-4 py-2 rounded-lg border border-paper-accent text-paper-accent text-sm font-medium hover:bg-paper-accent/10 transition-colors">Code</a>}
    </div>
    <Image
      src={teaserImage}
      alt={p.hero.teaser_alt}
      width={900}
      height={450}
      class="w-full max-w-[800px] mx-auto rounded-xl shadow-lg"
      densities={[1, 2]}
    />
  </section>

  <!-- Abstract Section -->
  <section class="mb-12" id="abstract">
    <h2 class="section-heading font-medium text-[28px] mb-4">Abstract</h2>
    <p class="text-base leading-relaxed text-text-primary dark:text-text-dark">{p.abstract}</p>
  </section>

  <!-- Motivation Section -->
  <section class="mb-12" id="motivation">
    <h2 class="section-heading font-medium text-[28px] mb-4">{p.motivation.heading}</h2>
    <p class="text-base leading-relaxed text-text-primary dark:text-text-dark mb-4">{p.motivation.content}</p>
    {p.motivation.image && (
      <img src={p.motivation.image} alt="Motivation" class="w-full rounded-lg shadow-md" loading="lazy" />
    )}
  </section>

  <!-- Method Section -->
  <section class="mb-12" id="method">
    <h2 class="section-heading font-medium text-[28px] mb-4">{p.method.heading}</h2>
    <p class="text-base leading-relaxed text-text-primary dark:text-text-dark mb-6">{p.method.overview}</p>
    {p.method.sections.map((section) => (
      <div class="mb-8">
        <h3 class="font-semibold text-xl mb-3 text-heading-primary dark:text-heading-dark">{section.title}</h3>
        <p class="text-base leading-relaxed text-text-primary dark:text-text-dark mb-4">{section.content}</p>
        {section.image && (
          <img src={section.image} alt={section.title} class="w-full rounded-lg shadow-md" loading="lazy" />
        )}
      </div>
    ))}
  </section>

  <!-- Results Section -->
  <section class="mb-12" id="results">
    <h2 class="section-heading font-medium text-[28px] mb-4">{p.results.heading}</h2>
    <p class="text-base leading-relaxed text-text-primary dark:text-text-dark mb-6">{p.results.overview}</p>
    {p.results.images.map((img) => (
      <figure class="mb-6">
        <img src={img.src} alt={img.caption} class="w-full rounded-lg shadow-md" loading="lazy" />
        <figcaption class="text-center text-sm text-text-secondary dark:text-text-secondary-dark mt-2">{img.caption}</figcaption>
      </figure>
    ))}
  </section>

  <!-- BibTeX Section -->
  <section class="mb-12" id="bibtex">
    <h2 class="section-heading font-medium text-[28px] mb-4">BibTeX</h2>
    <div class="relative">
      <pre class="bg-paper-bg dark:bg-paper-bg-dark border border-paper-border dark:border-paper-border-dark rounded-lg p-4 overflow-x-auto text-sm font-mono"><code>{p.bibtex}</code></pre>
      <button
        class="absolute top-2 right-2 px-3 py-1 text-xs rounded bg-paper-accent/10 text-paper-accent dark:bg-paper-accent-dark/10 dark:text-paper-accent-dark hover:bg-paper-accent/20 transition-colors"
        onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000);"
      >
        Copy
      </button>
    </div>
  </section>
</ProjectLayout>
```

#### Step 2.3 — 更新导航数据

在 `src/data/navigation.ts` 中，为项目页添加导航支持（如果需要）。项目页通常不需要锚点导航，但 Masthead 的 home 链接和语言切换必须正常工作。

确认 `Masthead.astro` 中的语言切换逻辑支持 `/osa/en/` ↔ `/osa/zh/` 切换。

---

### Phase 3: 配置更新

#### Step 3.1 — 更新 astro.config.mjs

添加 `/osa` 重定向：

```javascript
redirects: {
  '/cv': '/zh/cv',
  '/osa': '/osa/zh',
},
```

#### Step 3.2 — 清理旧资产

删除旧的大小写重定向文件：

```bash
rm -rf /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro/public/OSA
```

---

### Phase 4: 构建与验证

#### Step 4.1 — 类型检查

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro
npx astro check
```

#### Step 4.2 — 构建

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro
npm run build
```

#### Step 4.3 — 验证清单

| 检查项 | 命令/方法 |
|--------|-----------|
| 构建产物存在 | `ls dist/osa/zh/index.html` |
| 重定向生效 | `cat dist/osa/index.html` 包含 `location.replace('/osa/zh/')` |
| 无 TS 错误 | `npx astro check` |
| 图片路径正确 | 检查 HTML 中 `src` 指向 `/academic/images/...` |
| 语言切换正常 | 访问 `/osa/en/` 和 `/osa/zh/`，点击导航栏语言按钮 |
| 主题切换正常 | 切换 dark/light，确认所有区块颜色正确 |
| BibTeX 复制按钮 | 点击 Copy，确认剪贴板内容正确 |
| SEO 标签 | 检查 `<meta property="og:title">`、`<link rel="canonical">` |
| Schema.org | 确认页面包含 `ScholarlyArticle` structured data |
| 响应式 | 浏览器 DevTools 切换移动端 viewport，确认布局正常 |

---

### Phase 5: 提交

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io
bash scripts/smart-autopush.sh . "feat(osa): add CVPR 2026 OSA bilingual project page with Hero/Abstract/Method/Results/BibTeX sections" done
```

---

## 3. 文件变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `src/content/osa/en.json` | OSA 项目页英文内容 |
| `src/content/osa/zh.json` | OSA 项目页中文内容 |
| `src/layouts/ProjectLayout.astro` | 项目页专用布局 |
| `src/pages/osa.astro` | `/osa` 重定向到 `/osa/zh/` |
| `src/pages/osa/[lang].astro` | 双语项目页主组件 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `src/content.config.ts` | 新增 `osa` collection schema |
| `astro.config.mjs` | 添加 `/osa` → `/osa/zh` redirect |
| `src/data/navigation.ts` | 如需，添加项目页导航支持 |

### 删除文件

| 文件 | 说明 |
|------|------|
| `public/OSA/index.html` | 旧的大小写重定向页，由 Astro 路由替代 |

---

## 4. 设计规范

### 4.1 颜色（复用现有主题）

| Token | Light | Dark |
|-------|-------|------|
| Background | `#f5f4ed` | `#141413` |
| Text | `#3d3d3d` | `#c9c9c9` |
| Heading | `#141413` | `#e8e8e8` |
| Accent | `#c96442` | `#d97757` |
| Card BG | `#faf9f5` | `#30302e` |
| Border | `#f0eee6` | `#30302e` |

### 4.2 排版

| 元素 | 字体 | 大小 | 字重 |
|------|------|------|------|
| 页面标题 | Plus Jakarta Sans | 40-48px | 600 |
| Section 标题 | Plus Jakarta Sans | 28px | 500 |
| 子标题 | Plus Jakarta Sans | 20px | 600 |
| 正文 | Inter | 16px | 400 |
| 按钮/标签 | Inter | 14px | 500 |

### 4.3 间距

- Section 间距：`mb-12`（3rem）
- 内容最大宽度：`max-w-[960px]`（比首页 1200px 窄，聚焦阅读）
- 图片圆角：`rounded-lg`（8px）
- 卡片阴影：`shadow-md` / `shadow-lg`

---

## 5. 风险与应对

| 风险 | 概率 | 应对 |
|------|------|------|
| Content Collection schema 不匹配 | 低 | 严格按 `content.config.ts` 定义，build 前 `astro check` |
| 图片路径 404 | 中 | 使用 `public/` 绝对路径，build 后检查 dist 产物 |
| 语言切换 URL 错误 | 低 | 复用 `getRelativeLocaleUrl` 模式，手动验证 |
| 主题切换颜色异常 | 低 | 所有颜色使用 `dark:` 变体，DevTools 验证 |
| 旧 `public/OSA` 与 Astro 路由冲突 | 中 | 删除旧目录，确保大小写不敏感部署正常 |

---

## 6. 验收标准

- [ ] `npx astro check` 0 errors
- [ ] `npm run build` 成功
- [ ] `/osa/` 重定向到 `/osa/zh/`
- [ ] `/osa/en/` 和 `/osa/zh/` 均可访问
- [ ] Hero 区块显示标题、作者、venue badge、teaser 图
- [ ] Abstract 区块显示论文摘要
- [ ] Method 区块显示方法 overview 和子模块
- [ ] Results 区块显示实验结果图和表格
- [ ] BibTeX 区块显示可复制的引用文本
- [ ] 语言切换按钮在 `/osa/en/` 和 `/osa/zh/` 间正确跳转
- [ ] 主题切换（dark/light）在所有区块正常工作
- [ ] 移动端响应式布局正常
