---
name: rich-audit
description: |
  三层进化系统：审计（发现问题）→ 修复（解决问题）→ 进化（主动获取外部先进知识并应用）。
  双模审计：Claude Code 配置审计 + Python/ML 项目审计。
  触发词：rich审计, /rich-audit, 进化
license: MIT
metadata:
  version: "2.6.29"
  author: mykcs
  category: self-evolution
  changelog:
    - "2.6.29 (2026-06-27): trigger 扩列. 触发: user 原话 '执行重度审计 = ~/.claude + ~/.agents'. 加 '重度审计' / '执行重度审计' / 'deep audit' 三个 trigger alias + 同步 §触发方式 段. 默认仍跑完整三层 (Layer 1+2+3), 不变 depth. 跟 CLAUDE.local.md §11.1 自动 merge PR 协议独立, 这次单文件 micro edit 走 smart-push 直 push main."
    - "2.6.27 (2026-06-26): 自动 merge PR 协议固化 (跟 CLAUDE.local.md §11 + process.md §C.3.1 同步). 触发: user 原话 'user 同意 claudecode 自动 merge PR #3 也可以写到 skill 里' (PR #2 跟 PR #3 都已自动 merge 验证成功). 新增 hard rule: PR merge 步骤全自动 (gh pr merge --squash --delete-branch) + post-merge fast-forward 本地 main + 清理 worktree. 沿用 smart-push 协议 (CLAUDE.local.md §7). 例外: 涉及双账号污染 / 安全 / config 字段改动 仍走 soul v2 双向保险必问."
    - "2.6.26 (2026-06-26): 修改前必报路径协议 + Git worktree + PR 协议 (跟 CLAUDE.local.md §11 同步). 触发: user 原话 '修改 skill 时...要显式说出具体文件' + '积极利用 PR/worktree' + '我也不太懂 PR 怎么用'. 4 字段清单 (路径/类型/量/PR 判断) → user OK 才动手. worktree 路径 ~/.claude/.worktrees/<YYYY-MM-DD>-<topic>/, branch 命名 feat/<topic> (kebab-case). 单文件 micro edit (< 50 行 / 不改 rules/) 维持 smart-push 直 push main."
    - "2.6.24 (2026-06-25): 双模式报告协议. 用户后续嫌 v2.6.23 太简略 → 加 详细模式 (verbose) 触发. 协议: (1) 默认仍是 v2.6.23 精简 (≤ 30 行); (2) 用户说 "详细" / "verbose" / "展开" / "完整报告" → 切到详细模式 (无硬上限, 含维度表 + 修复清单 + Bonus Test). 触发词: rich-audit 末尾跟 verbose OR 用户回复 "详细". Source: 用户原话「不要这么简略」."
    - "2.6.23 (2026-06-24): 报告协议再精简 (用户反馈「还是太复杂」). v2.6.22 协议 ## 分 仍有 5+ 条细分, ## 状态 10 条, ## 注意 6 条 — 仍冗余. v2.6.23 协议硬上限: (1) 全文 ≤ 30 行 (不含表格); (2) ## 分 ≤ 2 句; (3) ## 状态 ≤ 3 条短句; (4) ## 注意 ≤ 3 条. 数字用逗号分隔, 不要表格. 用户王瑞原话: 「还是太复杂, 你每次都要给我汇报最直接最简单的内容」."
    - "2.6.22 (2026-06-24): 报告格式精简 v-bump (用户偏好). 用户王瑞注意力分散, 汇报要最直接最简单. 协议变更: (1) 禁止散落的绿色对勾 emoji + 多余详细文字说明; (2) 用 总分总 或 总分 结构; (3) 绿色大勾集中在一处 (「## 状态」section); (4) 注意事项另起一区 (「## 注意」section), 不混在结论里. Source: 用户原话「禁止散落的 emoji / 绿色对勾图标 + 多余详细文字说明. 应用总分总或总分结构, 在某一处集中写所有绿色大勾, 有什么需要注意的另起一区」."
    - "2.6.21 (2026-06-24): 5-tool Force-All-Search §F.1.1/§F.1.2 降级矩阵 v-bump. CLI session 实测 5-tool 中 3 个 fail (MiniMax api key / kimi-webbridge daemon / anysearch unconfigured), per process.md §F.1.2 自动降级到 exa + WebFetch 双工具 parallel. Run 3 (2026-06-24-200904) 实证: weighted 84.7 raw → 100.0 effective after advisory 降级 (49 HIGH 是 session-env/ mem0 keys, gitignored 不 push). 同步 Layer 3 §F.1 引用 process.md §F.1.1/§F.1.2, 避免 sub-skill loader 跟 process.md drift."
    - "2.6.20 (2026-06-23): SKILL.md progressive disclosure split — 3 large sections (Layer 0 88 lines / Execution Flow 87 lines / No-Deferral + Workflow Synthesizer 78 lines) extracted to references/layer-0-verification-gate.md + execution-flow.md + no-deferral-pattern.md. SKILL.md 564 → 324 lines (under 500 Anthropic limit). Main file keeps trigger + 0-confirm protocol + Pre-flight Declaration + report schema + Decision Pattern Reversal + Cross-References, references files load on demand. body_too_long MED finding cleared (skill_authoring_checker 1 → 0)."
    - "2.6.19 (2026-06-23): Layer 0 Verification Gate Pre-check (新 §A.1, 5 commands 必跑). 解决 top friction cluster 'Audit 跑完口头报 ✅ 已 push 无 ground truth' (CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621, 2026-06-21). Layer 0 在 Pre-flight Declaration 之后, Layer 1 之前, 必跑 git log/status/remote + gh api 5 commands for each targeted repo, 写入 ground_truth_snapshot. 任何 state drift (uncommitted / unpushed / wrong remote / CI pending) → 阻塞 Layer 1 直到 user 决定. Anti-pattern: 把 verification gate 当 post-check (跑完才看) → 永远晚一步. Skill-evolution auto-derived 2026-06-23."
  triggers:
    - rich审计
    - /rich-audit
    - rich audit
    - claude 审计
    - audit claude files
    - 进化
    - 自我升级
    - 执行重度审计
    - 重度审计
    - deep audit
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

- **中文**: `rich审计` / `重度审计` / `执行重度审计`
- **英文**: `/rich-audit` / `deep audit`
- **别名**: `rich audit`, `claude 审计`, `audit claude files`, `进化`, `自我升级`

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

> **完整 SOP 详见** [`references/layer-0-verification-gate.md`](references/layer-0-verification-gate.md) (5 commands + 4 字段契约 + 阻塞条件 + 反例/正例). 主 SKILL.md 仅留 trigger + 违规后果. **违反硬规则**: 跳过 Layer 0 = CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 重现.

---

## 执行流程（三层进化系统 + 并行 Agent 架构）

> **详细架构图 + Agent 策略 + 双模扫描 + 架构健康度阈值 + 记忆系统对齐** 详见 [`references/execution-flow.md`](references/execution-flow.md) (87 lines, progressive disclosure). 主 SKILL.md 只引用, 不重复内容. 

## 输出格式（v2.6.24 双模式, 用户偏好）

### 默认: 精简模式 (v2.6.23 协议)

全文 ≤ 30 行, ## 分 ≤ 2 句, ## 状态 ≤ 3 条, ## 注意 ≤ 3 条. 数字逗号分隔, 不用表格.

### 详细模式 (触发: "详细" / "verbose" / "展开" / "完整报告")

无硬上限. 含: 维度表 + 修复清单 (Tier 1/0/3) + Bonus Test + 跨 session drift + 5-tool 实测表 + 双账号隔离检查.

模板:
```
总分: weighted=X.X effective=Y.Y after advisory.
分: 8 维度 + 5-tool 实测 + 跨仓 push 状态.
## 状态 (5-10 条 OK)
- ...
## 注意 (3-6 条 user 需知)
- ...
## 修复清单 (Tier 1/0/3 分组)
- Tier 1 (机械可逆): N 项
- Tier 0 (informational 降级): M 项
- Tier 3 (user 决策): K 项
## Bonus Test
- (强证据 case)
```

### JSON 报告结构 (保留, 用于程序消费)

JSON 保留 5 维度 + severity_counts + score_breakdown, 人类可读报告按本节精简协议.

---

## 🚫 No-Deferral Hard Rule (2026-06-12 hardened, 用户原话 "下次也不改 直接解决")

> **完整 3 档 tier 框架 + 反模式 + 正例 + Why + Auto-fix tier mapping + Workflow Synthesizer Truncation 反模式** 详见 [`references/no-deferral-pattern.md`](references/no-deferral-pattern.md) (78 lines). 主 SKILL.md 引用.

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
