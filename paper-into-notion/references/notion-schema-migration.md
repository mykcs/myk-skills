# Notion Schema 迁移协议 (2025 API + 4 真实踩坑)

> 起源: 2026-07-14 跨 db 搬 paper 3 行 (源 9 字段 → 目标 8 property) 实测
> 配套: `templates/cross-db-migrate-payload.md` / `scripts/add-property.sh`
> 案例: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714
> ADR: ADR-0057-c

---

## §1. Notion 2025 API model 速查

Notion 2025-09-03 release 引入 **data source** 模型, 把老 `database` 拆成 2 层:

```
Notion API 2025+ model:
┌─────────────────────────────────────────────────────┐
│ Database (顶层容器, parent type = page_id / workspace)│
│   ↓ has many                                         │
│ Data Source (实际存 schema / rows, parent = database)│
│   ↓ has many                                         │
│ Page (实际存 row data, parent = data_source)         │
└─────────────────────────────────────────────────────┘
```

**对应 endpoint**:
- `POST /v1/databases` 创建新 database (自动建 1 个同名 data source)
- `PATCH /v1/databases/{id}` 更新 database metadata (title / icon)
- `GET /v1/databases/{id}` ⚠️ **返 404 如果 integration 只 share 了 data source**, 即使 database 存在
- `GET /v1/data_sources/{id}` ✅ 推荐, schema / title / properties 全在这里
- `PATCH /v1/data_sources/{id}` ✅ 推荐, 改 schema (含加 property) + 改 data source title
- `POST /v1/pages` 创建新 page, parent type 必是 `data_source_id` (新) 或 `database_id` (老, 已 deprecated)

**新模型下的 Notion-Version header**: `2026-03-11` (v2.6.30+ 默认), 老版本 `2022-06-28` 不支持 data source。

## §2. 4 真实踩坑 (按发生顺序)

### 踩坑 1: PATCH /v1/data_sources/{id} 加 property 成功路径

**实测** (7/7 成功):
```bash
DS="39dfedee-6267-807a-bcb2-000ba858dff2"
ntn api /v1/data_sources/$DS -X PATCH -d '{"properties":{"link":{"url":{}}}}'
# → 200 OK, 返 {"properties":{"link":{"type":"url","url":{}},"名称":{...},...}}
```

**矛盾 docs**: 多数 blog / Stack Overflow / Claude 训练数据都说"Notion API 不支持给现有 database 加 property, 必须 UI 操作"。这是 **stale 知识** (2025-09 之前的事实)。

**修法**: 任何 Notion schema 变更 (新建 / 扩 database property) **先试 PATCH /v1/data_sources/{id}**, 失败再走 kimi-webbridge / UI。

**限制**:
- 不能改 property name (无 PATCH name endpoint)
- 不能 delete property (无 DELETE endpoint, 只能 UI)
- 重复 name 第二次 PATCH 会覆盖原 property type

### 踩坑 2: 跨 db 搬 select / multi_select / status option 必 strip id

**实测错误** (跨 db 搬 3 行 paper 时):
```bash
# payload 用源库 option object (含 id)
{"multi_select": [{"id": "src-xxx-id", "name": "llm"}, ...]}
# → error 400: B=aN is an invalid select option "8dd3f609-8344-4803-bb98-28fe3c8bf815"
```

**真因**: Notion API 校验 `input option id must = target existing id`, 源库 option id 跟目标库不同。

**修法**: payload 永远 strip id 只留 `name`:
```json
{"multi_select": [{"name": "llm"}]}
```

API 按 name 自动匹配目标 db 同 name option, 找不到返 400 `option name "xxx" not found in target data source`。

**实测验证**: 3 行 paper 跨 db 搬, 21 字段 verify 100% (per CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714 §验证)。

### 踩坑 3: data source title ≠ property name

**实测误操作**:
```bash
# 想改 property name 「名称」→「页面」, 实际改了 data source 显示名
ntn api /v1/data_sources/39dfedee-6267-807a-bcb2-000ba858dff2 -X PATCH -d '{"title":[{"type":"text","text":{"content":"页面"}}]}'
# → 返 200, response 显示 data_source.title="页面", 但 properties.名称.name 仍是 "名称"
```

**真因**:
- `data_source.title` = data source 显示名 (e.g. 「论文」, 「New database」)
- `properties.{name}` = property 显示名 (e.g. 「名称」, 「页面」, 「模态类型」)
- API 没有 PATCH property name endpoint, 只能 UI 改

**修法**:
- 接受 property name 1 字段差异 (数据迁移时源「页面」映射到目标「名称」, value 一致)
- 如果非要改 property name 1:1, 必 UI 手动改 (Notion UI database → property header → 改 name)

### 踩坑 4: workspace-level database API 不能 archive

**实测误操作**:
```bash
# 想 archive 误建的新「论文」database
ntn api /v1/databases/51a1c1c9-ad58-48c7-8273-b3e12565b73b -X PATCH -d '{"in_trash":true}'
# → error 400: Archiving workspace level pages via API not supported
```

**真因**: Notion API 限制, workspace-level resource (parent type = workspace) archive / delete 必 UI 操作。child-level resource (parent type = page_id) 可 API archive。

**修法**: workspace-level database 误建 → AskUserQuestion 让 user UI 删, 给 URL + 操作步骤 (打开 URL → 右上角 ··· → Delete → 确认), 不卸给 user "记得删"。

**判断**:
```bash
ntn api /v1/databases/<id> -X GET | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('parent:', d.get('parent', {}).get('type'))
# workspace → API 不能 archive
# page_id → API 可 archive
"
```

## §3. 4 字段自检表 (跑完 schema 迁移必跑, per §H.1)

| # | 字段 | 验收命令 | 期望 |
|---|------|---------|------|
| 1 | path | `ls ~/.agents/skills/paper-into-notion/` | 1 SKILL + 1 .env.example + 1 USER-SETUP + 10 scripts (含 add-property.sh) + 5 templates (含 cross-db-migrate-payload.md) + 3 references (含 notion-schema-migration.md) = 21 file |
| 2 | commit | `git -C ~/.agents/skills log -1 --oneline` | feat(skill): paper-into-notion v2.1 (跨 db 搬 schema + 4 踩坑) |
| 3 | push | `git -C ~/.agents/skills status -sb` | ahead=0 |
| 4 | CI | `gh api repos/mykcs/myk-skills/commits/HEAD/status` | green |
| 5 | 验收证据 | `bash scripts/paper-into-notion.sh --verify` (主 skill 自检) + `bash scripts/add-property.sh 39dfedee-... link url` (新 script 自检) | 9/9 + 1/1 全过 |

## §4. Notion 2025 API endpoint 速查 (12 关键)

| Endpoint | Method | 用途 | 2025-09+ |
|---|---|---|---|
| `/v1/databases` | POST | 创建 database (auto 1 data source) | ✅ |
| `/v1/databases/{id}` | GET | 读 database metadata (title / icon) | ⚠️ 返 404 if integration 只 share data source |
| `/v1/databases/{id}` | PATCH | 改 database title / icon | ✅ |
| `/v1/databases/{id}/query` | POST | 读 page list (老, 已 deprecated) | ❌ 改用 data source |
| `/v1/data_sources` | POST | 创建 data source (不常用) | ✅ |
| `/v1/data_sources/{id}` | GET | 读 data source (含 schema / properties) | ✅ 推荐 |
| `/v1/data_sources/{id}` | PATCH | 改 schema (加 property) + 改 title | ✅ 推荐 |
| `/v1/data_sources/{id}/query` | POST | 读 page list (新, 替代老 database query) | ✅ |
| `/v1/data_sources/{id}/templates` | GET | 列 templates | ✅ |
| `/v1/pages` | POST | 创建 page (parent = data_source_id) | ✅ |
| `/v1/pages/{id}` | PATCH | 改 page properties (跟 v2.0 paper-into-notion 一致) | ✅ |
| `/v1/pages/{id}` | GET | 读 page | ✅ |
| `/v1/search` | POST | 搜 page / database / data_source | ✅ |

**推荐** (新代码):
- 读 schema: `GET /v1/data_sources/{id}`
- 读 rows: `POST /v1/data_sources/{id}/query`
- 写 page: `POST /v1/pages` (parent.type = "data_source_id")
- 改 schema: `PATCH /v1/data_sources/{id}` (properties map)

**避免** (老 / deprecated):
- `GET /v1/databases/{id}/query` (老 database query, 已 deprecated)
- `POST /v1/pages` (parent.type = "database_id") (老, 已 deprecated)

## §5. Notion 错误码速查 (5 高频)

| 错误码 | HTTP | 含义 | 修法 |
|---|---|---|---|
| `validation_error` | 400 | payload 校验失败 (option id 跨库 / property 缺 / 字段名错) | 读 body message 找具体字段, per 错误码速查 (cross-db-migrate-payload.md §5) |
| `object_not_found` | 404 | database / data source / page id 错或 integration 未 share | UI 加 Connections: Notion CLI / 重新拿 id (per nt datasources resolve) |
| `unauthorized` | 401 | Notion API token 错或过期 | 重 ntn login (per ADR-0026 必读 body) |
| `restricted_resource` | 403 | integration 没 share 权限 | UI 加 Connections |
| `rate_limited` | 429 | API rate limit (3 req/s) | 退避 1s 重试, per CASE-LARK-CLI-1-0-63-CWD-FILE-20260706 |

## §6. 联动引用

- 起源 case: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714
- ADR: ADR-0057-c (v2.1 升级) / ADR-0026 (curl verify 必读 body) / ADR-0054 (Notion 严格层) / ADR-0057-b / ADR-0057
- 协议: §H.1 Acceptance Protocol 5 字段验收 / §C.3.1 worktree / §C.3.2 PR auto-merge / v2.6.30 §I self-evolution
- 工具: `ntn` CLI 0.18.1 (Notion-Version: 2026-03-11 header) / `scripts/add-property.sh` (本 skill) / `templates/cross-db-migrate-payload.md` (本 skill)
- Notion 官方: [data sources 2025-09 release notes](https://developers.notion.com/changelog) (用户实际查证入口)
