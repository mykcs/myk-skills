---
name: website-improve
description: |
  一站式网站改进 skill (v4.0.7 — §L27 3-role workflow 立, 跟 PR #6 §L21 默认反转 协同).
  触发: 改网页 / 提升网站 / site-improve / multi-site / 4 站 / sites≥2.
  Sub-mode A/B/C/D, 默认 4 sites (multi-site fan-out).
  L19-L27: 4 站 CI 全绿 / fix-validate-build / pre-flight / ToolSearch / recovery / heartbeat / deployed-layer curl / 验收 / 3-role workflow.
  不适用: 单文件 typo / 文档微调 / 跟网站无关的 bug 修.
  反模式: ❌ 4 站 CI red 仍说 done / ❌ 改 package.json 没重生成 lockfile / ❌ 跳过 pre-flight / ❌ 1 个 sub-agent 跑 3 角色.
when_to_use: |
  3-role workflow 触发词: 3 role / workflow / planner / executor / verifier / 计划者 / 执行者 / 检查验收者 / handoff.
  3 sub-agent 独立: planner 跑 plan_json_gen.py → executor 跑 exec_log_gen.py → verifier 跑 verdict_json_gen.py, verifier PASS 才 done, FAIL → executor 重做整轮. JSON schema 脚本立 ~/.claude/scripts/website-improve/.
metadata:
  version: "4.0.8"
  author: mykcs
  category: web-development
  changelog: |
    see references/changelog.md for full history (v3.x-v4.0.7)
    4.0.1 (2026-06-27): L19 (网站类 Run CI 4 站全绿硬规则) + L20 (fix-validate-build 防 lockfile 漂移). Source: CASE-MULTI-SITE-FULL-AUDIT-V4-20260627 — GDKVM CI red 因 fix agent 改 package.json exact pin 但未重生成 lockfile. §L20 硬规则: 改 package.json 后必跑 `npm install` + 二次 build verify. §L19 硬规则: 任何 website-improve run 4 站 (mykcs/GDKVM/OSA/content2html) 必须 CI 全 green 才算 done, 任一 red → BLOCKED on fix, 禁止声明完成. Sites 列表 v3.x 3 站 → v4.0.0 4 站, 移除 score=87 (GDKVM) 旧值同步到 Round 3 P1+lockfile 修复后实际分.
  tags: [website, improve, multi-site, astro]
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# website-improve Skill

## 调用方式

> **副作用声明**：本 skill 会修改代码、执行构建、并自动 `smart-autopush.sh` 提交。请勿在不确定时自动触发。

### 启动声明 — Pre-flight Declaration (§L21, v4.0.2 立, v4.0.6 默认反转)

> **强制**: 每次 website-improve run 启动时, claudecode **必**先输出 7 段 pre-flight declaration (audit trail). **v4.0.6 默认反转**: 输完 pre-flight 后, claudecode **直接进 Phase 1**, 不再等 user 回 OK (跟 v4.0.5 默认「等 OK」相反). Round 18 user 原话: "选 1 修改 skill 以后默认 1" = 默认行为 = 反转.
>
> **可逆**: user 显式说 "恢复 pre-flight 等 OK" / "回到等待模式" / "stop 自决" → 反转回 v4.0.5 默认 (等 OK).
>
> **禁止**: 不输 pre-flight 就直接跑 = 违反 §L21 (audit trail 必留), 同违反 §L19 (4 站 CI 全绿硬规则).

**7 段模板** (claudecode 启动时复制 + 填充, 末尾明确"v4.0.6 默认 = 直接进 Phase 1", user 可显式 "等 OK" 反转回 v4.0.5 默认):

```
═══════════════════════════════════════════════════════════
🚀 website-improve v4.0.6 启动 — Pre-flight Declaration (默认反转模式)
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
  ├─ 3. **§L19 4 站 CI 全绿** (`gh run list` × 4 全 success)
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
              预声明结束 — v4.0.6 默认 = 直接进 Phase 1 (反转模式)
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

### §L21 反转通道 (v4.0.3, user 显式触发)

> **触发关键词**: user 显式说"不需要再问我 OK/改/跳过, 就直接执行" / "直接修" / "快问我" (跟灵魂 v3 + CLAUDE.local.md §12 反转硬约束 #8 一脉相承).
>
> **行为反转**: 收到反转关键词后, claudecode 仍必输 §L21 pre-flight declaration (跟默认一致, 7 段全填), 但**不再等 user 回 OK** — 直接进 Phase 1, 后续每步自决 + decision-stream 追加.
>
> **可逆**: user 显式说"恢复 pre-flight 等 OK" / "回到等待模式" → 反转回默认.

**反转状态下决策流 schema** (calm-flow §4):
```yaml
- ts: 2026-06-27T18:30:00+08:00
  type: auto-decide
  content: "user 显式反转 §L21, claudecode 不等 OK 直接进 Phase 1"
  decision: "execute per pre-flight already declared"
  impact: "跳过 user OK gate, 后续决策全自决 + decision-stream 记录"
  reversible: true  # user 显式说"恢复"即可回默认
  risk: medium
  reason: "user 原话 '不需要再问我, OK 还是改, 还是跳过, 就直接执行' — 反转硬约束 §12 #8 触发"
```

**反模式 (反转状态下 claudecode 必避)**:
- ❌ 反转后仍问 "OK 吗" → 违反反转协议, 跟 user 显式意图冲突
- ❌ 反转后跳过 pre-flight declaration → 违反 §L21 主条款, 反转 ≠ 跳过
- ❌ 反转后写"等 user 决策" → 违反 calm-flow §6 + §C.6 no-stuck
- ✅ 反转后: pre-flight 仍输 → 直接进 Phase 1 → 每步 auto-decide + 5 commands verify

**联动**:
- **CLAUDE.local.md §12 反转硬约束 #8** (主位, 跨 skill 通用)
- **MEMORY.md HOT FACTS §10** 反转模式 8 类自决
- **rich-audit calm-flow-reverse-mode.md** 同步协议
- 反转 = 跟 §L21 默认行为合并, 跟 §C.3.6 no-stuck 协议兼容

**反模式 (claudecode 必避)**:
- ❌ 不输 pre-flight 直接跑 → 违反 §L21
- ❌ pre-flight 漏 4 站 CI 段 → 违反 §L19 联动
- ❌ pre-flight 漏 risk self-check → 违反 owner 隔离铁律
- ❌ pre-flight 完不"等 user 回" → 违反启动门控
- ❌ pre-flight 抄模板不填充具体 site → 反模式, 必填具体 paths + commit hashes

**联动**:
- **§L19** (4 站 CI 全绿硬规则) → pre-flight "完成标准 #3" 必须包含
- **§L20** (fix-validate-build 防 lockfile 漂移) → pre-flight "完成标准 #4" 必须包含
- **process.md §C.3.7** (主硬规则位) → pre-flight "关联范围 2" 引用
- **CLAUDE.local.md §15 + MEMORY.md §12** → auto-recall 入口
- **§C.2 deferred items 零容忍** → pre-flight "完成标准 #2" 体现

---

**用户主动调用**：说出触发词即可，例如：
- `website-improve`
- `改进网站` / `优化网站` / `audit website`
- `project page` / `项目页`
- `create astro` / `deploy astro`

---

## v4.0.0 架构 (BREAKING) — 1 个 Intent → 全 Sub-Mode Sweep

> **v4.0.0 核心变化** (2026-06-27): Before = 4 mode 平级 (user 必须选 1 个). After = **1 个 user intent 触发全 sub-mode sweep**, sub-mode 是阶段不是选项. 触发后默认行为 = 全跑, 内部 trigger 决定跳过哪个 sub-mode. 未来 user 不需要选 mode, 不会问 "用 Mode A 还是 Mode D".
>
> **Migration**: existing calls (`sync all sites` / `fan-out N` / `Mode A` 词) 仍 work — 触发后进对应 sub-mode 的主路径, 其他 sub-mode 也跑. `并行全量 audit` / `全量 fan-out` / `4-site sweep` / `full sweep` 直接进 v4 全 sweep (默认 4 站).
>
> **Default scope** (v4.0.0): 4 active sites = mykcs.github.io / GDKVM / OSA / content2html. User 可 override (e.g. "只跑 mykcs+OSA").

### Sub-Mode Sweep 顺序 (内部自动)

| 顺序 | Sub-Mode | 触发条件 | 跳过条件 | 加载 Reference |
|------|----------|---------|---------|---------------|
| 1 | **A. Check + Improve** | 默认必跑 (任何 website intent) | 几乎不跳 (除非显式 "只跑 build") | `scan-checklist.md` + `astro-modernization-checklist.md` + `site-audit-checklist.md` + `academic-project-checklist.md`(条件) |
| 2 | **B. Astro Build** | 项目是 Astro / 含 `astro.config.mjs` | 非 Astro 项目跳过 | `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` |
| 3 | **C. Project Page** | 触发词 "project page" / "项目页" **或** 检测到 DESIGN.md / Poster/Slides 组件 | 都不是跳过 | `project-page-template.astro` + `academic-project-checklist.md` |
| 4 | **D. Multi-Site Fan-out** | sites count ≥ 2 **或** 触发表项命中 (`sync all sites` / `fan-out` / `parallel full audit` / `full sweep` 等) | 1 site 时跳过 | (per-site 调 Sub-mode A) |

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

| v3.x 调用 | v4.0.0 行为 |
|-----------|------------|
| "audit mykcs" (single site) | Sweep A only |
| "sync all sites" / "fan-out 3 sites" | Sweep A + D (per-site A sweep) |
| "create astro site" | Sweep A + B |
| "project page" / "项目页" | Sweep A + C |
| "并行全量 audit" / "4-site sweep" / "full sweep" (v4.0.0 新增) | Sweep A + B + C + D 全跑, default 4 sites |
| "我不需要 Mode D" (user feedback 2026-06-27) | **不存在此用法** — v4.0.0 不再选 mode, 全跑 |
| (v3.x "只跑 Mode A") | 不存在此用法 — v4.0.0 默认 Sweep A, 跳过 B/C/D 是自动判定 |

### v3.11.0 旧 4-Mode 表（保留为历史 reference, v5+ 移除）

<details>
<summary>点击展开 v3.11.0 旧表 (deprecated since 4.0.0)</summary>

| 模式 | 触发条件 | 预计耗时 | 加载的 Reference |
|------|---------|---------|-----------------|
| **A. 检查+提升** | 默认（所有"改进/审计/优化/检查"类请求） | 30min+ | `scan-checklist.md` + `astro-modernization-checklist.md` + `site-audit-checklist.md` + `academic-project-checklist.md`(条件) |
| **B. Astro 建站** | `create astro` / `deploy astro` / `build static blog` 等 | 视 scope | `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md` |
| **C. 项目页创建** | `project page` / `项目页` | 20-40 min | `project-page-template.astro` + `academic-project-checklist.md` |
| **D. Multi-Site 编排** | `sync all sites` / `fan-out N sites` / `deploy all` / `audit all` / "同时在 N 个站点上部署 N 个 agent" | 10-20 min wall-clock (= slowest site) | (无额外 reference; 调用 Mode A per site) |

旧意图路由（4-选-1 OR 表，已废弃）：

```
用户输入
  │
  ├─ 包含 "sync all sites" / "fan-out" / "deploy all" / "audit all" / "multi-site" / "并行部署 N 个 agent" / "3 个独立审计" → 模式 D
  ├─ 包含 "project page" / "项目页" → 模式 C
  ├─ 包含 "create astro" / "deploy astro" / "build static blog" → 模式 B
  └─ 其他 → 模式 A（默认）
```

</details>

### ⚠️ §A.5 Multi-Round Audit Protocol (v3.9.0, 强制)

> **单 audit run 不能保证找全所有 bug**. Round 1+Round 2 案例 (CASE-WEBSITE-IMPROVE-INCREMENTAL-AUDIT-20260622) 证明: Round 1 修了 canonical/og:image → Round 2 发现 hreflang x-default regression + CVE + i18n + 404. 每次 audit 必跑 4 sub-provisions:

1. **Re-evaluate deferred items** — Round 1 deferred ≠ 关掉. Round 2 必重新评估 (用更新的工具 + 视角).
2. **Deployed behavior check** — 不是 source grep. 必 `curl <deployed-url>/...` 测真实行为. e.g. 404 page 必须 `curl /nonexistent-path/` 验证 HTTP 404 + content, 不只 `test -f src/pages/[lang]/404.astro`.
3. **CVE registry override** — `npm audit --registry=https://registry.npmjs.org/` 绕过 npmmirror 404. 否则 dev-only 中危会被遗漏.
4. **Snapshot diff** — 每次 audit 写 `/tmp/audit-<site>-<date>.md`, diff vs 上次. 立刻看到: 新增 finding (regression) / 已修 finding (progress) / 长期存在 (stale deferred, 重新评估).

**触发式决策**:
- IF user 触发 audit, 必先 `ls -1t /tmp/audit-<site>-*.md 2>/dev/null | head -1` 找上次 snapshot
- IF 上次存在 → 跑 audit + diff vs 上次 → 输出 regression report
- IF 上次不存在 → 跑 audit + 写 snapshot (无 diff)
- IF 用户说 "再检查一遍" → 必走 snapshot diff 流程, 不允许"manual 重跑全部 agent"

**Bonus test (v3.9.0)**: `diff -u <last-snapshot> <new-snapshot>` 在响应中显示 (用户可见). Empty diff = 项目干净.

### §A.6 Verifier Self-Test Protocol (v3.10.0, 强制)

> **Verifier 没 self-test = false-positive / false-negative 双风险**. content2html v3.9.0 verifier 用 absolute 5KB threshold → 6-page paper (2606.18246) 每页 ~2.4KB at 50dpi → 全 false-positive "blank page" 警报. 改 relative threshold (`<avg × 0.5`) 解决.

**Hard rule**: 任何 E2E verifier 必含 **2-sample test**:
1. **PASS sample**: known-good state → verifier 报 PASS
2. **FAIL sample**: known-bad state (e.g. 注入 trailing blank, 改 CSS 制造 overflow) → verifier 报 FAIL

**Trigger 模式**:
- IF verifier 改动后没跑 self-test → 必跑 2-sample (PASS sample first, then FAIL sample)
- IF 2-sample 任意一个 fail → revert verifier 改动, 重写
- IF 2-sample 都 PASS → ship verifier

**Real examples (content2html)**:
```javascript
// PASS sample: known-good 13-page paper
SLIDE_COUNT=13 node scripts/verify-print-e2e.mjs
// expected: ✅ PASS, noBlank=true

// PASS sample 2: known-good 16-page paper  
SLIDE_COUNT=16 node scripts/verify-print-e2e.mjs
// expected: ✅ PASS, noBlank=true (relative threshold, not absolute)

// FAIL sample: artificially inject trailing blank page
echo "extra blank" >> dist/index.html
SLIDE_COUNT=16 node scripts/verify-print-e2e.mjs
// expected: ❌ FAIL, noBlank=false
```

### §A.7 Template Consistency Check (v3.10.0, 强制)

> **Template drift = silent regression**. content2html 2606.18246 R5 之前只有 4 slides (plain headings, no Swiss editorial signature) vs 2603.12109 16 slides (full template: top-accent + accent-bar + kicker + takeaway-item + info-corner). Template 不一致 → 视觉混乱.

**Hard rule**: 当多页面 share 同一 template (e.g. paper slides × N papers) → 必跑 `check-template-consistency.sh` 在每次 commit 后.

**Trigger 模式**:
- IF N pages share template (e.g. paper-slide × papers collection) → 必 verify:
  - 同一组 template elements (top-accent + meta-page + accent-bar + kicker + h2 count + takeaway-item count)
  - 同一组 helpers (extractBullets / cleanHeading / slide structure)
  - 同一 visual signature (font sizes, spacing, info-corner)

**Real examples (content2html)**:
```bash
# scripts/check-template-consistency.sh
# 验证 paper slide.astro 在所有 N papers 有相同 template structure:
# 1. grep "slide-top-accent" count: should be N (slides)
# 2. grep "slide-info-corner" count: should be N papers
# 3. grep "kicker" count: should be similar across files
# 4. grep "takeaway-item" count: should be similar (depends on content)
# 5. JSX structure: same slide-page attrs (top-accent, meta-bar, accent-bar order)
```

**Diff output** (per file):
```
src/pages/zh/paper/2603.12109/slide.astro:
  slide-top-accent: 16 ✓
  slide-info-corner: 1
  kicker: 16
  takeaway-item: 39

src/pages/zh/paper/2606.18246/slide.astro:
  slide-top-accent: 6 ✓
  slide-info-corner: 1
  kicker: 5
  takeaway-item: 0
```

### ⚠️ §L19 4-Site CI 全绿硬规则 (v4.0.1, 强制, 适用所有 sub-mode)

> **Source**: user 2026-06-27 原话 "把这个四站全绿, 或者是你, 就是只要你提升网页的站, 都都要保持这个运行成功". CASE-MULTI-SITE-FULL-AUDIT-V4-20260627 验证 v4.0.0 4 站 fan-out 可达 CI 全绿.

**硬规则 (Hard Rule)**: 任何 website-improve run (单 sub-mode 或 v4 sweep) 涉及 **4 active sites = mykcs.github.io / GDKVM / OSA / content2html** 中任一站 → **4 站 CI 必须全部 `conclusion: success` 才算 done**.

**判定**:
- ✅ Run 4/4 CI green → done
- ❌ 任一站 CI red/pending → **BLOCKED on `<site>: <reason>`**, 禁止声明 "完成"
- ❌ 任一站 CI red 但 fix 不可行 (e.g. 物理不可达) → **BLOCKED on user decision**, 必须 `AskUserQuestion` 给选项 (回滚 / 接受 red / 重试)

**强制流程** (Phase 4 末段 + 任何 fix 之后):
```bash
# 4 站 CI 5 commands verification (per site)
for owner_repo in "mykcs/mykcs.github.io" "wangrui2025/GDKVM" "wangrui2025/osa" "mykcs/content2html"; do
  gh run list --repo "$owner_repo" --limit 1 --json conclusion,status,name,headSha
done

# 4/4 success → 输出 "✅ 4 站 CI 全绿", 写 case file + decision-stream
# < 4 success → 输出 "❌ BLOCKED on <site> CI red", 走 fix 路径或 AskUserQuestion
```

**触发判断**:
- ✅ 单 sub-mode A sweep 4 站 → 触发
- ✅ Multi-site D fan-out → 触发
- ✅ 任何 Phase 3 fix 后 → 触发 (per-site CI verify, 至少修过的站必须 green)
- ✅ 跨项目改动 (e.g. 改 shared script 被 4 站共用) → 触发
- ❌ 单 sub-mode A 跑 1 站 + user override scope (e.g. "只跑 mykcs") → 不触发 (4 站全绿不适用)

**owner 隔离 (双账号铁律)**:
- mykcs/* → mykcs/GitHub token
- wangrui2025/* → wangrui2025/GitHub token
- 跑前必 `git remote -v` 三次确认, 避免 push 错 owner (历史污染 4+ 次)

**反模式 (claudecode 历史反复踩)**:
- ❌ 报 "完成" 但 1+ 站 CI red / pending → 违反 §C verification gate
- ❌ "CI 大概会过" / "应该 OK" → 违反 §H acceptance protocol
- ❌ 不跑 gh run list 直接声明 done → 违反 CLAUDE.local.md §5.2 5 commands verification
- ❌ "我只跑 X 站, 其他站不用管" → 违反 v4.0.0 default 4-site scope

### ⚠️ §L20 Fix-Validate-Build 防 Lockfile 漂移 (v4.0.1, 强制, 适用 Phase 3 fix agent)

> **Source**: CASE-MULTI-SITE-FULL-AUDIT-V4-20260627 — GDKVM fix agent 改 `package.json` exact pin (`^4.1.18` → `4.1.18`) 但**未跑 `npm install` 重生成 `package-lock.json`** → CI `npm ci` 拒绝 (lockfile 含 `tailwindcss@4.3.0` caret 解析, 与 package.json 4.1.18 exact pin 冲突) → CI red → 二次 commit `72294b3` 修复. 根因: fix agent 改 package.json 后口头报 "已 fix", 未跑 build verify.

**硬规则 (Hard Rule)**: 任何 Phase 3 fix agent 修改 `package.json` 或 `package-lock.json` 后 → **必跑 `npm install` (重生成 lockfile) + `npm run build` (验证 build pass)** → 才算 commit 完成. 禁止口头报 "改完" 无 verify.

**强制流程** (Phase 3 fix agent 末段):
```bash
# Step 1: 改完 package.json 后, 必重生成 lockfile
npm install
# 或 --save-exact (如果改 pin):
npm install --save-exact <pkg>@<version>

# Step 2: 验证 build pass (本地)
npm run build
echo "exit=$?"  # 必须 0

# Step 3: 验证 build pass (本地跑 ci 关键步骤, 模拟)
npm ci        # 模拟 CI 用 lockfile 安装
npm run build
echo "exit=$?"  # 必须 0
```

**触发判断**:
- ✅ 改 package.json (dependencies / devDependencies / scripts / version pin) → 必跑
- ✅ 改 package-lock.json 直接 → 必跑 `npm ci` 验证一致性
- ❌ 只改 source code (.astro / .ts / .mjs / .css) → 不强制 (但建议 build smoke test)

**反模式**:
- ❌ 改 package.json exact pin 但不跑 `npm install` → 假 fix, lockfile 漂移
- ❌ 改完口头报 "已 fix" 无 build 验证 → §C.5 false-positive 风险
- ❌ 信任 agent 自报 "我跑了 build" → 必自己跑, 不可信报告

**联动**: §C.5 5 步 false-positive 诊断协议 — 改某项后 E2E fail, revert 后仍 fail, 怀疑 lockfile 漂移时, 优先跑 `npm install --save-exact` 重 lockfile.

### ⚠️ §L22 Subagent Tool Provisioning (v4.0.4, 治本 subagent stall)

> **Source**: Round 10 (2026-06-27) 4 fix agents 全部 stalled on 6 retries × 180s each (`workflowProgress[].error = "stalled — no progress for 180000ms"`). 根因 = Claude Code subagent tool provisioning 偶尔失败, per Issue #60237 (sub-agent frontmatter `tools:` 静默 drop first/last position) + Issue #49150 (Task() 无 timeout, subagent hang 让 orchestrator stuck 30+ min).

**硬规则 (Hard Rule)**: 任何 Phase 2/3 启动 subagent 前 → **Phase 0 必显式 ToolSearch load 基础 5 tool** (Bash / Read / Edit / Grep / Glob) + 检测 subagent 拿到 tool 数 > 0. 若 tool count = 0 → subagent 必 retry (with retry attempt counter, max 3).

**强制流程** (orchestrator 在 Phase 1 之后, Phase 2/3 之前):
```bash
# Phase 0: 显式 load 基础 5 tool (治本 L18)
ToolSearch(query="select:Bash,Read,Edit,Grep,Glob")

# 仍可能有 deferred tool (WebFetch / WebSearch / LSP / mcp_*) 需 on-demand load
# Phase 2/3 agent prompt 顶部明示: "如需 WebFetch, 用前先 ToolSearch load"
```

**治本 vs 治标**:
- 治本 (Phase 0 ToolSearch) — 治 Issue #60237 frontmatter tools 静默 drop
- 治标 (L23 orchestrator recovery) — subagent stalled 时补救 (Issue #49150 #3 work product on disk 范式)

**反模式 (claudecode 必避)**:
- ❌ Phase 0 跳过 ToolSearch → subagent tool count = 0 → 全部 stalled (Round 10 重演)
- ❌ 信任 subagent "我用了 N 个 tool" → 必 orchestrator 端 cross-verify tool count
- ❌ subagent stall 5+ retries 仍让它跑 → 触发 L23 recovery, 不空等

**联动**: §L23 Orchestrator Recovery (subagent stalled 时), §L24 Stall Heartbeat (每 5min 检测).

### ⚠️ §L23 Orchestrator Recovery SOP (v4.0.4, 治标 subagent stall)

> **Source**: Round 10 (2026-06-27) 4 fix agents stalled, 但磁盘 work product 已存在 (gdkvm 35678df committed, osa 36fe9c4 committed, mysite/content2html edited 但未 commit). claudecode 接管 push 4 站全成功. 范式来自 Anthropic Issue #49150 #3 (Completion state should be written to disk, not only communicated via IPC).

**触发条件**: subagent workflow 报 `error = "stalled"` 或 orchestrator 检测 subagent transcript mtime > 10min 无更新 (见 §L24).

**强制流程** (orchestrator 在 subagent stall 后立即跑):
```bash
# Step 1: 检测磁盘 work product (per Issue #49150 #3 work product on disk 范式)
for site in $SITES; do
  d="$HOME/Claude/Projects/webs/$site"
  cd "$d"
  echo "=== $site ==="
  echo "uncommitted: $(git status --short | wc -l | tr -d ' ')"
  echo "unpushed: $(git rev-list --left-right --count @{u}...HEAD | tr '\t' '/')"
  git log -1 --format='%h %s' HEAD
done

# Step 2: 接管 push (优先 smart-push, fallback manual rebase + raw push)
for site in $SITES; do
  d="$HOME/Claude/Projects/webs/$site"
  cd "$d"
  # 2a: smart-push 试 (debounce aware)
  if [ $(git rev-list --left-right --count @{u}...HEAD | tr -d '\t' | tr -d '0') -gt 0 ]; then
    "$HOME/.claude/scripts/smart-push.sh" "$d" "fix($site): Round 10 orchestrator-recovery (subagent stalled)" done --skip-review 2>&1 | tail -5
  fi
  # 2b: smart-push 误报 "无改动" → manual git push origin main + rebase fallback
  if [ $(git status --short | wc -l | tr -d ' ') -gt 0 ]; then
    git add -A
    git commit -m "fix($site): Round 10 orchestrator-recovery (subagent stalled)" --no-verify || true
  fi
  git fetch origin
  git pull --rebase origin main 2>&1 | tail -3
  git push origin main 2>&1 | tail -5
done

# Step 3: CI verify (4 站 L19 硬规则)
for owner_repo in "mykcs/mykcs.github.io" "wangrui2025/GDKVM" "wangrui2025/osa" "mykcs/content2html"; do
  gh run list --repo "$owner_repo" --limit 1 --json conclusion,status,name,headSha
done
```

**反模式 (claudecode 必避)**:
- ❌ Subagent stalled 6+ retries 后放弃整个 run → 违反 §C.1 verification gate
- ❌ "Subagent 死了, 用户接手" → 违反反转硬约束 #8 修复类自决
- ❌ Manual raw `git push` 不 rebase → 跨 session 污染 / diverged 风险
- ❌ smart-push 报 "无改动" 就不 push → 实际有 commit (debounce state cross-session 残留), 必 raw push

**联动**: §L22 (治本), §L24 (heartbeat 检测), §L19 (4 站 CI gate).

### ⚠️ §L24 Stall Heartbeat Check (v4.0.4, subagent 静默检测)

> **Source**: Round 10 (2026-06-27) subagent stalled 总耗时 ~9h (5023s+ × N retries), 期间 orchestrator 无任何信号显示 subagent 静默. 范式来自 Anthropic Issue #49150 #2 heartbeat protocol: "A simple periodic mtime update on a health file in the task dir would let the parent detect liveness."

**硬规则**: orchestrator 启动 subagent 后, 每 5 min 跑 1 次 heartbeat check. 检测 subagent transcript mtime + last tool call.

**强制流程** (orchestrator 监控):
```bash
# 每 5 min 跑 (per subagent)
TRANSCRIPT_FILE="/Users/myk/.claude/projects/-Users-myk--claude/<session_id>/subagents/workflows/<wf_id>/agent-<id>.jsonl"
HEALTH_FILE="$TRANSCRIPT_FILE.health"

# 写 health marker (subagent 必每 5 min 更新 — 但 Round 10 显示 subagent 卡死时连 health 也不更新, 所以 fallback 到 mtime)
echo "$(date -Iseconds) heartbeat" > "$HEALTH_FILE"

# orchestrator 监控 mtime
LAST_MTIME=$(stat -f %m "$TRANSCRIPT_FILE" 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE=$((NOW - LAST_MTIME))
if [ $AGE -gt 600 ]; then
  echo "⚠️ SUBAGENT STALLED: $TRANSCRIPT_FILE (mtime ${AGE}s ago)"
  echo "→ 触发 L23 Orchestrator Recovery SOP"
fi
```

**触发判断**:
- ⚠️ mtime > 5min (300s) → warning, 继续 monitor
- ❌ mtime > 10min (600s) → STALLED, 立即触发 L23 recovery
- ✅ mtime < 1min → active, 不干预

**反模式**:
- ❌ 只看 subagent total runtime (e.g. "跑了 30 min 应该还在跑") → 不准, stalled 也会累计 runtime
- ❌ 不写 health marker → 无法区分 "working silently" vs "stalled"
- ❌ mtime > 30min 才触发 recovery → 太晚, 已损失大量 wall-clock

**联动**: §L22 (治本), §L23 (recovery SOP), Issue #49150 #2 heartbeat protocol.

### ⚠️ §L25 Deployed-Layer Verify Protocol (v4.0.4, Round 11 P0/P1 regression 治本)

> **Source**: Round 11 (2026-06-29) §A.5 snapshot diff 发现 2 个 P0/P1 deployed-layer regression:
> 1. **mysite**: `astro/public/.well-known/security.txt` 文件 on disk, 但 `curl https://mykcs.github.io/.well-known/security.txt` 返 HTTP 404 (Astro 404 handler 拦截 .well-known/ 路径).
> 2. **content2html**: `public/_headers` 文件 17 行 (X-Frame-Options / CSP / X-Content-Type-Options), 但 `curl -sI https://mykcs.github.io/content2html/` 返 HTTP 200, **无任何 security header** — GH Pages user/org site 不 serve `_headers` 文件 (仅 Project Pages 支持).
>
> 文件存在 ≠ deployed. 治本 = §A.5 sub-provision #2 deployed behavior check 必跑.

**硬规则 (Hard Rule)**: 任何 Phase 3 fix commit 包含下列类型文件时, 必跑 deployed-layer verify (curl live URL) 才算 fix 完成:

| 文件类型 | 必跑 curl 验证 | 反例 (Round 11) |
|---------|---------------|-----------------|
| `public/_headers` | `curl -sI <live-url>/` 看是否含 X-Frame-Options/CSP/X-Content-Type-Options | content2html _headers 文件 on disk but GH Pages user/org site 不 serve (P0) |
| `public/.well-known/*` | `curl -sI <live-url>/.well-known/<file>` 看是否 200 + correct content-type | mysite security.txt on disk but Astro 404 handler 拦截 (P1) |
| `public/robots.txt` | `curl -s <live-url>/robots.txt` 看内容是否匹配 disk | (Round 11 content2html 验证 ✅ pass) |
| `public/manifest.json` | `curl -sI <live-url>/manifest.json` | (待 Round 12 验证) |
| `public/sitemap*.xml` | `curl -s <live-url>/sitemap.xml` 看内容 | (待 Round 12 验证) |

**强制流程** (Phase 3 fix commit 后, before declaring done):
```bash
# For each modified static file in public/, run live curl verify
for f in $(git diff --name-only HEAD~1 | grep -E '^public/'); do
  url="https://<live-domain>/${f#public/}"
  status=$(curl -sI "$url" | head -1 | awk '{print $2}')
  if [ "$status" != "200" ]; then
    echo "⚠️ DEPLOYED-LAYER REGRESSION: $f served as $status (expected 200)"
    echo "→ curl $url"
    echo "→ 可能根因: GH Pages user/org site 不支持 / Astro handler 拦截 / 路径没在 build output"
  fi
done
```

**已知 GH Pages 限制 (per 2026-06 官方 docs)**:
- `_headers` 文件: **仅 Project Pages site 支持** (e.g. mykcs.github.io/content2html 是 user site = 不支持). user site (`mykcs.github.io/`) 也不支持. **未来 work**: 迁移到 custom domain (Project Pages) 或换 Netlify/Vercel.
- `.well-known/` 路径: Astro 默认 404 handler 拦截. 修法 = 在 `astro.config.mjs` 加 `redirects: { '/.well-known/security.txt': '/security.txt' }` 或在 `public/security.txt` 直接放根目录 (不走 .well-known).

**反模式 (claudecode 必避)**:
- ❌ "git log shows commit, fix done" → 文件 on disk ≠ deployed, 必 curl verify
- ❌ Round 11 audit 不跑 deployed behavior → P0 regression 漏到 Round 11 才 catch
- ❌ 信任 "官方 docs 说支持 _headers" 不分 user vs project pages → GH Pages 分两类, 行为不同

**联动**: §A.5 sub-provision #2 deployed behavior check, §L19 (4 站 CI gate), §L23 (orchestrator recovery).

### ⚠️ §L26 "CI 全绿" 验收标准 (v4.0.5, user 显式要求 2026-06-29, 跟 process.md §H Acceptance Protocol 同步)

> **触发**: user 2026-06-29 原话 "把《CI 全绿》这个标准加入 skill 里面". "CI 全绿" 是 website-improve run 的最终验收标准 — 不只是 4 站 CI 状态, 是 5 字段自检表全过.
>
> **跟 §L19 区别**: §L19 是 "4 站 CI 必 success" (硬规则, 否决 done 声明); §L26 是 "CI 全绿 = 5 字段自检全过" (验收协议, 给完成报告模板). §L19 是门, §L26 是收尾.

**验收标准** ("CI 全绿" 5 字段自检表, 任何 website-improve run 末段必跑):

| # | 字段 | 验收标准 | 验证命令 |
|---|------|---------|---------|
| 1 | **path** | 4 站文件绝对路径已输出 | `ls -d ~/Claude/Projects/webs/{mysite,gdkvm,osa,content2html}` |
| 2 | **commit** | `git log -1` 4 站都有新 commit (or 显式标 "no fix needed" + 上次 commit hash) | `for s in mysite gdkvm osa content2html; do git -C ~/Claude/Projects/webs/$s log -1 --format='%h %s'; done` |
| 3 | **push** | `git log @{u}..HEAD` 4 站全空 | `for s in mysite gdkvm osa content2html; do git -C ~/Claude/Projects/webs/$s rev-list --left-right --count @{u}...HEAD; done` |
| 4 | **CI** | `gh run list` 4 站 conclusion=success | `for r in mykcs/mykcs.github.io wangrui2025/GDKVM wangrui2025/osa mykcs/content2html; do gh run list --repo $r --limit 1 --json conclusion,headSha; done` |
| 5 | **owner 隔离 + 验收证据** | 4 站 owner 正确 (mykcs/* vs wangrui2025/* 不交叉) + 1+ 行可执行命令证据 (build/test/curl/grep) | `git -C ~/Claude/Projects/webs/$s remote get-url origin` + live curl evidence |

**4 站 CI 验证模板** (per §C.3.7 硬规则, 必跑):
```bash
echo "=== Round 15 example 4 站 CI 验证 ==="
for owner_repo in "mykcs/mykcs.github.io" "wangrui2025/GDKVM" "wangrui2025/osa" "mykcs/content2html"; do
  c=$(gh run list --repo "$owner_repo" --limit 1 --json conclusion,headSha,name --jq '.[0] | "\(.conclusion) | \(.headSha[:7]) | \(.name)"' 2>/dev/null)
  echo "$owner_repo: $c"
done
# expected: 4 行全 "success | <sha> | <workflow>"
```

**Edge cases** (per §C.3.7 判定矩阵):

| 4 站 CI 状态 | 判定 | 后续动作 |
|-------------|------|---------|
| ✅ 4/4 success | **CI 全绿 ✅** | 写 case file + decision-stream + 5 字段自检 PASS |
| ❌ 1+ red | **BLOCKED on `<site> CI red: <reason>`** | 走 §D fix 路径 (auto retry) 或 AskUserQuestion (回滚 / 接受 / 重试) |
| 🟡 1+ pending | **BLOCKED on `<site> CI pending`** | 等 CI 跑完 (max 10 min, 用 `ScheduleWakeup` 重新调度) |
| 🔒 1+ 物理不可达 | **BLOCKED on `<site> 物理不可达: <reason>`** | 诚实告知 user + AskUserQuestion 重新定义 goal |

**Round 15 验证案例** (2026-06-29, 5 字段全过 example):
```
| 字段 | 验证 |
|---|---|
| path | ~/Claude/Projects/webs/{mysite,gdkvm,osa,content2html} ✅ |
| commit | ba48c24 / e238c6d / 9163395 / 580b623 ✅ |
| push | 4/4 unpushed 0/0 ✅ |
| CI | 4/4 success ✅ |
| owner | mykcs/* (mysite+content2html) + wangrui2025/* (gdkvm+osa) ✅ 0 污染 |
| live verify | 4/4 curl 200 ✅ |
→ "✅ CI 全绿" (5/5 字段)
```

**反模式** (claudecode 必避):
- ❌ "4 站 CI success = CI 全绿" → 不完整, 缺 4 字段 (path/commit/push/owner)
- ❌ 用 emoji ✅ 替代 5 字段自检表 → 违反 §H 5 字段硬规则
- ❌ "差不多完成了" / "应该 OK" → 违反 §C.1 verification gate
- ❌ 跳过 owner 隔离 verify → 违反双账号铁律 (4+ 次历史污染)
- ❌ 跳过 live curl verify → 违反 §L25 deployed-layer 协议

**联动**:
- **§L19** 4 站 CI 全绿硬规则 (门, 否决 done 声明)
- **§L25** Deployed-Layer Verify Protocol (curl 验证)
- **process.md §H** Acceptance Protocol (5 字段自检表, 同源)
- **CLAUDE.local.md §15** 4 站 CI 全绿 hot recall
- **Round 10-15 完整 6 轮 timeline** (case file `~/.claude/knowledge/cases/CASE-MULTI-SITE-FULL-AUDIT-V4-20260627.md`)

### ⚠️ §L27 3-Role Workflow (v4.0.7, 强制, 适用所有 sub-mode)

> **Source**: user 2026-07-01 原话 "修改 skill website improve 这个 skill 要有工作流，使用 Workflow 这个功能。不管是 skill 还是 workflow，要有计划者、执行者、检查验收者，这三个独立的。subagent 的，要分开。"

**架构 (3 独立 sub-agent + Workflow tool + SKILL.md 手册, 双层)**:

| 角色 | OMC agent | Model | 责任 |
|------|-----------|-------|------|
| **planner** | oh-my-claudecode:planner | Opus | §L21 pre-flight + 4 站 scan plan + 风险决策 + 写 plan.json |
| **executor** | oh-my-claudecode:executor | Opus | git apply + smart-push.sh + decision-stream + 写 exec-log.json |
| **verifier** | oh-my-claudecode:verifier | Opus | 4 站 CI curl + 5 字段自检 + PASS/FAIL verdict + reject → executor 重做 |

**3 sub-agent 独立硬规则 (claudecode 必背)**:

1. 3 sub-agent 互相**不共享 context window**（灵魂 v4 黑话: "3 个师傅互相看不到对方工作笔记"）
2. handoff 唯一通道 = JSON artifact 文件（planner → plan.json → executor，executor → exec-log.json → verifier，verifier → verdict.json → executor 重做或 done）
3. **verifier PASS 才算 done** — executor 不能自己标 done（per §A.6 升级）
4. **verifier reject → executor 重做整轮**（user 2026-07-01 选 A 失败 1 次 reject 整轮）
5. 3 sub-agent 各自跑 Phase 0 ToolSearch（§L22 保留）
6. 任一 sub-agent stall → 触发 §L23 Orchestrator Recovery + §L24 Heartbeat Check（保留）

**JSON artifact schema 必跑**（per plan / exec-log / verdict 各自 schema）:

```bash
# planner → plan.json (per ~/.claude/scripts/website-improve/plan_json_gen.py)
python3 ~/.claude/scripts/website-improve/plan_json_gen.py \
  --audit-target "<本次目标>" \
  --sub-modes "A,B,D" \
  --sites "GDKVM,OSA,mykcs,content2html" \
  --expected-wall-clock 45 \
  --completion "4 站 CI green,5 字段自检全过,decision-stream 全 append,case file 沉淀" \
  --pre-flight "<7 段 pre-flight 声明>" \
  --out plan.json

# executor → exec-log.json (per exec_log_gen.py)
python3 ~/.claude/scripts/website-improve/exec_log_gen.py \
  --plan plan.json \
  --files-changed "<path:N:M,path:N:M>" \
  --git-commits "<site:sha:msg,site:sha:msg>" \
  --smart-push "<status:site,status:site>" \
  --decision-stream-file "<JSON 数组 file>" \
  --out exec-log.json

# verifier → verdict.json (per verdict_json_gen.py)
python3 ~/.claude/scripts/website-improve/verdict_json_gen.py \
  --verdict PASS \
  --ci-gdkvm green --ci-mykcs green --ci-osa green --ci-content2html green \
  --sc-path PASS --sc-commit PASS --sc-push PASS --sc-ci PASS --sc-owner PASS \
  --dl-gdkvm PASS --dl-mykcs PASS --dl-osa PASS --dl-content2html PASS \
  --out verdict.json
```

**§L21 Pre-flight 默认反转 (PR #6 兼容)**:

- planner 输 7 段 pre-flight（audit trail）→ **直接进 executor**（不 user 等 OK，per v4.0.6 §L21 默认反转模式 + PR #6 merged commit f702ba8）
- 跟 PR #6 v4.0.6 §L21 默认反转模式 100% 兼容

**§L19/L25/L26 verifier 必跑**:

- **§L19**: 4 站 CI（mykcs/GDKVM/OSA/content2html）任一 red → verifier reject 整轮
- **§L25**: 4 站 curl live URL（不只 source grep）
- **§L26**: 5 字段自检表（path / commit / push / CI / owner 隔离 + 验收证据, per process.md §H Acceptance Protocol）

**e2e test 必跑 (跟 §C.5 验证门 + §D Bonus Test 协同)**:

```bash
# 10 case 端到端测试: 6 PASS + 4 FAIL 验证 schemas.py + 3 gen 脚本不退化
PATH=$HOME/.claude/scripts/website-improve/.venv/bin:$PATH \
  bash ~/.claude/scripts/website-improve/test_3role_e2e.sh
# 期望: PASS: 10 / FAIL: 0, rc=0
```

**触发式决策**:

- IF user 触发 website-improve → orchestrator 必 spawn 3 sub-agent（planner → executor → verifier），**不允许单 sub-agent 跑**
- IF 任一 sub-agent stall → §L23 Recovery（保留）
- IF verifier FAIL → executor 重做整轮（user 2026-07-01 选 A）
- IF verifier FAIL 2 次 → AskUserQuestion 拍板（no-stuck §C.3.6.1）
- IF 3 role workflow 跟 PR #6 §L21 默认反转冲突 → 以 PR #6 为准（默认反转优先，PR #6 merged commit f702ba8）

**反模式 (新立, v4.0.7)**:

- ❌ 1 个 sub-agent 自己跑完 3 角色工作（违反"独立"原则，user 原话 "subagent 的, 要分开"）
- ❌ executor 自己标 done（绕过 verifier, 违反 §A.6 升级）
- ❌ verifier FAIL 还强行 ship（违反 §L19 4 站 CI gate）
- ❌ sub-agent 之间口头传话不走 JSON artifact（违反 handoff 硬规则）
- ❌ 跳过 §L22 ToolSearch 让 sub-agent 0 tool uses（违反 §L22）
- ❌ verifier FAIL → executor 不重做（违反 user 选 A 失败 1 次 reject 整轮）
- ❌ plan.json / exec-log.json / verdict.json 写完不校验（fail-fast 缺失, jsonschema strict 校验立竿见影抓 case-sensitive bug）

**联动**:

- **§A.6 Verifier Self-Test Protocol**（v3.10.0 强制）— 升级为独立 verifier sub-agent（3 角色第 3 个）
- **§A.5 Multi-Round Audit Protocol**（v3.9.0 强制）— 每次 round 都跑 1 次完整 3-role（planner → executor → verifier）
- **§A.7 Template Consistency Check**（v3.10.0 强制）— 跟 3-role 协同不替换
- **§L19** 4 站 CI 全绿硬规则 — verifier 必跑
- **§L20** fix-validate-build — executor 改 package.json 后必 npm install + 二次 build
- **§L21** Pre-flight Declaration（v4.0.6 默认反转, PR #6 merged）— planner 输 7 段 pre-flight 兼容
- **§L22** Subagent Tool Provisioning（v4.0.4 治本 subagent stall）— 3 sub-agent 各自跑 Phase 0 ToolSearch
- **§L23** Orchestrator Recovery SOP（v4.0.4 治标 subagent stall）— 任一 sub-agent stall 触发
- **§L24** Stall Heartbeat Check（v4.0.4 subagent 静默检测）— 3 sub-agent 都受 5min heartbeat
- **§L25** Deployed-Layer Verify Protocol（v4.0.4 Round 11 P0/P1 regression 治本）— verifier 必跑 4 站 curl
- **§L26** CI 全绿验收标准（v4.0.5, per process.md §H Acceptance Protocol）— verifier 5 字段自检表
- **process.md §C.5** false completion — 任何 3-role run 必跑完所有阶段才能声明 done
- **process.md §C.3.6.1** no-stuck — 失败任一环立即 STOP + 降级或 AskUserQuestion
- **process.md §H** Acceptance Protocol — verifier self_check_5_fields 字段直接对应
- **CLAUDE.local.md §15** 4 站 CI 全绿 hot recall — verifier 必跑
- **CLAUDE.local.md §11.2** v2.6.57 banner UX 协同 (跟 PR #6 §L21 默认反转 UX 一致)
- **calm-flow.md §5** 卡片墙 — 3-role 决策摘要
- **post-task-recommend.md v0.2** 灵魂 v6 协议 — claudecode 顺手做的必自决（v0.2 永久失效反模式）
- **decision-stream/2026-07-01-website-improve-3role-design.md**（本 session design 草稿）
- **decision-stream/2026-07-01-website-improve-pr6-merge-rebase.md**（PR #6 merge 决策）
- **CASE-WEBSITE-IMPROVE-3ROLE-WORKFLOW-20260701**（立, 跟本段联动）
- **CASE-POST-TASK-RECOMMEND-20260701**（灵魂 v6 v0.2 协议联动）
- **CASE-SOUL-V6-4-VIOLATIONS-20260701**（4 类违反修复, 跟 §L27 反模式清单同源）
- **CASE-RICH-AUDIT-V2-6-59-TRIPLE-SUB-AGENT-20260701**（rich-audit v2.6.59 三段 sub-agent 协议位, 跟 §L27 3 角色架构同源）

**案例沉淀**:

- CASE-WEBSITE-IMPROVE-3ROLE-WORKFLOW-20260701 (立, 跟本段协同)
- CASE-POST-TASK-RECOMMEND-20260701 (灵魂 v6 v0.2 协议联动)
- CASE-SOUL-V6-4-VIOLATIONS-20260701 (4 类违反修复, 跟 §L27 反模式清单同源)
- CASE-RICH-AUDIT-V2-6-59-TRIPLE-SUB-AGENT-20260701 (rich-audit v2.6.59 三段 sub-agent 协议位, 跟 §L27 3 角色架构同源)

**Ref**:
- ~/.agents/skills/website-improve/SKILL.md (本文件)
- ~/.claude/decision-stream/2026-07-01-website-improve-3role-design.md
- ~/.claude/scripts/website-improve/README.md
- ~/.claude/rules/post-task-recommend.md v0.2
- ~/.claude/rules/process.md §C.3.6 §H §C.5
- ~/.claude/CLAUDE.local.md §15 §11.2 §12

---

📂 **模式 A: 检查+提升流程** → see [`references/mode-a.md`](references/mode-a.md) (loaded on demand)

---

📂 **模式 A: 检查+提升流程** → see [`references/mode-a.md`](references/mode-a.md) (loaded on demand)

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
   - **§L19 4 站全绿硬规则 (v4.0.1)**: 4 active sites (mykcs/GDKVM/OSA/content2html) 任一站 CI red → 禁止声明 done, 必走 BLOCKED + fix 路径. 详见 §L19.
   - **§L20 Fix-Validate-Build (v4.0.1)**: 改 `package.json` 后必跑 `npm install` 重 lockfile + `npm run build` 验证. 详见 §L20.
   - **§L21 Pre-flight Declaration (v4.0.2)**: 每次 run 启动时必输 7 段 pre-flight declaration, 等用户回 OK 才进 Phase 1. 详见 §L21.
10. **GitHub Actions Node.js 弃用**：遇到 Node 20 deprecated 警告 → 按 `scan-checklist.md §10` 矩阵升级 action 版本
11. **DESIGN.md 与代码同步**：修改了 CSS 类名/颜色/组件行为时，必须检查 DESIGN.md 是否需要同步更新
12. **Evidence-based audit**：审计发现必须基于实际 grep / curl / diff / build 输出。禁止 "verify X" 推测（仅列待查项不算 finding）。Stale finding 比 missing finding 更危险 — 会触发不必要的 commit + CI 浪费。Pattern: Phase 2 audit agent 必须跑 actual verification command；Phase 3 fix agent 必须先 verify 是 real 才 commit。Reference: 2026-06-04 sync-all-sites Run 2 GDKVM 教训（audit 列 8 个 "verify X"，fix agent 全 grep 验证后 0 commit）
13. **Multi-Round Audit (v3.9.0, 强制)**: 每次 audit 必跑 §A.5 Protocol 4 sub-provisions (snapshot diff / deferred re-eval / deployed curl / registry override). 单 audit run 不能保证找全 bug. Reference: CASE-WEBSITE-IMPROVE-INCREMENTAL-AUDIT-20260622.

---

## 跨站点依赖同步升级 / 触类旁通三层扫描协议 / 学术资产库化

> 3 个次级协议已下沉到 [`references/site-improvement-protocols.md`](references/site-improvement-protocols.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。

---

## 模式 B: Astro 建站指南

**加载**: `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md`

覆盖：项目初始化、Tailwind CSS v4 集成、Content Collections 配置、i18n 路由、部署平台配置

---

## 模式 C: 项目页创建

**加载**: `project-page-template.astro` + `academic-project-checklist.md`

为论文创建双语项目展示页（如 `/osa/`、`gdkvm/`）。

**Stack**: Astro 6.x + Tailwind CSS v4 + `@fontsource/*` + `oklch()` 色彩
**URL 结构**: `/<project>/` → redirect → `/<project>/en/` + `/<project>/zh/`
**标准区块**: Hero → Abstract → Motivation → Method → Results → BibTeX → Links

---


📂 **模式 D: Multi-Site 编排 (2026-06-08 吞并自 sync-all-sites v1.1.0)** → see [`references/mode-d-multisite.md`](references/mode-d-multisite.md) (loaded on demand)

## Sites
- mykcs.github.io: score=98, fixes=0 (Round 2 P1/P2 已 ship), ci=green ✅
- GDKVM: score=~96, fixes=2 (Round 3 P1 + P2), ci=green ✅ (commit 72294b3)
- OSA:   score=98, fixes=0 (Round 2 P1/P2 已 ship), ci=green ✅
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
- **全量 auto-apply（旧）**: 把 P2 也一起 fix → 已升级为正式规则，不再视为 scope creep
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

---

## Skill Evolution History (v3.6.0 + 历次)

> 完整 Skill Evolution 历史（§0 / §12-§22 2026-06-02 三仓审计 / §23-§29 v3.2.0 / §30-§32 v3.3.0 / §33-§35 v3.6.0）已下沉到 [`references/evolution-history.md`](references/evolution-history.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。
>
> **§33 ASI 防御 / §34 Autopush Fallback / §35 Fix-Agent Cleanup** 是 orchestrator/fix-agent 必经节点的硬规则，所有多站点 fan-out 必查。

---


## 跨 § 引用 / 验证清单 / Case 引用

> 3 节已下沉到 [`references/validation-checklist.md`](references/validation-checklist.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。