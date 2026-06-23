---
name: rich-audit
description: |
  三层进化系统：审计（发现问题）→ 修复（解决问题）→ 进化（主动获取外部先进知识并应用）。
  双模审计：Claude Code 配置审计 + Python/ML 项目审计。
  触发词：rich审计, /rich-audit, 进化
license: MIT
metadata:
  version: "2.6.19"
  author: mykcs
  category: self-evolution
  changelog:
    - "2.6.19 (2026-06-23): Layer 0 Verification Gate Pre-check (新 §A.1, 5 commands 必跑). 解决 top friction cluster 'Audit 跑完口头报 ✅ 已 push 无 ground truth' (CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621, 2026-06-21). Layer 0 在 Pre-flight Declaration 之后, Layer 1 之前, 必跑 git log/status/remote + gh api 5 commands for each targeted repo, 写入 ground_truth_snapshot. 任何 state drift (uncommitted / unpushed / wrong remote / CI pending) → 阻塞 Layer 1 直到 user 决定. Anti-pattern: 把 verification gate 当 post-check (跑完才看) → 永远晚一步. Skill-evolution auto-derived 2026-06-23."
  triggers:
    - rich审计
    - /rich-audit
    - rich audit
    - claude 审计
    - audit claude files
    - 进化
    - 自我升级
  tags:
    - audit
    - evolve
    - self-improvement
    - claude-code
    - omc
    - knowledge
    - benchmark
    - python
    - ml
    - pytorch
user-invocable: true
---

# rich-audit Skill

## 触发方式

- **中文**: `rich审计`
- **英文**: `/rich-audit`
- **别名**: `rich audit`, `claude 审计`, `audit claude files`

---

## 零确认协议（Zero-Confirmation Protocol）[强制 · 不可绕过 · 2026-06-05 固化]

> **核心规则**：rich-audit 触发后，**禁止**任何形式的用户确认（AskUserQuestion / 等待输入 / 等待 "y" / 等待 "go"）。
> 全部三层流水线（审计 + 修复 + 进化）默认直接执行；用户从触发词到执行无任何中间确认。

**默认行为（不可变）**：

| 维度 | 默认值 | 触发后行为 |
|------|--------|----------|
| 深度 | 完整三层（Layer 1 审计 + Layer 2 修复 + Layer 3 进化） | 不询问，自动跑完 |
| 模式 | 双模（配置审计 A + Python/ML 审计 B） | 不询问，并行启动 |
| 范围 | `~/.claude/` + `~/.agents/skills/` + mem0 对齐 | 不询问，全范围 |
| 修复 | 安全可论证的修复自动应用 | 不询问，幂等执行 |
| 备份 | 自动备份到 `~/.claude/backups/rich-audit-*/` | 不询问，先备份后修 |
| 报告 | 五段式进化报告 | 不询问，跑完输出 |

**反例（禁止 · 出现即视为违反本协议）**：

```text
❌ "是否要执行 rich-audit？（是/否）"
❌ "选择模式：A. Claude Code 配置 / B. Python/ML"
❌ "选择深度：1. 完整三层 / 2. 只审计不修 / 3. 审计+修复"
❌ "确认要修复 N 个问题吗？"
❌ "目标范围是？项目 A / B / C？"
❌ 任何 AskUserQuestion 触发的 rich-audit 预确认
```

**唯一允许的"决策点"**：

| 时机 | 形式 | 备注 |
|------|------|------|
| 报告末尾 | PENDING 进化项让用户决定 | 不是预确认，是事后决策 |
| 报告中段 | 检测到 P0 高危修复时输出"⚠️ P0 风险点"提示 | 仅展示，不阻塞 |
| 修复后 | Verification Gates 失败时暂停 | 硬性失败，非询问 |

**Why**（背景）：
- 用户触发词（`rich审计` / `/rich-audit` / `进化`）本身已是明确意图信号
- OMC 摩擦数据：misunderstood_request 32 次 / wrong_approach 31 次，多与反复确认相关
- rich-audit 的所有修复都是幂等的（见 §自动修复行为），失败可回滚
- Verification Gates (10 项) 是物理安全边界，事后验证强于事前确认
- 用户反馈（2026-06-05）："修改 skill 以后不要问我"

**生效范围**：本协议覆盖 §预声明、§执行流程、§自动修复行为 三个章节。任何与之冲突的旧表述以本协议为准。

---

## 预声明（Pre-flight Declaration）[强制]

> **触发时机**：用户说出触发词（`rich审计` / `/rich-audit` / `进化` 等）后，**立即**输出本段，**再**进入 Layer 1 审计。
>
> **Why**: 防止审计跑偏到错误范围（例如误以为是"全机器扫描"），并向用户明示"我接下来要做什么"。同时与 OMC 协议中"先告诉用户再动手"的原则对齐。

**固定输出格式**（中文，大声、明确、不可省略）：

```
═══════════════════════════════════════════════════════════
🚀 rich-audit 启动 — 预声明（Pre-flight Declaration）
═══════════════════════════════════════════════════════════

📌 审计目标（What I will audit）：
  ├─ [Layer 1 — 审计层]
  │   ├─ 模式 A（默认）：Claude Code 配置审计
  │   │   ├─ 规则系统：~/.claude/rules/
  │   │   ├─ 记忆系统：~/.claude/memory/
  │   │   ├─ 案例库：  ~/.claude/knowledge/cases/wiki/
  │   │   ├─ Hooks:   ~/.claude/hooks/
  │   │   ├─ 脚本:    ~/.claude/scripts/
  │   │   ├─ Skills:  ~/.claude/skills/ + ~/.agents/skills/
  │   │   └─ 配置:    ~/.claude/settings.json
  │   └─ 模式 B（条件触发）：Python/ML 项目审计
  │       └─ 仅当工作区含 pyproject.toml / requirements.txt
  ├─ [Layer 2 — 修复层] 基于 Layer 1 汇总结果执行安全可论证的修复
  └─ [Layer 3 — 进化层] 外部知识扫描（WebSearch + Context7）—— 永不可跳过

📂 目标文件夹（Target folders）：
  ├─ 主审计范围：~/.claude/  （独立配置仓库，default scope）
  ├─ 关联范围 1：~/.agents/skills/  （skill 源，需与 ~/.claude/skills 保持 symlink 一致）
  ├─ 关联范围 2：mem0 云端记忆  （双轨同步检测的 L3 来源）
  └─ 条件范围  ：当前工作区 Python 项目  （仅 Layer 1 模式 B 触发时审计）

⏱️ 预期耗时：60-180 秒（取决于 Agent 并行度 + WebSearch 响应速度）
🎯 完成标准：五段式进化报告 + 前后健康分 + 10 项 Verification Gates 全部通过

═══════════════════════════════════════════════════════════
              预声明结束 — 正式审计即将开始
═══════════════════════════════════════════════════════════
```

**特殊情况处理**：

| 场景 | 预声明补充内容 |
|------|----------------|
| 用户未指定工作区，但当前 cwd 在 `~/Repo/xxx` 下且有 Python 项目 | 在 "条件范围" 一行追加：当前 cwd = `$(pwd)` |
| 用户明确指定了"只审计 X" | 将"目标文件夹"章节替换为用户指定的 X，其他保持默认 |
| 用户说"全面审计" / "深度审计" | 在 "Layer 3 进化层" 标注 `深度模式：3-tool cascade (minimax → kimi-webbridge → anysearch) + 2 次 Context7` |
| mem0 MCP 不可用 | 在 "关联范围 2" 后追加警告：`⚠️ mem0 MCP 不可用，L3 记忆对齐将降级为 L1/L2 双轨` |

**反例（禁止）**：

```text
❌ 直接开始扫描 ~/.claude/rules/ 而无任何说明
❌ "我将审计你的 Claude Code 配置..."  ← 太口语、缺格式
❌ 只说"开始审计"  ← 完全没告知范围
```

---

## §A.1 Layer 0: Verification Gate Pre-check (v2.6.19, 强制 · 不可跳过)

> **Why**: rich-audit 跑完口头报 "✅ 已 push" / "审计完成" 是典型 form violation (CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621, 2026-06-21). Verification Gate 只能事后验证 ground truth, 不能事后编造. Layer 0 把 ground-truth 收集**前置**到 Pre-flight Declaration 之后, Layer 1 之前 — 任何 state drift 在 audit 启动前显式可见.
>
> **Trigger**: rich-audit 任何触发 (含 `rich审计` / `/rich-audit` / `进化` / `rich audit` / `自我升级` / `claude 审计` / `audit claude files`).
>
> **违反硬规则**: 跳过 Layer 0 直接进 Layer 1 = 等同把 verification gate 延后到 "✅ 已 push" 之后 = CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 重现.

### Layer 0 必跑 5 commands (per targeted repo)

**Pre-flight Declaration 输出目标文件夹后, 立即对每个 git repo 跑:**

```bash
# 1. Commit 真存在 (过去 1 周至少 1 commit)
git log --oneline -1

# 2. 5 commits 连续性 (sanity check: 是真仓, 不是空仓)
git log --oneline -5 | head -5

# 3. 0 uncommitted (避免 audit 期间被中断污染)
git status --short

# 4. Remote 对 (双账号隔离铁律: wangrui2025/* 禁止 push 到 mykcs)
git remote -v | head -2

# 5. CI 状态 (针对 active project repo, e.g. mykcs.github.io)
gh api repos/<owner>/<repo>/commits/HEAD/status 2>/dev/null | jq -r '.state // "NO_CI"'
```

### Layer 0 输出契约 (4 字段 per repo, 必填)

```text
╭─────────────────────────────────────────────────────────╮
│  Layer 0 Ground Truth Snapshot — <repo>                 │
│  path: <absolute-path>                                  │
│  remote: <owner>/<repo>                                │
│  1. head:   <hash> | <subject>                          │
│  2. recent: [<hash1>, <hash2>, ...]                     │
│  3. status: <clean | N uncommitted>                     │
│  4. remote_url: <url>                                  │
│  5. ci_state: <success | pending | failure | NO_CI>     │
╰─────────────────────────────────────────────────────────╯
```

**如果任何字段触发以下条件 → 阻塞 Layer 1, AskUserQuestion 询问 user**:

| 条件 | 含义 | 询问 |
|------|------|------|
| `head` empty | 仓为空 / 未初始化 | "此仓未初始化, audit 跳过?" |
| `status` ≥ 1 uncommitted | 改动未 commit | "有 uncommitted 改动, 先 commit 还是 audit 时忽略?" |
| `remote` 错 | 双账号污染 / wrong owner | "remote 是 X, 期望 Y, 切换?" |
| `ci_state` = failure | CI red | "CI 失败, audit 仍继续?" |
| `ci_state` = pending | CI running | "CI pending, 等还是先 audit?" |

### 反例 (禁止 — 这些就是 friction cluster 反复出现的 root cause)

```text
❌ "我开始 audit 了"  (跳过 Layer 0 → 不知道仓的 current state → 报"完成"时无 ground truth)
❌ "我 audit 完了, 报告如下..."  (Layer 1 跑完才看 git log → 形式违反 verification gate)
❌ "5 commits 已 push"  (口头声明, 没跑 git log -5 → CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 复现)
❌ 把 Layer 0 当 optional pre-check 跑一下就 skip → 违反 hard rule
```

### 正例 (强制)

```text
✅ "Layer 0 完成: 5 repos 全部 clean + remote 对 + CI green. 进入 Layer 1 审计..."
✅ "Layer 0 检测到 status 1 uncommitted, 阻塞 Layer 1, AskUserQuestion: commit 或 ignore?"
✅ "Layer 0 检测到 remote 是 wangrui2025, 期望 mykcs (双账号隔离), 阻塞, AskUserQuestion: 切换 remote 或 跳过此仓?"
✅ "Layer 0 完成: 写入 /tmp/rich-audit-L0-<run-id>.json, 包含 5 repos × 5 commands = 25 行 ground truth"
```

### Layer 0 实现位置

- **代码**: `scripts/verification_gate_precheck.py` (v2.6.19 新增, 必跑)
- **输出文件**: `/tmp/rich-audit-L0-<run-id>.json` (含 5 repos × 5 commands)
- **整合点**: Pre-flight Declaration 输出后, 调用此脚本, 5 commands 跑完才进 Layer 1

### Bonus test (v2.6.19)

**Bug 本质**: rich-audit 报"完成"无 ground truth (与 website-improve Mode A 报告"✅ 已 push" 同源)
**End-to-end command**: `python3 scripts/verification_gate_precheck.py --repos ~/.claude,~/.agents/skills,~/Repo/webs/active/mykcs.github.io`
- 旧代码预期: 0 ground truth captured, audit 跑完仍可能误报 "✅ 全部正常"
- 新代码预期: 25 行 ground truth (5 repos × 5 commands) 写入 `/tmp/rich-audit-L0-*.json`, audit 报告 reference 此文件
**Actual**: TBD (A/B test in Step 6)

---

## 执行流程（三层进化系统 + 并行 Agent 架构）

```
User: "rich审计" / "进化"
  |
  v
[1] Layer 1 — 审计层（Audit）【并行 Agent 启动】
    ├─ Agent-Audit-A → Claude Code 配置审计（默认）
    ├─ Agent-Audit-C → Python/ML 项目审计（条件触发）
    └─ 汇总 → 合并两份审计 JSON，计算综合健康分
  |
  v
[2] Layer 2 — 修复层（Fix）【顺序执行】
    AI 读取 Layer 1 汇总 JSON + 关键配置文件
    执行规则语义冲突检测、行为漂移检测、OMC 健康评估
    自动修复安全可论证的问题
  |
  v
[3] Layer 3 — 进化层（Evolve）【3-tool WebSearch cascade + 并行 Agent 启动】
    ├─ Step 1 (primary): mcp__MiniMax__web_search — Claude Code / OMC / Python/ML 最新实践
    ├─ Step 2 (deeper): kimi-webbridge skill — 真实浏览器交互, 抓需要登录的 docs / 论坛 / GitHub issues
    ├─ Step 3 (cross-validate): anysearch skill — 多源 cross-search 验证 (避免单源偏差)
    ├─ Context7: 官方文档 fallback (Python / Claude SDK)
    └─ 汇总 → 3-tool cascade 产出进化建议
  |
  v
[4] 生成进化报告（五段式）
  |
  v
[5] 最终报告（前后健康分 + 修复清单 + 进化清单 + 待处理项）
```

---


📂 **并行 Agent 策略** → see [`references/agent-strategy.md`](references/agent-strategy.md) (loaded on demand)

## 双模扫描范围

> **模式 A**: Claude Code 配置审计（默认）。详见 [`references/audit-patterns.md`](references/audit-patterns.md)（663 行详细检测命令）。
>
> **模式 B**: Python / ML 项目审计（条件触发，检测 `pyproject.toml` / `requirements.txt` 时启用）。详见 [`references/python-checklist.md`](references/python-checklist.md)。

**模式 A 路径清单**（速查表，详细检测见 audit-patterns.md）：

| 路径 | 用途 |
|------|------|
| `~/.claude/rules/` | 行为护栏与约束 |
| `~/.claude/memory/` | 持久化用户/项目/上下文记忆 |
| `~/.claude/knowledge/cases/wiki/` | Case 文件系统（221+ case files） |
| **mem0 ↔ filesystem 对齐** | 双轨记忆同步检测 |
| `~/.claude/hooks/` | PreToolUse / PostToolUse / Stop hooks |
| `~/.claude/scripts/` | 自动化脚本 |
| `~/.claude/skills/` | OMC 和自定义 skills |
| `~/.claude/settings.json` | Claude Code 配置 |
| `~/.omc/skills/` | OMC 市场与用户 skills |
| `~/.agents/skills/` | `.agents` 框架 skills（应与 `~/.claude/skills/` 保持硬链接一致） |

---

## 架构健康度检测（Architecture Health）

| 指标 | 健康阈值 | 超标后果 |
|------|----------|----------|
| 规则文件总数 | ≤ 10 个 | 注意力竞争 |
| 规则总行数 | ≤ 200 行 | 遵守率暴跌 |
| CLAUDE.md 长度 | ≤ 80 行 | resume 挤占上下文 |
| 单规则文件长度 | ≤ 50 行 | 长规则被忽略 |
| frontmatter 覆盖率 | 100% | 加载器不识别 |

> 检测命令、可执行脚本、9 维度加权模型见 [`references/audit-patterns.md`](references/audit-patterns.md)。

---


📂 **v2.6.2+ 新增检测脚本 (2026-06-10)** → see [`references/detection-scripts.md`](references/detection-scripts.md) (loaded on demand)

## 记忆系统对齐检测（双轨同步）

> 详细内容见 [`references/memory-alignment.md`](references/memory-alignment.md)。摘要：
> - **L1** MEMORY.md → case 文件：Phantom entries
> - **L2** case 文件 → MEMORY.md：Missing entries
> - **L3** mem0 → case 文件：mem0 cloud drift
> - 已知陷阱（2026-06-02）：glob 模式不递归 `archive-*/` 子目录导致 197 false positives（已修）

---

## 输出格式（五段式进化报告 + Action Plan）

1. **审计层**: 按维度汇总发现，附证据
2. **指令进化**: 建议新增/修改的规则
3. **SOP 提取**: 可复用检查流程
4. **进化层**: 外部知识扫描结果 + 已采纳/待确认进化项
5. **最终状态**: 前后健康分 + 修复清单 + 待处理项

### JSON 报告结构（v2.0）

```json
{
  "meta": { "tool": "rich-audit.py", "version": "2.0.0", "fix_mode": false },
  "project_modes": { "python": true, "python_ml": true },
  "dimensions": { "integrity": { "findings_count": 0, "findings": [] }, ... },
  "summary": {
    "health_score": 98,
    "severity_counts": { "HIGH": 0, "MED": 3, "LOW": 2 },
    "score_breakdown": {
      "architecture": { "raw_score": 100, "weight": 0.25, "contribution": 25.0, ... }
    }
  },
  "action_plan": {
    "P0": [],
    "P1": [ { "severity": "MED", "message": "...", "auto_fix": "fix_symlink" } ],
    "P2": []
  }
}
```

- **`action_plan`**: 按 P0/P1/P2 优先级分组，每条附 `auto_fix` 类型（如有）
- **`score_breakdown`**: 8 维度加权明细，便于定位短板
- **`project_modes`**: 自动检测当前工作区的 Python 项目类型

---

## 🚫 No-Deferral Hard Rule (2026-06-12 hardened, 用户原话 "下次也不改 直接解决")

**禁止任何形式的 "剩余 LOW 项 / 下次 audit 会改善" 的尾部短语.** 这种短语是 theater — 下次 audit 也不会自动改善, 因为没人在中间动它.

### 强制流程

任何 audit 报告中检测到的项 **必须** 走以下三档之一, 没有第四档:

| Tier | 行动 | 不能 |
|------|------|------|
| **解决** | 当场 fix (Tier 1/2/可推荐 Tier 3 per `feedback-auto-recommend-not-ask`) | 不能"留到下次" |
| **降级到非 finding** | 改阈值 / 加 allowlist / 改用 informational summary (不入 health score) | 不能写"虽然 LOW 但下次会自动改善" |
| **真不可处理** | 写到 `must_fix_before_completion` 阻塞 audit 完成 + AskUserQuestion | 不能静默列入 "remaining items" |

### 反例 (禁止)

```text
❌ "剩余 LOW 项: cases 索引部分老条目 / hook 系统已 2 真 orphan 出清 / settings env 漂移. 下次 rich-audit 应直接收到改善的分数"
❌ "These 405 informational LOW findings will resolve over time as skills are updated"
❌ "Recommended: next audit will pick up the cleanup"
❌ "## Remaining items (next session)" / "## Out of scope this run"
```

### 正例 (强制)

```text
✅ "原 405 LOW informational → patched skill_authoring_checker v2.6.16 默认不报 (改阈值, 降级到非 finding). 当前 finding count: 28 MED + 0 LOW."
✅ "Cases 索引经 grep 实证 — 全部 7-20 处引用, 不是 stale, 是 load-bearing. 已校正 audit 误判. Score 维度 'knowledge_cases' raw=62→90."
✅ "env drift MED finding → 用户已固化 feedback-env-drift-accepted, audit 默认跳过. 不再 emit."
```

### Why

- "下次会改善" = scope creep + 责任 dump (没人在 audit 之间专门动 LOW 项)
- 与 `~/.claude/rules/behavioral-process.md §C` "禁止 Deferred items 列表 (零容忍)" 对齐
- 与 `~/.claude/memory/feedback/feedback-auto-recommend-not-ask.md` (2026-06-12) 对齐: 能解决就解决, 不能就阻塞
- audit 工具的诚信 = 当前状态的诚实快照; 报"下次会改善" = 拿未来对赌掩盖当前 (典型 build-pass theater 变种)

### Auto-fix tier mapping (post-2026-06-12)

| Finding 类型 | 默认 tier | 不能做的事 |
|------------|----------|------------|
| 405 LOW informational (metadata.version etc missing) | Tier 0 — 不入 findings | 不能"标 LOW 然后 defer" |
| LOW false positive (cases load-bearing, hook 假 orphan) | Tier 0 — 修阈值/allowlist | 不能"标 LOW 然后 defer" |
| LOW 真问题, claudecode 能修 | Tier 1 自动执行 | 不能"标 LOW 然后 defer" |
| LOW 真问题, 用户偏好接受 | Tier 0 + 写 feedback | 不能"标 LOW 然后 defer" |
| LOW 真问题, 用户必须决策 | Tier 3 阻塞 + AskUserQuestion | 不能"标 LOW 然后 defer" |

---

## ⚠️ Workflow Synthesizer Truncation 反模式 (2026-06-12 hardened)

任何 rich-audit-style workflow 在 final-report 装配阶段, **禁止** 用 `JSON.stringify(multiAgentResults).slice(0, N)` 截断多 agent 输出. 截断会让装配器产生 "tool missing" / "无 disclosure block" 类**幻觉**.

**反例**: `wf_80569fec-62b` (CASE-RICH-AUDIT-WORKFLOW-SYNTHESIZER-TRUNCATION-20260612):
- 5 个 FAS tool segments (总 ~40KB) 序列化后被 `.slice(0, 8000)` 截到只剩前 1-2 个完整披露
- 装配器报 "3/5 tools missing disclosure" → 触发 Layer 2 fail-fast 假警报
- 实际 5 个 jsonl 全部 `stop=end_turn` + 都有 StructuredOutput ✅

**正确做法 (任选)**:
1. **File swap**: `Bash` 写入 `/tmp/rich-audit-<run-id>-<phase>.json`, 装配器 prompt 引用文件路径 + 让它 Read 完整
2. **Pre-summarize**: 每个 agent segment 在传给装配器前压到 ≤500 字符
3. **Truncation aware**: 显式告诉装配器 `"slice 了到 N 字节, full size 是 M, 缺失的看 /tmp/xxx.json"`

**诊断协议** (装配器报 "tool missing" 时):
```bash
# 第一步: 不要相信装配器, 先看 transcript
for jsonl in $WF_DIR/agent-*.jsonl; do
  stop=$(tail -1 "$jsonl" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('message',{}).get('stop_reason','?'))")
  has_so=$(grep -c "StructuredOutput" "$jsonl")
  echo "$jsonl: stop=$stop StructuredOutput=$has_so"
done
# 若全部 stop=end_turn + StructuredOutput≥1 → 100% 装配器 truncation bug, 不要修 L3 协议
```

**Force-All-Search Skills 验证**: kimi-webbridge / anysearch 在 workflow subagent 上下文**完全可用** (通过 Skill tool). 不需要 fallback 到 direct MCP. 但 anysearch 自己会 fallback (这是它内部容错, 与 Skill 加载无关).

---

## 自动修复行为

> 完整 19 行已下沉到 [`references/auto-fix.md`](references/auto-fix.md)。本节保留摘要。

**脚本层安全修复**（无破坏性）：hook 清理、JSON 修复、权限重置、skill symlink 修复、orphan 清理、Python README 模板。

**AI 层语义修复**（允许编辑）：合并重复规则、补充 Binary Assertions、更新陈旧记忆引用、统一 torch 版本。

---

## Decision Pattern Reversal (2026-06-11 引入)

> **核心**: 用户决策的是"是否 revert"，而不是"是否执行"。
> 触发 case: `~/.claude/knowledge/cases/wiki/CASE-RICH-AUDIT-DECISION-PATTERN-REVERSAL-20260611.md`
> 反馈文件: `~/.claude/memory/feedback/feedback-rich-audit-decision-pattern-reversal.md`

### 三档 auto-fix tier

| Tier | 性质 | risk | requires_user_review | 例子 |
|------|------|------|----------------------|------|
| **1 (mechanical safe)** | 机械可逆 | low | **False** (auto-executable) | shellcheck violation / frontmatter missing field / file size > documented limit / cross-ref dangling |
| **2 (语义安全)** | 语义判断但有客观标准 | medium | **False** (auto-executable + 30-min revert window) | skill 重命名 (Jaccard > 0.5) / 重复规则合并 / stale ref 更新 / hooks symlink stale |
| **3 (intent-required)** | 涉及业务选择 / 价值权衡 | high OR intent type | **True** (需 user 决策) | skill 重命名 vs 删除 / 业务优先级排序 / 跨多文件改动无明确标准 / 改 framework config |

### Tier 判定实现

`scripts/auto_fix_proposer.py` 新增 helper:

```python
TIER3_INTENT_TYPES = frozenset({
    "rename_skill", "delete_skill", "merge_strategy",
    "rename_rule", "delete_rule",
})

def tier_for(risk_level, finding_type=""):
    if finding_type in TIER3_INTENT_TYPES:
        return 3
    if risk_level == "high":
        return 3
    if risk_level == "medium":
        return 2
    return 1

def should_require_user_review(risk_level, finding_type=""):
    return tier_for(risk_level, finding_type) == 3
```

输出增加 `tier_counts` 字段: `{1: N, 2: M, 3: K}` 反映各 tier 数量。

### 输出契约 (4 字段)

```json
{
  "count": 136,
  "risk_counts": {"low": 18, "high": 2, "medium": 116},
  "tier_counts": {"1": 18, "2": 116, "3": 2},
  "requires_user_review_count": 2
}
```

### 反例 (仍需 user 决策 — Decision Pattern Reversal 不适用)

- 跨多文件改动无明确标准 → 仍走 `behavioral-discipline.md §A` scope discipline
- 涉及删除不可逆操作 → 仍需 user 决策
- 改 framework config → 仍需 user 决策 (per CASE-OVER-ENGINEERED-I18N-CHANGE-20260604)

### 实测验证 (2026-06-11)

| 指标 | 旧模式 (2026-06-10) | 新模式 (2026-06-11) | Δ |
|------|---------------------|---------------------|---|
| requires_user_review_count | 141 | **2** | **-99%** |
| Tier 1 (auto) | (混在一起) | 18 | new |
| Tier 2 (auto + 30-min revert) | (混在一起) | 116 | new |
| Tier 3 (user required) | 141 | **2** (only high risk) | -139 |

---

## OMC 生态联动

- **审计前**: 调用 `/instinct-status`，将 instinct 健康度纳入上下文
- **审计后**: 若发现 >= 3 个同类问题，建议运行 `/evolve` 固化新本能
- **Case 联动**: 若发现新的失败模式，建议生成 CASE 归档

---

## 触类旁通处理协议

> 详细内容见 [`references/cascade-reports.md`](references/cascade-reports.md)。摘要：
> - 触发词："触类旁通" / 未指定 scope
> - 三层行动：L1 workspace / L2 全机器 repo / L3 同类现象
> - 报告位置：`~/.claude/knowledge/cascade-reports.md`

---

## 成功标准

1. `rich审计` 触发后执行完整三层流水线（审计 + 修复 + 进化）
2. 双模检测：Claude Code 配置 + Python/ML 项目（如适用）
3. Layer 1 JSON 输出有效，覆盖架构健康度 + Python 健康度
4. Layer 3 产出进化报告，包含外部知识对比与搜索证据
5. 安全机械修复自动应用，无需用户干预
6. 计算修复前后健康评分（0-100）和进化度评分（0-100）
7. **永不休眠：无论健康度多少，Layer 3 必须执行 Force-All-Search Protocol v2.9 (5-tool parallel fan-out: `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` ∥ `exa` (`web_search_exa` + `web_fetch_exa`) → merge+compare → 冲突再查 ≤2 层) + 1 次 Context7 查询。输出契约 (per-tool 显式披露, 5 段必填): 工具 / 搜索内容 / 结论 / 状态 (每工具 1 段) + 共识/冲突/缺失工具 (Phase B/C 段)。** 若任一 5-tool 必需工具未注册 (Layer 2 fail-fast), 禁止静默降级到 <5-tool 跑 Force-All-Search; 必须报告"❌ BLOCKED: 缺失 <tool_name>" + 阻止 Layer 3 继续.
8. **进化报告必须包含"本次搜索发现的新知识"段落，即使结论为"无新进展"，也必须附搜索证据**

## Verification Gates (报告完成前强制检查)

> **下沉到 references**：10 项物理验证完整版见 [`references/verification-gates.md`](references/verification-gates.md)。
>
> **Why**：rich-audit 自身曾多次出现误报（memory-audit cascade、ghost case detection）。验证门禁防止审计工具自身的幻觉被当作结论输出。

**简版 5 项速查**（完整 10 项见 references）：

1. **备份确认**: `ls -la ~/.claude/backups/` — 确认本次审计备份已创建
2. **规则语法检查**: 修改的 `.md` 规则文件 frontmatter 未损坏
3. **JSON 有效性**: 修改的 `settings.json` `python3 -m json.tool` 通过
4. **GitHub 同步状态**: `git -C ~/.claude log @{u}..HEAD --oneline` 无未推送
5. **MEMORY.md 索引一致性**: L1_PHANTOM=0 / L2_MISSING=0 / L3_CASE_GAP=0
## 安全与回滚

- 任何修改前自动备份到 `~/.claude/backups/rich-audit-YYYY-MM-DD-HHMMSS/`
- 所有修复均为幂等操作，可安全重跑
