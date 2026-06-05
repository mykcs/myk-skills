# ADR 0003: 粒度 — session-level 与 sub-problem-level 二元

**Status**: Accepted
**Date**: 2026-06-05
**Context**: healer-cannot-self-heal skill 的"粒度"决策（v0.2.0）

## Context

v0.1.0（2026-06-02）只支持 session-level（整个对话）。用户 2026-06-05 反馈：

> "有时候不是一个对话级别的 可能是这个对话里最近一个子问题引起的"

**观察**：现实里"整个 session 失控"是稀有事件（可能 5%/100 次急诊召唤）；而"最近一个子问题反复卡 / 漂移 / 跑偏"是常态（约 60%）。剩余 35% 是其他场景（工具配置/外部依赖/环境问题，不在 skill 范围内）。

如果 skill 只能处理 session-level，对 sub-problem 场景要么过度反应（整 session 报告淹没子问题根因），要么无反应（用户没有"session 失控"的语义化感受，召唤门槛过高）。

## 决策

引入 **二元粒度**（binary granularity），由**触发词显式分叉**：

| Mode | 触发词 | 范围 |
|------|--------|------|
| `session-level` | `医者不可自医` / `healer-cannot-self-heal` / `session 急诊` / `claudecode 自检` / `急诊` / `session-autopsy` / `claudecode-checkup` | 整个对话 |
| `sub-problem-level` | `claudecode 子问题急诊` / `子问题急诊` / `sub-problem triage` / `subproblem-triage` | 最近一个子问题（claudecode 判定话题转换点作为起点） |

子问题边界 = claudecode 在 transcript 中**判定的话题转换点**（L_start_subproblem），详见 SKILL.md "sub-problem mode 专属" 段。

## 候选与拒绝

| 候选 | 评价 | 决策 |
|------|------|------|
| **二元粒度 + 显式触发词分叉** | 词边界清晰；claudecode 不自判粒度（与"医者不可信"一致）；现有 session-level 用户不需迁移 | ✅ **Accept** |
| 二元粒度 + 同一触发词自动判定 | claudecode 看用户描述（"最近一个子问题"）自动切粒度 | ❌ 违反 Decision 4 "医者不可信"——claudecode 自判粒度本身不可靠 |
| 三级粒度（task / sub-problem / session） | 粒度更细 | ❌ 触发词爆炸；现实里 session + sub-problem 已覆盖 95% 场景；task 级与"急诊"语义不符（task 是日常操作，急诊是异常状态） |
| session-only | 保持 v0.1.0 不变 | ❌ 用户已明确反馈粒度不足；不作为强制升级路径 |
| sub-problem-only | 只保留子问题粒度 | ❌ 整个 session 真正失控时仍需要 session-level 报告 |

## 与已有决策的一致性

| 已有决策 | 一致性论证 |
|---------|-----------|
| Decision 1（人工触发） | ✅ sub-problem mode 同样人工触发，不破坏 |
| Decision 2（密集证据） | ✅ sub-problem 模式天然范围小，证据更密集 |
| Decision 3（claudecode 主语） | ✅ 沿用 |
| Decision 4（不调 audit） | ✅ 沿用 |
| Decision 5（与 session-chapter 互斥） | ✅ 沿用（sub-problem mode 也不调 session-chapter） |
| Decision 6（命名 = 医者不可自医） | ✅ skill 名不变；"sub-problem" 是 mode 名，不是 skill 名 |

## 张力点

### 张力 1：claudecode 判定 Scope 起点的可信度

**问题**：sub-problem 模式下，claudecode 自己找"话题转换点"——这与"医者不可信"原则有张力。

**缓解**：
1. claudecode 自判的 Scope 起点必须在报告中**显式标"自判"** + 附 `?`
2. 用户明示的切换词（"另外"/"顺便"/"换个话题"）优先于 claudecode 自判
3. claudecode 找不到明确转换点时，**必须**主动问用户，而不是假装"找到了"

### 张力 2：触发词数量膨胀

**问题**：v0.1.0 7 个触发词 → v0.2.0 11 个触发词。

**评估**：可接受。v0.2.0 触发词分两组（session 7 + sub-problem 4），无歧义。如果未来需要第三组（如 `claudecode tool-triage`），需要重新审视分桶原则。

### 张力 3：与 `/doctor` 的边界

**问题**：Claude Code 内置 `/doctor` 是 plugin/MCP 诊断器，是否会与 `claudecode 子问题急诊` 抢用户？

**评估**：不会。原因：
- `/doctor` 触发词不含 `claudecode` / `急诊` / `triage` 任何子串
- `/doctor` 关注 plugin / MCP / cache 健康度，本 skill 关注 transcript 行为模式
- 详见 [CONTEXT.md Decision 1 Avoid 词](../CONTEXT.md) 的"反 trigger"承诺

## Consequences

**正面**：
- 覆盖 session-level 之外的 60% sub-problem 场景
- 触发词显式分叉，claudecode 不自判粒度 → 与"医者不可信"原则一致
- 报告体积在 sub-problem 模式下显著缩小（G3 默认升级到上下文窗口）
- 与"session-chapter" 形成完整的"搬家 / 急诊"二元决策树

**负面**：
- skill 触发词总数从 7 → 11，可能让用户首次接触时困惑
- sub-problem 边界判定是 claudecode 的"软判断"，不可靠
- 二元粒度可能仍不够细（如一个 sub-problem 内还有"嵌套 sub-sub-problem"），但**不**在本版本处理

## 验证

### 手工验证（用户执行）

1. 在某个真实场景触发 `claudecode 子问题急诊`，观察报告：
   - ✅ `Scope: sub-problem`
   - ✅ 报告体积远小于 session-level
   - ✅ Scope 起点被显式标"自判"或"用户明示"
   - ✅ 证据严格 ≥ Scope 起点
2. 在 sub-problem 报告中 re-verify 一条证据，确认可独立 reproduce

### 回归测试

v0.1.0 已有行为不破坏：
- `医者不可自医` 仍触发 session-level
- 所有不变量（不写 case / 不调 audit / claudecode 主语）保持

## Re-verification（用户独立判断）

- 用户应能通过报告中的 transcript 路径 + Scope 起点，独立 reproduce claudecode 描述的"子问题症状"
- 如果用户认为 Scope 起点选错，应主动指出 → 写新 case 记录"claudecode 边界判定失败"模式

## 详见

- 决策同步：[CONTEXT.md Decision 7](../CONTEXT.md)
- SKILL.md 触发词与何时触发：[../../SKILL.md](../../SKILL.md)
- 报告模板：[../../references/output-template.md](../../references/output-template.md)
- 命名原则参照：[0001-name-healer-paradox.md](./0001-name-healer-paradox.md)
- 证据密度规范参照：[0002-evidence-density.md](./0002-evidence-density.md)
