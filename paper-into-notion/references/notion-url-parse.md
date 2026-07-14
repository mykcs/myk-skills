# Notion URL 解读 + 修哪一部分 4 决路径

> 起源: 2026-07-14 v2.1 merge 后 user 反馈 "把这一路出现的问题经验教训都总结在 skill 里面，尤其是 notion 链接，怎么修改哪一部分"
> 配套: `templates/notion-fix-cheatsheet.md` (4 类常见问题 + 决路径) / `templates/cross-db-migrate-payload.md` (§0 Notion URL 解读) / `references/notion-schema-migration.md` (Notion 2025 API model)
> 案例: CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714
> ADR: ADR-0057-d

---

## §1. Notion URL 4 类

Notion URL 形如 `https://app.notion.com/p/{32-char-id}?v={view-id}&source=copy_link`, **32-char id 本身不携带类型信息**, 必须调 API 反查。

| # | URL 形态 | 类型 | API 反查 | 改哪一部分 |
|---|---|---|---|---|
| 1 | `app.notion.com/p/{id}` 指向 database (有 schema) | **database / data source** | `ntn datasources resolve {id}` | **改 schema** (加 property) 或 **改 page row** (cell value) |
| 2 | `app.notion.com/p/{id}` 指向 page (普通 doc) | **page** | `ntn pages get {id}` | **改 page content** (block) |
| 3 | `app.notion.com/p/{id}?v={view-id}` 指向 database view | **data source (跟 #1 同)** | `ntn datasources query {ds_id}` (用 `?v=` 前面的 id) | **改 schema** (影响所有 view) |
| 4 | `app.notion.com/{workspace}/{page-name}-{short-id}` 旧格式 | **page** (workspace-relative) | `ntn pages get {short-id}` (dash 后的 32 char) | **改 page content** |

**判定顺序**:
1. URL 有 `?v=` 视图参数 → 视图参数前面 id = database / data source
2. URL 无 `?v=`, 32 char id → `ntn datasources resolve {id}` 测, 返 200 = database, 404 = page
3. URL 含 `/workspace/` 路径 → workspace 内部 page

## §2. id 提取 Python 函数

```python
import re

def parse_notion_url(url):
    """从 Notion URL 提取 id + 判定类型"""
    # 去 ?v=...&source=...
    base = url.split('?')[0]
    # 32 char UUID (8-4-4-4-12)
    m = re.search(r'([0-9a-f]{32})', base.replace('-', ''))
    if not m:
        return None
    raw = m.group(1)
    # 加 dashes (UUID 格式)
    id_with_dashes = f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    return id_with_dashes


def detect_notion_type(id_with_dashes):
    """API 反查 id 类型: database / data source / page"""
    import subprocess
    # 试 datasources resolve (新 endpoint, 优先)
    r = subprocess.run(['ntn', 'datasources', 'resolve', id_with_dashes],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return 'data_source', id_with_dashes
    # 试 pages get
    r = subprocess.run(['ntn', 'pages', 'get', id_with_dashes],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return 'page', id_with_dashes
    return 'unknown', id_with_dashes


# 用法
url = 'https://app.notion.com/p/39dfedee6267808fafc7d9b3cc2d43f1'
id_ = parse_notion_url(url)
type_, _ = detect_notion_type(id_)
print(f'{type_}: {id_}')
# → data_source: 39dfedee-6267-808f-afc7-d9b3cc2d43f1
```

## §3. 修哪一部分 4 决路径表

**关键问题**: 1 个 Notion bug 怎么知道改 schema / page row / database metadata / page content?

| 触发场景 | 修哪 | 工具 | endpoint | 例子 |
|---|---|---|---|---|
| database 缺字段 / 类型不对 | **改 schema** (加 property / 改 type) | `scripts/add-property.sh` | PATCH /v1/data_sources/{id} | "目标 db 缺 link 字段" → add-property.sh 加 |
| 单行 page 字段值错 | **改 page row** (cell value) | `scripts/paper-into-notion.sh` | PATCH /v1/pages/{id} | "QLoRA 行的 link 错了" → paper-into-notion.sh PATCH |
| database 显示名错 | **改 database metadata** (title / icon) | ntn api | PATCH /v1/databases/{id} | "database 标题想改" → ntn api PATCH |
| page 内文字 / heading / list 错 | **改 page content** (block) | ntn pages edit | PATCH /v1/blocks/{id} | "page 标题或段落错" → ntn pages edit |

**判定顺序** (1 跳决策):
1. 改的是 database 字段? → schema (加 property / 改 type)
2. 改的是 page 内字段值? → page row (cell value)
3. 改的是 database 标题 / icon? → database metadata
4. 改的是 page 内文字? → page content (block)

## §4. integration share 3 步判定

**关键问题**: user 加了 Notion CLI integration 但 API 返 404, 怎么判定 access?

```bash
# Step 1: resolve (找 id 类型, 不判定 access)
ntn datasources resolve <id> 2>&1
# → 200 + name = 找到 (data source 存在)
# → 404 = id 错或 integration 没 share

# Step 2: query (read access 判定)
ntn datasources query <ds_id> 2>&1
# → 200 + [] 或 [{...}] = 有 read access
# → 404 = integration 没 share 或 read scope 缺

# Step 3: create test (write access 判定, 必跑)
ntn api /v1/pages -X POST -d '{
  "parent": {"type": "data_source_id", "data_source_id": "<ds_id>"},
  "properties": {"<title_field>": {"title": [{"type": "text", "text": {"content": "_test_access_check"}}]}}
}' 2>&1
# → 200 + id = 有 write access, **立即 trash 这个 test page**
# → 401/403 = integration 没 share 或 write scope 缺
```

**实测关键**: read access 跟 write access 独立. `datasources query` 返 200 不代表 `pages create` 必成功. **必跑 3 步独立判定**.

**Notion CLI scope 申请**: UI → https://www.notion.so/profile/integrations → 选 "Notion CLI" → Capabilities tab → 勾 Read/Update/Insert content (4 个 checkbox).

## §5. Notion 5 类 URL 错误信息速查 (跟 §3 §4 联动)

| 错误信息 | 真因 | 修法 |
|---|---|---|
| `Could not find database with ID: {id}` (404) | 老 endpoint `/v1/databases/{id}` 对 integration 只 share data source 返 404 | 改用 `ntn datasources resolve {id}` (新 endpoint) |
| `Could not find page with ID: {id}` (404) | id 是 page id 不是 database id, 或 integration 没 share | 跑 §4 3 步判定 |
| `B=aN is an invalid select option "xxx-id"` | 跨 db 搬 option 传了 source id | payload strip id 只留 name (per cross-db-migrate-payload.md §2) |
| `link is not a property that exists.` | target db 缺 property | `add-property.sh <ds_id> link url` |
| `Archiving workspace level pages via API not supported` | workspace-level database API 不能 archive | UI 删 (per `templates/cross-db-migrate-payload.md` §7) |

## §6. 联动引用

- 起源 case: CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714
- ADR: ADR-0057-d (v2.2 升级) / ADR-0057-c (v2.1 跨 db 搬 schema) / ADR-0026 (curl verify 必读 body) / ADR-0054 (Notion 严格层)
- 配套: `templates/notion-fix-cheatsheet.md` (4 类常见问题 + 决路径) / `templates/cross-db-migrate-payload.md` (§0 Notion URL 解读) / `references/notion-schema-migration.md` (Notion 2025 API model)
- 工具: `ntn` CLI 0.18.1 (datasources resolve/query + pages get/create + search + Notion-Version: 2026-03-11 header)
- Notion 官方: [data sources 2025-09 release notes](https://developers.notion.com/changelog) / [integration scope 申请](https://www.notion.so/profile/integrations)
