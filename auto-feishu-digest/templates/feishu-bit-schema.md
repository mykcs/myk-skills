# Feishu Bitable 4 表 Schema (字段定义 + DuplexLink)

> **目的**: 给飞书 Bitable 4 表统一字段定义, claudecode create_field 时 1:1 对位.
> **来源**: 2026-07-02 user 拍板 4 表拆分 + 调研产物映射表.

---

## 表 1: Paper (主表, ≤25 字段)

| # | 字段名 | 类型 (type code) | ui_type | 必填 | 选项 / 公式 |
|---|---|---|---|---|---|
| 1 | title | 1 | Text | ✅ | 单行 |
| 2 | url | 15 | Url | ✅ | — |
| 3 | arxiv_id | 1 | Text | ❌ | unique (防重) |
| 4 | source | 3 | SingleSelect | ✅ | arxiv / venue-conference / blog-rss / hn / github |
| 5 | authors | 4 | MultiSelect | ❌ | (跟 Author 表 DuplexLink 联动, 此 cell 可省) |
| 6 | venue | 18 | SingleLink → Venue 表 | ❌ | — |
| 7 | submit_date | 5 | DateTime | ❌ | auto-fill = false |
| 8 | fetch_date | 5 | DateTime | ✅ | 当前时间 (record 创建时) |
| 9 | subareas | 4 | MultiSelect | ❌ | 自演化智能体 / memory / prompt / skills / modules / reasoning / agentic-protocol / ... |
| 10 | citation_count | 2 | Number | ❌ | — |
| 11 | venue_score | 2 | Rating | ✅ | 1-5 stars |
| 12 | author_score | 2 | Rating | ✅ | 1-5 stars |
| 13 | code_score | 2 | Rating | ✅ | 1-5 stars |
| 14 | dataset_score | 2 | Rating | ✅ | 1-5 stars |
| 15 | number_score | 2 | Rating | ✅ | 1-5 stars |
| 16 | citation_score | 2 | Rating | ✅ | 1-5 stars |
| 17 | match_score | 2 | Rating | ✅ | 1-5 stars |
| 18 | composite_score | 20 | Formula | ❌ | `AVERAGE(venue_score, author_score, code_score, dataset_score, number_score, citation_score, match_score)` (输出 0.0-5.0, 1 位小数) |
| 19 | caution_flag | 20 | Formula | ❌ | `IF(composite_score <= 2, "❌ 不引", IF(composite_score <= 3, "⚠️ 慎引", "✅ 可引"))` |
| 20 | user_read | 7 | Checkbox | ❌ | — |
| 21 | round_history | 1 | Text (long) | ❌ | 结构化: `round 1 (YYYY-MM-DD HH:MM): ... \n round 2 ...` |
| 22 | reference_urls | 1 | Text (long) | ❌ | `<URL 1> — <date> \n <URL 2> — <date>` |
| 23 | weekly | 18 | SingleLink → Weekly 表 | ❌ | — |
| 24 | modified | 1002 | ModifiedTime | ❌ | 系统字段 |
| 25 | created_by | 1003 | CreatedUser | ❌ | 系统字段 |

---

## 表 2: Author (作者表, ≤10 字段)

| # | 字段名 | 类型 | ui_type | 必填 |
|---|---|---|---|---|
| 1 | name | 1 | Text | ✅ |
| 2 | affiliation | 1 | Text | ❌ |
| 3 | h_index | 2 | Number | ❌ |
| 4 | papers | 21 | DuplexLink → Paper | ❌ |
| 5 | field | 4 | MultiSelect | ❌ |
| 6 | influence_trend | 20 | Formula | ❌ | `COUNT(papers) — 引用 sub-table count` |
| 7 | created | 1001 | CreatedTime | ❌ |
| 8 | modified | 1002 | ModifiedTime | ❌ |

---

## 表 3: Venue (场地/会议表, ≤10 字段)

| # | 字段名 | 类型 | ui_type | 必填 |
|---|---|---|---|---|
| 1 | name | 1 | Text | ✅ (unique) |
| 2 | tier | 3 | SingleSelect | ❌ | tier-1 (NIPS/ICML/ICLR/CVPR) / tier-2 (workshop / 其他) / blog / github-repo |
| 3 | impact_factor | 2 | Number | ❌ |
| 4 | papers | 21 | DuplexLink → Paper | ❌ |
| 5 | topics | 4 | MultiSelect | ❌ |
| 6 | created | 1001 | CreatedTime | ❌ |

---

## 表 4: Weekly (周报表, ≤12 字段)

| # | 字段名 | 类型 | ui_type | 必填 |
|---|---|---|---|---|
| 1 | week_id | 1 | Text | ✅ (unique, e.g. `2026-W27`) |
| 2 | period | 5 | DateTime (range) | ❌ | (start_date + end_date 通过 2 cell 或 formula) |
| 3 | theme | 3 | SingleSelect | ❌ | 自演化智能体 / 工具增强 / benchmark / failure / ... |
| 4 | papers | 21 | DuplexLink → Paper | ❌ | 跨表反向可见 |
| 5 | report_md_url | 15 | Url | ❌ | 周报 md 仓库 URL (e.g. github.com/mykcs/weiying20260624/blob/main/...) |
| 6 | fetch_count | 2 | Number | ❌ | (本周 fetch paper 数) |
| 7 | top_paper_score | 2 | Number | ❌ | MAX(papers.composite_score) |
| 8 | digest_status | 3 | SingleSelect | ❌ | pending / scored / published |
| 9 | published_date | 5 | DateTime | ❌ | 写表时间 |
| 10 | created | 1001 | CreatedTime | ❌ |

---

## 跨表联动说明 (DuplexLink 反向同步)

| 联动 | 主表 | 反向表 | 行为 |
|---|---|---|---|
| Paper.venue → Venue.papers | Paper | Venue | Paper 改 venue, Venue.papers 自动同步 |
| Paper.authors → Author.papers | Paper | Author | 同上, 一作多 paper 自动聚类 |
| Paper.weekly → Weekly.papers | Paper | Weekly | Weekly record 自动看到本周所有 paper |

**Week 自动汇总 (Formula)**: `Weekly.fetch_count = COUNT(Weekly.papers)` (基于反向 DuplexLink)

---

## 反模式 (永久失效)

- ❌ Paper 表塞 30+ 字段 (填充率 < 60%, 填表疲劳)
- ❌ 用 SingleLink 想反向同步 (必须 DuplexLink)
- ❌ Lookup 当 Formula (Lookup 只能拉值, 不能算)
- ❌ Formula 跨表嵌套 > 10 层 (无限循环风险)
- ❌ 必填 User 字段 (record 创建卡住)

---

## 🔗 相关

- `~/.agents/skills/auto-feishu-digest/SKILL.md` §4 表拆分决策
- `~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh` (create_field 时 1:1 套本表)
- 飞书 OpenAPI `bitable/v1/app-table-field/create` 端点
