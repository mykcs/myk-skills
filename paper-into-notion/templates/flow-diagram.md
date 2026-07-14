# paper-into-notion flow diagram v1.0

> ASCII 全流程图, 从 URL 输入到 Notion record_id 输出, 含 6 scripts 调用链 + 4 阶段.

```
┌──────────────┐
│   user URL   │  (e.g. https://arxiv.org/abs/1706.03762)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ Phase 1: 模态判定 (scripts/modal-detect.sh)          │
│   case URL in arxiv.org / mp.weixin / twitter / ...  │
│   → "arXiv" / "微信公众号" / "博客" / "Twitter" / "其他" │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ Phase 2: 数据抓取                                     │
│   arXiv → scripts/arxiv-fetch.sh                     │
│     ├─ curl https://export.arxiv.org/api/query      │
│     ├─ 重试 3 次 (sleep 3s, per Q4 rate limit)      │
│     └─ ElementTree 解析 → JSON title/authors/abstract│
│   其他模态 → 用 URL 当 fallback title (不抓内容)     │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ Phase 3: 字段级 merge (scripts/field-merge.sh)      │
│   POST /v1/data_sources/$DS_ID/query                │
│     ├─ 0 条 → POST 新 page                           │
│     │   body 只含 3 auto 字段:                       │
│     │     页面 (title) / 状态 (select=未开始) /       │
│     │     模态类型 (select=arXiv)                     │
│     │                                                 │
│     ├─ 1 条 → PATCH 已有 page                        │
│     │   body 含 3 auto 字段 (title 更新 + select)    │
│     │   ⚠️ body 永远不含:                            │
│     │     教育类型 (multi_select)                     │
│     │     标签 (multi_select)                         │
│     │     关键词 (multi_select)                       │
│     │     亮点 (rich_text)                            │
│     │     上次编辑时间 (Notion auto, 不能 PATCH)      │
│     │                                                 │
│     └─ 2+ 条 → exit 1 "duplicate title"              │
│                  (需 user 手动 dedup)                 │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ Phase 4: 跑后验证 (scripts/verify-5-fields.sh)      │
│   GET /v1/pages/$PAGE_ID                            │
│     ├─ [1/5] 页面 (title) ✅                          │
│     ├─ [2/5] 状态 (select=未开始) ✅                   │
│     ├─ [3/5] 模态类型 (select=arXiv) ✅                │
│     ├─ [4/5] multi_select 保护:                       │
│     │       教育类型 / 标签 / 关键词                  │
│     │       新建 = 0 项 / 更新 = 保留原值             │
│     │       ⚠️ 任何 > 0 表示 PATCH 覆盖了 → ❌         │
│     └─ [5/5] 上次编辑时间 (Notion auto) ✅             │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ ✅ record_id + page_url 输出                         │
│ (per §H.1 5 字段自检 PASS)                           │
└──────────────────────────────────────────────────────┘
```

---

## 6 scripts 调用链

```
paper-into-notion.sh (主入口)
  ├─→ modal-detect.sh          # Phase 1
  ├─→ arxiv-fetch.sh           # Phase 2 (仅 arXiv)
  ├─→ check-notion-version.sh  # (可选, 跑前 doctor)
  ├─→ field-merge.sh           # Phase 3 (核心 4 步算法)
  └─→ verify-5-fields.sh       # Phase 4 (5 字段 + multi_select 保护)
```

---

## 6 反模式自检 (per SKILL.md §6 反模式)

| # | 检查点 | 期望 |
|---|---|---|
| 1 | PATCH body 不含 multi_select | ✅ (scripts/field-merge.sh hardcoded) |
| 2 | 模态判定 5 pattern | ✅ (scripts/modal-detect.sh case 全 cover) |
| 3 | arXiv 抓失败 3 次 + exit 1 | ✅ (scripts/arxiv-fetch.sh retry loop) |
| 4 | record_id 必返 | ✅ (scripts/paper-into-notion.sh 校验) |
| 5 | verify-5-fields 必跑 | ✅ (Phase 4 强制) |
| 6 | 不写 fallback record (per Q4) | ✅ (exit 1, 不 catch) |