---
name: healer-cannot-self-heal
description: |
  医者不可自医 — Session 急诊室。claudecode 在判断当前对话已失控（上下文耗尽、反复卡同一处、漂移）时，
  不修复自己，只输出一份"密集证据 + 最小化怀疑标注"的症状报告，让用户（医者）做判断。

  核心原则：医者不可信 → 输出保持怀疑语气，处方显式标 LOW-CONFIDENCE。
  触发：用户判断 session 不行时主动召唤（不是自动 hook）。
  与 session-chapter 互斥：session-chapter 是"搬家"，本 skill 是"急诊"。
  反 trigger（绝不接管）：Claude Code 内置 `/doctor`（plugin/MCP 诊断器）不是本 skill 别名，触发词不与之重叠。`doctor` 与"医者"语义隔离 — 详见 CONTEXT.md Decision 1 Avoid 词。

  粒度（v0.2.0）: 两种独立 mode，触发词显式分叉
    - session-level: 整个对话失控
    - sub-problem-level: 最近一个子问题卡住（更常见 — 用户反馈 2026-06-05）

  触发词:
    主（session-level）: 医者不可自医, healer-cannot-self-heal
    主（sub-problem-level）: claudecode 子问题急诊, 子问题急诊, sub-problem triage, subproblem-triage
    副: session 急诊, claudecode 自检, 急诊, session-autopsy, claudecode-checkup
license: MIT
metadata:
  version: "0.2.0"
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
    - claudecode 子问题急诊
    - 子问题急诊
    - sub-problem triage
    - subproblem-triage
  tags:
    - session
    - diagnosis
    - introspection
    - symptom-report
    - evidence
    - healer-paradox
user-invocable: true
version: "1.0.0"
author: "mykcs"
last_updated: "2026-07-19"
---

# 医者不可自医 — Session 急诊室

> **核心原则**：医者无法自医。所以本 skill 不修复自己。
> 它只描述症状，且必须保持怀疑语气。
> 它产出的"处方"显式标注为 LOW-CONFIDENCE，因为医者对自己病情的判断本质上不可信。

## 何时触发

### session-level（整个对话失控）

| 信号 | 含义 | 触发动作 |
|------|------|---------|
| "上下文满了 / 快到 limit" | token 接近耗尽 | 考虑 `/session-chapter`（搬家） |
| **"claudecode 反复卡同一处"** | 行为漂移 | **本 skill（session mode）** |
| **"claudecode 疯了 / 解释为什么"** | 失控 | **本 skill（session mode）** |
| **"session 急诊"** | 主动召唤 | **本 skill（session mode）** |
| "新窗口继续" | session 还能抢救 | `/session-chapter`（不调本 skill） |

### sub-problem-level（最近一个子问题卡住）

> 用户反馈 2026-06-05：现实里更常见的不是整个 session 失控，而是"这个对话里最近一个子问题"反复卡、漂移、跑偏，但 session 整体还能抢救。

| 信号 | 含义 | 触发动作 |
|------|------|---------|
| **"claudecode 卡这个子问题了"** | 单个子问题反复失败 | **本 skill（sub-problem mode）** |
| **"刚才那个子问题到底怎么回事"** | 用户想知道子问题根因 | **本 skill（sub-problem mode）** |
| **"claudecode 在 X 这个事上疯了"** | X = 显式指定的子问题 | **本 skill（sub-problem mode）** |
| **"子问题急诊"** | 主动召唤 | **本 skill（sub-problem mode）** |

### 粒度判定（caller 自决）

**claudecode 不自动判定粒度**——遵循"医者不可信"原则（参见 [CONTEXT.md Decision 4](./CONTEXT.md)）。caller（用户）通过触发词显式选择 mode：

- `医者不可自医` / `session 急诊` → session mode
- `claudecode 子问题急诊` / `子问题急诊` / `sub-problem triage` → sub-problem mode

如果 caller 词义模糊（如只说"急诊"），claudecode 应**主动问粒度**而不是自己猜。

## 与 session-chapter 的边界（C3 互斥）

- **`session-chapter`**：session 还能抢救 → 保留状态 → 开新窗口继续
- **本 skill**：session 即将死 / 已失控 → 不修复 → 只剖析

## 输出 contract

报告写到：`~/.claude/state/healer-reports/{session-id}-{YYYYMMDD-HHMMSS}[-{scope}].md`

`{scope}` 仅在 sub-problem mode 下出现：
- session mode（默认）：文件名不附加 scope
- sub-problem mode：`-subproblem-{n}.md`（n = 子问题序号，claudecode 自增）

### 必须包含

1. **`Scope` 字段**（必填）：
   - `session` = 整个对话范围
   - `sub-problem` = 最近一个子问题范围（claudecode 判定话题转换点作为起点）
2. **transcript 原始路径**（让用户能 re-verify）
3. **claudecode 作第三方主语**（不写"我"）
4. **密集证据**（不是叙述）：
   - 默认：**完整工具调用**（input + output + error）
   - 关键反复处：升级到**上下文窗口**（前后各 N 行）
   - sub-problem mode 下：证据范围 = "话题转换点 L_start → 现在 L_end"，**不**回溯更早
5. **怀疑标注**：只在不确定时标 `?`，不在每条都加
6. **`next-step hints` 区**：每条标 LOW-CONF
   - 建议调 `/record-case` (conf: low)
   - 建议调 `/rich-audit` (conf: low)
7. **不落地**：不写 case、不改规则、不调 evolution-trigger

### sub-problem mode 专属

- **边界判定**：claudecode 在 transcript 中找"最近一次明确的话题/任务切换"作为子问题起点 `L_start`
  - 判定信号：用户用 "另外" / "顺便" / "回到" / "换个话题" / "刚才说的 X" 等明示切换 → 信任用户词
  - 判定信号：claudecode 观察到工具调用上下文从 A 主题跳到 B 主题 → 标记 `?` 标"claudecode 自判"
  - 判定信号：用户未明示切换但子问题明显卡住 → 取最近一次"该子问题首次出现"的 L 作为起点
- **报告体积**：sub-problem 模式天然较小（不抓整 session），允许 G3 升级（始终上下文窗口）
- **递归保护**：sub-problem mode 报告**不**包含其他 sub-problem mode 报告的内容（避免嵌套）

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
