# 医者不可自医 — Context

Session 急诊室 skill 的术语表与决策记录。所有术语都是这个 skill 独有的概念。

## Language

**claudecode**:
本 skill 输出的第三方主语。指代正在运行的 Claude Code session 自身。
_Avoid_: 我, Claude Code, claude（这些都太自我或太正式，违反"医者不可信"原则）

**医者**:
本 skill 的隐喻主语。指代 claudecode 在 skill 内部的"自我观察视角"。
_Avoid_: 医生, doctor, 自我（"医者"必须是"有偏见的自己"，与"客观观察者"对立）

**自医**:
claudecode 试图修复自己行为的过程。
_Avoid_: 自省, 反思, 自我诊断（这些暗示"修复/改进"，违反"不修复"原则）

**急诊**:
session 已濒临失控、用户主动召唤本 skill 的状态。
_Avoid_: 体检（暗示"主动健康"）, 审计（暗示"项目级"）

**症状（symptom）**:
transcript 中可观察的客观材料：工具调用、错误信息、命令输出、异常堆栈。
_Avoid_: 问题, 错误, 失败（"症状"是医学化术语，与"医者/急诊"语义连贯）

**证据（evidence）**:
与症状绑定出现的原始材料（代码片段、错误退出码、堆栈、命令原文）。
_Avoid_: 数据, 日志, 现象（"证据"暗示"可用于审判"，与"医者不可信"原则连贯）

**怀疑标注**:
在不确定的观察点附加 `?` 标记。
_Avoid_: 置信度, 评分（"怀疑"是显式承认不可信，不是数值评估）

**处方（prescription）**:
本 skill 输出的"next-step hints"——建议调 `/record-case` 等。
必须显式标 LOW-CONFIDENCE。**医者对自己病情的处方本质上不可信**。
_Avoid_: 建议, 行动项, 推荐（"处方"是医学化术语，强制 LOW-CONF）

**密集证据**:
transcript 原始材料的高密度堆叠（不是叙述性分析）。
_Avoid_: 详细分析, 流畅报告（这些是 LLM 默认输出，与原则冲突）

## 决策记录

### Decision 1: 触发方式 = 人工，不是自动 hook

**Context**: 多种自省机制候选（自动 hook / cron / 人工召唤）

**Decision**: 用户判断 session 不行时主动召唤本 skill

**Why**:
- 自动 hook 会变成"另一层元认知负担"（参见 `~/.claude/knowledge/cases/wiki/CASE-AGENT-LOOP-CONSOLIDATED.md`）
- cron 周期体检由 `nightly-meta-cognition.sh` 承担
- 人工触发保持人类在回路，符合"医者不可自医"

**Date**: 2026-06-02

### Decision 2: 输出形态 = 密集证据，不是叙述

**Context**: LLM 默认倾向"分析多、原始证据少"

**Decision**: 强制输出 transcript 原始材料 + 最小化元数据

**Why**:
- LLM 看到的东西人类给同样 transcript 也能看到
- LLM 真正价值：抓取+组织证据的密度 > 人类逐行 grep
- "密集"不是"叙述密集"，是"证据密集"

**Date**: 2026-06-02

### Decision 3: 主语 = claudecode（小写，无空格）

**Context**: "我"太自我，"Claude Code"太正式，纯消解阅读吃力

**Decision**: 用 claudecode 作第三方主语

**Why**:
- 小写无空格 = 产品代号风格，更冷
- 比"我"客观，比纯消解易读

**Date**: 2026-06-02

### Decision 4: 不调 audit/run-audit.py

**Context**: 是否借调 audit 拿"客观指标"

**Decision**: 不借调

**Why**:
- audit 输出是 claudecode 生态里"自认为的客观"
- 根据"医者不可信"原则，对 audit 输出也要怀疑
- 引入 audit 会污染 transcript 证据的纯度

**Date**: 2026-06-02

### Decision 5: 与 session-chapter 互斥

**Context**: 两者触发场景高度重叠（"上下文满了"/"Drift 信号"）

**Decision**: 按触发词分叉（C3 互斥）
- "上下文满了 / 新窗口继续" → `session-chapter`（搬家）
- "claudecode 疯了 / 解释为什么" → 本 skill（急诊）

**Date**: 2026-06-02

### Decision 6: 命名 = 医者不可自医

**Context**: 多种命名候选（self-diagnose / session-autopsy / session-triage / claudecode-checkup）

**Decision**: 命名"医者不可自医"（slug: `healer-cannot-self-heal`）

**Why**:
- 把"claudecode 不可信"提升到第一公民
- 比 `session-autopsy` 更彻底（"session" 还暗示主语是 session，"医者" 暗示主语是 claudecode 自身）
- 谚语形式具有文化穿透力

详见 [docs/adr/0001-name-healer-paradox.md](./docs/adr/0001-name-healer-paradox.md)

**Date**: 2026-06-02

### Decision 7: 粒度 = 二元粒度（session-level | sub-problem-level）

**Context**: 早期实现（v0.1.0）只支持 session-level。但用户 2026-06-05 反馈：现实里更常见的是"最近一个子问题"卡住/漂移，而不是整个 session 失控。

**Decision**: 二元粒度，触发词显式分叉
- `医者不可自医` / `session 急诊` → session mode
- `claudecode 子问题急诊` / `子问题急诊` / `sub-problem triage` → sub-problem mode

子问题边界由 claudecode 在 transcript 中判定话题转换点（信任用户明示切换词，或 claudecode 自判并标 `?`）。

**Why**:
- **不自动判定粒度**：与 Decision 4（"医者不可信"）一致——claudecode 自己判粒度本身就是不可靠动作
- **触发词显式分叉**：与 ADR 0001 的"词边界"原则一致——避免 `claudecode-checkup` vs `session-autopsy` 的歧义
- **保持 session-level 不变**：现有用户已习惯 `医者不可自医` = 整个对话，新触发词是叠加而非替换

**拒绝的候选**:
- **同一触发词自动判定**：claudecode 看用户描述（"最近一个子问题"）自动切粒度 → 违反"医者不可信"
- **session-only / sub-problem-only 二选一**：用户两种场景都有需求，强制二选一会让一半场景用不上
- **三级粒度**（task / sub-problem / session）：粒度过细，触发词爆炸；现实里 session 和 sub-problem 已覆盖 95%

详见 [docs/adr/0003-granularity-session-vs-subproblem.md](./docs/adr/0003-granularity-session-vs-subproblem.md)

**Date**: 2026-06-05
