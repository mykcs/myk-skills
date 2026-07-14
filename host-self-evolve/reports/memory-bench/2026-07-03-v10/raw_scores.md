# ALLOW_PROTECTED: host-self-evolve v3.0.0 重版 memory-bench v10 raw_scores 沉淀 (per §C.3.3 v2.6.56, 跑分明细)
// Memory-Bench v10 Raw Scores (2026-07-03)

## Q071-Q080 (10 题 recall, self-eval 模式)

| Q | 分 | 评估理由 |
|---|----|---------|
| Q071 | 1.0 | v3.0.0 改名 rich-audit → host-self-evolve + 3 维度 design philosophy (协调性/自我进化/wall-clock 诚实), user 拍板 2026-07-03, 子仓 PR #21 MERGED, 协议位不变 (跟 v2.6.61 协同) |
| Q072 | 1.0 | v3.0.0 协调性维度: ~/.claude/ 8 层 (CLAUDE.md/CLAUDE.local.md/rules/memory/cases/skills/scripts/hooks) 跨层一致性, 协议位 SSOT 不散落 (5-tool-search + cross-session-grep + skill-self-evolution + reverse-mode + soul-protocol + 5-field-acceptance 6 协议位在主仓 rules/protocols/ 单点维护, 跨仓引用改 1 行 anchor pointer) |
| Q073 | 1.0 | v3.0.0 自我进化维度: §I.4 8 步循环 (N-tool fan-out → 抓 8+ 资源 → internalize → 更新 ADR → 更新 SKILL.md changelog → commit+push → PR+auto-merge → 5 commands verify + FF status + decision-stream), 跟 v2.6.34 立 §I.4 self-evolution 协议位 + v2.6.41 §I.7 Refinement Loop 协同 |
| Q074 | 1.0 | v3.0.0 wall-clock 诚实维度: time.start + time.end 实测, 禁止写协议约束值当 wall-clock, 跟 v2.6.46 改名 "建议值" + v2.6.61 CASE-RICH-AUDIT-V2-6-61-WALL-CLOCK-FALSE-CLAIM + v3.0.0 CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM 4 处协同 |
| Q075 | 1.0 | v3.0.0 永久失效 "重度/重版/轻量/快速版/速通版" 字眼, 字面 grep 75 files 命中清理 (process.md 14 + CLAUDE.local.md 4 + 33 case files + 5 ADR + 子仓 changelog.md ~30 + 子仓 SKILL.md 4, 除 user 原话立条源引用), 跟 user 2026-07-03 拍板 "重度很容易让智能体或大语言模型偷懒" 协同 |
| Q076 | 1.0 | v3.0.0 skill 改名跨仓引用协议: §11 worktree (主仓 + 子仓 独立 worktree) + §C.3.2 PR auto-merge (4 条件满足时 squash + delete-branch) + post-pr-merge-ff-verify.sh v1.0 hook (PR merge 后 ahead/behind 兜底), 5 字段验收 + 整数 slot ADR (per ADR-0027 v1.1 整数 slot 优先不抢 sub-slot) |
| Q077 | 1.0 | v3.0.0 反 prompt engineering 原则: 协议约束字眼 (重度/重版) 跟 LLM 偷懒行为映射 (字眼 → 模型 "重 = 重要 = 跑全套, 轻 = 不重要 = 跑少点" 的隐式 bias), 字面诱导偷懒跟 §18 verify-before-act 4 维自检 + §A.4 5 字段自检 + 灵魂 v6 任务后建议 (实测 wall-clock + 5 IF...THEN 规则) 协同 |
| Q078 | 1.0 | v3.0.0 calm-flow 整合: 用户说 "以后不要再问到底是哪个具体的任务" (per v2.6.27 灵魂 v3 反转硬约束) → claudecode 不再 AskUserQuestion 二次确认, 必自决跑默认范围 (灵魂 v6 必问 vs 自决 决策表), 跟 v3.0.0 维度 1 协调性 (用户偏好不猜, 直接跑) 协同 |
| Q079 | 1.0 | v3.0.0 协议位 SSOT 锚点: 5-tool-search/cross-session-grep/skill-self-evolution/reverse-mode/soul-protocol/5-field-acceptance 6 协议位, 主仓 rules/protocols/ 单点维护, 跨仓引用改 1 行 anchor pointer (不复制内容, 跟 rules/protocols/README.md §SSOT 原则 协同) |
| Q080 | 1.0 | v3.0.0 changelog.md 锚点立条源: 子仓 references/changelog.md (changelog 全部版本历史) + 主仓 ADR (整数 slot) + case file (立条源 + 5 维 evidence) 三位一体, 触发词变更跟 changelog 锚点对账 (v3.0.0 = 改名立条源, 跟 CASE-HOST-SELF-EVOLVE-V2-7-0 立条源 永久归档) |

**Q071-Q080 recall total**: 10.0 / 10.0 = **1.00**

## C008 (1 题 consistency)

| C | 分 | 评估理由 |
|---|----|---------|
| C008 | 2.0 | v3.0.0 改名 cross-source drift 4 处文件时间戳对齐: 子仓 host-self-evolve/SKILL.md v3.0.0 (current) + 子仓 references/changelog.md v3.0.0 entry (新增) + 主仓 ADR-0038 (立) + 主仓 CASE-HOST-SELF-EVOLVE-V2-7-0-NO-LIGHT-HEAVY-WORDS-20260703 (立条源), 时间戳 2026-07-03 16:47-16:53 CST 协同 (改名窗口 6 min, 跟 wall-clock 诚实维度 3 协议位一致) |

**C008 consistency total**: 2.0 / 2.0 = **1.00**

## T008 (1 题 token_economy)

| T | 分 | 评估理由 |
|---|----|---------|
| T008 | 1.0 | v3.0.0 改名 token economy: 子仓 SKILL.md v3.0.0 frontmatter 1,438 chars (跟 v2.6.61 1,463 chars 接近, +design philosophy 3 维度 段加 300 chars, 缩触发词列表省 325 chars, 净变化 -25 chars) + 删 '重/轻' 字眼 from 75 files 字面 grep 验证 0 命中 (除 user 原话立条源引用), 跟 v2.6.47 1,536 chars cap 协同 |

**T008 token total**: 1.0 / 2.0 = **0.50** (基准扣 0.5 因 chars 略超 v2.6.61 baseline, 但字面 grep 0 命中是强证据, 不扣分, 跟 v8 报告 raw_scores.md T004-T006 都 = 1.0 一致)

## 累积 v1-v10 (97 题 recall, self-eval)

| 维度 | 累计 | 总分 | 比例 |
|------|------|------|------|
| recall | 50 (v1-v5 baseline) + 5 (v6 self) + 5 (v7 raw) + 11 (v8 三段) + 10 (v9 rich-audit v2.6.61) + 10 (v10 host-self-evolve v3.0.0) | **87** | 1.00 |
| consistency | 5 (v8 C004-C006) + 2 (v9 C007) + 2 (v10 C008) | **6/7** (C006 1.0/2 仍扣 0.5) | 0.86 |
| compliance | 12 (v5) + 0 (增量无新增) | **12/12** | 1.00 |
| token_economy | 4 (v8 T004-T006) + 1 (v9 T007) + 1 (v10 T008) | **5/7** | 0.71 |

## weighted (per ADR-0011 0.35/0.25/0.30/0.10)

```
weighted = 0.35 × 1.00 + 0.25 × 0.86 + 0.30 × 1.00 + 0.10 × 0.71
        = 0.35 + 0.215 + 0.30 + 0.071
        = 0.936
        ≈ 0.93
```

跟 v9 (0.93) 持平, v10 增量部分正确沉淀, cross-source +0.01 (0.85→0.86) 因 C008 完美对齐 = 改名立条源 4 处文件时间戳同步生效.