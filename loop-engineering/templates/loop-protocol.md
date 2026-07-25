# Loop Protocol 模板 (Stage 1 起点)

> **来源**: weiying20260624 week2 全谱系奠基 paper 流水线 (commit 53c2401, 2026-06-29)
> **用途**: 启动一个 1 周+ pipeline 任务时, 复制本协议 + 改 4 占位符即可

## 4 占位符 (必改)

| # | 占位符 | 改成什么 | 例 |
|---|---|---|---|
| 1 | `<TASK_NAME>` | 任务名 (kebab-case) | `week3-cross-dim` / `paper-survey-llm-2026` |
| 2 | `<N_SUB>` | 子方向数 (推荐 7 = C1-C6 + 概念基础) | 7 |
| 3 | `<T_WINDOW>` | 时间窗 | `2020-2026` / `近 1 年` |
| 4 | `<EXPECTED_PAPERS>` | 期望 paper 数 | `30-50` / `30` |

## 协议骨架 (复制下面整段)

```markdown
# Loop Protocol — <TASK_NAME>

> **设计**: YYYY-MM-DD
> **目标**: 1 周跑完 <N_SUB> 个子方向 × 4 stage 串行, 产出 <EXPECTED_PAPERS> 篇 paper
> **不变量**: L4 4-stage 串行 (SEARCH → FILTER → NOTE → REPORT), 0 死循环

---

## §1. 4-stage 流水线

| Stage | 目的 | sub-agent | 输入 | 输出 | 时间 |
|---|---|---|---|---|---|
| 1 SEARCH | N-tool fan-out（6 工具, per [N-tool-search.md](~/.claude/rules/protocols/N-tool-search.md) v1.1.3）抓候选 <!-- 历史标 (2026-07-25 ADR-0056): 原 "5-tool fan-out", 2026-07-13 收口为 N-tool 6 工具 --> | sonnet | query | `search-<C>-<date>.jsonl` | 2-5 min |
| 2 FILTER | A+B+C 三方交叉 | sonnet | jsonl | `filtered-papers-<date>.md` | 5-10 min |
| 3 NOTE | v2.1 模板精读 | sonnet | 通过清单 | `<n>-<slug>.md` | 5-10 min |
| 4 REPORT | 全谱索引 | sonnet | notes | `report-<date>.md` + `.html` | 10-15 min |

## §2. <N_SUB> 子方向 (define 时填)

| 子方向 | 主题 | search 关键词 | 期望候选 | 通过阈值 |
|---|---|---|---|---|
| C1 | <...> | "<query>" | 5-10 | ≥3 |
| C2 | <...> | "<query>" | 5-10 | ≥3 |
| ... | <...> | ... | ... | ... |
| C<N_SUB> | 概念基础 | "<query>" | 5-10 | ≥3 |

## §3. 时间窗 <T_WINDOW>

- 起点: <YYYY-MM>
- 终点: <YYYY-MM>
- 跟 weekly-03 / weekly-04 关联: ...

## §4. 验收标准 (5 字段)

| # | 字段 | 验证 |
|---|---|---|
| 1 | path | `ls -la <deliverable>` |
| 2 | commit | `git log -1 --oneline` |
| 3 | push | `git log @{u}..HEAD` (空=已 push) |
| 4 | owner | 仓归属正确, 双账号铁律 |
| 5 | 验收证据 | 1+ 行可执行命令 |

## §5. 反模式 (必避)

- ❌ 6 sub-agent 全并行 (违反 L4)
- ❌ 单源 web search (违反 §F.1)
- ❌ "差不多完成" (违反 §H 5 字段)
- ❌ 抄模板不改 4 占位符 (复用 ≠ 改版)
```

## 使用流程

```bash
cp templates/loop-protocol.md 00-meta/loop-<TASK_NAME>.md
# 改 4 占位符
sed -i '' 's/<TASK_NAME>/<your-task>/g; s/<N_SUB>/<N>/g; ...' 00-meta/loop-<TASK_NAME>.md
vim 00-meta/loop-<TASK_NAME>.md  # 二次微调
```

## 🔗 相关

- `~/.agents/skills/loop-engineering/SKILL.md` §4-stage 串行架构
- `~/.agents/skills/loop-engineering/templates/filtered-papers.md`
- `~/.agents/skills/loop-engineering/templates/paper-note-v2.1.md`
- `~/.agents/skills/loop-engineering/templates/report-index.md`
- weiying20260624/00-meta/loop-protocol.md (week2 原始版, 390 行)
