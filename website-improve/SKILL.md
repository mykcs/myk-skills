---
name: website-improve
description: |
  一站式网站改进 skill。覆盖深度审计+现代化、Astro 建站、项目页创建三大场景。
  所有"改进/审计/优化/检查/upgrade/modernize/重构/cleanup"类请求默认进入深度审计+现代化模式；
  说"create astro""deploy astro""build static blog"时触发 Astro 建站指南；说"project page""项目页"时触发项目页创建。
  这是网站相关工作的唯一入口，替代 site-modernizer、publishing-astro-websites 等分散 skill。
license: MIT
metadata:
  version: "2.2.0"
  author: mykcs
  category: web-development
  triggers:
    - website-improve
    - 改进网站
    - 优化网站
    - audit website
    - 网站审计
    - 网站检查
    - improve site
    - site health
    - health check
    - check website
    - site check
    - audit site
    - upgrade
    - modernize
    - 升级
    - 重构
    - cleanup
    - clean up
    - 清理
    - 反模式扫描
    - anti-pattern scan
    - build fix
    - fix build
    - architecture decision
    - ADR
    - build pipeline
    - 构建脚本
    - duplicate pages
    - 重复页面
    - merge scripts
    - redirect
    - 重定向
    - project page
    - 项目页
    - astro
    - astro website
    - astro static site
    - astro content collections
    - astro deployment
    - astro firebase
    - astro mermaid
    - starlight
    - build astro site
    - create astro site
    - deploy astro to firebase
    - set up content collections
    - add mermaid diagrams to astro
    - configure astro i18n
    - build static blog
    - astro markdown setup
  tags:
    - audit
    - improve
    - astro
    - performance
    - a11y
    - security
    - layout
    - modernization
    - deployment
    - checklist
user-invocable: true
disable-model-invocation: true
---

# website-improve Skill

## 调用方式

> **副作用声明**：本 skill 会修改代码、执行构建、并自动 `smart-autopush.sh` 提交。请勿在不确定时自动触发。

**用户主动调用**：说出触发词即可，例如：
- `website-improve`
- `改进网站` / `优化网站` / `audit website`
- `project page` / `项目页`
- `create astro site` / `deploy astro`

**由于 `disable-model-invocation: true`，Claude 不会在其他对话中自动触发本 skill。** 只有当你明确说出触发词时才会执行。

---

## 触发方式

- `website-improve`
- `改进网站` / `优化网站` / `audit website` / `网站审计` / `网站检查`
- `improve site` / `site health` / `health check`
- `check website` / `site check` / `audit site`
- `upgrade` / `modernize` / `升级` / `重构` / `cleanup` / `clean up` / `清理`
- `反模式扫描` / `anti-pattern scan`
- `build fix` / `fix build`
- `project page` / `项目页`
- `astro` / `create astro site` / `deploy astro` / `build static blog`
- `redirect` / `重定向`

---

## 定位

| 模式 | 场景 | 预计耗时 | 加载的 Reference |
|------|------|---------|-----------------|
| **A. 深度审计+现代化** | 默认模式。所有"改进/审计/优化/检查"类请求进入此模式 | 30min+ | `scan-checklist.md` + `astro-modernization-checklist.md` + `site-audit-checklist.md` + `academic-project-checklist.md`(条件加载) |
| **B. Astro 建站** | "create astro/deploy astro"等 | 视 scope | `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md` |
| **C. 项目页创建** | "project page/项目页" | 20-40min | `project-page-template.astro` + `academic-project-checklist.md` |

---

## 意图路由

收到请求后，按以下优先级判断模式：

```
用户输入
  |
  v
包含 "project page" / "项目页" ?
  ├─ 是 → 模式 C: 项目页创建
  └─ 否 → 包含 "create astro" / "deploy astro" / "build static blog" / "astro markdown" / "starlight" ?
       ├─ 是 → 模式 B: Astro 建站指南
       └─ 否 → 模式 A: 深度审计+现代化（默认）
```

**模式 A 的子路由（运行时检测，非用户输入触发）：**

```
进入模式 A 后
  |
  v
检测项目类型
  ├─ 发现 DESIGN.md 或 Poster/Slides 组件 → 学术项目页审计
  │   ├─ 有 DESIGN.md → 读取硬约束，执行学术项目专用检查
  │   └─ 无 DESIGN.md → 自动创建 DESIGN.md 模板，标记为 P0 建议人工填充
  └─ 未发现 → 通用网站审计
```

---

## 模式 A: 深度审计+现代化（默认）

**加载**: `references/scan-checklist.md` + `references/astro-modernization-checklist.md` + `references/site-audit-checklist.md` + 条件加载 `references/academic-project-checklist.md`

完整工作流（并行 Agent 架构）：

```
阶段 1 — 并行探测（Probe）【同时启动】
  ├─ Agent-Detect-Type → 检测项目类型 + DESIGN.md 检查 + UPGRADE-CHECK
  └─ Agent-Docs-Lookup → Context7 + WebSearch 验证当前最佳实践
  |
  v
阶段 2 — 并行评估（Assess）【同时启动】
  ├─ Agent-Assess-Code   → 代码库结构、组件、反模式、重复页面
  ├─ Agent-Assess-Build  → 构建配置、依赖分析、脚本检查
  └─ Agent-Assess-Content → SEO/OG/PWA、i18n 内容对等、a11y
  |
  v
阶段 3 — 顺序修复（Fix）【依赖阶段 2 结果】
  CLEAN → BUILD → SCAN → PROJECT-SPEC → REDIRECT
  |
  v
阶段 4 — 并行验证（Verify）【同时启动】
  ├─ Agent-Verify-Build   → npm run build + npx astro check
  ├─ Agent-Verify-Visual  → Playwright 响应式 + WebKit 验证
  └─ Agent-Verify-i18n    → zh/en 内容对等检查
```

### 并行 Agent 调用模板

**阶段 1 — 并行探测**：
```
Agent({
  description: "Detect project type",
  prompt: "Check current workspace: 1) Is there DESIGN.md or Poster/Slides components? 2) Run 'npm outdated --depth=0' and 'npx astro --version' for UPGRADE-CHECK. 3) If academic project without DESIGN.md, create template. Return: {type: 'generic'|'academic'|'homepage', has_design_md: bool, upgrade_opportunities: [...]}."
})
Agent({
  description: "Lookup docs best practices",
  prompt: "Query Context7 for Astro 6 latest patterns, Tailwind v4 best practices. WebSearch for 'Astro 6 best practices 2026', 'Tailwind CSS v4 oklch 2026'. Return: {findings: [{source, topic, finding}]}."
})
```

**阶段 2 — 并行评估**：
```
Agent({
  description: "Assess code patterns",
  prompt: "Explore src/ directory. Check for: Astro.glob usage, Image format prop, ViewTransitions (should be ClientRouter), i18n conditional rendering, duplicate pages. Return: {issues: [{file, line, severity, message, fix_type}]}."
})
Agent({
  description: "Assess build and deps",
  prompt: "Check package.json, astro.config.mjs, build scripts. Identify unused deps, missing lock file, outdated build pipeline. Return: {issues: [...], unused_deps: [...]}."
})
Agent({
  description: "Assess content and SEO",
  prompt: "Check SEO meta tags, Open Graph, JSON-LD, PWA manifest. Verify en.json/zh.json parity. Check alt text on images. Return: {issues: [...], i18n_gaps: [...]}."
})
```

**阶段 4 — 并行验证**：
```
Agent({
  description: "Verify build passes",
  prompt: "Run 'npm run build' and 'npx astro check'. Return: {build_passed: bool, errors: [...], astro_check_passed: bool}."
})
Agent({
  description: "Verify visual layout",
  prompt: "Run Playwright responsive checks (mobile/desktop). If academic project with Poster/Slides, run WebKit verification per DESIGN.md constraints. Return: {responsive_ok: bool, webkit_ok: bool, screenshots: [...]}."
})
Agent({
  description: "Verify i18n parity",
  prompt: "Compare en.json and zh.json key counts. Check for missing keys in either language. Return: {parity_ok: bool, missing_en: [...], missing_zh: [...]}."
})
```

### 依赖升级检查（UPGRADE-CHECK）

执行任何升级前，先读取 `~/.claude/memory/reference/do-not-upgrade-packages.md` 黑名单。

**升级流程**：
1. `pnpm outdated` / `npm outdated` 列出可升级包
2. **Patch/Minor**（如 4.2.2 → 4.3.0）：可直接升级，构建验证通过即可 push
3. **Major**（如 1.8.6 → 2.0.0）：需先读 CHANGELOG，确认无破坏性变更后再升级
4. 升级后必须执行：`npx astro check` + `npm run build`，全部通过才算完成
5. 跨站点升级（如 mykcs.github.io + OSA + GDKVM）需在每个仓库分别验证构建

**当前已知可升级项（2026-05-20）**：
- `tailwindcss` 4.2.2 → 4.3.0（**四站全部完成**）
- `astro-expressive-code` 0.41.7 → 0.42.0（GDKVM 已完成，零影响确认）
- `astro` 6.1.8 → 6.3.6（wangrui2025.github.io 已完成，其他站待评估）
- `astro-pagefind` 1.8.6 → 2.0.0（**major**，需读 CHANGELOG 再决定）

**兼容性记录（已解决）**：
- wangrui2025.github.io `@tailwindcss/vite` 4.3.0 构建失败 → **修复方案**：显式锁定 `vite` 到 `^7.3.2`（避免 npm 解析到 Vite 8.x）。mykcs.github.io 因使用 pnpm-lock 天然锁定 Vite 7.x，未触发此问题。

### 跨站点依赖同步升级

> 适用于 `repo/webs` 下的多站点矩阵（mykcs.github.io / wangrui2025.github.io / OSA / GDKVM 等）

**触发条件**：发现某一站点升级了共享依赖（如 Tailwind CSS、Astro、@tailwindcss/vite），或用户问"其他站点是否也能升级"。

**执行顺序**：
1. **扫描版本矩阵**
   ```bash
   cd ~/Repo/webs
   for d in */; do
     echo "=== $d ==="
     cat "$d/package.json" 2>/dev/null | grep -E "tailwindcss|@tailwindcss/vite|astro" | head -6
     cat "$d/astro/package.json" 2>/dev/null | grep -E "tailwindcss|@tailwindcss/vite|astro" | head -6
   done
   ```
2. **判断升级范围**
   - 主站（mykcs.github.io）→ 优先升级，作为验证基准
   - 活跃维护子站（OSA / GDKVM）→ 同步升级
   - 重定向/归档站（wangrui2025.github.io / sprites-gallery）→ 也升级，保持依赖一致，避免技术债
3. **先主站验证，再批量同步**
   - 步骤 A：主站升级 → `npm run build` 通过 → `smart-autopush.sh` 提交
   - 步骤 B：其他站逐站执行相同升级 → 每站 `npm run build` 验证 → 逐站提交
   - 禁止：多站同时改完再一起验证（一旦失败难以定位）
4. **Commit 规范**：`chore(deps): upgrade tailwindcss to 4.3.0`
5. **版本差异记录**：升级完成后更新 `webs-context.md` 中的依赖版本表

**扫描后强制修复**（见 `scan-checklist.md` 详细命令）：
- i18n 条件渲染 `lang === 'zh' ? '中文' : 'English'` → 统一替换为 `t('key')`
- Google Fonts CDN → `@fontsource/*` 本地字体
- 非首屏图片添加 `loading="lazy" decoding="async"`
- 卸载未使用依赖

**评分**: Build Health 20% + Astro 6.x Compliance 15% + i18n Parity 15% + Responsive 10% + Performance 10% + Security 10% + **Project-Specific 20%**（学术项目：Poster 约束/WebKit/公式渲染；主站：SEO/OG/PWA）

---

## 模式 B: Astro 建站指南

**加载**: `references/astro-build-guide.md` + `references/astro-modernization-checklist.md` + `references/deployment-platforms.md` + `references/markdown-deep-dive.md`

覆盖：
- 项目初始化与目录结构（`astro-build-guide.md`）
- Tailwind CSS v4 集成（`astro-build-guide.md`）
- Content Collections 配置（`astro-build-guide.md`）
- i18n 路由设置（`astro-build-guide.md`）
- 布局、组件、Slots（`astro-build-guide.md`）
- 图片与资源处理（`astro-build-guide.md`）
- SEO / Open Graph / JSON-LD（`astro-build-guide.md`）
- 升级路径与反模式（`astro-modernization-checklist.md`）
- 部署平台配置（`deployment-platforms.md`）
- Markdown/MDX、Mermaid 图表（`markdown-deep-dive.md`）

---

## 模式 C: 项目页创建

**加载**: `references/project-page-template.astro`

为论文创建双语项目展示页（如 `/osa/`、`/gdkvm/`）：

**Stack**: Astro 6.x + Tailwind CSS v4 + `@fontsource/*` + `oklch()` 色彩
**URL 结构**: `/<project>/` → redirect → `/<project>/en/` + `/<project>/zh/`
**标准区块**: Hero → Abstract → Motivation → Method → Results → BibTeX → Links

创建后：Stage → `smart-autopush.sh` → `git log --oneline -1` 确认。

---

## 通用非协商规则

适用于所有模式：

1. **不破坏构建**：任何修改后必须 `npm run build` 通过
2. **安全优先**：`set:html` / secrets 问题标记为 P0，不自动修复
3. **中英同步**：a11y/UI 修复涉及文本时，同步更新 en.json / zh.json
4. **Commit 必须**：修改文件后必须 `smart-autopush.sh` 提交（永远不要裸 `git push`）
5. **验证门禁**：声明完成前，粘贴 `npm run build` 最后 5 行 + `git log --oneline -1`
6. **批量维护标记**：>10 文件变更时 commit message 加 `[BATCH MODE]`，完成后 `git log --oneline` + `git diff --stat`
7. **CSS 跨浏览器验证**：涉及 grid/flex/图片尺寸时，必须双端验证（Chromium + WebKit）
8. **视觉布局协议**：修改前 FULL_AUDIT（Playwright 测溢出）→ 变更批处理 → 修改后重新 FULL_AUDIT → 零溢出才报告 done
