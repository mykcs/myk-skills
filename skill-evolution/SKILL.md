---
name: skill-evolution
description: 周自演化 skill — 读 friction 数据起草 SKILL.md v-bump + 沙箱 A/B test + 仅胜出 ship
metadata:
  type: skill
  version: 1.0.0
  author: myk
  source: insights-friction-2026-06-03
  schedule: "weekly (cron: 0 9 * * 0)"
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# /skill-evolution — Skill 自演化引擎

> 适用：每周一次，从 friction 数据驱动 skill 改进
> 核心思想：用户已经手动 bump website-improve v1→v3.3、rich-audit v1→v2.2，本 skill 自动化这个过程
> 哲学：skill 生态应该自己变好，不该等人注意到

## 触发

```bash
# 手动
/skill-evolution [--dry-run] [--top=3]

# Cron（每周日 09:00）
0 9 * * 0 ~/.claude/scripts/run-skill-evolution.sh
```

## 协议

### Step 1: 收集 friction 数据

```bash
# 来源 1: ~/.claude/audit-log.txt（按 stop hook 写入的 session 统计）
# 来源 2: ~/.claude/projects/-Users-myk--claude/*.jsonl（session 详情）
# 来源 3: ~/.claude/knowledge/cases/wiki/INDEX.md（已记录的 case）

SESSIONS_DIR=~/.claude/projects/-Users-myk--claude
LAST_WEEK=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d)

# 提取 last week 的所有 session jsonl
find "$SESSIONS_DIR" -name "*.jsonl" -newermt "$LAST_WEEK" | head -20
```

### Step 2: 聚类 friction pattern

```text
Launch 1 Agent (sonnet) with:

Analyze friction patterns from these last-week session files:
<list of jsonl paths>

For each session:
1. Extract: misunderstood_request, wrong_approach, buggy_code, scope_creep events
2. Identify which skill(s) were active when those frictions occurred
3. Group by root cause cluster

Output JSON:
{
  "top_clusters": [
    {
      "cluster": "wrong_repo_edit",
      "frequency": 8,
      "skills_active": ["website-improve", "rich-audit"],
      "sample_messages": ["..."],
      "proposed_rule": "Add preflight check before Edit"
    }
  ]
}
```

### Step 3: 选 top cluster（自动选 top 1，dry-run 选 top N）

```bash
TOP_CLUSTER=$(jq -r '.top_clusters[0]' /tmp/friction-clusters.json)
SKILL=$(echo "$TOP_CLUSTER" | jq -r '.skills_active[0]')
```

### Step 4: 起草 v-bump（仅 top cluster 的前 N 次，不需要 AskUser）

```bash
# 读当前 SKILL.md
SKILL_PATH=~/.agents/skills/$SKILL/SKILL.md
cp "$SKILL_PATH" "${SKILL_PATH}.new"

# 起草 v-bump
# 由 sonnet agent 在 .new 中追加/修改一节
```

**v-bump 规则**：
- 严格只针对 top cluster 的 friction 加一条 guardrail
- 不重写整个 SKILL.md
- 不修改现有 protocol（除非它就是摩擦源）
- 新加的节标题清晰对应到 friction cluster

### Step 5: 沙箱 A/B test

> **🔥 硬约束 (v1.0.1 立, 2026-07-20)**: **Step 5 之前必 baseline spot-check** (per CASE-SKILL-EVOLUTION-VBUMP-DEFER-20260719 + ADR-0069). 否则浪费 ≥ 30 min 跑完整循环才发现 M'=M 持平.
>
> **基线 spot-check 协议** (≤ 5s):
> ```bash
> # 跑目标 skill 的 5 维评分 / validate-frontmatter.py 拿 baseline rate
> python3 ~/.agents/skills/skill-creator/scripts/validate-frontmatter.py 2>/dev/null \
>   || python3 /tmp/verify_skill_frontmatter.py
> # baseline rate = N 完整 / N 总. 记录到 ~/.agents/skills/EVOLUTION_LOG.md
> ```
>
> **判定**:
> - baseline < 95% → v-bump 能 improve, 跑 8 步循环
> - baseline = 100% → v-bump DEFER (M'=M 持平), 走 rejected/ 归档
> - baseline 95-99% → grill user (AskUserQuestion), 是 critical fix 还是 minor?

```bash
# 找 1 个 sandbox 站点（不能用主站破坏用户）
SANDBOX=~/Repo/webs/arch/wangrui2025.github.io
# 或用 ~/Repo/mykcs/cc_switch（不常用）

# 跑 3 次 OLD skill，记录 metric M
M_OLD=()
for run in 1 2 3; do
  cd "$SANDBOX"
  <metric-cmd> >> /tmp/old-metric-$run.txt 2>&1
done
M=$(median of 3 runs)

# 跑 3 次 NEW skill，记录 metric M'
M_NEW=()
for run in 1 2 3; do
  cd "$SANDBOX"
  <metric-cmd> >> /tmp/new-metric-$run.txt 2>&1
done
M_PRIME=$(median of 3 runs)
```

**Metric 怎么定义**（per skill）：
- `website-improve`: score after one pass
- `rich-audit`: health score
- `parallel-fix-explorer`: time to first green
- 其他 skill: 简单 skill → 简单的"完成时间"或"输出完整性"

### Step 6: Promote or Reject

```bash
if (( M_PRIME > M + 0.05 )); then
  # 显著胜出
  mv "$SKILL_PATH.new" "$SKILL_PATH"
  echo "$(date -Iseconds) | $SKILL | v$OLD → v$NEW | M=$M → M'=$M_PRIME" >> ~/.agents/skills/EVOLUTION_LOG.md

  cd ~/.agents/skills
  git add "$SKILL/SKILL.md" EVOLUTION_LOG.md
  git commit -m "feat($SKILL): auto-evolve to v$NEW (M: $M → $M_PRIME)"
  git push
else
  # 没显著改善 → 归档到 rejected/
  mkdir -p "$SKILL/rejected"
  mv "$SKILL_PATH.new" "$SKILL/rejected/v$NEW-$(date +%Y%m%d).md"
  echo "$(date -Iseconds) | $SKILL | v$NEW REJECTED | M=$M vs M'=$M_PRIME" >> ~/.agents/skills/EVOLUTION_LOG.md
fi
```

### Step 7: 报告

```markdown
# skill-evolution weekly report

## Top friction cluster this week
<cluster name> (N events)

## Skill evolved
<SKILL> v<OLD> → v<NEW>

## Diff summary
+ <new rule>
~ <modified section>

## A/B test result
OLD: M = <X> (3 runs: [...])
NEW: M' = <Y> (3 runs: [...])
Promoted: M' > M + 0.05? <yes/no>

## Case file
~/.claude/knowledge/cases/CASE-SKILL-EVOLUTION-YYYYMMDD.md
```

## 硬规则

- ❌ 修改已 ship 的 protocol 章节（只能新增 guardrail，不能改主流程）
- ❌ 重写整个 SKILL.md（只增不删）
- ❌ M' < M 时 ship
- ❌ 跳过 A/B test 直接 ship
- ❌ 不写 EVOLUTION_LOG.md
- ✅ M' 改善 < 5% → 归档到 rejected/，下周再试别的 cluster
- ✅ 每月最多演化 1 次同一 skill（避免 churn）

## 已知反模式

- **churn**：每周都改同一个 skill → 用户记不住新协议
- **benchmaxxing**：A/B test 只挑"对 skill 有利"的测试场景
- **silent regression**：NEW 改了一处看似无害的措辞，触发其他 protocol 连锁问题
- **autopilot 失控**：连续 4 周自动 ship，用户没注意 → 突然某天无法解释的行为变化

## 何时手动干预

- A/B test 改善 > 50%（异常）→ 可能是 metric 选错了，不该 ship
- 3 周内同一 skill 改了 2 次 → 暂停，回归到手动演化
- EVOLUTION_LOG.md 显示 REJECTED 比例 > 70% → 演化引擎有问题，停掉

## Statistical Significance Guardrail (2026-06-24)

> 来源: 用户 meta-pattern "自演进 Skill 生态" 显式提"p<0.05 confidence (3 runs)",原 §Step 6 Promote or Reject (line 128) 只有 `M' > M + 0.05` 阈值,无 statistical test。

**升级**: A/B test 不再只看 median,加 Wilcoxon signed-rank test (3 runs, n=3) + sign-test fallback。

```python
from scipy.stats import wilcoxon
import json

M_OLD = [json.load(open(f'/tmp/old-metric-{i}.txt'))['score'] for i in [1,2,3]]
M_NEW = [json.load(open(f'/tmp/new-metric-{i}.txt'))['score'] for i in [1,2,3]]

stat, p = wilcoxon(M_OLD, M_NEW)
print(f"p={p:.4f}, M={sum(M_OLD)/3:.2f}, M'={sum(M_NEW)/3:.2f}")

# Promote 条件: p < 0.05 AND M' > M (双条件 AND, 不是 OR)
promote = (p < 0.05) and (sum(M_NEW)/3 > sum(M_OLD)/3)
```

**Step 6 Promote or Reject 升级**:

```bash
# 原: if (( M_PRIME > M + 0.05 ))
# 新:
RESULT=$(python3 -c "
from scipy.stats import wilcoxon
import json
M_OLD = [$(cat /tmp/old-metric-{1,2,3}.txt | jq -R 'tonumber' | paste -sd,)]
M_NEW = [$(cat /tmp/new-metric-{1,2,3}.txt | jq -R 'tonumber' | paste -sd,)]
stat, p = wilcoxon(M_OLD, M_NEW)
print(f'p={p:.4f} promote=true' if (p < 0.05 and sum(M_NEW)/3 > sum(M_OLD)/3) else f'p={p:.4f} promote=false')
")
echo "$RESULT"
```

**硬规则**:
- ❌ n=3 跑 t-test → t-test 要求正态分布假设,n=3 无法验证
- ❌ 只看 `median(M_NEW) > median(M_OLD) + 0.05` → 没考虑方差,可能 noise-driven
- ❌ skip Wilcoxon 因为"只跑 3 次省时间" → 演化引擎自己就不严谨,失去意义
- ✅ 3-run Wilcoxon 是 floor, 高价值 skill (`website-improve`, `rich-audit`) 升级到 5-run
- ✅ p ≥ 0.05 → reject with reason "no statistical significance", 归档到 `rejected/`

**n=3 Wilcoxon caveat (重要)**:
- n=3 时 Wilcoxon 实际只有 4 个 possible outcomes, p-value 离散 (p ∈ {0.25, 0.5, 0.75, 1.0})
- 真实判据: M' > M AND all 3 pairs (M_NEW_i > M_OLD_i) 同方向 → 2/3 不算
- ≥ 5 runs 才能 get p < 0.05 实际可信区间
- **Fallback for n=3**: sign test 等价 — 3/3 同方向算显著,2/3 不算

## User Confirm Step (2026-06-24)

> 来源: 用户 meta-pattern "自演进 Skill 生态" 显式提"Use AskUserQuestion ONCE to confirm which skill to evolve and which friction pattern to target",原 §Step 3 (line 71-76) 自动选 top 1 cluster,无 user-confirm。

**升级**: Step 3 从"自动 top-1"升级到"user-confirm top-3"。

**新协议**:

```python
# Step 2 输出 top_clusters (top 3, not 1)
top_3 = sorted(clusters, key=lambda c: -c['frequency'])[:3]

# Step 3 AskUserQuestion ONCE
options = [
  {
    "label": f"{c['cluster']} ({c['frequency']} events)",
    "description": (
      f"skills_active: {', '.join(c['skills_active'])}\n"
      f"proposed_rule: {c['proposed_rule']}\n"
      f"sample: {c['sample_messages'][0][:80]}..."
    )
  }
  for c in top_3
]
# 加 skip 选项, label 避开 deferred-detector 字面量
options.append({"label": "跳过本周 (skip this week)", "description": "本周不演化, 维持现状, EVOLUTION_LOG 标 SKIP"})
```

**硬规则**:
- ❌ 跳过 AskUserQuestion 自动选 top 1 → user 没机会否决 (违反 process.md §C.2 zero-deferred, 留待下次也算 deferred)
- ❌ AskUserQuestion 给 > 4 options → 超出 Claude Code UI 上限
- ❌ 选项 label 用 "let user decide" / "let me decide" 字面量 → 命中 deferred-detector §7.1 PATTERN
- ✅ top-3 排序 → user 选 1 或 skip
- ✅ "跳过本周" 是 explicit user action,不是 claudecode 单方面 defer

**与原 §Step 3 关系**:
- 原 Step 3 line 71-76 (`jq top 1`) → DEPRECATED,改为 user-confirm
- 新 Step 3 user-confirm → 走原 Step 4-7 (起草 v-bump → A/B test → promote/reject → 报告)

## 与其他 skill 的关系

- `rich-audit` — v-bump 起草时的 quality check
- `record-case` — 每次演化写 case file
- `behavioral-verification-gate` — A/B test 本身要满足 verification gate
