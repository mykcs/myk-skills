---
name: website-improve
description: |
  一站式网站改进 skill。覆盖 4 大场景：
  - Mode A: 检查+提升 (默认, 所有"改进/审计/优化/检查/upgrade/modernize/重构/cleanup"类请求)
  - Mode B: Astro 建站 ("create astro" / "deploy astro" / "build static blog")
  - Mode C: 项目页创建 ("project page" / "项目页")
  - Mode D: Multi-Site 编排 (2026-06-08 吞并 sync-all-sites; "sync all sites" / "fan-out N sites" / "deploy all" / "audit all" / "multi-site")
  这是网站相关工作的唯一入口，替代 site-modernizer、publishing-astro-websites、sync-all-sites 等分散 skill。
license: MIT
metadata:
  version: "3.7.0"
  author: mykcs
  category: web-development
  changelog:
    - 3.7.0 (2026-06-10): Progressive disclosure refactor (per Anthropic SKILL.md best practices). 861 → 487 行 (-43%). Skill Evolution 历史 307 行 → references/evolution-history.md; 跨站点/触类旁通/学术资产化 34 行 → references/site-improvement-protocols.md; triggers 长尾 36 行 → references/triggers.md. 满足 Anthropic 500-line hard limit + AEM 200-line reliability sweet spot.
    - 3.6.0 (2026-06-09): §33-§35 orchestrator + fix-agent 硬化. H1 ASI 防御 (Workflow 脚本 `SITES.map(...)\n({...})` ASI 解析 bug → TypeError recovery) / H2 autopush fallback (autopush 误判 staged-only deletion → direct `git push` 兜底) / H3 fix agent 二次 `git status` 验证 (避免 dangling untracked-deletion). 来自 CASE-MULTI-SITE-IMPROVE-20260609.
    - 3.5.0 (2026-06-08): L17+L18 orchestrator 硬化. Phase 0 工具预加载 (ToolSearch 治本 subagent tool loading bug) + L17 auto-fallback (agent ack → SendMessage 重发 JSON). 解决 Run 4 暴露的 L14 enforcement 2/3 success + GDKVM 0 tool uses 2 个 bug.
    - 3.4.0 (2026-06-08): 吞并 sync-all-sites as Mode D (multi-site 编排). 4-phase 协议 + L14 + 4-section output contract. sync-all-sites 目录删除.
    - 3.3.0 (2026-06-03): 自进化协议 + 反模式硬化 (§30-§32)
    - 3.2.0 (2026-06-03): 3 站 Mode A 跨站 bug 模式 (§23-§29)
  triggers:
    # 核心入口 (8 个, 必查)
    - website-improve
    - 改进网站
    - 优化网站
    - audit website
    - 网站审计
    - site health
    - project page
    - 项目页
    # Astro 模式 (4 个)
    - create astro site
    - deploy astro to firebase
    - build static blog
    - astro markdown setup
    # Multi-Site 模式 (6 个)
    - sync all sites
    - fan-out
    - deploy all
    - audit all
    - multi-site
    - 多站点
    # 改进/重构 (6 个)
    - upgrade
    - 重构
    - cleanup
    - 反模式扫描
    - build fix
    - fix build
    # 完整列表见 references/triggers.md (24 个长尾触发器, v3.7.0 拆分)
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
| **D. Multi-Site 编排** | `sync all sites` / `fan-out` / `deploy all` / `audit all` / `multi-site` / "同时在 N 个站点上部署 N 个 agent" | 10-20 min wall-clock (= slowest site) | (无额外 reference; 调用 Mode A per site) |

### 意图路由（入口判断）

```
用户输入
  │
  ├─ 包含 "sync all sites" / "fan-out" / "deploy all" / "audit all" / "multi-site" / "并行部署 N 个 agent" / "3 个独立审计" → 模式 D
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
12. **Evidence-based audit**：审计发现必须基于实际 grep / curl / diff / build 输出。禁止 "verify X" 推测（仅列待查项不算 finding）。Stale finding 比 missing finding 更危险 — 会触发不必要的 commit + CI 浪费。Pattern: Phase 2 audit agent 必须跑 actual verification command；Phase 3 fix agent 必须先 verify 是 real 才 commit。Reference: 2026-06-04 sync-all-sites Run 2 GDKVM 教训（audit 列 8 个 "verify X"，fix agent 全 grep 验证后 0 commit）

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

为论文创建双语项目展示页（如 `/osa/`、`/gdkvm/`）。

**Stack**: Astro 6.x + Tailwind CSS v4 + `@fontsource/*` + `oklch()` 色彩
**URL 结构**: `/<project>/` → redirect → `/<project>/en/` + `/<project>/zh/`
**标准区块**: Hero → Abstract → Motivation → Method → Results → BibTeX → Links

---

## 模式 D: Multi-Site 编排 (2026-06-08 吞并自 sync-all-sites v1.1.0)

> **适用**：mykcs.github.io / GDKVM / OSA / Academic / wangrui2025(arch) 等 Astro 站点
> **来源**：insights 2026-06-03 — 用户 5-9 parallel agent runs 显著提升 session 完成度
> **吞并决策**：2026-06-08 (CASE-MERGE-SYNC-ALL-SITES-20260608) — 减少 skill 分散, 单一入口更易调用

**适用场景**: 用户要求"在 N 个站点上同时部署 N 个 agent"/"sync all sites"/"fan-out"/"deploy all"。Wall-clock = 最慢站点时长, 通常 10-15 min for 3 sites。

**与 Mode A 关系**: 每个 per-site agent 内部用 Mode A 协议 (Check → Fix → Improve → Verify)。Mode D 是 multi-site 编排层, 负责 4-phase 同步 (验仓/audit/fix/CI)。

### 触发

```bash
# 直接说触发词即可
"sync all sites" / "fan-out 3 sites" / "audit all" / "deploy all" / "multi-site"
"同时在 N 个站点部署 N 个 agent" / "并行 audit" / "3 个独立审计会话变成一次协调操作"
```

默认 scope: `mykcs, GDKVM, OSA` (3 个 active Astro 站). User 可 override scope 指定 sites.

### 4 阶段协议

#### Phase 0: 工具预加载 (L18 硬化, 2026-06-08 Run 4 验证 — 治本 subagent tool loading bug)

> **Run 4 发现**: GDKVM agent 0 tool uses. 错误信息: "SubagentStart hook did not provide working tools to begin audit. Deferred tool schemas (WebFetch, WebSearch, etc.) require ToolSearch loading before use." mykcs + OSA 同时跑 66 + 44 tool uses, 正常. 根因: General-purpose subagent tool provisioning 偶尔失败 (SubagentStart hook 漏 inject 某些 tool schema).

**强制流程** (orchestrator 在 Phase 1 之前必须跑):

```bash
# 1. 显式 load 基础 5 tool (确保 subagent 拿到 schemas)
ToolSearch(query="select:Bash,Read,Edit,Grep,Glob")
```

**为什么**: SubagentStart hook 偶尔漏 inject tool schemas. 预加载是治本方案 — 显式 load 后所有后续 subagent 都能拿到基础 5 tool.

**注意**: 仍可能有其他 deferred tool (WebFetch / WebSearch / LSP / mcp_*) 需 on-demand load. Phase 2 agent prompt 需明确 "如需 WebFetch, 用前先 ToolSearch load".

#### Phase 1: 验仓 (必须先做, 不能跳过)

```bash
# 对每个目标站点：
for site in $SITES; do
  case "$site" in
    mykcs)   repo=~/Repo/webs/active/mykcs.github.io ;;
    GDKVM)   repo=~/Repo/webs/active/GDKVM ;;
    OSA)     repo=~/Repo/webs/active/OSA ;;
    *)       echo "Unknown site: $site"; exit 1 ;;
  esac
  cd "$repo" || exit 1
  echo "=== $site ==="
  git remote -v
  git status --short
  git log @{u}..HEAD --oneline | wc -l
done
```

**abort 条件**:
- 任何站点 `git status` 非空 (uncommitted changes) → 提示用户提交
- 任何站点 `git log HEAD..origin/main` 有新 commit → 提示 `git pull --rebase`

#### Phase 2: 并行 audit (N agent, N = site count)

```text
For each site, launch 1 Agent with this prompt:

You are auditing <SITE_REPO> for SEO/accessibility/i18n/CI/build issues.

**EVIDENCE-BASED AUDIT (强制)**:
每个 issue 必须给出 grep/curl/ls 的实际命令输出, **禁止报"verify X" / "check Y" / "should audit Z"**。
- ❌ BAD: {"fix": "verify if Google Sans is configured"}
- ✅ GOOD: {"fix": "Google Sans fallback — global.css:7 'was Google Sans' comment", "evidence": "grep -n 'Google_Sans\\|Google Sans' src/ 2>/dev/null | head -5"}

**DEAD-CODE PROOF 协议**:
- 报"dead i18n key"前必须 `grep -rn '<key>' src/` 显示 0 matches
- 报"unused font"前必须 `grep -rn 'fontfile' src/ --include="*.astro"` 显示 0 imports
- 报"unused file"前必须 `grep -rn 'filename' src/` 显示 0 references
- **找不到 = 不存在, 不算 dead**

**L14 FINAL MESSAGE PROTOCOL (mandatory, orchestrator 会 grep 验证 JSON 合法性)**:
- 你的 final message MUST 是 EXACTLY 一个 JSON block matching 上面的 schema
- Wrap in ` ```json ... ``` ` 三反引号
- NO prose / NO "Task complete" / NO acknowledgments / NO preamble / NO postamble
- 任何非 JSON 内容 (含 ack / 解释 / "Subagent acknowledged" / "Acknowledged") → orchestrator 拒收, 整个 run 失败, Phase 2/3 需重做
- 验证方式: orchestrator 评分前会 `grep -q '"site":' <output>` + `python3 -c "import json; json.loads(...)"` 双层 check

Output JSON schema:
{
  "site": "<name>",
  "score": 0-100,
  "issues": [
    {"severity": "P0|P1|P2", "type": "seo|a11y|i18n|build|ci|security", "file": "path", "fix": "concrete action", "evidence": "grep/curl/ls output snippet"}
  ]
}

**No `deferred` field** — 报出来就是要 fix 的, 看不到 grep 证据的不报。

Use the website-improve skill (Mode A) for the audit protocol.
Do NOT make any edits — read-only mode.
Report back as a single JSON block.
```

**barrier**: 等所有 agent 返回后聚合。

#### Phase 3: 并行 fix (仅 P0 + P1)

```text
Filter issues by severity ∈ {P0, P1}.
Group by site. Launch 1 Agent per site with this prompt:

Apply the following fixes to <SITE_REPO>:
<issue list>

For each fix:
1. Show the diff
2. Run the relevant build/test command
3. Commit with conventional commit message
4. Push via autopush.sh (not raw git push)

Do NOT touch issues not in this list. (scope discipline)
Do NOT mark done until build passes.

**L14 FINAL MESSAGE PROTOCOL (mandatory)**:
- 你的 final message MUST 是 EXACTLY 一个 JSON block:
{
  "site": "<name>",
  "p0_fixed": <count>,
  "p1_fixed": <count>,
  "p2_deferred": <count>,
  "commits": ["<hash1>: <msg1>", "<hash2>: <msg2>"],
  "ci_status": "green|red|pending|unknown",
  "evidence_blocking": "<reason if not all P0/P1 fixed, else empty>"
}
- Wrap in ` ```json ... ``` ` 三反引号
- NO prose / NO "Task complete" / NO acknowledgments / NO preamble / NO postamble
- 任何非 JSON 内容 → orchestrator 拒收
- 验证方式同 Phase 2 (grep + python3 json.loads)
```

**barrier**: 所有 agent 返回后聚合。

#### Phase 4: CI gate + case 记录

```bash
# Wait for all CI runs to settle
for site in $SITES; do
  echo "=== $site CI ==="
  gh run list --repo <OWNER>/<REPO> --limit 3 --json status,conclusion,name
done
```

**Case file** (强制):
```bash
CASE_PATH=~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-$(date +%Y%m%d).md
```

### L17 Orchestrator Fallback (Agent ack → 自动 follow-up, 2026-06-08 Run 4 验证)

> **Run 4 发现**: L14 enforcement 2/3 success. 即便 prompt 顶部硬性要求 JSON, 仍有 ~33% agent 返 plain text ack (e.g. OSA "OSA Run 4 audit complete."). L14 内化非 100% 有效.

**强制流程** (orchestrator 在收到 agent final message 后, Phase 2/3 barrier 之前):

1. **验证 L14 compliance**:
   ```bash
   # 双层 check: JSON 存在 + 合法
   grep -q '"site":' <agent_output> && \
   python3 -c "import json; json.loads(<agent_output_with_fences>)"
   ```
2. **L14 失败时**: 自动 `SendMessage(to=<agent_id>, message="L14 violation detected. Please resend your final message as a single JSON block matching the schema, wrapped in \`\`\`json fences. NO other text. NO acknowledgments.")` 一次
3. **二次失败**: 不再 retry, 改用 `git log + gh run list` 重建证据链 (Run 3 fallback 模式). 在 evidence_blocking 字段标注 `"L17 fallback applied: agent returned plain text after 1 retry"`.

**为什么**: L14 prompt 内化非 100% 有效. Orchestrator 端兜底是必要的. 与 Run 3 mykcs agent 行为同款 (那次也用 SendMessage 救场). **不要让 plain-text 失败导致整 run 失败** — 用 fallback 重建即可.

### Output contract (strict 4-section)

```markdown
# sync-all-sites report

## Sites
- mykcs: score=98, fixes=3, ci=green ✅
- GDKVM: score=87, fixes=12, ci=green ✅
- OSA:   score=92, fixes=5, ci=green ✅

## Total commits
N

## Case file
~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-YYYYMMDD.md
```

**禁用的输出段** (2026-06-05 规则硬化):
- ❌ `## Deferred items (next run)` 列表
- ❌ `## P2 (out of scope this run)` 段落
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
- **全量 auto-apply**: 把 P2 也一起 fix → scope creep
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
- L14 enforcement 仅在 orchestrator 评分前生效, 旁路 agent (不用本协议) 不受约束

---

## Skill Evolution History (v3.6.0 + 历次)

> 完整 Skill Evolution 历史（§0 / §12-§22 2026-06-02 三仓审计 / §23-§29 v3.2.0 / §30-§32 v3.3.0 / §33-§35 v3.6.0）已下沉到 [`references/evolution-history.md`](references/evolution-history.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。
>
> **§33 ASI 防御 / §34 Autopush Fallback / §35 Fix-Agent Cleanup** 是 orchestrator/fix-agent 必经节点的硬规则，所有多站点 fan-out 必查。

---


## 跨 § 引用 / 验证清单 / Case 引用

> 3 节已下沉到 [`references/validation-checklist.md`](references/validation-checklist.md) (v3.7.0 progressive disclosure refactor, 2026-06-10)。按需加载。
