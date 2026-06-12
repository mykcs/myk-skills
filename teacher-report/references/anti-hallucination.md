## Anti-Hallucination Rules (v0.2.9+, 2026-06-06+)

> **完整 6 类校验矩阵 + 3 层生成防御 + 1 层使用防御 + 4 类绝对禁止**已下沉到 [`references/anti-hallucination-rules.md`](references/anti-hallucination-rules.md) (53 行, 2026-06-11 拆分).
>
> **核心**: v0.2.8 之前 teacher-report 曾出现系统性幻觉 (5 字段从 AI 推断而非平台校验, 5 篇 ICLR 2026 "已撤稿" 标注全部错误, 行政职务滞后 2 时间点)。v0.2.9+ 强制走 OpenReview/arXiv 校验矩阵。
