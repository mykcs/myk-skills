# ADR 0001: 命名 — 医者不可自医

**Status**: Accepted
**Date**: 2026-06-02
**Context**: Session 急诊室 skill 的命名抉择

## Context

需要一个 skill 名来表达"claudecode 在 session 失控时做自我剖析"的概念。

### 候选

| 候选 | 隐喻 | 评价 |
|------|------|------|
| `self-diagnose` | 自我诊断 | "self" 暗示了"自我修复"，与"不修复"原则**直接冲突** |
| `session-autopsy` | session 尸检 | 医学化、承认 session 濒死、不暗示修复，但"session" 作为主语淡化了"不可信"原则 |
| `session-triage` | session 分诊 | 还承认"可能救活"，与"claudecode 不可信"**略有冲突** |
| `claudecode-checkup` | claudecode 体检 | 暗示"修好"，与"不落地"**直接冲突** |
| **`医者不可自医`** | 谚语 | 把"claudecode 不可信"提升到第一公民 |

## Decision

**命名：医者不可自医**（slug: `healer-cannot-self-heal`）

把"claudecode 不可信"提升到第一公民，作为 skill 的本质声明。

### Slug 选择

- ✅ `healer-cannot-self-heal`（英文谚语，保留完整意蕴，与"医者悖论"原则对齐）
- ❌ `healer-paradox`（概念化，但丢失"自医"动作）
- ❌ `yi-zhe-bu-ke-zi-yi`（拼音，国际理解不便）

### 触发词

主触发：
- 中文：`医者不可自医`
- 英文：`healer-cannot-self-heal`

副触发：
- `session 急诊`
- `claudecode 自检`
- `急诊`
- `session-autopsy`
- `claudecode-checkup`

## Consequences

**正面**：
- 直接传达"claudecode 不可自医 = claudecode 不能修复自己"的核心原则
- "医者"作为隐喻主语，与"症状/处方/急诊"等医学化术语自然衔接
- 谚语形式具有文化穿透力

**负面**：
- 谚语形式的命名与现有 `grill-me` / `record-case` / `session-chapter` 等"功能命名"风格不一致
- 国际开发者可能不熟悉这个中文谚语 → 配套英文 slug `healer-cannot-self-heal` 缓解
- 谚语隐喻可能让"何时触发"语义模糊 → 必须配 SKILL.md 的"何时触发"表强制明确

**Reject**:
- `self-diagnose`: "self" 暗示了修复动作
- `session-autopsy`: "session" 作为主语，淡化了"不可信"原则
- `session-triage`: "triage" 暗示"分诊后可能救活"

## Grill 记录

通过 `/grill-with-docs` skill 完成 5 轮访谈：
1. "自我"指代 → 当前 Claude session（急诊室）
2. 诊断范围 → 症状描述 + 怀疑（不修复）
3. 输出形态 → 密集证据 + claudecode 主语 + G4 粒度
4. 与已有机制边界 → 与 session-chapter 互斥 / 不调 audit / next-step hints LOW-CONF
5. 命名 → 医者不可自医（用户主动推翻 session-autopsy）
