# Notion 4 类常见问题 + 修哪一部分 决路径

> 起源: 2026-07-14 v2.1 merge 后 user 反馈 "怎么修改哪一部分" → 立本 cheatsheet
> 配套: `references/notion-url-parse.md` (URL 4 类 + 修哪 4 决路径) / `templates/cross-db-migrate-payload.md` (跨 db 搬) / `references/notion-schema-migration.md` (Notion 2025 API model)
> ADR: ADR-0057-d

---

## §1. 4 类常见问题 + 决路径表

| # | 问题 | 错误信息 | 真因 | 修哪 | 决路径 |
|---|---|---|---|---|---|
| 1 | **URL 错** | `Could not find database with ID: xxx` (404) | URL 32-char id 是 page 不是 database, 或 integration 没 share | 改 URL 解读 / integration share | §2 1 跳决策树 → 步 1 |
| 2 | **字段不存在** | `link is not a property that exists.` | target db 缺该 property | **改 schema** (加 property) | `bash scripts/add-property.sh <ds_id> link url` |
| 3 | **跨 db 搬 option 错** | `B=aN is an invalid select option "xxx-id"` | payload 传了 source option id | 改 payload (strip id) | per `cross-db-migrate-payload.md` §2 |
| 4 | **workspace-level archive 失败** | `Archiving workspace level pages via API not supported` | Notion API 限制, 必 UI 删 | **改方法** (API → UI) | per `cross-db-migrate-payload.md` §7 |

## §2. 1 跳决策树 (URL 错 → 找对 id → 走对应工具)

```
问题: Notion API 返 404 / 字段不存在 / option id 错
  │
  ├─ Step 1: URL 解读 (per references/notion-url-parse.md §1)
  │   URL → 32-char id
  │   ├─ 有 ?v= 参数 → id = database / data source
  │   └─ 无 ?v= → ntn datasources resolve 测
  │
  ├─ Step 2: integration access 3 步判定 (per references/notion-url-parse.md §4)
  │   ├─ resolve 200 → 找到 (不是 access 判定)
  │   ├─ query 200 → 有 read access
  │   └─ create test 200 → 有 write access
  │   任一 FAIL → UI 加 Connections: Notion CLI + 勾 Read/Update/Insert scope
  │
  ├─ Step 3: 改哪一部分 (per references/notion-url-parse.md §3)
  │   ├─ 改 database 字段? → 改 schema → scripts/add-property.sh
  │   ├─ 改 page 字段值? → 改 page row → scripts/paper-into-notion.sh
  │   ├─ 改 database 标题? → 改 metadata → ntn api PATCH /v1/databases/{id}
  │   └─ 改 page 文字? → 改 content → ntn pages edit
  │
  └─ Step 4: 修
      └─ 改完跑 verify-5-fields.sh + ntn datasources query 验证
```

## §3. 修哪一部分 quickref (4 类修改场景)

### 场景 1: 改 schema (加 property / 改 type)

```bash
# 加 1 个 property
bash scripts/add-property.sh <ds_id> "link" "url"
bash scripts/add-property.sh <ds_id> "模态类型" "select" '[{"name":"arXiv","color":"blue"}]'

# 7 个 property 一次性 (per cross-db-migrate-payload.md §6)
DS="<ds_id>"
for spec in \
  'link|url|' \
  '亮点|rich_text|' \
  '教育类型|multi_select|[{"name":"论文阅读","color":"blue"}]' \
  '日期|date|' \
  '模态类型|select|[{"name":"arXiv","color":"blue"},{"name":"微信公众号","color":"green"},{"name":"博客","color":"purple"},{"name":"Twitter","color":"default"},{"name":"其他","color":"gray"}]' \
  '状态|status|[{"name":"未开始","color":"default"},{"name":"进行中","color":"blue"},{"name":"已完成","color":"green"}]' \
  '知识点|multi_select|[{"name":"llm","color":"blue"},{"name":"超声心动","color":"pink"},{"name":"线性注意力","color":"purple"}]'
do
  IFS='|' read -r NAME TYPE OPTS <<< "$spec"
  bash scripts/add-property.sh "$DS" "$NAME" "$TYPE" "$OPTS"
done
```

### 场景 2: 改 page row (cell value)

```bash
# 改 1 个 page 的字段值
PAGE_ID="<page_id>"
ntn api /v1/pages/$PAGE_ID -X PATCH -d '{
  "properties": {
    "link": {"url": "https://arxiv.org/abs/2512.10252"},
    "模态类型": {"select": {"name": "arXiv"}}
  }
}'
# 重要: multi_select / select / status 必 strip id (per cross-db-migrate-payload.md §2)
```

### 场景 3: 改 database metadata (title / icon)

```bash
# 改 database 显示名
DB_ID="<db_id>"  # 顶层 database id, 不是 data source id
ntn api /v1/databases/$DB_ID -X PATCH -d '{
  "title": [{"type": "text", "text": {"content": "新标题"}}]
}'
# 注: 改 data source title 也是 PATCH /v1/data_sources/{id}, 不是改 property
```

### 场景 4: 改 page content (block)

```bash
# 改 page 内文字 (markdown 模式)
PAGE_ID="<page_id>"
echo "# 新标题\n\n新内容" | ntn pages edit $PAGE_ID
# 或 API 模式: ntn api /v1/blocks/<block_id> -X PATCH
```

## §4. 4 决路径 vs 4 反模式 (v2.2 沉淀)

| 4 决路径 (改哪) | 对应反模式 (踩坑) |
|---|---|
| 改 schema | ❌ 想改 property name 但 PATCH data source title (真因: data source title ≠ property name) |
| 改 page row | ❌ 跨 db 搬 option 复制 source id (真因: Notion 校验 input id) |
| 改 database metadata | ❌ 想 archive workspace-level db 走 API (真因: API 不支持) |
| 改 page content | ❌ kimi-webbridge 0 button 改 Notion UI (真因: Notion 2025 button 渲染兼容) |

## §5. 联动引用

- 起源 case: CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714
- ADR: ADR-0057-d (v2.2 升级)
- 配套 reference: `references/notion-url-parse.md` (URL 4 类 + 4 决路径) / `references/notion-schema-migration.md` (Notion 2025 API model) / `templates/cross-db-migrate-payload.md` (跨 db 搬 9→8 字段映射)
- 工具: `ntn` CLI 0.18.1 / `scripts/add-property.sh` (跨 db 加 property) / `scripts/paper-into-notion.sh` (单行 page 字段值) / `verify-5-fields.sh` (跑完 5 字段自检)
- 主 skill: SKILL.md v2.2 (frontmatter 4 字段全合规 + 触发词 22 + 反模式 16)
