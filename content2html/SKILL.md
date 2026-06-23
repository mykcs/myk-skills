---
name: content2html
description: |
  内容 (arxiv paper / DOI / PDF / 本地 progress) → HTML (slide + long-form) 4 产物自动生成。
  Fork guizang-ppt-skill Style B 视觉 (IKB 蓝 / Swiss editorial)。
  独立 Astro project，部署到 mykcs.github.io/content2html/。
  双语支持，默认中文 (zh)，可切英文 (en)。

  触发场景：用户问 "制作组会 slide" / "arxiv paperlink 转 html" / "周报 slide" / "论文 long-form 摘要"，
  或提供 paperlink (arxiv URL / DOI / PDF / 本地 path) 要求产出 HTML。
license: MIT
metadata:
  type: skill
  category: content-generation
  version: 1.0.0
  author: mykcs
  created: 2026-06-17
  updated: 2026-06-22
  changelog:
    - "1.0.0 (2026-06-22): 完整 SKILL.md（v1.0 之前只有 case file 设计记录 + 4 产物 paper/progress HTML 模板）。合并 9 轮 grill-with-docs 决策 + 6 轮 print 修复 (4-layer root cause + print.css 模板抽取) + 9/9 Astro 回归 + Tailwind v4 directive 升级 + CSS var 命名规则 (per CASE-CONTENT2HTML-CSS-VAR-NAMING-COLLISION-20260622)."
  related_adrs:
    - "~/.claude/docs/adr/0001-claudecode-self-citation-anti-pattern.md"
    - "~/.claude/docs/adr/0002-content2html-architecture.md"
    - "~/.claude/docs/adr/0003-content2html-i18n.md"
    - "~/.claude/docs/adr/0004-content2html-visual-fork.md"
    - "~/.claude/docs/adr/0005-content2html-dispatch.md"
    - "~/.claude/docs/adr/0006-content2html-print-strategy.md"
  related_cases:
    - "~/.claude/knowledge/cases/wiki/CASE-SKILL-CONTENT2HTML-DESIGN-20260617.md"
    - "~/.claude/knowledge/cases/wiki/CASE-SKILL-CONTENT2HTML-IMPLEMENT-20260617.md"
    - "~/.claude/knowledge/cases/wiki/CASE-CONTENT2HTML-PRINT-PAGE-COUNT-DVR-20260622.md"
    - "~/.claude/knowledge/cases/wiki/CASE-CONTENT2HTML-CSS-VAR-NAMING-COLLISION-20260622.md"
  source_repo: "github.com/mykcs/content2html (独立 Astro project)"
  triggers:
    - /content2html
    - /c2h
    - content2html
    - 内容转html
    - 论文转slide
    - paper slide
    - 周报 slide
    - 进度报告
---

# content2html Skill

> 内容 → HTML 4 产物自动生成。Astro + Tailwind v4 + guizang Style B fork。

## 1. 4 产物 (按场景)

| 产物 | URL pattern | 用途 | 阅读模式 |
|------|-------------|------|----------|
| `paper-slide` | `/{lang}/paper/{arxiv-id}/slide/` | 学术组会 paper-reading 演讲 | 横向翻页 + 键盘导航 |
| `paper-summary` | `/{lang}/paper/{arxiv-id}/summary/` | 异步阅读 paper 摘要 | 单栏 long-form (滚动) |
| `progress-slide` | `/{lang}/progress/{date}/slide/` | 周报 / 工作进展演讲 | 横向翻页 + 键盘导航 |
| `progress-report` | `/{lang}/progress/{date}/report/` | 周报 long-form 归档 | 单栏 long-form (滚动) |

## 2. 架构 (11 个决策 — 9 轮 grill-with-docs 收敛)

| 维度 | 决定 | ADR |
|------|------|-----|
| Skill 数量 | **1 个 skill** (合并 paper + progress) | — |
| Trigger | 单一 `/content2html` (智能 dispatch) | ADR-0005 |
| 输入 | arxiv URL / DOI / PDF / 本地 path | — |
| 视觉 | 4 产物统一 fork guizang Style B | ADR-0004 |
| Astro | **独立 project** (`mykcs/content2html`) | ADR-0002 |
| 部署 | GitHub Pages → mykcs.github.io/content2html/ | — |
| i18n | 双语 (zh 默认 + en 切换) | ADR-0003 |
| Print | 1 slide / page, 297×167mm, 1:1 slide ↔ PDF | ADR-0006 |

完整决策历史见 `CASE-SKILL-CONTENT2HTML-DESIGN-20260617.md`。

## 3. 项目结构 (独立 Astro project)

```
mykcs/content2html/
├── astro.config.mjs                # Astro v6 + Tailwind v4 (@tailwindcss/vite)
├── package.json                    # tailwindcss 4.1.18 + @tailwindcss/vite
├── src/
│   ├── styles/
│   │   ├── global.css              # @theme design tokens + @utility typography
│   │   ├── print.css               # 独立 print template (@media print scoped)
│   │   └── README.md               # styles/ 架构 + 加新元素指引
│   ├── layouts/BaseLayout.astro    # 共享 header / slide nav
│   ├── components/                 # SlideNav / PageNumber / Kicker / ...
│   ├── content/
│   │   └── papers/{arxiv-id}.json  # paper content (zod schema)
│   └── pages/
│       ├── [lang]/
│       │   ├── paper/{arxiv-id}/   # paper-slide.html + paper-summary.html
│       │   └── progress/{date}/    # progress-slide.html + progress-report.html
│       └── 404.astro
├── scripts/
│   ├── verify-print-e2e.mjs        # E2E verifier (5 layers + page count + no trailing)
│   └── diag-print.mjs              # 诊断脚本 (Playwright + pdftoppm)
├── public/
│   ├── figures/{arxiv-id}/         # paper figures (git submodule or copy)
│   └── 404.html
└── .github/workflows/deploy.yml   # push to main → GitHub Pages
```

## 4. 关键约定 (locked in print.css 模板)

### 4.1 Print template — 新加 paper 不需改 print.css

```css
/* @media print { } — 7 sections */
@media print {
  @page { size: 297mm 167mm; margin: 0; }                    /* §1: 1:1 slide ↔ PDF */
  html, body { background: white !important; }                  /* §2: 去除 dark frame */
  .slide-deck { display: contents !important; }                 /* §2: 解除 deck 约束 */
  .slide-page {                                                     /* §3: 全套 sizing */
    width: 297mm !important;
    height: 167mm !important;
    padding: 35px 40px !important;
    display: grid !important;
    grid-template-columns: repeat(12, 1fr) !important;
    visibility: visible !important; opacity: 1 !important;
    page-break-after: auto !important; break-after: auto !important;
  }
  .slide-page + .slide-page {                                      /* §3b: 关键 — adjacent sibling */
    page-break-before: always !important;
    break-before: page !important;
  }
  /* §4-§7: 绝对定位装饰 + figures + per-element px + UI hide */
}
```

**关键 fix 模式**:
- ❌ `.slide-page { break-after: page }` → real browser 加 trailing blank
- ✅ `.slide-page + .slide-page { break-before: page }` → 1:1 slide ↔ PDF
- ❌ `transform: scale()` / `zoom:` 在 print 管线不生效
- ✅ mm + em + px 显式缩放 (跨浏览器兼容)

### 4.2 Tailwind v4 directives (CSS-first config)

```css
@import "tailwindcss";

@source "../pages/**/*.astro";        /* A.3: 显式 scan paths */
@source "../layouts/**/*.astro";
@source "../components/**/*.{astro,ts,tsx}";

@custom-variant dark (&:where(.dark, .dark *));  /* A.2: dark mode infra (CLAUDE.md 要求) */

@theme {                                              /* 设计 token */
  --color-ikb-blue: #002FA7; ...                       /* IKB blue, lemon yellow, ... */
  --text-display: 5rem; --text-headline: 3.5rem; ...  /* 字号层级 */
  --print-scale: 0.5846;                              /* C.1: print 缩放因子 */
}

@utility text-kicker { ... }                          /* A.1: typography utility */
@utility text-caption { ... }
@utility text-meta-page { ... }
```

### 4.3 4-layer print page count root cause (锁定的根因)

| Layer | 症状 | 修复 |
|-------|------|------|
| 1. `transform: scale()` 在 print 管线不生效 | 13 slides → 26 pages (× 2) | mm + em + px 显式缩放 |
| 2. `rem` 引用 root `<html>`, 非 `.slide-page` | font-size 撑爆 | `html { font-size: 9.37px }` 让 rem 同步缩 0.585× |
| 3. `break-after: page` on all slides | real browser trailing blank | `break-before: page` on adjacent siblings |
| 4. `:last-child` selector 不匹配 | slide 13 不是 last-child | adjacent sibling `+` 替代 |

### 4.4 CSS var 命名规则 (跨 context 必须前缀)

```css
/* ❌ 错的命名 — 跨 context 冲突 (后定义者赢) */
:root { --scale: 1; }              /* screen */
@theme { --scale: 0.585; }        /* print 期望值 — 被 screen :root 覆盖 */

/* ✅ 对的命名 — context 前缀 */
:root { --screen-scale: 1; }       /* screen 媒体 */
@theme { --print-scale: 0.585; }  /* print 媒体 */
```

**永远加 context 前缀**: `--print-*` (print) / `--screen-*` (screen) / `--theme-*` (cross-context tokens)。

## 5. E2E Verifier (5 layers)

```bash
SLIDE_COUNT=N URL=http://localhost:4321/content2html/{lang}/paper/{arxiv-id}/slide/ \
  node scripts/verify-print-e2e.mjs
```

**5 layer checks (全 PASS 必满足)**:
1. `mm_based` — slide width = 1122.52px (297mm @ 96 DPI)
2. `rem_scaling` — html font-size = 9.37px (0.585× of 16px base)
3. `break_before` — slide 2 break-before = page (adjacent sibling)
4. `no_trailing` — last slide break-after = auto (无 trailing blank)
5. `takeaway_scaled` — `.takeaway-item` font-size < 25px (≈ 18.74px, not 32px screen)

**Page count check**: `pdfinfo dist.pdf` should equal `SLIDE_COUNT` (no trailing blank in real browser).

## 6. 加新元素的 step-by-step

### 6.1 加新 paper

1. 写 `src/content/papers/{arxiv-id}.json` (zod schema 验证)
2. 加 figures 到 `public/figures/{arxiv-id}/` (或 submodule)
3. 跑 `npm run build` (Astro 自动 detect 新 page route)
4. 跑 `SLIDE_COUNT=N node scripts/verify-print-e2e.mjs` (5/5 PASS?)
5. `git add + smart-push` 推送 → GitHub Pages 自动 deploy

### 6.2 加新 progress

类似 paper, 但 `src/content/progress/{date}.json` + `src/pages/{lang}/progress/{date}/`。

### 6.3 加新 design token (e.g. 新的 accent color)

1. `src/styles/global.css` `@theme {}` 块加 `--color-accent-new: #...`
2. (optional) `@utility text-accent-new` 包装 typography 模式
3. 在 components / .astro 用 `class="text-accent-new"` 或 `style="color: var(--color-accent-new)"`
4. **print 自动 follow** (不需改 print.css — em 缩放机制覆盖)

### 6.4 加新 absolute 装饰 (e.g. 新的 logo)

1. screen CSS 加 `.slide-page .logo { top: 32px; left: 100px; }`
2. print.css §4 加 override: `.slide-page .logo { top: 19px; left: 58px; }` (× 0.585)
3. 跑 verifier 验证 page count + visibility 仍 PASS

### 6.5 加新 figure aspect (e.g. r-3x4)

1. screen CSS 加 `.frame-img.r-3x4 { aspect-ratio: 3/4; max-height: 56vh; }`
2. print.css §5 append `.slide-page .frame-img.r-3x4` 到现有 frame-img 规则列表
3. 跑 verifier

## 7. 验证 checklist (commit 前必跑)

```bash
# 1. E2E verifier (3 个产物 × 各自的 SLIDE_COUNT)
for n in 16 4 5; do
  case $n in 16) P="zh/paper/2603.12109/slide/";; 4) P="zh/paper/2606.18246/slide/";; 5) P="zh/progress/2026-06-17/slide/";; esac
  SLIDE_COUNT=$n URL=http://localhost:4321/content2html/$P node scripts/verify-print-e2e.mjs
done
# 期望: 3/3 PASS, 5/5 layers each

# 2. 9-point Astro regression
npm run build && \
  ls -d dist/ && \
  npx astro check && \
  grep -r "astro-route-announcer" dist/ && \
  grep -r "application/ld+json" dist/ && \
  grep -r "navigator.serviceWorker.register" dist/ || true && \
  (grep -r "@fontsource" dist/ || grep -rE "\-\-color\-" dist/_astro/*.css) && \
  grep -rE 'class="[^"]*bg-[^"]*"' dist/ | head -5 && \
  (test -z "$(grep -r 'is:inline' dist/ | grep -v 'third-party')" && echo OK) && \
  grep -r "og:image" dist/

# 3. 5-command verification gate (CLAUDE.local.md §5.2)
git log -1 && git log --oneline -5 && git status --short && git remote -v | head -2 && gh api repos/mykcs/content2html/commits/HEAD/status
```

## 8. 已知限制 (写在 README.md / ADR-0006)

- 4 figure overflow on slide 6/10 (4-panel chart 2x2 grid, content 太长) — source layout 限制
- `transform: scale()` / `zoom:` 在 print 管线不生效 (CSS spec 限制) — 用 mm/em 替代
- Playwright `page.pdf()` 不复制 trailing blank (Chromium internal API) — real browser 多 1 page
- single-line HTML grep 漏数 (always use `grep -oE 'tagname[^>]*' | wc -l`)

## 9. Quick reference — 常用命令

```bash
# 开发
cd ~/Repo/mykcs/content2html/ && npm run dev  # localhost:4321

# 构建 + 部署
cd ~/Repo/mykcs/content2html/ && npm run build  # dist/

# 验证 print
SLIDE_COUNT=N URL=... node scripts/verify-print-e2e.mjs

# 推 GitHub Pages
cd ~/Repo/mykcs/content2html/ && git add -A && git commit -m "..." && git push
# CI auto-deploys to https://mykcs.github.io/content2html/

# 加新 paper (arxiv-id = 1234.56789)
$EDITOR src/content/papers/1234.56789.json
cp -r figures/ public/figures/1234.56789/
npm run build && SLIDE_COUNT=N node scripts/verify-print-e2e.mjs
git add . && git commit -m "feat(paper): add 1234.56789" && git push
```

## 10. 双账号隔离铁律 (from CLAUDE.md)

- content2html 仓库是 `mykcs/content2html` (主账号)
- **禁止 push 到 `wangrui2025/*`** (双账号隔离 4+ 次历史污染教训)
- smart-push.sh 内部 git remote 检查 + CLAUDE.local.md kill switch 自动约束

## 11. 相关文档

- **Design 决策**: `~/.claude/docs/adr/000{1,2,3,4,5}-*.md` (5 个 ADR) + `~/.claude/knowledge/cases/wiki/CASE-SKILL-CONTENT2HTML-DESIGN-20260617.md`
- **Print 根因 (4-layer)**: `~/.claude/docs/adr/0006-content2html-print-strategy.md` (4 个 Update) + `~/.claude/knowledge/cases/wiki/CASE-CONTENT2HTML-PRINT-PAGE-COUNT-DVR-20260622.md`
- **CSS var 命名 lesson**: `~/.claude/knowledge/cases/wiki/CASE-CONTENT2HTML-CSS-VAR-NAMING-COLLISION-20260622.md`
- **Verifier 强制 5-command gate**: `~/.claude/CLAUDE.local.md` §5.2
