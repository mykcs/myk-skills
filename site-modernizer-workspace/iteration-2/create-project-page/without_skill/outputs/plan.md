# OSA 项目展示页 — 执行计划

## 项目信息
- **论文**: OSA: Echocardiography Video Segmentation via Orthogonalized State Update and Anatomical Prior-aware Feature Enhancement
- **会议**: CVPR 2026 Highlight
- **目标路径**: `/osa/` (对应 `src/pages/osa.astro`)
- **对标基准**: GDKVM 项目页质量
- **技术栈**: Astro 6 + Tailwind v4 + i18n (en/zh)

---

## 一、前置分析

### 1.1 现有架构摸底

| 维度 | 现状 |
|------|------|
| i18n 路由 | `astro.config.mjs` 已配置 `prefixDefaultLocale: false`，默认中文，英文前缀 `/en/` |
| 语言切换 | `Masthead.astro` 通过 `getRelativeLocaleUrl(targetLang, pathWithoutLocale)` 实现 |
| 内容集合 | `content.config.ts` 定义了 `papers` / `scholar` / `homepage` / `education` / `honors` 集合 |
| 翻译工具 | `src/utils/i18n.ts` 提供 `createTranslator(lang)` |
| 样式系统 | Tailwind v4 (`@import "tailwindcss"`) + `@theme` 自定义 design tokens |
| 暗色模式 | `html.dark` class 切换，localStorage 持久化 |
| 图标 | `astro-icon` + `tabler` 图标集 |
| 图片 | `astro:assets` + `sharp` 优化服务 |
| SEO | Open Graph、Twitter Card、Schema.org、canonical URL、hreflang 全配齐 |

### 1.2 已有数据资产

`src/content/papers/osa.json` 已包含：
- 日期、会议、标签、封面图路径、arXiv 链接、项目页链接
- 中英文标题、作者列表（含 `is_self` / `is_corresponding` 标记）
- 研究领域、技术标签

`src/archive/cv/CVPR2026-OSA.md` 包含：CVPR 2026 双栏引用格式模板

### 1.3 GDKVM 对标缺失分析

当前站点 **没有** GDKVM 独立项目展示页，仅有首页 `PaperCard` 组件中的论文卡片。OSA 项目页需要从零构建一个完整的项目展示页，包含：

- Hero 区块（大标题 + 会议徽章 + 作者 + 关键链接）
- Abstract 区块（中英文双语摘要）
- Method 区块（方法框架图 + 技术亮点）
- Results 区块（定量表格 + 定性对比图）
- BibTeX 区块（一键复制引用）

---

## 二、执行计划

### Phase 1: 数据层准备

#### Step 1.1 — 创建 OSA 项目专属内容数据

**新建文件**: `src/content/project-pages/osa.json`

```json
{
  "paper_id": "osa",
  "venue": "CVPR 2026",
  "venue_full": "CVPR 2026 Highlight",
  "tags": ["csranking", "CCF-A"],
  "arxiv": "https://arxiv.org/pdf/2603.26188",
  "project": "https://wangrui2025.github.io/osa/",
  "zh": {
    "title": "OSA: 使用正交状态更新与解剖先验感知特征增强的超声心动图视频分割",
    "abstract": "...",
    "method_title": "方法",
    "method_description": "...",
    "results_title": "实验结果",
    "bibtex_title": "引用"
  },
  "en": {
    "title": "OSA: Echocardiography Video Segmentation via Orthogonalized State Update and Anatomical Prior-aware Feature Enhancement",
    "abstract": "...",
    "method_title": "Method",
    "method_description": "...",
    "results_title": "Results",
    "bibtex_title": "BibTeX"
  }
}
```

> **注意**: 若不想扩展 content collection schema，可将项目页数据直接硬编码在 Astro 页面中，或放在 `src/data/` 下的 TS 模块中。考虑到项目页数据量不大且结构固定，推荐 **直接硬编码在页面组件中**，减少 schema 变更和 collection 注册的复杂度。

#### Step 1.2 — 确认图片资源路径

当前 `osa.json` 引用的框架图路径：
```
../../../../vendor/academic/images/papers/cvpr2026-osa/fig_osu_page-0001.jpg
```

项目页需要额外准备（如不存在需后续补充）：
- 方法框架图 (method overview)
- 定量结果表格截图 (results table)
- 定性对比图 (qualitative comparison)
- 视频 demo 封面 (optional)

**命令验证图片存在性**:
```bash
ls -la /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro/vendor/academic/images/papers/cvpr2026-osa/
```

---

### Phase 2: 页面层构建

#### Step 2.1 — 创建项目页布局组件

**新建文件**: `src/layouts/ProjectLayout.astro`

职责：
- 继承 `BaseLayout.astro` 的 SEO、暗色模式、导航等基础能力
- 提供项目页专用的 `<slot>` 结构（Hero / Content / Sidebar）
- 注入论文 Schema.org `ScholarlyArticle` structured data
- 设置 `og:image` 为论文框架图

Props 接口：
```ts
interface Props {
  title: string;
  description: string;
  lang: 'en' | 'zh';
  ogImage?: string;
  paperSchema?: object; // Schema.org ScholarlyArticle
}
```

#### Step 2.2 — 创建 OSA 项目页

**新建文件**: `src/pages/osa.astro` (中文默认)
**新建文件**: `src/pages/en/osa.astro` (英文版)

> **路由策略分析**: 当前 i18n 配置 `prefixDefaultLocale: false`，默认中文无前缀，英文加 `/en/` 前缀。项目页需要两个独立文件以支持语言切换。`Masthead.astro` 中的语言切换链接会自动处理路径映射。

页面结构（两个文件内容对称，仅语言不同）：

```astro
---
import ProjectLayout from '../layouts/ProjectLayout.astro';
import { Image } from 'astro:assets';
import { Icon } from 'astro-icon/components';
import osaFrameworkImage from '../../../vendor/academic/images/papers/cvpr2026-osa/fig_osu_page-0001.jpg';

const lang = 'zh'; // 'en' for en/osa.astro
const t = {
  zh: { /* ... */ },
  en: { /* ... */ }
}[lang];
---

<ProjectLayout title={t.title} description={t.abstract} lang={lang} ogImage={osaFrameworkImage.src}>
  <!-- Hero Section -->
  <section id="hero" class="...">
    <div class="venue-badge">CVPR 2026 Highlight</div>
    <h1>{t.title}</h1>
    <p class="authors">...</p>
    <div class="affiliation">...</div>
    <div class="action-links">
      <a href="arxiv">[Paper]</a>
      <a href="code">[Code]</a>
      <a href="#bibtex">[BibTeX]</a>
    </div>
  </section>

  <!-- Abstract Section -->
  <section id="abstract" class="...">
    <h2>{t.abstract_title}</h2>
    <p>{t.abstract}</p>
  </section>

  <!-- Method Section -->
  <section id="method" class="...">
    <h2>{t.method_title}</h2>
    <Image src={osaFrameworkImage} alt={t.framework_alt} ... />
    <p>{t.method_description}</p>
  </section>

  <!-- Results Section -->
  <section id="results" class="...">
    <h2>{t.results_title}</h2>
    <!-- 定量表格 / 定性对比 -->
  </section>

  <!-- BibTeX Section -->
  <section id="bibtex" class="...">
    <h2>{t.bibtex_title}</h2>
    <pre class="bibtex-block"><code>{t.bibtex}</code></pre>
    <button class="copy-btn" data-copy-target="bibtex-code">Copy</button>
  </section>
</ProjectLayout>
```

#### Step 2.3 — 样式细节（Tailwind v4）

Hero 区块关键样式：
- 背景: `bg-bg-primary dark:bg-bg-dark`
- 会议徽章: 圆角胶囊，背景 `bg-paper-accent`，文字白色
- 标题: `font-serif text-4xl md:text-5xl font-semibold leading-tight`
- 作者: `text-lg text-text-secondary dark:text-text-secondary-dark`
- 链接按钮组: flex gap-4，按钮带 hover underline + 图标

Abstract / Method / Results / BibTeX 区块：
- 统一使用 `section-heading` class（已定义在 `global.css` 中，带底部装饰线）
- 内容区 max-width 约束，居中
- 图片带 `rounded-lg shadow-md border border-paper-border`
- BibTeX 代码块使用 `astro-expressive-code` 或原生 `<pre>` + 暗色适配

Copy 按钮交互：
- 原生 JS (is:inline)：navigator.clipboard.writeText() + 状态反馈

---

### Phase 3: 导航与链接集成

#### Step 3.1 — 更新 PaperCard 项目页链接

**修改文件**: `src/components/PaperCard.astro`

当前 `[Project]` 链接指向外部 `https://wangrui2025.github.io/osa/`。项目页建成后，需确认：
- 若项目页部署在同域名下，`project` 字段可改为相对路径 `/osa/` 或保持绝对 URL
- 无需修改 `osa.json`，因为 `PaperCard.astro` 直接读取 `paper.data.project`

#### Step 3.2 — 验证导航栏语言切换

`Masthead.astro` 中的语言切换逻辑：
```ts
const pathWithoutLocale = currentPath.replace(/^\/en/, '') || '/';
const switchUrl = getRelativeLocaleUrl(targetLang, pathWithoutLocale);
```

当用户在 `/osa/` 时，切换英文应跳转到 `/en/osa/`。需要确保 `src/pages/en/osa.astro` 存在。

---

### Phase 4: SEO & 结构化数据

#### Step 4.1 — 注入 Schema.org ScholarlyArticle

在 `ProjectLayout.astro` 的 `<head>` 中注入：

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "OSA: ...",
  "author": [
    { "@type": "Person", "name": "Rui Wang" },
    { "@type": "Person", "name": "Huisi Wu" },
    { "@type": "Person", "name": "Jing Qin" }
  ],
  "isPartOf": {
    "@type": "PublicationEvent",
    "name": "CVPR 2026"
  },
  "sameAs": "https://arxiv.org/pdf/2603.26188"
}
```

#### Step 4.2 — Open Graph 优化

- `og:title`: 论文标题
- `og:description`: 摘要前 200 字符
- `og:image`: 论文框架图（绝对 URL）
- `og:type`: `article`

---

### Phase 5: 构建与验证

#### Step 5.1 — 本地构建

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro
npm run build
```

#### Step 5.2 — 验证清单

| 检查项 | 验证方法 |
|--------|---------|
| 页面渲染 | `npm run dev` 访问 `http://localhost:4321/osa/` |
| 英文版 | 访问 `http://localhost:4321/en/osa/` |
| 语言切换 | 点击导航栏 "English"/"中文" 双向跳转 |
| 暗色模式 | 切换主题，检查所有区块颜色适配 |
| 响应式 | 缩小 viewport，检查移动端布局 |
| SEO | 查看页面源码中 `og:*` meta 和 JSON-LD |
| 图片加载 | 检查框架图是否正常显示，无 404 |
| BibTeX 复制 | 点击 Copy 按钮，验证剪贴板内容 |
| 构建产物 | `dist/osa/index.html` 和 `dist/en/osa/index.html` 存在 |

#### Step 5.3 — Playwright 截图验证（可选，对标 GDKVM 质量）

```bash
npx playwright screenshot http://localhost:4321/osa/ osa-desktop.png --viewport-size=1280,720
npx playwright screenshot http://localhost:4321/osa/ osa-mobile.png --viewport-size=375,667
```

---

## 三、文件清单

### 新建文件

| 文件路径 | 说明 |
|---------|------|
| `src/layouts/ProjectLayout.astro` | 项目页专用布局 |
| `src/pages/osa.astro` | OSA 中文项目页 |
| `src/pages/en/osa.astro` | OSA 英文项目页 |

### 修改文件

| 文件路径 | 说明 |
|---------|------|
| `src/components/PaperCard.astro` | 可选：更新项目页链接为相对路径 |

### 复用资产

| 资产 | 来源 |
|------|------|
| 论文框架图 | `vendor/academic/images/papers/cvpr2026-osa/fig_osu_page-0001.jpg` |
| 作者信息 | `src/content/papers/osa.json` |
| 样式系统 | `src/styles/global.css` (Tailwind v4 + 自定义 tokens) |
| 布局基础 | `src/layouts/BaseLayout.astro` |
| 导航组件 | `src/components/Masthead.astro` |

---

## 四、风险与依赖

| 风险 | 缓解措施 |
|------|---------|
| 缺少方法图/结果图 | 先用现有 `fig_osu_page-0001.jpg` 占位，后续替换高清图 |
| 摘要内容未提供 | 从 arXiv PDF 提取或先用占位文本，用户确认后填充 |
| BibTeX 格式 | 复用 `src/archive/cv/CVPR2026-OSA.md` 中的引用格式 |
| 构建失败 | 严格遵循现有 Tailwind v4 语法，不使用 v3 旧语法 |
| i18n 路由冲突 | 确保 `src/pages/en/osa.astro` 与 `src/pages/osa.astro` 同步维护 |

---

## 五、验收标准

- [ ] `src/pages/osa.astro` 和 `src/pages/en/osa.astro` 文件存在且语法正确
- [ ] 页面包含 Hero、Abstract、Method、Results、BibTeX 五个区块
- [ ] 中英文双语内容完整
- [ ] 暗色模式适配无瑕疵
- [ ] 导航栏语言切换正常工作
- [ ] `npm run build` 零错误
- [ ] `dist/osa/index.html` 和 `dist/en/osa/index.html` 存在于构建产物中
- [ ] PaperCard 中的 `[Project]` 链接指向有效页面
