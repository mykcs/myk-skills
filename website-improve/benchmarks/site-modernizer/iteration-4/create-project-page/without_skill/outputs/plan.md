# OSA 项目展示页执行计划

## 目标

为 CVPR 2026 OSA 论文创建项目展示页，部署于 `/osa/`，对标 GDKVM 质量。

## 技术栈

- Astro 6 + Tailwind v4
- 中英文双语（`[lang]` 动态路由）
- 静态输出 `output: 'static'`

---

## Phase 1: 内容准备

### 1.1 创建内容数据文件

**文件**: `astro/src/content/osa/osa.json`

数据结构（ bilingual, 匹配 papers schema 风格）：

```json
{
  "date": "2026-06",
  "venue": "CVPR 2026",
  "venue_full": "CVPR 2026 Highlight",
  "arxiv": "https://arxiv.org/pdf/2603.26188",
  "project": "https://wangrui2025.github.io/osa/",
  "zh": {
    "title": "OSA: 使用正交状态更新与解剖先验感知特征增强的超声心动图视频分割",
    "authors": [...],
    "abstract": "...",
    "method": "...",
    "results": "...",
    "bibtex": "..."
  },
  "en": {
    "title": "OSA: Echocardiography Video Segmentation via Orthogonalized State Update and Anatomical Prior-aware Feature Enhancement",
    "authors": [...],
    "abstract": "...",
    "method": "...",
    "results": "...",
    "bibtex": "..."
  }
}
```

**图片清单**（已确认存在于 `public/academic/images/papers/cvpr2026-osa/`）：

| 图片 | 用途 |
|------|------|
| `fig_osu_page-0001.jpg` | Hero / 封面图 |
| `fig/osu/fig_osu.png` | Method - OSU 模块 |
| `fig/apfe/fig_apfe.png` | Method - APFE 模块 |
| `fig/Met/fig_overview.png` | Method - 整体框架 |
| `fig/abl/fig_abl.png` | Results - 消融实验 |
| `fig/Exp/image.png` | Results - 主实验 |
| `fig/challenge/image.png` | Results - 挑战场景 |
| `fig/first/fig_first.png` | Results - 首帧对比 |
| `fig/landscape/fig_landscape.png` | Results - 全景图 |
| `fig/landscape_2d/image.png` | Results - 2D 全景 |
| `fig/fail/fig_fail.png` | Results - 失败案例 |
| `tab/tab_abl.png` | Results - 消融表格 |
| `tab/tab_cap.png` | Results - 能力表格 |

### 1.2 注册 Content Collection

在 `astro/src/content.config.ts` 中新增 `osa` collection：

```typescript
const osa = defineCollection({
  loader: glob({ pattern: '**/osa.json', base: './src/content/osa' }),
  schema: z.object({
    date: z.string(),
    venue: z.string(),
    venue_full: z.string(),
    arxiv: z.string().url(),
    project: z.string().url(),
    zh: z.object({
      title: z.string(),
      authors: z.array(authorSchema),
      abstract: z.string(),
      method: z.string(),
      results: z.string(),
      bibtex: z.string(),
    }),
    en: z.object({
      title: z.string(),
      authors: z.array(authorSchema),
      abstract: z.string(),
      method: z.string(),
      results: z.string(),
      bibtex: z.string(),
    }),
  }),
});
```

---

## Phase 2: 页面实现

### 2.1 创建页面路由

**文件**: `astro/src/pages/[lang]/osa.astro`

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import OsaHero from '../../components/osa/OsaHero.astro';
import OsaAbstract from '../../components/osa/OsaAbstract.astro';
import OsaMethod from '../../components/osa/OsaMethod.astro';
import OsaResults from '../../components/osa/OsaResults.astro';
import OsaBibTeX from '../../components/osa/OsaBibTeX.astro';

export async function getStaticPaths() {
  return [
    { params: { lang: 'en' } },
    { params: { lang: 'zh' } },
  ];
}

const { lang } = Astro.params;
const osaData = await getCollection('osa');
const data = osaData[0];
const content = data[lang];
---

<BaseLayout
  title={content.title}
  description={content.abstract.slice(0, 160)}
  lang={lang}
>
  <OsaHero content={content} data={data} />
  <OsaAbstract content={content} />
  <OsaMethod content={content} />
  <OsaResults content={content} />
  <OsaBibTeX content={content} />
</BaseLayout>
```

### 2.2 创建区块组件

| 组件 | 文件 | 功能 |
|------|------|------|
| Hero | `src/components/osa/OsaHero.astro` | 论文标题、作者、venue badge、arxiv/project 按钮、封面图 |
| Abstract | `src/components/osa/OsaAbstract.astro` | 摘要文本 + teaser 图 |
| Method | `src/components/osa/OsaMethod.astro` | 方法描述 + 框架图/模块图 |
| Results | `src/components/osa/OsaResults.astro` | 实验结果 + 图表/表格 |
| BibTeX | `src/components/osa/OsaBibTeX.astro` | BibTeX 引用块 + 一键复制 |

### 2.3 样式规范

- 使用 Tailwind v4 utility classes
- 主题色从 `global.css` `@theme` 变量读取
- Dark mode 通过 `dark:` 变体实现
- 响应式: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- Section spacing: `py-16 lg:py-24`

---

## Phase 3: 导航与链接

### 3.1 更新 PaperCard 链接

修改 `src/components/PaperCard.astro`：
- 当 `paper.project` 存在时，"Project" 按钮指向 `/{lang}/osa/`

### 3.2 添加语言切换

在 `osa.astro` 页面头部添加语言切换链接（复用现有 LanguageSwitcher 模式）。

---

## Phase 4: 构建验证

### 4.1 开发验证

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io/astro
npm run dev
# 访问 http://127.0.0.1:4321/zh/osa/ 和 /en/osa/
```

### 4.2 构建验证

```bash
npm run build
# 验证 dist/osa/index.html 和 dist/en/osa/index.html 存在
```

### 4.3 回归检查

- [ ] `npx astro check` 0 errors
- [ ] `npm run build` 通过
- [ ] 中英文页面均可访问
- [ ] Dark mode 切换正常
- [ ] 图片加载正常
- [ ] BibTeX 复制功能正常

---

## Phase 5: 部署

```bash
cd /Users/myk/Repo/wangrui2025/wangrui2025.github.io
./scripts/smart-autopush.sh "feat(osa): add CVPR 2026 OSA project showcase page with bilingual support"
```

---

## 文件清单

| # | 文件路径 | 操作 |
|---|----------|------|
| 1 | `astro/src/content/osa/osa.json` | 新建 |
| 2 | `astro/src/content.config.ts` | 修改（注册 collection） |
| 3 | `astro/src/pages/[lang]/osa.astro` | 新建 |
| 4 | `astro/src/components/osa/OsaHero.astro` | 新建 |
| 5 | `astro/src/components/osa/OsaAbstract.astro` | 新建 |
| 6 | `astro/src/components/osa/OsaMethod.astro` | 新建 |
| 7 | `astro/src/components/osa/OsaResults.astro` | 新建 |
| 8 | `astro/src/components/osa/OsaBibTeX.astro` | 新建 |
| 9 | `astro/src/components/PaperCard.astro` | 修改（更新 project 链接） |

---

## 风险与依赖

1. **图片路径**: 所有图片通过 `/academic/images/papers/cvpr2026-osa/...` 引用（build pipeline 已处理）
2. **BibTeX 格式**: 需用户提供准确的 BibTeX 条目
3. **摘要/方法文本**: 需用户提供或从论文中提取
