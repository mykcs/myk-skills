# ADR-0011: Memory Benchmark v1 报告路径选择

## 状态
Accepted, 2026-06-26

## 上下文

claudecode 设计 memory benchmark v1 时，需要决定 6 月 26 日这次首次跑分的报告 / 数据 / 元数据存放路径。

候选 3 个：

| 路径 | 位置 | 形式 |
|------|------|------|
| A. 知识库 case 文件 | `~/.claude/knowledge/cases/wiki/CASE-MEMORY-BENCH-V1-20260626.md` | 跟现有 case 库同位置 |
| B. 专建子目录 | `~/.claude/docs/memory-bench/2026-06-26-v1/` | 给未来的 C2 仪表盘留位置 |
| C. 两个都写 | 简化版在 A + 完整版在 B | 兼顾搜索可见 + 未来扩展 |

## 决策

**最终决议（2026-06-26 第二次修正）: 选 C (即 `rich-audit/reports/memory-bench/`) 作为 rich-audit 配套报告路径, 但 memory-bench 主体保持独立 skill (在 `~/.agents/skills/memory-bench/SKILL.md`).**

> ⚠️ **2026-06-26 修正 1**: 原始决定 B (`~/.claude/docs/memory-bench/2026-06-26-v1/`) 已被 grill 20.2 反转决议否定, 因为 memory-bench 被并入 rich-audit Layer 1+2, 报告应跟 rich-audit 同仓. 详见 ADR-0014 关联.
>
> ⚠️ **2026-06-26 修正 2 (本次 final)**: 实际发现 之前 session 已立独立 skill (`~/.agents/skills/memory-bench/SKILL.md`, 3.4KB, 完整骨架). 所以**主体保持独立**, **rich-audit 报告配套**走 `rich-audit/reports/memory-bench/`. 这是 11.1 = a + 9.1 = a 的现实落地, 跟 11.1 = c 决议部分反转.

## 理由

| 维度 | A | B | C |
|------|---|---|---|
| 跟现有 case 库一致 | ✅ | — | ✅ |
| 给 C2 持续仪表盘留位置（每跑分周期一个子目录） | ❌ | ✅ | ✅ |
| 历史跑分数据可版本化（`2026-06-26-v1/` 是日期 + 版本号） | ❌ | ✅ | ⚠️ |
| 一次写一次 commit 闭环 | ✅ | ⚠️（要写多个文件） | ❌ |
| Git diff 干净 | ⚠️ | ✅ | ❌ |
| search 命中（user 在 cases/ 找 memory-bench） | ✅ | ❌ | ✅ |

**关键 trade-off**：B 选"未来 C2 仪表盘可扩展"，代价是"失去 cases/ 库的 search 可见性"。但 user 原始诉求是"**整理**记忆"，cases/ 库 168 个文件已过载，**新增 memory-bench 不应再加重 cases/**。

## 反例 / 不选 A 的原因

A 路径会让 `~/.claude/knowledge/cases/wiki/` 从 168 个 case 涨到 N+M 个（每次跑分一次），**违反 user "整理"诉求**。

## 不选 C 的原因

C 看似兼顾，但**重复写两份数据 = 数据一致性风险**。一旦 11 行总表在 A 跟 B 不一致，下次跑分时哪份为准 = 治理成本。单一 source of truth 是 memory system 的核心约束。

## 影响

- `~/.claude/docs/memory-bench/` 是新顶级目录
- 每次跑分 = 一个子目录 `{YYYY-MM-DD}-v{N}/`
- 跑分产物：`50-question-set.json` + `b2-baseline.json` + `b3-sota-comparison.json` + `ablation-5-deletion.json` + `report.md` + `summary-card-wall.md`
- Mini-bench（每次 session 收尾）追加到 `~/.claude/docs/memory-bench/mini-bench-history.jsonl`（append-only）

## 相关

- ADR-0012: memory benchmark 4 metric 加权（compliance 0.30 vs recall 0.35）
- ADR-0013: task_score 0.6 + soul_score 0.4 sub-weights 拆分
- ADR-0007: calm-flow 默认协议（task completion ≠ decision point）