## Paper Card v0.11.0 完整版 (2026-06-11 新增, 替代 v0.3.9 完整版)

> **完整 12 决策 grill-with-docs 记录 + 12 行/paper 模板 + 8 enum status + 7 paper URL 优先级 + 22 项 LLM 自检 (Check 1-22)** 已下沉到 [`references/paper-entry.md`](references/paper-entry.md) (~260 行, v0.11.0 paper card 升级, 2026-06-11 改写).
>
> **TL;DR**: v0.3.9 完整版 15 行/paper 缺 status / arXiv 可空 / OpenReview 表达, v0.11.0 完整版 ~10 行/paper 加 4 新字段 (status / arXiv 状态 / paper URL / 编号样式), 解决 3 类历史痛点: ① 无 arXiv 的 OpenReview-only 投稿 (ICML/NeurIPS/IJCAI 在投) ② 论文状态非"已发表" (被拒/R&R/Preprint) ③ 单一 URL 入口 (v0.3.9 拆 arXiv + paperscool 2 行).
>
> **选型**: 论文 ≤3 篇 → **v0.11.0 完整版** (推荐); 论文 ≥10 篇 → v0.4.0 紧凑版 (保留); 同一 doc 可混用但同一论文不混.
>
> **v0.11.0 paper card 模板 (~10 行/paper)**:
> ```
> 1. {论文完整标题 (verbatim)}
> {AUTHOR_LIST_WITH_INLINE_MARKERS_CHINESE_PARENS}
> {venue} {year} ({role})
> {venue_year} {status_enum_8values}     ← v0.11.0 新 (独立行)
> arXiv：{url 或 "暂无"}                  ← v0.11.0 新 (独立行, arXiv 可空)
> paper：{url_openreview_or_arxiv_or_doi}  ← v0.11.0 新 (统一 1-click 入口)
> 大领域：{大领域}
> 中方向：{中方向}
> 小任务：{小任务}
> 子技术：{子技术}
> ```
>
> **22 项 LLM 自检 (Check 1-22)**: v0.10.0 17 项 + v0.11.0 新 5 项 (Check 18 status enum 严格 enum / 19 paper URL 7 种合法类型 / 20 arXiv/paper 一致性 / 21 status/paper URL 联动 / 22 paper card 编号样式纯文本). 详见 `references/paper-entry.md` 完整 12 行/paper 模板.
