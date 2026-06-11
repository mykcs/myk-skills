---
name: teacher-report-anti-hallucination
description: |
  teacher-report v0.2.9 anti-hallucination rules (强制). 6 类事实主张校验矩阵 + 3 层生成防御 + 1 层使用防御 + 4 类绝对禁止.
  v0.7.0 起强制 (per main SKILL.md).
---

# Anti-Hallucination Rules (teacher-report v0.2.9+)

> **背景**: v0.2.8 之前的 teacher-report 曾出现系统性幻觉 —— 5 字段(论文状态/年份/作者/学生身份/职务)直接从 AI 推断而非平台校验, 5 篇 ICLR 2026 论文"已撤稿"标注全部错误, 行政职务滞后 2 个时间点。**v0.2.9+ 强制走以下规则**。

## 6 类事实主张的强制校验矩阵

| 字段 | 必查源 | 不允许的来源 | 失败处理 |
|------|--------|-------------|---------|
| **论文发表状态**(Withdrawn/Accepted/Rejected/Submitted) | OpenReview API (`openreview.net/forum?id=...`) **OR** arXiv 摘要页 | ❌ AI 推断、❌ 二手数据库快照、❌ 课题组主页文字 | 查不到 → 标"❓状态未核 (OpenReview/arXiv 未公开)", 不写"已撤稿"或"已接收" |
| **发表年/月** | arXiv 首次提交时间戳 OR DOI 公布时间 | ❌ 论文里写"2025"但实际 arXiv 提交"2024"的情况 | 必须给出 arXiv ID 或 DOI 作为锚点 |
| **论文标题 + 作者** | arXiv abs 页 `Title:` `Authors:` 字段 | ❌ 凭印象写(中文名常错字,如"叶鑫海"vs"叶昕海") | 标题必须 verbatim 复制, 作者必须 verbatim 复制 |
| **导师行政职务** | 现任学校官网"现任职务"页(注意时间戳) | ❌ 旧版缓存、❌ 3 年前的新闻稿、❌ 维基类聚合页 | 必须给出官网 URL, 注意区分"曾任"(过去)vs"现任" |
| **学生身份归属** | 论文 byline + 课题组主页"组内成员"页 | ❌ "高频合作 = 学生"(合作者也可能是同事) | 论文里 byline + 合作频率 ≥ 5 篇 + 推断"<推断>"前缀 |
| **统计数字**(104 篇、CCF-A ~65 等) | L1-L4 抓取后**实际计数**, 不预估值 | ❌ "估算"、"约" | 必须给精确数字(自报"+"多少待补充) |

## 3 个生成层 + 1 个使用层防御

### 生成前 (L1-L4 抓取阶段)

- 任何 L1-L4 抓取后, 关键字段(year/status/author/title)必须有可追溯的 URL/arXiv ID
- L1 抓到 SPA 不全时, 必须切 playwright 渲染, 不要只 webfetch(见 main SKILL.md §Failure handling)
- 优先使用 **OpenReview API** (`https://api.openreview.net/notes`) 批量查 ICLR/NeurIPS 等会议的状态(撤回/接受/审稿中), 不要靠搜索结果拼凑

### 生成中 (LLM synthesis 阶段)

- **关键字段不预填**: LLM 写论文清单时, 状态列如果 L1-L4 没明确给出, 留空 + 标"待核", **不**凭"看起来像 Withdrawn"就填 Withdrawn
- **数字必精确**: 统计 "104 篇" 这种, 必须是 L1-L4 实际抓到的论文数, **不**用"约 100"或"估算"
- **名字 verbatim**: 作者中文名必须从 arXiv abs 页 verbatim 复制, AI 不要"纠正"看起来错的中文字(常因 OCR/转写污染)

### 生成后 (LLM 自检阶段)

- **5 字段抽样自检**: 写完 docx 后, LMM 必须**随机抽 5 篇**论文, 逐条在 arXiv/OpenReview 上核对(year + status + authors), 不通过 → 重写该字段
- **可信度标签**: 每篇论文的 status 列后必须可加 `[v: arxiv:2512.09396]` 或 `[v: openreview:xxx]` 标签(可选用), 让用户能看到哪些字段被实时核过

### 使用时 (用户使用 / 后续 agent 复用)

- **AI-to-AI 不免责**: 后续 agent 拿到本 skill 生成的 docx 做编辑/审计/补强时, **任何事实主张必须重新核**, 不允许"原文写的所以照搬"
- **抽样校验 ≥ 10%**: 用户拿到 docx 后, 使用前应至少抽样 10% 的论文在 arXiv/OpenReview 上验证; **不验证 = 接受幻觉风险**
- **"AI 整理"红线**: 文档底部如有"整理人:AI"字样, 后续使用者必须降低置信度, 优先复核关键决策字段(导师职务/招生状态/论文状态)

## 4 类绝对禁止 (违反 = skill 协议破坏)

1. **❌ 禁止**"凭印象 / 估算 / 大约"写论文状态 → 必须可追溯到 arXiv / OpenReview
2. **❌ 禁止**照搬前任 AI 输出不做事实复核 → AI-to-AI 链式污染
3. **❌ 禁止**用"高置信度模板"装饰不确凿的事实(例如把未核的"导师职务"放在 TL;DR callout 高亮框里, 会被用户当作可信结论)
4. **❌ 禁止**把"未核"状态字段(❓)藏在大段表格里, 必须显式标黄/标红/单独成行, 让用户能一眼看到哪些是"待补"
