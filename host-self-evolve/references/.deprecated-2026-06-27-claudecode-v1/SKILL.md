---
name: memory-bench
description: Benchmark claudecode's memory system against official SOTA (LongMemEval / LOCOMO / MSC) + Oracle + ablation 5-deletion. Tests 4 metrics: recall (35%) / cross-source consistency (25%) / compliance (30%) / token economy (10%). Runs opus-as-judge over 50 recall questions + 15 consistency checks + 12 compliance scenarios. Use when user says "memory bench", "recall test", "claudecode 记忆打分", or asks "claudecode 现在记忆系统排第几".
metadata:
  type: tool
  category: benchmark
  status: v1-skeleton (2026-06-26, no full run yet)
  triggers:
    - "memory bench"
    - "记忆打分"
    - "claudecode 记忆现在排第几"
    - "recall test"
    - "/memory-bench"
  plan: "B (conservative merge, 2026-06-26)"
---

# Memory Bench v1 (claudecode 记忆系统打分协议)

> **状态**: v1 骨架 — ADR + 决策表全固化，跑分未执行（2026-06-26 grill 6 大问 / 30 决策 / 3 ADR 落地完成）
> **首跑时间**: 待 user 启（建议下 session 启，7-9h wall clock 分多 session 跑）
> **路径**: `~/.claude/docs/memory-bench/{YYYY-MM-DD}-v{N}/`

## 1. 4 Metric 加权 (ADR-0011/0012/0013)

```
score = 0.35 × recall + 0.25 × consistency + 0.30 × compliance + 0.10 × token_economy
```

其中 `compliance = 0.6 × task_score + 0.4 × soul_score` (ADR-0013)

## 2. 跑分流水线 (6 步)

| 步骤 | 动作 | 工具 |
|------|------|------|
| 1 | 建仓 `~/.claude/docs/memory-bench/{date}-v{N}/` | mkdir |
| 2 | 抽 60 题（自动）+ opus 评难度 + user 审 5 题 + 锁 50 题 | Python + opus + user |
| 3 | opus-judge 评分（单 judge + 5% 升级 3-judge） | opus model |
| 4 | B2 baseline (claudecode 当前 6 源) | 77 评估 |
| 5 | 2.3b ablation 5 删（删 HOT FACTS / MEMORY.md / rules/ / cases/ / mem0） | 5 × 62 = 310 评估 |
| 6 | B3 SOTA × 4 套（LongMemEval 50q + LOCOMO 10 + MSC 30 + Oracle 50） | 140 评估 |
| 7 | 11 行总表 + C1 report.md + summary-card-wall.md | Write |

## 3. 50 题分布 (10.1 = c)

| 类型 | 题数 | 占比 |
|------|------|------|
| Recall | 20 | 40% |
| Cross-source consistency | 20 | 40% |
| Compliance 触发题 | 10 | 20% |

## 4. Compliance 12 场景 (ADR-0013)

**Task (10)**：deferred-detector / CSS context 前缀 / cascade-kill 三件套 / 跨境 API timeout+retry / SKILL.md frontmatter / 5 commands verification / WebFetch framework config / git remote -v / smart-push / 报告 verification evidence

**Soul (2)**：
- #11 反向提问以「用户」开头（灵魂规则 v2）
- #12 给方案含 A vs B + 推荐 + 1 句理由 + 结尾"请回 X"（灵魂规则 v3）

## 5. Mini-bench (C2 持续仪表盘)

- 触发：每个 session 收尾（Stop hook）+ user 手动 `/memory-bench mini`
- 题数：3 题（1 task + 1 soul + 1 cross-source）
- 时间：< 1min
- 输出：append 到 `~/.claude/docs/memory-bench/mini-bench-history.jsonl`

## 6. 使用方法

```bash
# 完整跑分 (首次 / 重大更新后)
~/.agents/skills/memory-bench/bin/run-full-bench.sh

# Mini-bench (session 收尾 / 手动)
~/.agents/skills/memory-bench/bin/run-mini-bench.sh
```

## 7. 相关

- `~/.claude/docs/adr/0011-memory-bench-v1-path-choice.md`
- `~/.claude/docs/adr/0012-memory-bench-compliance-weight.md`
- `~/.claude/docs/adr/0013-memory-bench-task-soul-subweights.md`
- `~/.claude/CLAUDE.md` 灵魂规则 v2/v3
- `~/.claude/rules/calm-flow.md` ADR 0007（任务完成 ≠ 决策时刻）