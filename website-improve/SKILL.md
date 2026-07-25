---
name: website-improve
description: |
  一站式网站改进 skill (v4.1.1 — PER Workflow + body 拆 4 references/ 1 层深).
  触发: 改网页 / 提升网站 / site-improve / multi-site / 4 站 / sites≥2.
  Sub-mode A/B/C/D, 默认 4 sites (multi-site fan-out).
  L19-L27: 4 站 CI 全绿 / fix-validate-build / pre-flight / ToolSearch / recovery / heartbeat / deployed-layer curl / 验收 / 3-role workflow.
  不适用: 单文件 typo / 文档微调 / 跟网站无关的 bug 修.
  反模式: ❌ 4 站 CI red 仍说 done / ❌ 改 package.json 没重生成 lockfile / ❌ 跳过 pre-flight / ❌ 1 个 sub-agent 跑 3 角色.
when_to_use: |
  3-role workflow 触发词: 3 role / workflow / planner / executor / verifier / 计划者 / 执行者 / 检查验收者 / handoff.
  3 sub-agent 独立: planner 跑 plan_json_gen.py → executor 跑 exec_log_gen.py → verifier 跑 verdict_json_gen.py, verifier PASS 才 done, FAIL → executor 重做整轮. JSON schema 脚本立 ~/.claude/scripts/website-improve/.
  v4.1.1 body 拆 4 references/ 1 层深 (per Anthropic best-practices + deep-research P0 #3): SKILL.md body 935 → ~470 行 (< 500 cap).
metadata:
  version: "4.1.1"
  author: mykcs
  category: web-development
  changelog: |
    see references/changelog.md for full history (v3.x-v4.0.8)
    4.1.1 (2026-07-25): body 拆 4 references/ 1 层深 (per Anthropic best-practices + deep-research P0 #3). SKILL.md body 935 → ~470 行 (< 500 cap). references/4-site-ci-gate.md (§L19 + §L20 + §L25 + §L26) + references/orchestrator-recovery.md (§L22 + §L23 + §L24) + references/quality-checks.md (§A.5 + §A.6 + §A.7) + references/3-role-workflow.md (§L27).
    4.1.0 (2026-07-19): PER Workflow 统一抽象；新增 references/per-workflow-framework.md；L19-L26 明确归属 Executor/Verifier/Planner.
    4.0.1 (2026-06-27): L19 (网站类 Run CI 4 站全绿硬规则) + L20 (fix-validate-build 防 lockfile 漂移). Source: CASE-MULTI-SITE-FULL-AUDIT-V4-20260627 — GDKVM CI red 因 fix agent 改 package.json exact pin 但未重生成 lockfile.
  tags: [website, improve, multi-site, astro]
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-25"
---

# website-improve Skill (v4.1.1)

> **v4.1.1 body 拆 4 references/** (per Anthropic best-practices + deep-research P0 #3): SKILL.md body 935 → ~470 行. 引用 1 层深, 禁嵌套.

| references/ 段             | 内容                                                                                                               | 引用原因                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| `4-site-ci-gate.md`        | §L19 (4 站 CI 全绿硬规则) + §L20 (fix-validate-build) + §L25 (Deployed-Layer curl) + §L26 (CI 全绿验收 5 字段自检) | 4 站 owner 隔离 + CI 硬规则, Verifier 必跑                        |
| `orchestrator-recovery.md` | §L22 (Subagent Tool Provisioning) + §L23 (Orchestrator Recovery SOP) + §L24 (Stall Heartbeat Check)                | subagent stall 治本 + 治标 + 静默检测                             |
| `quality-checks.md`        | §A.5 (Multi-Round Audit) + §A.6 (Verifier Self-Test) + §A.7 (Template Consistency Check)                           | audit 4 sub-provisions + verifier self-test + template drift 检测 |
| `3-role-workflow.md`       | §L27 (3-Role Workflow, planner/executor/verifier + JSON schema)                                                    | 3 独立 sub-agent + Workflow tool 协同                             |

## 启动声明 — Pre-flight Declaration (§L21, v4.0.2 立, v4.0.6 默认反转)

> **强制**: 每次 website-improve run 启动时, claudecode **必**先输出 7 段 pre-flight declaration (audit trail). **v4.1.0 默认反转** (继承 v4.0.6 PR #6): 输完 pre-flight 后, claudecode **直接进 Phase 1**, 不再等 user 回 OK (跟 v4.0.5 默认「等 OK」相反). Round 18 user 原话: "选 1 修改 skill 以后默认 1" = 默认行为 = 反转.
>
> **可逆**: user 显式说 "恢复 pre-flight 等 OK" / "回到等待模式" / "stop 自决" → 反转回 v4.0.5 默认 (等 OK).
>
> **禁止**: 不输 pre-flight 就直接跑 = 违反 §L21 (audit trail 必留), 同违反 §L19 (4 站 CI 全绿硬规则).
>
> **PER 角色归属**: **Planner** 负责输出 7 段 pre-flight declaration 并生成 `plan.json`；**Executor** 启动时读取 `plan.json` 的 pre-flight 字段并执行后续阶段。

**7 段模板** (claudecode 启动时复制 + 填充, 末尾明确"v4.1.0 默认 = 直接进 Phase 1", user 可显式 "等 OK" 反转回 v4.0.5 默认):

```
═══════════════════════════════════════════════════════════
🚀 website-improve v4.1.0 启动 — Pre-flight Declaration (默认反转模式)
═══════════════════════════════════════════════════════════

📌 审计目标 (What I will audit):
  ├─ [Sub-mode A — Check + Improve, 默认必跑]
  │   ├─ SEO: hreflang / canonical / sitemap / OG / Twitter
  │   ├─ a11y: aria / lang / skip-to-content / focus-visible
  │   ├─ i18n: en ↔ zh 同步, 多 locale hreflang 覆盖
  │   ├─ Build: dist 产物 + Astro 9 项回归 + Tailwind v4 pin
  │   ├─ CI: npm audit --registry override + multi-site-checks
  │   └─ Security: set:html surface / CSP / external link rel
  ├─ [Sub-mode B — Astro Build, Astro 项目自动跑]
  │   └─ build pipeline / Tailwind v4 / deploy platform
  ├─ [Sub-mode C — Project Page, 触发词 / DESIGN.md 检测命中]
  │   └─ 学术项目页 / 模板 / 资产
  └─ [Sub-mode D — Multi-site Fan-out, sites ≥ 2 或触发词命中]
      ├─ 默认 4 站: mykcs.github.io / GDKVM / OSA / content2html
      ├─ **§L19 4 站 CI 全绿硬规则** (任一 red → BLOCKED on <site>)
      └─ wall-clock = slowest site

📂 目标文件夹 (Target folders):
  ├─ 主审计范围: <~/Repo/webs/active/<site>/>  (single-site 模式)
  │              或 4 sites loop (multi-site D 模式)
  ├─ 关联范围 1: <~/.agents/skills/website-improve/>  (skill 源)
  ├─ 关联范围 2: <~/.claude/rules/process.md §C.3.7>  (4 站 CI 硬规则位)
  └─ 联动 skill:  <~/.claude/CLAUDE.local.md §15 + MEMORY.md §12>  (auto-recall)

⏱️ 预期耗时: 30-60 min (single-site) / 45-65 min (4-site sweep, parallel)

🎯 完成标准 (Definition of Done):
  ├─ 1. Sub-mode A+B+C+D sweep 全跑 (或按 user override 跳过)
  ├─ 2. P0/P1/P2 全修或显式 BLOCKED (无 silent defer, §C.2 零容忍)
  ├─ 3. **§L19 4 站 CI 全绿** (`gh api .../check-runs` × 4 全 success, /check-runs 优先 per process.md §H.1 + ADR-0070)
  ├─ 4. **§L20 fix-validate-build** (改 package.json 后 `npm install` + `npm run build`)
  ├─ 5. 5 commands verification (commit / push / CI / owner / case file)
  └─ 6. 报告输出前 deferred-detector exit 0

🚨 风险自检 (Risk self-check):
  ├─ 双账号隔离: mykcs/* vs wangrui2025/* — push 前 `git remote -v` 三次确认
  ├─ owner 隔离: mykcs/mykcs.github.io vs wangrui2025/GDKVM vs wangrui2025/osa vs mykcs/content2html
  ├─ 不可逆操作: rm / reset --hard / push --force → AskUserQuestion 必问
  └─ 物理不可达: CI runner 跨境反 bot 风控 → 诚实告知 user

📝 决策流锚点 (Decision-stream anchor):
  └─ ~/.claude/decision-stream/<session-id>.md (calm-flow §4 schema)
      每次自决必追加 (auto-decide / must-ask / risk / reversible)

═══════════════════════════════════════════════════════════
              预声明结束 — v4.1.0 默认 = 直接进 Phase 1 (反转模式)
              可反转: user 说"恢复 pre-flight 等 OK" / "回到等待模式" → 回 v4.0.5 默认
═══════════════════════════════════════════════════════════
```

**核心 5 要素** (从 v3.x 沿用, 现在是 pre-flight 的子集):

```
🎯 修改目标：<具体要改什么>
📁 本地位置：<~/Repo/... 或实际路径>
🔗 GitHub 仓库：<owner/repo 名>
📊 影响范围：<单 sub-mode / 全 sweep / user override scope>
🎚️ 完成标准：<auto-pass / user-define>
```

**user 回复**: "OK" → 进 Phase 1 / "改 X" → 改 pre-flight / "跳过" → 跳过 pre-flight (违反 §L21, 留 case 记录).

**联动**: §L19 + §L21 + §C.3.6 no-stuck + §C.2 deferred items 零容忍 + §H Acceptance Protocol.

---

## 调用方式

> **副作用声明**：本 skill 会修改代码、执行构建、并自动 `smart-autopush.sh` 提交。请勿在不确定时自动触发。

**用户主动调用**：说出触发词即可，例如：

- `website-improve`
- `改进网站` / `优化网站` / `audit website`
- `project page` / `项目页`
- `create astro` / `deploy astro`

---

## PER Workflow（Plan → Execute → Verify）

> 本 skill 统一采用 PER Workflow 框架。完整框架见 [`references/per-workflow-framework.md`](references/per-workflow-framework.md)。
> 核心思想：把每次 website-improve run 拆成 **Plan → Execute → Verify** 三段，三段之间通过 JSON artifact 文件 handoff，禁止口头传话或共享 context window。

### 角色映射

| 角色         | 在 website-improve 中的职责                                                                           | 产出 artifact                   |
| ------------ | ----------------------------------------------------------------------------------------------------- | ------------------------------- |
| **Planner**  | 输出 7 段 pre-flight declaration + sub-mode 路由（A/B/C/D）+ 风险识别 + `plan.json`                   | `plan.json` / `plan.md`         |
| **Executor** | 按 plan 跑 audit、fix、smart-push；改 `package.json` 后重跑 `npm install` + build；写 `exec-log.json` | `exec-log.json` / `exec-log.md` |
| **Verifier** | 读 plan + exec-log，验证 4 站 CI green、5 字段自检全过、live curl deployed-layer；输出 `verdict.json` | `verdict.json` / `verdict.md`   |

### 三段 handoff

1. **Planner → Executor**：交付 `plan.json`，含 scope、acceptance criteria、risk list、sub-mode 路由。
2. **Executor → Verifier**：交付 `exec-log.json`，含实际改动、命令输出、git commits、deferred/blockers。
3. **Verifier → Executor（FAIL）**：指出具体 FAIL 项 + 复现证据，Executor **重做整轮**。
4. **Verifier → User（PASS）**：附 5 字段自检表（path / commit / push / CI / owner）。

### 反模式（永久失效）

- ❌ 1 个 sub-agent 跑完 3 角色。
- ❌ Executor 自己标 done。
- ❌ Verifier FAIL 还强行 ship。
- ❌ sub-agent 之间口头传话，不走 artifact。
- ❌ Planner 直接改文件或跑命令。
- ❌ Verifier 改文件替 Executor 修 bug。

### L19-L27 角色归属速查

| §    | 规则                                                         | 主责角色                                       | references/ 段           |
| ---- | ------------------------------------------------------------ | ---------------------------------------------- | ------------------------ |
| §L19 | 4 站 CI 全绿硬规则                                           | Verifier                                       | 4-site-ci-gate.md        |
| §L20 | fix-validate-build（改 package.json 后 npm install + build） | Executor                                       | 4-site-ci-gate.md        |
| §L21 | pre-flight declaration + 默认反转                            | Planner                                        | (本 SKILL.md)            |
| §L22 | ToolSearch 预加载基础 5 tool                                 | Executor（orchestrator 端为各 sub-agent 执行） | orchestrator-recovery.md |
| §L23 | Orchestrator Recovery SOP（subagent stall）                  | Executor/Planner（orchestrator 角色）          | orchestrator-recovery.md |
| §L24 | Stall Heartbeat Check（5min 检测）                           | Executor/Verifier（监控 sub-agent 存活）       | orchestrator-recovery.md |
| §L25 | Deployed-Layer curl 验证                                     | Verifier                                       | 4-site-ci-gate.md        |
| §L26 | "CI 全绿" 5 字段自检表                                       | Verifier                                       | 4-site-ci-gate.md        |
| §L27 | 3-Role Workflow (planner/executor/verifier)                  | Planner → Executor → Verifier                  | 3-role-workflow.md       |
| §A.5 | Multi-Round Audit Protocol                                   | Verifier                                       | quality-checks.md        |
| §A.6 | Verifier Self-Test                                           | Verifier                                       | quality-checks.md        |
| §A.7 | Template Consistency Check                                   | Verifier                                       | quality-checks.md        |

---

## v4.0.0 架构 (BREAKING) — 1 个 Intent → 全 Sub-Mode Sweep

> **v4.0.0 核心变化** (2026-06-27): Before = 4 mode 平级 (user 必须选 1 个). After = **1 个 user intent 触发全 sub-mode sweep**, sub-mode 是阶段不是选项. 触发后默认行为 = 全跑, 内部 trigger 决定跳过哪个 sub-mode. 未来 user 不需要选 mode, 不会问 "用 Mode A 还是 Mode D".
>
> **Migration**: existing calls (`sync all sites` / `fan-out N` / `Mode A` 词) 仍 work — 触发后进对应 sub-mode 的主路径, 其他 sub-mode 也跑. `并行全量 audit` / `全量 fan-out` / `4-site sweep` / `full sweep` 直接进 v4 全 sweep (默认 4 站).
>
> **Default scope** (v4.0.0): 4 active sites = mykcs.github.io / GDKVM / OSA / content2html. User 可 override (e.g. "只跑 mykcs+OSA").

### Sub-Mode Sweep 顺序 (内部自动)

| 顺序 | Sub-Mode                  | 触发条件                                                                                                     | 跳过条件                         | 加载 Reference                                                                                                               |
| ---- | ------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1    | **A. Check + Improve**    | 默认必跑 (任何 website intent)                                                                               | 几乎不跳 (除非显式 "只跑 build") | `scan-checklist.md` + `astro-modernization-checklist.md` + `site-audit-checklist.md` + `academic-project-checklist.md`(条件) |
| 2    | **B. Astro Build**        | 项目是 Astro / 含 `astro.config.mjs`                                                                         | 非 Astro 项目跳过                | `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md`                                      |
| 3    | **C. Project Page**       | 触发词 "project page" / "项目页" **或** 检测到 DESIGN.md / Poster/Slides 组件                                | 都不是跳过                       | `project-page-template.astro` + `academic-project-checklist.md`                                                              |
| 4    | **D. Multi-Site Fan-out** | sites count ≥ 2 **或** 触发表项命中 (`sync all sites` / `fan-out` / `parallel full audit` / `full sweep` 等) | 1 site 时跳过                    | (per-site 调 Sub-mode A)                                                                                                     |

### 意图路由（v4.0.0 — 1 行触发，4 sub-mode 自动 sweep）

```
用户输入 (任意 website intent)
  │
  └─→ 1. 跑 Sub-mode A (Check + Improve, 默认)
      │
      └─→ 2. IF Astro 项目 → 跑 Sub-mode B (Build)
          │
          └─→ 3. IF "project page" 词 / DESIGN.md 检测 → 跑 Sub-mode C
              │
              └─→ 4. IF sites count ≥ 2 / multi-site 触发表项 → 跑 Sub-mode D (per-site A+B+C sweep)
```

### Mode A 子路由（运行时检测 — 不变）

```
检测项目类型
  ├─ 发现 DESIGN.md 或 Poster/Slides 组件 → 学术项目页审计（+ academic-project-checklist.md）
  └─ 未发现 → 通用网站审计（+ site-audit-checklist.md）
```

### v3.x → v4.0.0 Migration Table

| v3.x 调用                                                      | v4.0.0 行为                                               |
| -------------------------------------------------------------- | --------------------------------------------------------- |
| "audit mykcs" (single site)                                    | Sweep A only                                              |
| "sync all sites" / "fan-out 3 sites"                           | Sweep A + D (per-site A sweep)                            |
| "create astro site"                                            | Sweep A + B                                               |
| "project page" / "项目页"                                      | Sweep A + C                                               |
| "并行全量 audit" / "4-site sweep" / "full sweep" (v4.0.0 新增) | Sweep A + B + C + D 全跑, default 4 sites                 |
| "我不需要 Mode D" (user feedback 2026-06-27)                   | **不存在此用法** — v4.0.0 不再选 mode, 全跑               |
| (v3.x "只跑 Mode A")                                           | 不存在此用法 — v4.0.0 默认 Sweep A, 跳过 B/C/D 是自动判定 |

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
10. **GitHub Actions Node.js 弃用**：遇到 Node 20 deprecated 警告 → 按 `scan-checklist.md §10` 矩阵升级 action 版本
11. **DESIGN.md 与代码同步**：修改了 CSS 类名/颜色/组件行为时，必须检查 DESIGN.md 是否需要同步更新
12. **Evidence-based audit**：审计发现必须基于实际 grep / curl / diff / build 输出。禁止 "verify X" 推测（仅列待查项不算 finding）。Stale finding 比 missing finding 更危险 — 会触发不必要的 commit + CI 浪费。Pattern: Phase 2 audit agent 必须跑 actual verification command；Phase 3 fix agent 必须先 verify 是 real 才 commit。Reference: 2026-06-04 sync-all-sites Run 2 GDKVM 教训。
13. **Multi-Round Audit (v3.9.0, 强制)**: 每次 audit 必跑 §A.5 Protocol 4 sub-provisions (snapshot diff / deferred re-eval / deployed curl / registry override). 单 audit run 不能保证找全 bug. Reference: CASE-WEBSITE-IMPROVE-INCREMENTAL-AUDIT-20260622.

---

## 模式 A/B/C/D 索引

📂 **模式 A: 检查+提升流程** → see [`references/mode-a.md`](references/mode-a.md) (loaded on demand)

## 模式 B: Astro 建站指南

**加载**: `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md`

覆盖：项目初始化、Tailwind CSS v4 集成、Content Collections 配置、i18n 路由、部署平台配置

## 模式 C: 项目页创建

**加载**: `project-page-template.astro` + `academic-project-checklist.md`

为论文创建双语项目展示页（如 `/osa/`、`gdkvm/`）。

**Stack**: Astro 6.x + Tailwind CSS v4 + `@fontsource/*` + `oklch()` 色彩
**URL 结构**: `/<project>/` → redirect → `/<project>/en/` + `/<project>/zh/`
**标准区块**: Hero → Abstract → Motivation → Method → Results → BibTeX → Links

📂 **模式 D: Multi-Site 编排 (2026-06-08 吞并自 sync-all-sites v1.1.0)** → see [`references/mode-d-multisite.md`](references/mode-d-multisite.md) (loaded on demand)

## 跨站点依赖同步升级 / 触类旁通三层扫描协议 / 学术资产库化

> 3 个次级协议已下沉到 [`references/site-improvement-protocols.md`](references/site-improvement-protocols.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。

## Skill Evolution History (v3.6.0 + 历次)

> 完整 Skill Evolution 历史（§0 / §12-§22 2026-06-02 三仓审计 / §23-§29 v3.2.0 / §30-§32 v3.3.0 / §33-§35 v3.6.0）已下沉到 [`references/evolution-history.md`](references/evolution-history.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。
>
> **§33 ASI 防御 / §34 Autopush Fallback / §35 Fix-Agent Cleanup** 是 orchestrator/fix-agent 必经节点的硬规则，所有多站点 fan-out 必查。

## 跨 § 引用 / 验证清单 / Case 引用

> 3 节已下沉到 [`references/validation-checklist.md`](references/validation-checklist.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。

---

## Sites

- mykcs.github.io: score=98, fixes=0 (Round 2 P1/P2 已 ship), ci=green ✅
- GDKVM: score=~96, fixes=2 (Round 3 P1 + P2), ci=green ✅ (commit 72294b3)
- OSA: score=98, fixes=0 (Round 2 P1/P2 已 ship), ci=green ✅
- content2html: score=82→90 (Round 7), fixes=5 (1 P0 + 3 P1 + 1 P2), ci=green ✅ (commit cb80fec)

## Total commits

N

## Case file

~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-YYYYMMDD.md

```

**禁用的输出段** (2026-06-05 规则硬化, 2026-06-15 更新 P2 也须修复):
- ❌ `## Deferred items (next run)` 列表
- ❌ `## P2 (out of scope this run)` / `## P2 (deferred)` 段落
- ❌ `## Followup` / `## TODO next session` / `## Carried over` 任何形式
- ❌ 案例文件"Lessons"段里出现"待做" / "建议改" / "应该审计" 的 follow-up 项

**未完成项的唯一合法出口**:
1. 当场 commit + push (写"已完成 N 项"入 case)
2. `AskUserQuestion` 立即问用户 (不静默 defer)
3. 标 `BLOCKED on <X>` 并写明触发条件 ("等用户跑 X 命令" / "等 CI 跑完确认 Y")

**NEVER 在响应中加** (这些进 case file on disk, 不进 chat):
- Audit score breakdown tables
- Per-commit hash tables
- Wall-clock summary
- Key insights / Lessons
- Verification evidence with raw grep output

**Inline en+zh 规则**: 报告提到有 en+zh 两种形式的值 (e.g. `aria-label`), pick ONE (zh 或 en) and reference the other in case file. **禁止 inline concatenate** (曾导致 `aria-label="Switch"切换语言"` shipped bug).

### Mode D 硬规则

- ❌ 跳过 Phase 1 验仓 → 禁止进入 Phase 2
- ❌ Phase 3 编辑未被 issue 列表覆盖的文件 → scope creep
- ❌ Phase 3 跳过 P2 不修复 → 新规则要求 P0/P1/P2 全部处理, 不得静默 defer
- ❌ 任何 CI red 时声明"完成" → verification gate 违反
- ❌ 不写 case 文件 → self-evolution 协议违反
- ❌ 输出报告含 "Deferred items" 段 → 零容忍
- ❌ audit 报"verify X 是否存在"式推测 → 必须 grep/curl 给出证据
- ❌ Agent final message 含非 JSON 内容 (L14) → orchestrator 自动 follow-up 一次 (L17 fallback); 二次仍 fail → 重建证据链, 标 `evidence_blocking: L17 fallback applied`
- ❌ 跳过 Phase 0 工具预加载 (L18) → subagent 0 tool uses 风险; 必须 `ToolSearch(select:Bash,Read,Edit,Grep,Glob)` 在 Phase 1 之前
- ✅ 任何 abort 条件触发时立即停, 不重试

### Mode D 已知反模式

- **快速通道**: 跳过 Phase 1 直接派 agent → 改错仓 (已发生 4+ 次)
- **silent skip**: CI red 不报"未完成"
- **选择性跳过 P2**: 将 P2 标记为 deferred/out-of-scope 而不修复 → 违反新规则
- **不写 case**: 跑完不沉淀 → 下次跑同样的问题
- **deferred theater** (2026-06-05 新增): 用"Deferred items"段把没做的事写得很整齐, 假装在管理 follow-up
- **speculative audit** (2026-06-05 新增): audit 报"verify X" / "check Y" / "should audit Z" → 不是审计, 是 todo list
- **fake dead code** (2026-06-05 新增): 报 dead 但未 grep 证明 → 数据捏造
- **L14 · Agent ack 协议弱点** (2026-06-08 新增): 3 个 sonnet agent 中 2 个只返 ack → 强制 JSON final message
- **L17 · L14 enforcement 不一致** (2026-06-08 新增): 即使 prompt 顶部硬性要求 JSON, 仍有 ~33% agent 返 plain text (Run 4 OSA). 解决: orchestrator 端 L17 fallback (auto SendMessage 重发一次)
- **L18 · Subagent tool loading bug** (2026-06-08 新增): General-purpose subagent 偶尔 0 tool uses (Run 4 GDKVM). 解决: Phase 0 ToolSearch 预加载基础 5 tool (Bash/Read/Edit/Grep/Glob)

### 触发式决策表 (Mode D 入口判定)

| 场景 | 决策 |
|------|------|
| "sync all sites" / "fan-out" / "deploy all" | 直接进 Mode D |
| "audit mykcs" (single site) | 走 Mode A (default) |
| "compare mykcs vs GDKVM" | 走 Mode D (multi-site), 但 audit 而非 fix |
| "all sites broken" (no specific) | AskUserQuestion: 确认是 Mode D multi-site 还是 single-site 深度 audit |
| 5+ sites | 警告: context overflow 风险, 建议拆 2 个 session (per §15 5-site audit 教训) |

### v3.4.0 已知限制 (从 sync-all-sites 继承)

- 不处理 monorepo (每个 site 必须是独立 git 仓)
- 不处理"某站点需要不同的 base branch" (默认 main)
- 不处理"某站点有手动 hold" (用户需在调用前告知)
- 5+ sites 时 wall-clock 优势递减 (token cost linear 但 context overflow 风险)
- L14 enforcement 仅在 orchestrator 评分前生效, 旁路 agent (不用本协议) 不受 L14 约束
```
