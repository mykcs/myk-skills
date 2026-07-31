---
name: paper-card-formats
description: |
  teacher-report 论文 paper card v0.13.6 整合入口 (2026-06-17 新增). v0.4.0 紧凑 (7 行) + v0.11.0 完整 (10 行) 2 个 active 版本选型指南 + 22 项 LLM 自检 (Check 1-22) + 论文重组 (1.3.A 顶会 / 1.3.B 主题表) 选型. 替代原 paper-card-v04.md + paper-card-v11.md 2 个索引文件.
---

# Paper Card v0.13.6 选型 (2026-06-17 整合)

> **核心**: 2 个 active paper card 格式 (v0.4.0 紧凑 + v0.11.0 完整) + 1 套 22 项 LLM 自检清单 (Check 1-22) + 与 §1.3 论文重组 (1.3.A 顶会 / 1.3.B 主题表) 联动.

## 1. 选型决策树 (v0.13.6)

```
论文总数 N
  ├─ N ≤ 3 → v0.11.0 完整版 (10 行/paper, 含 status / arXiv 状态 / paper URL)
  ├─ 3 < N < 10 → 视场景
  │   ├─ 套磁信深度引用 → v0.11.0 完整版
  │   └─ 论文列表浏览 → v0.4.0 紧凑版
  └─ N ≥ 10 → 重组为 §1.3.A 顶会 10 篇 (v0.3.0 增强 h3 + 12 行) + §1.3.B 主题表 (5-7 主题, v0.4.0 紧凑)
      (v0.13.0 NEW: 不再列 N 篇, 必重组; v0.13.2: 1.3.A 顶会 10 改 v0.3.0 增强 h3 + 12 行)
```

**v0.13.0 NEW 硬要求**:
- **论文 ≥ 10 篇必重组** §1.3.A 顶会 10 (callout 4 行 metadata) + §1.3.B 主题表 (5-7 主题 table)
- **1.3.A 顶会 10 篇**: 选 oral/spotlight/long talk/BP Finalist, 跨方向覆盖
- **1.3.B 主题表**: 5-7 主题, 每主题 1 callout 内部 table, 4 列 (# / 标题 / 会议 / arXiv)
- **1.3.C 趋势**: 1 callout 5 观察点 (方向漂移 / 主线强度 / 次主线占比 / 国际合作 / 顶会比例)

## 2. v0.4.0 紧凑版 (7 行/paper)

**适用**: 论文 3-10 篇浏览, 1.3.A 顶会 10 callout, 需 scannable 横向对比

**模板**:

```xml
<h3>{N}. {TITLE} <a href="https://arxiv.org/abs/{ARXIV_ID}">[arXiv {ARXIV_ID}]</a></h3>
<p>{AUTHOR_LIST_WITH_INLINE_MARKERS}</p>
<p>{VENUE} {YEAR} ({ROLE})</p>
<p>大领域：{D}</p>
<p>中方向：{M}</p>
<p>小任务：{T}</p>
<p>子技术：{S}</p>
```

**详细规范**: `references/paper-card.md` (295 行 v0.4.0 完整规范, 含 inline 标记规则 / 13 项 v0.4.0 自检 / 与 v0.3.9 对比 / 12 papers 真实样例 / 迁移路径)

## 3. v0.11.0 完整版 (10 行/paper)

**适用**: 论文 ≤ 3 篇, 套磁信深度引用, 单篇 deep-dive

**模板**:

```
1. {论文完整标题 (verbatim, 不可改字/改序/省字)}
{AUTHOR_LIST_WITH_INLINE_MARKERS_CHINESE_PARENS}    ← e.g. **Ying Wei（魏颖）**（大老板）（通讯）
{venue} {year} ({role})    ← e.g. ICML 2026 (Oral)
{venue_year} {status_enum_8values}    ← v0.11.0 新: 8 enum (被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿)
arXiv：{url_or_暂无}    ← v0.11.0 新: 独立行, "暂无" 是合法值
paper：{url_openreview_or_arxiv_or_doi}    ← v0.11.0 新: 7 优先级 URL 统一入口
大领域：{D}
中方向：{M}
小任务：{T}
子技术：{S}
```

**详细规范**: `references/paper-entry.md` (299 行 v0.11.0 完整规范, 含 8 enum status 严格定义 / 7 paper URL 优先级 / 22 项 LLM 自检 / 迁移指南)

## 4. 22 项 LLM 自检清单 (v0.4.0 + v0.11.0 共享)

| # | 自检项 | 适用 | 通过条件 |
|---|--------|------|---------|
| 1 | 标题 verbatim | v0.4.0 / v0.11.0 | 完全从 arXiv abs 页复制 |
| 2 | 标题无 et al. 缩写 | 全部 | 完整标题 |
| 3 | 标题 h3 + arXiv ID inline | v0.4.0 | `<h3>N. Title [arXiv X]</h3>` |
| 4 | 4 行 taxonomy 顺序 | 全部 | 大领域→中方向→小任务→子技术 |
| 5 | 4 行 taxonomy 无 table | 全部 | 4 个 `<p>` 块 |
| 6 | taxonomy + 作者 无占位符 | 全部 | 4 字段 + 作者列表 均有具体值 |
| 7 | 作者完整 verbatim | 全部 | 全部列出, 无 et al. |
| 8 | 禁止 (末位/通讯) 缩写 | 全部 | author 行无描述性缩写 |
| 9 | 全作者中文括注 | 全部 | 100% 作者含 `Name（中文名）` |
| 10 | inline 标记 (通讯/大老板/一作) | v0.4.0 | 3 个 inline tag + bold 齐全 |
| 11 | 真实 1-click URL | 全部 | arXiv inline 或 paper URL 行 |
| 12 | arXiv ID 真实 | 全部 | arXiv ID 是真 ID (非 placeholder) |
| 13 | Wiki Subject Author Verification | 全部 | wiki subject 必须在 author list 里 |
| 14 | H2 装饰 emoji (v0.6.0) | 全部 | 👤📊✉📚📖🎯ℹ 等装饰 emoji 0 hits |
| 15 | H3 编号 dot 后缀 (v0.7.0) | 全部 | h3 全部带 dot 后缀 |
| 16 | 深度+1 编号 (v0.8.0) | 全部 | h2=1.X. / h3=1.X.Y. |
| 17 | 中文名字符级 typo (v0.10.0) | 全部 | 老师姓名与 L1-L4 来源字符级匹配 |
| 18 | status enum 严格 8 值 (v0.11.0) | v0.11.0 | paper card status ∈ 8 enum, free text auto-reject |
| 19 | paper URL 7 种合法类型 (v0.11.0) | v0.11.0 | paper URL ∈ 7 URL 模板之一 |
| 20 | arXiv/paper 一致性 (v0.11.0) | v0.11.0 | `arXiv：暂无` ↔ `paper：非空` 必同时成立 |
| 21 | status/paper URL 联动 (v0.11.0) | v0.11.0 | 被拒/在投/R&R 状态 → paper URL 必为 OpenReview |
| 22 | paper card 编号样式 (v0.11.0) | 全部 | 编号 `1.` `2.` `3.` 纯文本前缀, 非 hyperlink |

**任一 ❌ 必须修正后才能写入 docx**. 

**Check 1-13 工具**: `scripts/check_paper_card_v040.py` (v0.4.0 专用 13 项)
**Check 14-17 工具**: 集成在 `scripts/check_h2_emoji.py` + `scripts/check_chinese_name.py` (v0.6/v0.7/v0.8/v0.10)
**Check 18-22 工具**: `scripts/check_paper_card_v110.py` (v0.11.0 专用 5 项)

## 5. 8 enum status 严格定义 (v0.11.0 必含)

| 值 | 含义 | 必配 paper URL 类型 |
|----|------|------------------|
| **被拒** | rejected by venue | OpenReview (decision = reject) |
| **在投** | under review | OpenReview (decision pending) |
| **R&R** | revise & resubmit | OpenReview (decision = R&R) |
| **已收** | accepted, not yet presented | OpenReview 或 proceedings |
| **Camera Ready** | accepted + camera-ready submitted | proceedings 或 journal |
| **已发表** | published / presented / indexed | proceedings / journal / DOI |
| **Preprint** | arXiv-only, not submitted anywhere | arXiv abs |
| **撤稿** | withdrawn / retracted | OpenReview (decision = withdraw) |

**严禁** free text (`unknown` / `pending` / `submitted` / `[待补]` / `未发表`) — Check 18 auto-reject.

## 6. 7 paper URL 优先级 (v0.11.0 必含)

1. **OpenReview forum** `https://openreview.net/forum?id={forum_id}` — 被拒/在投/R&R 状态**强制**
2. **arXiv abs** `https://arxiv.org/abs/{id}` — Preprint 状态必此 URL
3. **DOI** `https://doi.org/{doi}` — 期刊论文 (无 OpenReview 时)
4. **papers.cool** `https://papers.cool/arxiv/{id}` — 备用
5. **会议 proceedings** — Camera Ready / 已发表
6. **期刊页** — 期刊论文
7. **主页 PDF** — 最后 fallback

## 7. v0.13.6 选型决策表 (NEW)

| 论文数 N | 主选 | 备选 | §1.3 结构 |
|---------|------|------|----------|
| N ≤ 3 | v0.11.0 完整 | v0.4.0 紧凑 | 单层 h3 列表 |
| 3 < N < 10 | v0.4.0 紧凑 | v0.11.0 完整 | 单层 h3 列表 |
| N ≥ 10 | 重组 (v0.4.0 紧凑) | — | **§1.3.A 顶会 10 + §1.3.B 主题表 + §1.3.C 趋势** (v0.13.0 NEW 硬要求) |

**§1.3.A 顶会 10 选稿标准**:
- 优先级: ICLR/NeurIPS/ICML oral > spotlight > long talk > BP Finalist
- 跨方向覆盖 (持续学习 / LLM / CV / AI4Science / 迁移 / 元学习 等)
- 兼顾近期 (近 3 年 50%+) + 历史奠基 (早期 1-2 篇)
- **v0.13.2 硬要求**: 1 h3 + 10 p (11 行) 格式, 不用 callout, 无 emoji="⭐", 通讯作者独立行 (无 inline bold), 中文括注全作者, 4 行独立 taxonomy (1 行 4 项违反 Check 8)
- **v0.13.4 硬要求**: h3 标题**只**含编号+标题, **禁止** [arXiv xxx] inline (arXiv 移到独立 p 行). 必跑 `python3 scripts/check_arxiv_url.py --id {arxiv-id}` verify HTTP 200 + title 匹配 L1 byline. **LLM 禁止** 编造 arXiv ID. 失败标 "待补" + 删 href.
- **v0.13.5 硬要求 (Check 24)**: 字段名 `arXiv：` → `paper link:`. Fallback 顺序: (1) arXiv ID 真 → arXiv URL. (2) arXiv ID 假/无 → OpenReview URL. (3) 都没有 → 暂无. 1.3.A #1 (22hBwIf7OC 假) → OpenReview URL. 1.3.A #4/#6/#8/#9 真 → arXiv URL. 1.3.A #10 无 → 暂无.

**§1.3.B 主题表 5-7 主题选稿**:
- 按中方向 (来自 paper card 4 维 taxonomy) 分类
- 主题数 = 5-7 (避免过细或过粗)
- 论文数 < 5 的主题合并到 "其他" 主题
- 论文数 top 5 主题必独立成 callout

**§1.3.C 趋势 5 观察点**:
1. 方向漂移 (year1-year2 → year3-year4)
2. 主线强度 (主方向 论文数 + oral 占比)
3. 次主线占比 (次方向 占比 + 关联)
4. 国际合作网络 (通讯单位 + 合作者)
5. 顶会比例 (N/N = 100% + 0 期刊主作)

## 8. 共存策略

- 同一 doc 中可混用 v0.4.0 和 v0.11.0, 但**同一论文不能同时用两种格式**
- 1.3.A 顶会 10 篇 → 全部 v0.4.0 紧凑 (callout 内 4 行 metadata, 信息密度合适)
- 1.3.B 主题表 → 仅 title + venue + arXiv (无完整 paper card, table 列出)
- 套磁信引用具体论文 → v0.11.0 完整 (1-2 篇)

## 9. 详细规范 reference

| 文件 | 内容 | 行数 |
|------|------|------|
| `references/paper-card.md` | v0.4.0 紧凑版完整规范 (含 inline 标记规则 / 13 项自检 / 12 papers 样例 / 迁移路径) | 295 |
| `references/paper-entry.md` | v0.11.0 完整版完整规范 (含 8 enum status / 7 paper URL / 22 项自检 / 迁移指南) | 299 |
| `references/output-schema.md` | Output Schema 12 项硬要求 (v0.6.0 → v0.10.0) | 413 |
| `references/audit-checklist.md` | 12 项 audit mode 合规检查 | 495 |
