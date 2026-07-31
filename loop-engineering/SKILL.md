---
name: loop-engineering
description: |
  pipeline = 决策树 + 4-stage 串行 + 自决矩阵 + 5 字段验收
  把"调研一个领域 / 沉淀一份 paper / 跑完一组 8 决策"这种有终点、有阶段、有可验证交付物的任务, 变成可复用 SOP。
metadata:
  version: "1.0"
  author: mykcs
  category: research
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
triggers:
  - loop-engineering
  - /loop-engineering
  - pipeline
  - research pipeline
  - decision pipeline
  - 调研流水线
  - 串行 sub-agent
when_to_use: |
  loop engineering / 循环 SOP / pipeline 决策树
---

# Loop Engineering Skill

> **pipeline = 决策树 + 4-stage 串行 + 自决矩阵 + 5 字段验收**
>
> 把"调研一个领域 / 沉淀一份 paper / 跑完一组 8 决策"这种**有终点、有阶段、有可验证交付物**的任务, 变成可复用 SOP。
>
> 触发版本: v1.0 (从 weiying20260624 week2 全谱系奠基 paper 抽取, 2026-06-30)
> 适用场景: 任何 1 周以上的调研 / 阅读 / 综述 / 决策组任务。

---

## 🎯 触发词

| 关键词 | 命中 |
|---|---|
| "loop engineering" / "pipeline" / "调研流水线" | ✅ |
| "跑完 X 个决策" / "X 篇 paper 串起来" / "全谱系" | ✅ |
| "week2" / "week3" / "周 pipeline" / "立 pipeline" | ✅ |
| "串行 sub-agent" / "search-filter-note-report" | ✅ |

**不触发**:

- 单文件 typo / Edit (用 Edit)
- 单 paper deep-dive (用 deep-research)
- batch 处理同类 (用 batch 类 skill)
- 1-2 小时查询 (直接调 mcp 工具)

---

## 🏗️ 架构 (4-stage 串行, L4 决策)

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  STAGE 1 │   │  STAGE 2 │   │  STAGE 3 │   │  STAGE 4 │
│  SEARCH  │ ─→│  FILTER  │ ─→│   NOTE   │ ─→│  REPORT  │
│  广撒网  │   │ 精过滤   │   │  精读    │   │  全谱索引│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
     ↓              ↓              ↓              ↓
   jsonl         清单           paper-note     总索引
   (5-10/子)     (~80% 通过)    (4242 行/39)   (md + html)
```

| Stage | 目的 | 输入 | 输出 | 单 sub-agent 时间 |
|---|---|---|---|---|
| 1 SEARCH | N-tool fan-out 抓候选 (N 当前 = 6) | query | `search-<C>-<date>.jsonl` (5-10 条/子方向) | 2-5 min |
| 2 FILTER | A+B+C 三方交叉 | jsonl | `filtered-papers-<date>.md` (排除低质 / 重复) | 5-10 min |
| 3 NOTE | v2.1 模板精读 | 通过清单 | `<n>-<slug>.md` (每篇 100-120 行) | 5-10 min |
| 4 REPORT | 总谱系索引 | notes + 候选 | `report-<date>.md` + `.html` (4 粒度对位) | 10-15 min |

**关键不变量**:

- 每个 stage 独立 commit + push (atomic, 挂了可恢复)
- 每个 stage 用独立 sub-agent (Agent tool, **4 串行不并行**, see §反模式 #1)
- 每个 stage 有自包含产物 (jsonl / md / notes / report)

---

## 🎰 A/B/C/D 切片决策矩阵

第一次开 loop 时, **必跑 4 件 grill**:

| 决策 | 选项 | 推荐 | 理由 |
|---|---|---|---|
| **切片方式** | A 时间 / B 子方向 / C 方法 / D 组合 | **B 子方向** | 跟主题聚类对位, 1 周内可控 |
| **子方向数** | 5 / 6 / 7 / 8+ | **7** (C1-C6 + 概念基础) | 缺概念基础 = 缺根, 8+ 工作量翻倍 |
| **时间窗** | 4 年 / 6 年 / 8 年 / 12 年 | **6 年** (LLM 同期) | 全谱系 + 不含早期 NLP |
| **编排** | L1 6 并行 / L2 单 agent / L3 4 串行 / L4 + 时序错开 | **L4 4 串行 + 时序错开** | 0 死循环风险 + 可监控 |

**claudecode 自决路径** (per `~/.claude/CLAUDE.md` weekly v0.5 + soul v6):

- user 说"按推荐跑到底不问" → 全按推荐执行, 不问
- user 没拍板 → 4 件一起问 (1 段 ≤ 15 行, AskUserQuestion 1 次 4 问题)

详见: [`references/decision-matrix.md`](references/decision-matrix.md)

---

## ⚙️ 5 字段验收 (任务完成前必跑)

| # | 字段 | 验证命令 |
|---|---|---|
| 1 | path | `ls -la <file>` |
| 2 | commit | `git log -1 --oneline` |
| 3 | push | `git log @{u}..HEAD` (空 = 已 push) |
| 4 | CI | `gh api repos/{owner}/{repo}/commits/HEAD/status --jq '.state'` |
| 5 | owner | 仓归属 + 跟 user 意图一致 |

详见: [`scripts/verify-5fields.sh`](scripts/verify-5fields.sh)

---

## 🚫 4 反模式 (必避)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 1 | 6 sub-agent 全并行 | 1 挂 = 全盘重起 + 监控难 | **L4 4 串行 + 时序错开** |
| 2 | 单源 web search | 1 工具 = 单点故障 | N-tool fan-out (per SSOT §1, N 当前 = 6) |
| 3 | "差不多完成" | 缺 5 字段验收 | 必跑 §H.1 自检表, 缺一项 = FAIL |
| 4 | 抄模板不改 | 复用 ≠ 改版 | 每次必改: 子方向 / 时间窗 / 验证标准 |

详见: [`references/anti-patterns.md`](references/anti-patterns.md)

---

## 📚 4 模板 (Stage 2-4 产物)

| 模板 | 适用 Stage | 路径 |
|---|---|---|
| `loop-protocol.md` | Stage 1 起点 | [`templates/loop-protocol.md`](templates/loop-protocol.md) |
| `filtered-papers.md` | Stage 2 | [`templates/filtered-papers.md`](templates/filtered-papers.md) |
| `paper-note-v2.1.md` | Stage 3 | [`templates/paper-note-v2.1.md`](templates/paper-note-v2.1.md) |
| `report-index.md` | Stage 4 | [`templates/report-index.md`](templates/report-index.md) |

**模板使用规则**: 复制模板 → 改 4 处 (子方向 / 时间窗 / 通过阈值 / 验收字段) → 跑 SOP。

---

## 🔧 3 脚本 (工具)

| 脚本 | 用途 | 路径 |
|---|---|---|
| `loop-status.sh` | 看当前 loop 跑到哪 / 下一步 | [`scripts/loop-status.sh`](scripts/loop-status.sh) |
| `verify-5fields.sh` | §H.1 5 字段自检表 | [`scripts/verify-5fields.sh`](scripts/verify-5fields.sh) |
| `commit-and-push.sh` | atomic commit + smart-push | [`scripts/commit-and-push.sh`](scripts/commit-and-push.sh) |

---

## 📐 调用示例

```bash
# 1. 复制 skill 目录
cp -r ~/.agents/skills/loop-engineering/ ./my-week3-loop/

# 2. 改 4 模板的关键字段 (子方向 / 时间窗 / 验收)
vim templates/loop-protocol.md
vim templates/filtered-papers.md

# 3. 跑 stage-by-stage, 每阶段 atomic commit
bash scripts/loop-status.sh            # 看进度
bash scripts/commit-and-push.sh "stage 1 search"
... stage 2 filter ...
... stage 3 note ...
... stage 4 report ...

# 4. 验收
bash scripts/verify-5fields.sh ./deliverables/
```

---

## 🔗 相关

- `~/.agents/skills/rich-audit/` (重度审计, 5 Layer + 8 步循环, 进化层可叠加)
- `~/.agents/skills/teacher-report/` (单 paper deep-dive 走这)
- `~/.claude/CLAUDE.md` weekly v0.5 + soul v6 (本 skill 设计 basis)
- weiying20260624 week2 全谱系奠基 paper (本 skill source of truth, commit 53c2401 → cb76b63)

---

## 🧪 演化历史

- v1.0 (2026-06-30): 立。从 weiying20260624 week2 抽, 7 子方向 × 4 stage 串行, 39 paper, 0 死循环。
