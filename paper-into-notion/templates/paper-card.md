# paper-card.md — 12 行 paper card (per teacher-report v0.13.6 v0.3.0 增强 h3 format)

> 12 行 / paper 紧凑格式, 适用于 arXiv paper 调研场景.

```markdown
### [N]. [Title (arXiv inline)](https://arxiv.org/abs/[ID])

- **arXiv**: [ID] (v[N], [date])
- **Authors**: [First] [Last], [First] [Last], ... ([N] authors)
- **Taxonomy**: [cs.AI / cs.LG / cs.CL] | [primary_category]
- **通讯作者**: [Name] ([affiliation])
- **TL;DR**: [1 句核心贡献, ≤ 30 字]
- **Method**: [1 段方法概述, ≤ 100 字]
- **Result**: [1 段实验结果, ≤ 80 字]
- **Code**: [github.com/.../] (如可获得)
- **Citation**: [N] (Google Scholar 截至 [date])
- **My Take**: [1 句个人评价, ≤ 50 字]
- **Status**: [未读 / 精读 / 笔记完成] (per Notion `状态` 字段)
- **Tags**: [教育类型] / [关键词] / [标签] (per Notion multi_select, 后填)
```

---

## 字段填充顺序 (per teacher-report §Paper Entry Format v0.11.0)

| 顺序 | 字段 | 来源 | 自动 / 手动 |
|---|---|---|---|
| 1 | Title | arXiv API `<title>` | 自动 (scripts/arxiv-fetch.sh) |
| 2 | arXiv ID + version + date | arXiv API | 自动 |
| 3 | Authors | arXiv API `<author>` | 自动 |
| 4 | Taxonomy | arXiv API `<category>` | 自动 |
| 5 | 通讯作者 | arXiv API `<arxiv:doi>` 或 fallback | 半自动 (需 verify) |
| 6 | TL;DR | LLM 摘要 | 手动 (skill 不自动) |
| 7 | Method | LLM 摘要 | 手动 |
| 8 | Result | LLM 摘要 | 手动 |
| 9 | Code | arXiv API `arxiv:journal_ref` 或搜索 | 半自动 |
| 10 | Citation | Google Scholar | 半自动 |
| 11 | My Take | 人工评价 | 手动 (不可自动) |
| 12 | Status / Tags | Notion `状态` / multi_select | 手动 (Notion UI 后填) |

**关键约束**: paper-into-notion skill 只填 Notion 3 auto 字段 (页面 / 状态 / 模态类型), 其他 9 字段 (TL;DR / Method / Result / Code / Citation / My Take / Status 详情 / Tags 详情) 都在 Notion UI 后填或单独 weekly-report-phd skill 输出 paper card.

---

## Notion 写入策略

| 字段 | 自动填? | Notion 字段 |
|---|---|---|
| Title | ✅ | 页面 (title) |
| arXiv ID + date | ❌ | (放 My Take 或 Notes) |
| Authors | ❌ | (Notion schema 暂不支持, 后填) |
| Taxonomy | ❌ | (放 multi_select 关键词) |
| TL;DR / Method / Result | ❌ | (放 rich_text 亮点, 后填) |
| Code / Citation / My Take | ❌ | (放 rich_text 亮点) |
| Status | ✅ | 状态 (select) — 固定 "未开始" |
| 模态类型 | ✅ | 模态类型 (select) |
| 多选字段 | ❌ | 教育类型 / 关键词 / 标签 (后填) |