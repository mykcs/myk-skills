# ADR-0012: Memory Benchmark v1 — Compliance 0.30 vs Recall 0.35 接近权重

## 状态
Accepted, 2026-06-26

## 上下文

memory benchmark v1 设计 4 个 metric 加权：

```
score = 0.35 × recall + 0.25 × consistency + 0.30 × compliance + 0.10 × token_economy
```

**关键选择**：compliance (0.30) 接近 recall (0.35)，而非传统"recall 主 / 其他次"。

## 决策

**compliance 权重 0.30，仅次于 recall 0.35**。

## 理由

| 维度 | 论证 |
|------|------|
| User 原始痛点 | "我是 Coding Agent 小白，你得有意识引导我" — 核心痛点不是"claudecode 不知道"，是"claudecode 知道但不做" |
| 量化支撑 | cases/ 库 168 个 case 大量是"claudecode 记得规则但违反"（CLAUDE.local.md §6 cascade-kill 反复触发） |
| 灵魂规则 v3 直接对应 | 大姐姐大白话 + 主动引导 = behavior，不只是 knowledge |
| 5 个 metric 都不重 | 跟 user "整理"诉求对齐 — 单一维度 recall 高 ≠ 实用 |

**反直觉 trade-off**：传统 NLP benchmark 把 recall 当主指标（"模型知道多少"）。claudecode 把 compliance 当主指标（"模型照做多少"），因为**claudecode 已经是 knowledge-dense 模型**，差异化在 behavior。

## 反例 / 反方案

| 反方案 | 不选理由 |
|--------|----------|
| 0.50 recall + 0.20 compliance | 违背 user 痛点 |
| 0.35 recall + 0.35 compliance | 太对称，5 维度信息密度被 2 维度稀释 |
| 0.40 recall + 0.30 compliance + 0.20 consistency + 0.10 token | 仍 recall 主，user 痛点没解决 |

## 影响

- compliance 12 场景（10 task + 2 soul）评分权重 = 12 × 2 分制 = 满分 24
- task_score = 10 场景 hit 数 × 2 / 20
- soul_score = 2 灵魂场景 hit 数 × 2 / 4
- compliance 内部 task 0.6 + soul 0.4 拆分 → 见 ADR-0013

## 历史 record

- 2026-06-26 立（grill 协议 6 大问决定）

## 相关

- ADR-0011: report 路径选择
- ADR-0013: task 0.6 + soul 0.4 sub-weights
- `~/.claude/memory/identity-first-person.md` 灵魂规则 v2（合规来源）
- `~/.claude/memory/soul-elder-sister-explain.md` 灵魂规则 v3（合规来源）