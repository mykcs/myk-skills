---
name: website-improve
description: |
  一站式网站改进 skill。覆盖检查+提升、Astro 建站、项目页创建三大场景。
  所有"改进/审计/优化/检查/upgrade/modernize/重构/cleanup"类请求默认进入检查+提升模式；
  说"create astro""deploy astro""build static blog"时触发 Astro 建站指南；说"project page""项目页"时触发项目页创建。
  这是网站相关工作的唯一入口，替代 site-modernizer、publishing-astro-websites 等分散 skill。
license: MIT
metadata:
  version: "3.0.0"
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
disable-model-invocation: false
---

# website-improve Skill

## 调用方式

> **副作用声明**：本 skill 会修改代码、执行构建、并自动 `smart-autopush.sh` 提交。请勿在不确定时自动触发。

### 启动声明（强制）

**skill 运行开始时，大声声明以下三要素，作为复查确认：**

```
🎯 修改目标：<具体要改什么>
📁 本地位置：<~/Repo/... 或实际路径>
🔗 GitHub 仓库：<owner/repo 名>
```

**示例**：
```
🎯 修改目标：首页研究背景区块样式
📁 本地位置：~/Repo/webs/mykcs.github.io/astro/
🔗 GitHub 仓库：mykcs/mykcs.github.io
```

> 作用：让用户确认这是正确的目标路径，防止改错仓库/文件。

---

**用户主动调用**：说出触发词即可，例如：
- `website-improve`
- `改进网站` / `优化网站` / `audit website`
- `project page` / `项目页`
- `create astro site` / `deploy astro`

---

## 模式与路由

| 模式 | 触发条件 | 预计耗时 | 加载的 Reference |
|------|---------|---------|-----------------|
| **A. 检查+提升** | 默认（所有"改进/审计/优化/检查"类请求） | 30min+ | `scan-checklist.md` + `astro-modernization-checklist.md` + `site-audit-checklist.md` + `academic-project-checklist.md`(条件) |
| **B. Astro 建站** | `create astro` / `deploy astro` / `build static blog` 等 | 视 scope | `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md` |
| **C. 项目页创建** | `project page` / `项目页` | 20-40min | `project-page-template.astro` + `academic-project-checklist.md` |

### 意图路由（入口判断）

```
用户输入
  │
  ├─ 包含 "project page" / "项目页" → 模式 C
  ├─ 包含 "create astro" / "deploy astro" / "build static blog" → 模式 B
  └─ 其他 → 模式 A（默认）
```

### 模式 A 子路由（运行时检测）

```
检测项目类型
  ├─ 发现 DESIGN.md 或 Poster/Slides 组件 → 学术项目页审计（+ academic-project-checklist.md）
  └─ 未发现 → 通用网站审计（+ site-audit-checklist.md）
```

---

## 模式 A: 检查+提升流程

**核心理念**：先检查（发现错误），后提升（现代化改进）。禁止混为一谈。

```
阶段 1 — 并行检查（Check）【发现所有错误】
  ├─ Agent-Check-Build     → 构建错误、类型错误、CI 失败、弃用警告
  ├─ Agent-Check-Buttons   → 按钮功能完整性（data-action 监听器、下载链接文件存在性）
  ├─ Agent-Check-CodeQuality → GitHub 高星模板对照（组件结构、事件处理、print CSS）
  ├─ Agent-Check-Code      → 反模式、安全漏洞、重复页面、死代码
  ├─ Agent-Check-Content   → SEO 缺失、a11y 问题、i18n 不对等
  ├─ Agent-Check-Deps      → 未使用依赖、lockfile 问题、版本冲突
  ├─ Agent-Check-CV        → CV 页面 CSS specificity、作者颜色（主站必须）
  └─ Agent-Check-Routing   → i18n switch URL 指向实际文件、redirect 不截断 switch URL

阶段 2 — 顺序修复错误（Fix Errors）【必须清零】
  BUILD_PASS → TYPECHECK_PASS → CI_PASS → ZERO_WARNINGS

阶段 3 — 并行提升（Improve）【现代化改进】
  ├─ Agent-Upgrade-Deps       → 依赖升级、迁移到推荐方案
  ├─ Agent-Modernize-Code     → Astro 6.x 模式、Tailwind v4 最佳实践
  └─ Agent-Optimize-Assets    → 图片优化、字体本地化、学术资产库化、**CDN 加载模式 OSA vs GDKVM 判定（§12.2）**

阶段 4 — 并行验证（Verify）【检查+提升双重确认】
  ├─ Agent-Verify-Build    → npm run build + npx astro check
  ├─ Agent-Verify-CV       → Playwright 截图验证 CV 作者颜色
  ├─ Agent-Verify-Visual   → Playwright 响应式 + WebKit 验证
  └─ Agent-Verify-i18n     → zh/en 内容对等检查
```

### Agent 职责清单

| Agent | 检查什么 | 参考章节 |
|-------|---------|---------|
| Agent-Check-Build | npm run build、npx astro check、CI 历史、GitHub Actions 版本 | scan-checklist.md §1 |
| Agent-Check-Buttons | [data-action] 监听器、下载链接文件存在性、onclick 函数、外部链接 | scan-checklist.md §2 |
| Agent-Check-CodeQuality | 组件行数、事件委托模式、dark mode 实现、print CSS、GitHub 高星对照 | scan-checklist.md §3 |
| Agent-Check-Code | set:html XSS（**已知限制见 §4.6.1/§4.6.2 不修复**）、Astro.glob、ViewTransitions→ClientRouter、重复页面 | scan-checklist.md §4 |
| Agent-Check-Content | OG 标签、JSON-LD、PWA、i18n 对等性 | scan-checklist.md §5 |
| Agent-Check-Deps | 未使用依赖、tailwind.config.mjs 废弃、postcss.config.mjs、**npm audit 中危 dev-only（§4.6.1 不修复）** | scan-checklist.md §6 |
| Agent-Check-CV | .cv-paper-author-* CSS specificity、Playwright 截图验证 | scan-checklist.md §7 |
| Agent-Check-Routing | i18n switch URL 实际文件存在性、redirect 不截断 switch URL | scan-checklist.md §9 |
| Agent-Check-Hreflang | **§2.7 hreflang 路径去重**（subpath 站点硬编码 base 重复检测）| scan-checklist.md §2.7 |
| Agent-Verify-CV | Playwright + getComputedStyle 验证作者颜色 | — |

---

## 通用非协商规则

> 适用于所有模式。

1. **不破坏构建**：任何修改后必须 `npm run build` 通过
2. **安全优先**：`set:html` / secrets 问题标记为 P0，不自动修复；但 **§4.6.2 set:html 翻译文本（含 HTML）** 和 **§4.6.1 npm audit dev-only 中危** 属于已知限制，明确不修复
3. **中英同步**：a11y/UI 修复涉及文本时，同步更新 en.json / zh.json
4. **Commit 必须**：修改文件后必须 `smart-autopush.sh` 提交（永远不要裸 `git push`）
5. **验证门禁**：声明完成前，粘贴 `npm run build` 最后 5 行 + `git log --oneline -1`
6. **批量维护标记**：>10 文件变更时 commit message 加 `[BATCH MODE]`
7. **CSS 跨浏览器验证**：涉及 grid/flex/图片尺寸时，必须双端验证（Chromium + WebKit）
8. **视觉布局协议**：修改前 FULL_AUDIT → 变更批处理 → 修改后重新 FULL_AUDIT → 零溢出才报告 done
9. **CI 门禁**：push 后必须检查 GitHub Actions 状态。run fail → 修复 → 重新 push → 确认 `conclusion: success`
   - 检查：`gh run list --repo=<owner>/<repo> --limit=1 --json conclusion,status,headSha`
   - 诊断：`gh run view <run-id> --log-failed`
10. **GitHub Actions Node.js 弃用**：遇到 Node 20 deprecated 警告 → 按 `scan-checklist.md §10` 矩阵升级 action 版本
11. **DESIGN.md 与代码同步**：修改了 CSS 类名/颜色/组件行为时，必须检查 DESIGN.md 是否需要同步更新

---

## 跨站点依赖同步升级

> 适用于 `repo/webs` 下的多站点矩阵（mykcs.github.io / wangrui2025.github.io / OSA / GDKVM）

**触发条件**：发现某一站点升级了共享依赖，或用户问"其他站点是否也能升级"

**执行顺序**：主站优先验证 → 批量同步逐站验证 → 禁止同时改完再验证

详见 `scan-checklist.md` §跨站点依赖同步升级。

---

## 触类旁通三层扫描协议

> 触发条件：发现构建配置/反模式/依赖问题时，或用户说"触类旁通"

- **L1**：workspace 内检查（`~/Repo/webs` 下所有站点）
- **L2**：全机器 repo 扫描
- **L3**：同类现象扫描

详见 `scan-checklist.md` §触类旁通三层扫描协议。

---

## 学术资产库化（Academic Asset Library）

> 适用于使用 `mykcs/academic` 管理学术图片的项目。

**三阶段**：academic 仓库自动 tag → 消费者项目迁移 → 统一路径管理模块

详见 `scan-checklist.md` §学术资产库化。

---

## 模式 B: Astro 建站指南

**加载**: `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md`

覆盖：项目初始化、Tailwind CSS v4 集成、Content Collections 配置、i18n 路由、部署平台配置

---

## 模式 C: 项目页创建

**加载**: `project-page-template.astro` + `academic-project-checklist.md`

为论文创建双语项目展示页（如 `/osa/`、`/gdkvm/`）。

**Stack**: Astro 6.x + Tailwind CSS v4 + `@fontsource/*` + `oklch()` 色彩
**URL 结构**: `/<project>/` → redirect → `/<project>/en/` + `/<project>/zh/`
**标准区块**: Hero → Abstract → Motivation → Method → Results → BibTeX → Links

---

## Skill Evolution — Lessons from 2026-06-02 三仓审计

> **本节来源**：2026-06-02 对 `mykcs/mykcs.github.io`、`wangrui2025/GDKVM`、`wangrui2025/osa` 三仓库并行执行模式 A 全流程后沉淀的硬规则和反模式。每个新规则对应一个已归档的 case 文件，遵循 Deja-Vu Fix Protocol。

### 新增硬规则（紧接 §11 之后生效）

**§0 — 启动前必须验证 git remote**（**强制**，在 §1 之前执行）

> 之前我把 GDKVM 误判为 `mykcs/GDKVM`，实际是 `wangrui2025/GDKVM`（owner）— mykcs 只有 manager 权限。

```
1. cd <repo_path>
2. git remote -v                # 三次确认：origin / fetch / push 是否一致
3. git log --oneline -1         # 确认最近 commit 属于此 repo
4. 启动声明必须写 **owner/repo** 完整名，不要省略 owner
```

如果 push URL 与 fetch URL 不一致（如同时配置 mykcs/OSA 和 wangrui2025/osa），**先问用户主推哪个 remote**，再开始任何修改。

**§12 — 已知 bug 版本不升级（白名单/黑名单机制）**

升级前必须查询 case 库（`~/.claude/knowledge/cases/wiki/`）的 anti_pattern 条目：

| 包 | 黑名单版本 | 白名单（推荐）| 原因 |
|----|----------|--------------|------|
| `tailwindcss` | `4.3.0` | `4.1.18` | tsconfigPaths compatibility bug（v4.3.x 仅 1 个 release，未修） |
| `@tailwindcss/vite` | `4.3.0` | `4.1.18` | 同上 |

**升级 agent 硬规则**：发现目标版本在黑名单 → 立即停止升级并报告，不继续。

**§13 — 文档与代码同步检查（CONTEXT.md/CLAUDE.md vs package.json）**

GDKVM 审计时发现 `CONTEXT.md` 写 `Tailwind CSS ^4.3.0` 但 `package.json` 是 `^4.1.18`（**case 触发**）— 文档漂移是审计的副产品。

**强制流程**：
1. 每次修改 `package.json` / `astro.config.mjs` / `tailwind.config.mjs` 关键版本字段
2. 必须搜索 `CLAUDE.md` / `CONTEXT.md` / `README.md` / `DESIGN.md` 中的版本号引用
3. 不一致 → 立即在同一次 commit 修复 + 注明原因

**§14 — 跨仓 owner/manager 关系（项目级备忘）**

| 仓库 | owner | manager | 推送主目标 |
|------|-------|---------|----------|
| `mykcs/mykcs.github.io` | mykcs | — | `origin` = `mykcs/mykcs.github.io` |
| `wangrui2025/GDKVM` | wangrui2025 | mykcs | `origin` = `wangrui2025/GDKVM` |
| `wangrui2025/osa` | wangrui2025 | mykcs | `origin` = `wangrui2025/osa` |
| `wangrui2025/wangrui2025.github.io` | wangrui2025 | — | 已重定向到 mykcs/mykcs.github.io |

**启动声明必须用 owner/repo 完整名**，不要写 `mykcs/GDKVM`。

**§15 — P0 修复必须产硬化机制（Deja-Vu 防护）**

> IF 同一类问题在 ≤30 天内出现第二次（**跨 repo 同模式也算**），立即停止继续修复并按 `behavioral-deja-vu-gate.md` 执行：
> 1. 对比上次根因 vs 本次根因
> 2. 必须产出一项硬化规则或工具改进
> 3. 否则禁止继续

**已知 Deja-Vu 案例**（已加硬化）：
- **CASE-HREFLANG-BASE-DUPLICATION-20260602**：GDKVM + OSA 同次审计同时出现 → 已加 `scan-checklist.md` §2.7 检测脚本 + 3 仓 CI 集成
- **CASE-GDKVM-TAILWIND-V4-BROKEN-20260528**：双 `tailwindcss()` 注册 → 已加 `scan-checklist.md` §6 + §6.1 + 黑名单规则 §12

**§16 — §2.7 / §6 类检测脚本必须自动集成进 CI**

> 之前我把 §2.7 脚本加进 `scan-checklist.md` 但 SKILL.md 没有强制要求同步集成到 `.github/workflows/`。这次补做时才发现：脚本不集成进 CI = 装饰品。

**强制流程**（修复任何 P0 涉及 build 产物检测时）：
1. 在 `scan-checklist.md` 加检测章节
2. **同一次 PR/commit** 集成进 3 仓 `.github/workflows/*.yml`（deploy.yml / astro.yml / main.yml 视项目命名）
3. 脚本优先用 Node 内置 `fs/path`，不引入新 npm dep
4. **负样本测试**：注入反例 URL 验证 CI 真的会 fail（OSA agent 2026-06-02 实施）

### 新增 Agent（Agent 职责清单补全）

| Agent | 检查什么 | 参考章节 |
|-------|---------|---------|
| Agent-Check-Hreflang | **§2.7 hreflang 路径去重**（subpath 站点硬编码 base 重复）| scan-checklist.md §2.7 |
| Agent-Check-DocSync | **§13 文档同步**（CONTEXT.md/CLAUDE.md/README.md/DESIGN.md vs package.json）| 新增 §13（本 SKILL） |

### 跨仓 audit 拆分策略（默认变更）

> 之前 SKILL.md 推荐"7-8 agents per repo"细粒度模式。本次 3 仓 × 7-8 = 21+ 并行 agent，**token 消耗过大但效果并不更好**（每个 agent 都要重新读 scan-checklist.md）。

**新默认（2026-06-02 起）**：

| 场景 | 推荐模式 | agent 数 |
|------|---------|---------|
| 单仓审计 | 1 主 agent 跑全 §1-§9 + 1 verify agent = **2 agents** | 2 |
| 2-3 仓并行 | **每仓 1 个 agent 跑全 phases**（含 subagent 内部使用 Explore） | N |
| 4+ 仓并行 | 拆 2-3 阶段（check / fix / verify），每阶段 N agents | 3N |
| 极复杂（5+ 仓）| `Workflow` 工具 pipeline 编排 | 视规模 |

**否决条件**：
- 不要为了"细粒度"硬拆 agent — token 成本与隔离价值不对等
- 不要 21+ 个独立 agent 同时跑 — 浪费 context，主会话和子 agent 都会做相同工作

### 跨仓 audit 启动检查清单（新增，2026-06-02 起强制）

1. **3 个 agent 并行上限**（避免 21+ agent 烧 token）：单次 audit ≤ 3 个仓
2. **per-repo 路径验证**（每个仓独立 `git remote -v` + `git log --oneline -1`）
3. **owner/manager 关系查表**（§14）
4. **package manager 检测**（pnpm vs npm — 影响 `npm install` vs `pnpm install`）
5. **base path 收集**（subpath 站点：`GDKVM` / `osa` / `''` — 用于 §2.7 配置）

### 已知跨仓约束

| 约束 | 原因 | 适用 |
|------|------|------|
| `tailwindcss` 三仓必须同步 | v4.3.0 bug 跨仓传染风险 | GDKVM / OSA / mykcs |
| `astro` major 升级需单独 session | Breaking change 风险 + CI 验证耗时 | 三仓 |
| `wangrui2025/*` 不能 push 到 mykcs | 双账号污染历史教训 | GDKVM / osa |

### 已集成的 CI 检测（2026-06-02）

| 仓库 | Workflow | 检测 | SHA |
|------|----------|------|-----|
| mykcs.github.io | deploy.yml | §2.7 跨仓 base contamination | `14dae80` |
| GDKVM | deploy.yml | §2.7 自身 base duplication | `6b73cda` |
| OSA | astro.yml | §2.7 自身 base duplication | `0dced6b` |

下次 audit 新加 subpath 站点时，必须把对应的 §2.7 BASE 常量加进该仓的 CI 脚本。
