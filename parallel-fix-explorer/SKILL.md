---
name: parallel-fix-explorer
description: N worktree 并行 fix 同一 bug + 跑 test 选 winner（test-anchored 并行探索）
metadata:
  type: skill
  version: 1.0.0
  author: myk
  source: insights-friction-2026-06-03
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# /parallel-fix-explorer — 并行 fix 探索

> 适用：bug 根因不明、可能有多个 fix 路径、需要客观 test 验证的场景
> 核心思想：把"调试靠猜"变成"调试靠 test"，N 个 agent 在独立 worktree 各试一个 hypothesis，test 选 winner

## 触发

```bash
/parallel-fix-explorer [N=4] [test-cmd="npm test"] [-- fix-target]
```

默认 `N=4` 个并行 worktree。

## 协议

### Step 1: 评估可并行性

**abort 条件**（任一命中则降级到单 fix 流程）：
- Test 套件 > 5min（成本太高）
- 测试需要外部资源（DB、GPU、网络）且无法隔离
- 修复涉及跨仓改动（>1 个 git 仓）
- 修复需要用户反复确认

### Step 2: 准备 baseline

```bash
# 在主仓记录 baseline test 状态
cd <REPO>
git status --short  # 必须 clean
git rev-parse HEAD > /tmp/baseline-commit.txt
<test-cmd> > /tmp/baseline-test.log 2>&1
echo $? > /tmp/baseline-test-exit.txt
```

如果 baseline test 已 fail，记录"已知 fail 数 = X"。

### Step 3: 创建 N 个 worktree

```bash
WT_BASE=/tmp/fix-explore-$$
for i in $(seq 1 $N); do
  WT="$WT_BASE/wt-$i"
  git worktree add "$WT" -b "fix-explore-$i" main
  echo "Created: $WT"
done
```

### Step 4: 派 N 个并行 agent（每个一个 hypothesis）

```text
For each worktree $i ∈ {1..N}, launch 1 Agent with:

You are exploring fix strategy #$i for <BUG_DESCRIPTION> in <REPO_PATH> at <WT_PATH>.

Your hypothesis: <UNIQUE_HYPOTHESIS_FOR_i>
  (e.g., "minimal diff fixing only the assertion",
   "refactor the function to be more idiomatic",
   "add input validation upstream",
   "revert to last-known-good and re-apply with explicit reasoning")

Steps:
1. cd to WT_PATH
2. Read the failing test and the relevant code
3. Apply your hypothesis-driven fix (smallest correct diff)
4. Run: <test-cmd> > /tmp/fix-explore-N-test-i.log 2>&1
5. Record the result to /tmp/fix-explore-N-result-i.json:
   {
     "strategy": "<HYPOTHESIS>",
     "test_exit": <code>,
     "new_passes": <count>,
     "new_failures": <count>,
     "diff_size_lines": <n>,
     "files_changed": ["path1", "path2"]
   }
6. Do NOT push. Do NOT merge. Just record.

Report back the JSON.
```

**Hypothesis 来源**（任选 4 个）：
- (a) 最小 diff 修 assertion
- (b) 重构函数为更 idiomatic
- (c) 上游加 input validation
- (d) 回到 last-known-good 重新 apply
- (e) 类型系统化（加类型守卫）
- (f) 测试本身有问题 → 改测试
- (g) 配置层修复（env、tsconfig）
- (h) 依赖层修复（升级/降级某包）

### Step 5: 聚合 + 选 winner

```bash
for i in $(seq 1 $N); do
  cat /tmp/fix-explore-N-result-$i.json
done

# Winner criteria:
# 1. Most new_passes
# 2. Tie → fewest new_failures
# 3. Tie → smallest diff_size_lines
# 4. Tie → files_changed most localized to expected area
```

### Step 6: 合并 winner + 验证

```bash
# Apply winner's diff to main worktree
cd <REPO>
git checkout main
git diff main..fix-explore-<WINNER> > /tmp/winner.diff
git apply /tmp/winner.diff
git add -A
git commit -m "fix(<scope>): <desc>

Strategy: <HYPOTHESIS> (chose from $N parallel exploration)
Test result: <NEW_PASSES> new passes, <NEW_FAILURES> new failures

Co-explored strategies: <list with their scores>"

# Final verification
<test-cmd>
```

### Step 7: 清理 + 记录

```bash
# Cleanup worktrees
git worktree remove --force /tmp/fix-explore-$$
git branch -D fix-explore-{1..$N}

# Record case
CASE=~/.claude/knowledge/cases/CASE-PARALLEL-FIX-$(date +%Y%m%d-%H%M).md
cat > "$CASE" <<EOF
# parallel-fix-explorer run

## Bug
<description>

## Strategies explored
- Strategy 1: <HYPOTHESIS> → <RESULT>
- Strategy 2: <HYPOTHESIS> → <RESULT>
- Strategy 3: <HYPOTHESIS> → <RESULT>
- Strategy 4: <HYPOTHESIS> → <RESULT>

## Winner
<STRATEGY> with <RESULT>

## Why it won
<analysis>

## Lessons
- ...
EOF
```

## 输出契约

```markdown
# parallel-fix-explorer report

## Bug
<one-line>

## N
4

## Strategies + results
| # | Hypothesis | New passes | New fails | Diff size | Score |
|---|------------|-----------|-----------|-----------|-------|
| 1 | minimal diff | +3 | 0 | 12 | 3 |
| 2 | refactor | +5 | 2 | 47 | 3 |
| 3 | upstream validation | +4 | 0 | 23 | 4 ⭐ |
| 4 | revert + reapply | +1 | 0 | 8 | 1 |

## Winner
Strategy 3: upstream validation (+4 passes, 0 new fails)

## Committed
<hash>

## Case file
~/.claude/knowledge/cases/CASE-PARALLEL-FIX-YYYYMMDD-HHMM.md
```

## 硬规则

- ❌ N=1 跑这个 skill（用普通 fix 流程）
- ❌ 跳过 baseline test（不知道改善了多少）
- ❌ 选 winner 不写理由
- ❌ 直接 merge 第一个 pass 的策略（可能局部最优）
- ❌ 不写 case file
- ✅ winner 必须客观可复现（test 数字 + diff）
- ✅ 4 个 strategy 全部跑完才能选 winner
- ✅ 失败的 strategy 也要记录"为什么失败"

## 已知反模式

- **cherry-pick by 主观**：agent 自己说"我觉得 1 更好" → 必须用 test 数据
- **worktree 不隔离**：在主仓直接改 → agent 互相覆盖
- **test 不稳**：用 flaky test 选 winner → 选错策略
- **N=1 凑数**：只跑一个 strategy 然后说"4 个 agent 跑完了"

## 与其他 skill 的关系

- `website-improve` — 不直接相关（这是 bug fix 协议，audit 是另一回事）
- `confirm-edit` — Worktree 创建前的仓验证
- `behavioral-verification-gate` — 选 winner 后必须跑最终 test

## 何时不用这个 skill

- 单文件 typo → 直接改
- 简单 refactor 已知方向 → 普通 fix 流程
- Test 不存在 → 先写 test（用 tdd-guide）
- 根因清晰 → 普通 fix 流程即可
