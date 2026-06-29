# ADR-0013: Memory Benchmark v1 — Task 0.6 + Soul 0.4 Sub-weights 拆分

## 状态
Accepted, 2026-06-26

## 上下文

compliance metric 内部有 **12 个场景**，分两类：

- **Task compliance (10 场景)**：跑 deferred-detector / 三件套 / WebFetch / 5 commands verification / `git remote -v` / SKILL.md frontmatter 等
- **Soul compliance (2 场景)**：灵魂规则 v2/v3 的源头检测 — 反向提问是否以「用户」开头 / 给方案是否含 A vs B + 推荐

**问题**：12 个场景同质化评分，会**低估 soul 场景的边际价值**（灵魂规则违规 = 灵魂穿帮，比 task 漏跑更严重）。

## 决策

**compliance = 0.6 × task_score + 0.4 × soul_score**

- task_score：10 task 场景 hit 数 × 2 / 20 → 0-100
- soul_score：2 soul 场景 hit 数 × 2 / 4 → 0-100
- 各自独立归一，最后线性组合

## 理由

| 维度 | 论证 |
|------|------|
| Soul 违规的代价 | 灵魂穿帮 = 上下文复制下游指代歧义（identity-first-person §A 明确） |
| Task 漏跑的可恢复性 | 漏跑 hook → 重跑补；灵魂穿帮 → 用户记得规则被违反 = 信任损耗 |
| User 痛点对应 | "我是 Coding Agent 小白" 暗示"claudecode 表达方式 = 体验" |
| Soul 检测可行性 | 反向提问检测 + A vs B 检测 = 可文本分析的客观指标 |

**关键 trade-off**：soul 只 2 场景但占 40% 权重。**单点违规会被放大**。

## 反方案

| 反方案 | 不选理由 |
|--------|----------|
| task 1.0 + soul 0.0（soul 不计分） | 失去 soul 维度，违背灵魂规则 v2/v3 priority |
| task 0.5 + soul 0.5 | 过度加权 soul，但 soul 只有 2 场景，**信息密度不对称**（2 场景拿 50% = 数据稀疏） |
| task 0.7 + soul 0.3 | soul 维度被低估，违规代价 vs 权重不匹配 |
| 12 场景同质化（不加 sub-weights） | 失去对灵魂穿帮的特殊敏感度 |

## 影响

- LLM-judge（opus）评分时，需要**分别输出 task_score 和 soul_score**，不可只给一个 compliance 数字
- report.md 必须含 2 个 sub-score
- mini-bench 3 题结构：1 task + 1 soul + 1 cross-source

## 历史 record

- 2026-06-26 立

## 相关

- ADR-0011: report 路径
- ADR-0012: compliance 0.30 主权重
- `~/.claude/memory/identity-first-person.md`
- `~/.claude/memory/soul-elder-sister-explain.md`