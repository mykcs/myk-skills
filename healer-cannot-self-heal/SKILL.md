---
name: healer-cannot-self-heal
description: |
  医者不可自医 — Session 急诊室。claudecode 在判断当前对话已失控（上下文耗尽、反复卡同一处、漂移）时，
  不修复自己，只输出一份"密集证据 + 最小化怀疑标注"的症状报告，让用户（医者）做判断。

  核心原则：医者不可信 → 输出保持怀疑语气，处方显式标 LOW-CONFIDENCE。
  触发：用户判断 session 不行时主动召唤（不是自动 hook）。
  与 session-chapter 互斥：session-chapter 是"搬家"，本 skill 是"急诊"。
  反 trigger（绝不接管）：Claude Code 内置 `/doctor`（plugin/MCP 诊断器）不是本 skill 别名，触发词不与之重叠。`doctor` 与"医者"语义隔离 — 详见 CONTEXT.md Decision 1 Avoid 词。

  触发词:
    主: 医者不可自医, healer-cannot-self-heal
    副: session 急诊, claudecode 自检, 急诊, session-autopsy, claudecode-checkup
license: MIT
metadata:
  version: "0.1.0"
  author: mykcs
  category: self-reflection
  triggers:
    - 医者不可自医
    - healer-cannot-self-heal
    - session 急诊
    - claudecode 自检
    - 急诊
    - session-autopsy
    - claudecode-checkup
  tags:
    - session
    - diagnosis
    - introspection
    - symptom-report
    - evidence
    - healer-paradox
user-invocable: true
---

# 医者不可自医 — Session 急诊室

> **核心原则**：医者无法自医。所以本 skill 不修复自己。
> 它只描述症状，且必须保持怀疑语气。
> 它产出的"处方"显式标注为 LOW-CONFIDENCE，因为医者对自己病情的判断本质上不可信。

## 何时触发

| 信号 | 含义 | 触发动作 |
|------|------|---------|
| "上下文满了 / 快到 limit" | token 接近耗尽 | 考虑 `/session-chapter`（搬家） |
| **"claudecode 反复卡同一处"** | 行为漂移 | **本 skill** |
| **"claudecode 疯了 / 解释为什么"** | 失控 | **本 skill** |
| **"session 急诊"** | 主动召唤 | **本 skill** |
| "新窗口继续" | session 还能抢救 | `/session-chapter`（不调本 skill） |

## 与 session-chapter 的边界（C3 互斥）

- **`session-chapter`**：session 还能抢救 → 保留状态 → 开新窗口继续
- **本 skill**：session 即将死 / 已失控 → 不修复 → 只剖析

## 输出 contract

报告写到：`~/.claude/state/healer-reports/{session-id}-{YYYYMMDD-HHMMSS}.md`

### 必须包含

1. **transcript 原始路径**（让用户能 re-verify）
2. **claudecode 作第三方主语**（不写"我"）
3. **密集证据**（不是叙述）：
   - 默认：**完整工具调用**（input + output + error）
   - 关键反复处：升级到**上下文窗口**（前后各 N 行）
4. **怀疑标注**：只在不确定时标 `?`，不在每条都加
5. **`next-step hints` 区**：每条标 LOW-CONF
   - 建议调 `/record-case` (conf: low)
   - 建议调 `/rich-audit` (conf: low)
6. **不落地**：不写 case、不改规则、不调 evolution-trigger

### 报告模板

参见 [references/output-template.md](./references/output-template.md)

## 不变量（绝对禁止）

- ❌ 不写"我错了" / "我搞砸了"（无道歉规则的延伸）
- ❌ 不输出没有证据的叙述
- ❌ 不调 `audit/run-audit.py`（保持证据纯度）
- ❌ 不调 `record-case` / `rich-audit` / `evolution-trigger`（只建议，不落地）
- ❌ 不把处方当作事实

## 相关机制

| 机制 | 关系 |
|------|------|
| `session-chapter` | 互斥（搬家 vs 急诊） |
| `audit/run-audit.py` | 不调（避免污染证据纯度） |
| `record-case` | 只在 next-step hints 中建议，不主动调 |
| `rich-audit` | 只在 next-step hints 中建议，不主动调 |
| `nightly-meta-cognition.sh` | 时间维度不同（cron 周期 vs 人工急诊） |
| `evolution-trigger.sh` | 触发器 vs 报告器，不冲突 |
| `deja-vu-gate` | 30 天复发 vs 当下 session，不冲突 |
| `~/.claude/rules/behavioral-deja-vu-gate.md` | 同一文件，作为"硬化机制"被 next-step hints 引用 |
| `~/.claude/knowledge/cases/wiki/CASE-AGENT-LOOP-CONSOLIDATED.md` | 自动 hook 易引发循环的案例，作为"为什么是人工触发"的依据 |

## 详见

- 术语表与决策记录：[CONTEXT.md](./CONTEXT.md)
- 命名抉择 ADR：[docs/adr/0001-name-healer-paradox.md](./docs/adr/0001-name-healer-paradox.md)
- 证据密度规范 ADR：[docs/adr/0002-evidence-density.md](./docs/adr/0002-evidence-density.md)
- 报告模板：[references/output-template.md](./references/output-template.md)
