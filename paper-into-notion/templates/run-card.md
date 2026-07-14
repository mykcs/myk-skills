# paper-into-notion Run Card v1.0

> **Phase 1-4 banner** (per auto-feishu-digest v0.2.2 风格)
> **触发**: user 说 "paper 进 Notion" / "把这个 paper 加到 Notion" 时, claudecode 必输出本卡片

---

## Phase 1 — 输入解析

```text
URL: <input URL>
模态: arXiv / 微信公众号 / 博客 / Twitter / 其他 (per scripts/modal-detect.sh)
```

---

## Phase 2 — 数据抓取

```text
arXiv ID: <1706.03762>
Title: <Attention Is All You Need>
Authors: [<8 authors>]
Abstract: [<summary>]
抓取耗时: <3.5s> (含 3s rate limit sleep)
```

---

## Phase 3 — 字段级 merge (核心)

```text
GET /v1/data_sources/$DS_ID/query → 找到 <N> 条 page
  N=0 → POST 新 page (body 只含 3 auto 字段)
  N=1 → PATCH 已有 page (body 不含 multi_select, 永不覆盖)
  N=2+ → exit 1 duplicate (需 user 手动 dedup)
```

---

## Phase 4 — 跑后 GET 验证 (5 字段自检 + multi_select 保护)

```text
✅ record_id: xxx-xxx-xxx
✅ page_url: https://www.notion.so/...
✅ 页面 (title): "Attention Is All You Need"
✅ 状态 (select): 未开始
✅ 模态类型 (select): arXiv
✅ 教育类型 (multi_select): 0 项 (新建 page 全空, 符合预期)
✅ 标签 (multi_select): 0 项
✅ 知识点 (multi_select): 0 项
✅ 上次编辑时间 (auto): 2026-07-13T18:30:00.000Z
```

---

## 🎯 完成 (per §H.1 5 字段自检)

| # | 字段 | 期望 |
|---|---|---|
| 1 | path | ~/.agents/skills/paper-into-notion/ (15 file) |
| 2 | commit | feat(skill): paper-into-notion v1.0 (ADR-0057) |
| 3 | push | ahead=0 |
| 4 | CI | green |
| 5 | record_id + multi_select 保护 | 3 字段填对 + multi_select 永不被覆盖 |

---

## ⚠️ 4 异常路径 (per 6 反模式)

| # | 异常 | 处理 |
|---|---|---|
| 1 | arXiv 抓失败 3 次 | exit 1, 不写 fallback (per Q4) |
| 2 | Notion API 401 | 检查 ntn login |
| 3 | Notion API 404 | 检查 NOTION_DATA_SOURCE_ID |
| 4 | multi_select 保护失败 | 立即 abort + 报告 (per 反模式 #1) |