# field-merge-algorithm.md — 字段级 merge 算法详解

> **核心铁律**: PATCH body **永远不包含** `教育类型 / 标签 / 知识点` (multi_select) + `亮点` (rich_text) + `上次编辑时间` (Notion auto)
> **目的**: 保护 Notion 已有 page 的 multi_select 值不被 PATCH 覆盖

---

## §1 为什么 multi_select 不能 PATCH (Notion API 行为)

### §1.1 Notion PATCH 语义

| 字段类型 | PATCH 语义 | 安全 |
|---|---|---|
| `title` | 完整新值覆盖 (单值, OK) | ✅ 安全 |
| `select` | 完整新值覆盖 (单值, OK) | ✅ 安全 |
| `multi_select` | **完整新值覆盖 (数组)** | ❌ **覆盖已有选项** |
| `rich_text` | 完整新值覆盖 | ⚠️ 看你是否想保留 |
| `last_edited_time` | **Notion 自动管理, 不能 PATCH** | ❌ 422 error |

### §1.2 反例 (踩坑示例)

```bash
# 假设 page 已有:
教育类型 = ["论文阅读"]
标签 = ["入门引导"]
知识点 = ["llm"]

# 错误做法: 想"增量更新", PATCH 传 ["论文阅读"]
PATCH /v1/pages/$PAGE_ID
{
  "properties": {
    "教育类型": {"multi_select": [{"name": "论文阅读"}]}
  }
}

# 结果: Notion API 行为 = "完整新值覆盖"
# → 教育类型 = ["论文阅读"] (跟之前一样, 但**所有其他选项都被删**)
# ⚠️ 如果之前还有 "项目", PATCH 后就没了
```

### §1.3 正确做法 (per 核心铁律)

```bash
# body 永远不含 multi_select 字段
PATCH /v1/pages/$PAGE_ID
{
  "properties": {
    "页面": {"title": [{"text": {"content": "新 title"}}]},
    "状态": {"select": {"name": "未开始"}},
    "模态类型": {"select": {"name": "arXiv"}}
  }
}

# 结果: Notion 行为 = "body 字段更新 + 未传字段保留"
# → 多选字段保持 ["论文阅读"] / ["入门引导"] / ["llm"] ✅
```

---

## §2 4 步算法详解

### §2.1 Step 1: GET 找 page

```bash
QUERY_BODY='{
  "filter": {
    "property": "页面",
    "title": {"equals": "Attention Is All You Need"}
  },
  "page_size": 2  # 故意 size=2 检测重复
}'

QUERY_RESULT=$(ntn api --method POST "/v1/data_sources/$DS_ID/query" \
  -H "Notion-Version: 2026-03-11" \
  -d "$QUERY_BODY")
```

**为什么 size=2 不是 size=1**: 检测重复 title (如果 page 已经被 user 误重复创建, 立即报错)

### §2.2 Step 2: 0 条 → POST 新 page

```bash
POST_BODY='{
  "parent": {"type": "data_source_id", "data_source_id": "$DS_ID"},
  "properties": {
    "页面": {"title": [{"text": {"content": "Attention Is All You Need"}}]},
    "状态": {"select": {"name": "未开始"}},
    "模态类型": {"select": {"name": "arXiv"}}
  }
}'
```

**新 page multi_select 全空**: Notion 默认 multi_select = `[]`, 所以新 page 没有覆盖风险

### §2.3 Step 3: 1 条 → PATCH 3 auto 字段

```bash
PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id')

PATCH_BODY='{
  "properties": {
    "页面": {"title": [{"text": {"content": "新 title (如果 title 改了)"}}]},
    "状态": {"select": {"name": "未开始"}},
    "模态类型": {"select": {"name": "arXiv"}}
  }
}'
```

**核心铁律**:
- body 永远不含 `教育类型 / 标签 / 知识点` (multi_select)
- body 永远不含 `亮点` (rich_text, 你后填)
- body 永远不含 `上次编辑时间` (Notion auto, 422 error)

### §2.4 Step 4: 2+ 条 → exit 1

```bash
echo "❌ duplicate title: $TITLE (找到 $COUNT 条 page, 需 user 手动 dedup)" >&2
exit 1
```

**为什么不自动 dedup**: dedup 决策涉及"保留哪条 + 合并 multi_select", 应该 user 手动到 Notion UI 操作

---

## §3 验证 (跑后 GET)

```bash
PAGE=$(ntn api --method GET "/v1/pages/$PAGE_ID")

# 1. 3 auto 字段填对
TITLE=$(echo "$PAGE" | jq -r '.properties["页面"].title[0].text.content')
STATUS=$(echo "$PAGE" | jq -r '.properties["状态"].select.name')
MODAL=$(echo "$PAGE" | jq -r '.properties["模态类型"].select.name')

# 2. multi_select 保护 (per 核心铁律)
EDU=$(echo "$PAGE" | jq -r '.properties["教育类型"].multi_select | length')
TAG=$(echo "$PAGE" | jq -r '.properties["标签"].multi_select | length')
KNOW=$(echo "$PAGE" | jq -r '.properties["知识点"].multi_select | length')

# 新建 page: EDU=TAG=KNOW=0
# 更新 page: EDU/TAG/KNOW = PATCH 前的值 (没变)
```

---

## §4 反模式 vs 正确做法对照

| 场景 | ❌ 反模式 | ✅ 正确做法 |
|---|---|---|
| 想更新 title + 保留多选 | PATCH 含 multi_select (覆盖) | PATCH 只含 title + select, multi_select 不传 |
| 想加新 tag | PATCH 传 ["新 tag"] (覆盖) | 不动, user 在 Notion UI 加 |
| 想改状态 "未开始" → "进行中" | 跳过, 不更新 | PATCH 只含 状态字段, multi_select 不传 |
| 不知道 page 已有啥 | 不 GET, 直接 PATCH multi_select | 先 GET, 看现有值, 但 PATCH 永远不传 multi_select |
| 想 "merge" 多选 | 用 jq 拼数组, 期望 Notion 增量更新 | ❌ Notion 不支持, PATCH 数组 = 完整新值 |