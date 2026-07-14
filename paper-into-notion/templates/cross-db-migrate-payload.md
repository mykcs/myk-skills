# 跨 Notion database 搬 paper payload 生成模板

> 适用场景: 把 source database 的 1+ 行 page 跟 schema 1:1 搬到 target database (target 已建好 + 8 property 就位)
>
> 配套: `scripts/add-property.sh` (给 target 加 property) / `references/notion-schema-migration.md` (Notion 2025 API model 速查) / `references/notion-url-parse.md` (URL 4 类 + 修哪一部分 4 决路径) / `templates/notion-fix-cheatsheet.md` (4 类常见问题)
> v2.2 (2026-07-14) 加 §0 Notion URL 解读段 (per ADR-0057-d)
>
> 起源: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714

---

## §0. Notion URL 解读 (v2.2 新立, 跨 db 搬前必读)

跨 db 搬 paper 前, 必须从 user 给的 URL 拿对 id。Notion URL `https://app.notion.com/p/{32-char-id}?v={view-id}` 32-char id 本身不携带类型信息, 必跑 API 反查:

```bash
# Step 1: 拿 id
URL="https://app.notion.com/p/39dfedee6267808fafc7d9b3cc2d43f1"
ID=$(echo "$URL" | sed 's/.*p\///; s/?.*//; s/-//g')
ID_DASHED="${ID:0:8}-${ID:8:4}-${ID:12:4}-${ID:16:4}-${ID:20:12}"
echo "id: $ID_DASHED"

# Step 2: resolve (新 endpoint, 找 id 类型)
ntn datasources resolve "$ID_DASHED"
# → 200 + name = database / data source
# → 404 = id 是 page 不是 database (or integration 没 share)

# Step 3: query (read access 判定)
ntn datasources query "$ID_DASHED" --limit 1
# → 200 = 有 read access
# → 404 = integration 没 share (UI 加 Connections: Notion CLI)

# Step 4: 拿 data source id (跟 database id 可能不同)
# 真正用于 POST /v1/pages parent 的是 data source id, 不是 database id
DS_ID=$(ntn datasources resolve "$ID_DASHED" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id', ''))")
echo "data source id: $DS_ID"
```

**4 决路径** (改哪一部分, 跨 db 搬相关 2 类):
- 跨 db 搬 paper 前 target db 缺 schema → 改 schema → `scripts/add-property.sh`
- 跨 db 搬 paper 单行 cell 值 → 改 page row → `scripts/paper-into-notion.sh`

**更详细**: `references/notion-url-parse.md` §1 §2 §3 (4 类 URL + id 提取 + 4 决路径) / `templates/notion-fix-cheatsheet.md` §2 (1 跳决策树)

---

## §1. 字段映射表 (源「论文」9 field → 目标 8 property)

| 源 field | type | 目标 property | type | 必传字段 |
|---|---|---|---|---|
| 页面 | title | 名称 (或「页面」, 看 target 命名) | title | 整个 title array |
| link | url | link | url | `{"url": "<value>"}` 或 `{"url": null}` |
| 亮点 | rich_text | 亮点 | rich_text | 整个 rich_text array, 空时 `[]` |
| 教育类型 | multi_select | 教育类型 | multi_select | **strip id, 只留 name** (见 §2) |
| 日期 | date | 日期 | date | `{"date": <value>}` 或 `{"date": null}` |
| 模态类型 | select | 模态类型 | select | **strip id, 只留 name** |
| 状态 | status | 状态 | status | **strip id, 只留 name** |
| 知识点 | multi_select | 知识点 | multi_select | **strip id, 只留 name** |
| 地点 | place | (target 通常无) | — | 跳过 |

## §2. strip id 规则 (跨 db 必走, 永久生效)

**踩坑**: Notion API 校验 `input option id must = target existing id`, 源库 option id 跟目标库不同, 直接传 source object 报 `invalid select option "xxx-id"`。

**正确 payload** (跨 db 搬):
```json
{
  "multi_select": [{"name": "llm"}],
  "select": {"name": "arXiv"},
  "status": {"name": "未开始"}
}
```

**错误 payload** (跨 db 搬, 报 400):
```json
{
  "multi_select": [{"id": "src-xxx-id", "name": "llm"}],  // ← 错: 跨库 id 不通用
  "select": {"id": "src-yyy-id", "name": "arXiv"},          // ← 错
  "status": {"id": "src-zzz-id", "name": "未开始"}          // ← 错
}
```

## §3. payload 生成 Python 模板 (9 字段, 跨 db 搬)

```python
import json

def to_payload(props_src, target_title_field='名称'):
    """源 9 字段 → 目标 8 property 1:1, strip id 规则"""
    out = {}
    # title (源「页面」→ target 字段名通常是「名称」, 看你 target schema)
    out[target_title_field] = {'title': props_src['页面']['title']}
    out['link'] = {'url': props_src['link'].get('url')}
    out['亮点'] = {'rich_text': props_src['亮点']['rich_text'] if props_src['亮点']['rich_text'] else []}
    # multi_select: strip id
    out['教育类型'] = {'multi_select': [{'name': x['name']} for x in props_src['教育类型']['multi_select']]}
    out['日期'] = {'date': props_src['日期'].get('date')}
    # select: strip id
    sel = props_src['模态类型'].get('select')
    out['模态类型'] = {'select': {'name': sel['name']} if sel else None}
    # status: strip id
    sta = props_src['状态'].get('status')
    out['状态'] = {'status': {'name': sta['name']} if sta else {'name': '未开始'}}
    # multi_select: strip id
    out['知识点'] = {'multi_select': [{'name': x['name']} for x in props_src['知识点']['multi_select']]}
    return out

# 用法
for r in json.load(open('/tmp/source-papers.json'))['results']:
    payload = {
        "parent": {"type": "data_source_id", "data_source_id": "<target_ds_id>"},
        "properties": to_payload(r['properties'])
    }
    # POST 到 target
```

## §4. 验证脚本 (7 字段比对, 跟源 1:1)

```python
import json
src = json.load(open('/tmp/source-papers.json'))  # 源 datasources query 结果
tgt = json.load(open('/tmp/target-papers.json'))  # 目标 datasources query 结果

for tr in tgt['results']:
    tp = tr['properties']
    title = tp['名称']['title'][0]['plain_text'] if tp['名称']['title'] else '(空)'
    sr = next((r for r in src['results']
               if r['properties']['页面']['title'][0]['plain_text'] == title), None)
    if not sr: continue
    sp = sr['properties']
    # 7 字段比对 (link / 亮点 / 教育类型 / 日期 / 模态类型 / 状态 / 知识点)
    checks = {
        'link': (sp['link'].get('url'), tp['link'].get('url')),
        '亮点': (''.join(x['plain_text'] for x in sp['亮点']['rich_text']),
                ''.join(x['plain_text'] for x in tp['亮点']['rich_text'])),
        '教育类型': (sorted(x['name'] for x in sp['教育类型']['multi_select']),
                   sorted(x['name'] for x in tp['教育类型']['multi_select'])),
        '日期': (sp['日期'].get('date'), tp['日期'].get('date')),
        '模态类型': (sp['模态类型'].get('select', {}).get('name') if sp['模态类型'].get('select') else None,
                   tp['模态类型'].get('select', {}).get('name') if tp['模态类型'].get('select') else None),
        '状态': (sp['状态'].get('status', {}).get('name') if sp['状态'].get('status') else None,
                tp['状态'].get('status', {}).get('name') if tp['状态'].get('status') else None),
        '知识点': (sorted(x['name'] for x in sp['知识点']['multi_select']),
                  sorted(x['name'] for x in tp['知识点']['multi_select'])),
    }
    pass_n = sum(1 for k, (s, t) in checks.items() if s == t)
    print(f'{title}: {pass_n}/7 {"✅" if pass_n == 7 else "❌"}')
```

## §5. 错误码速查

| 错误信息 | 真因 | 修法 |
|---|---|---|
| `B=aN is an invalid select option "xxx-id"` | 跨 db 传了源库 option id | payload strip id 只留 name (per §2) |
| `~}nf is an invalid select option "yyy-id"` | 同上 (multi_select 跨 db id 冲突) | 同上 |
| `Could not find database with ID: xxx` | target database 没 share 给 integration | UI target database → ··· → Connections → 加 Notion CLI |
| `Could not find page with ID: xxx` | page id 格式错 (缺 dashes 位置) | 用 `ntn pages get` 或 `datasources query` 拿正确 id |
| `link is not a property that exists.` | target database 缺该 property | 先跑 `add-property.sh` 加 property (per §6) |
| `Archiving workspace level pages via API not supported` | workspace-level database API 不能 archive | UI 删 (per §7) |

## §6. add-property.sh 用法 (前置: target db 缺 property)

```bash
# 单个 property
bash scripts/add-property.sh <target_ds_id> "link" "url"
bash scripts/add-property.sh <target_ds_id> "亮点" "rich_text"
bash scripts/add-property.sh <target_ds_id> "教育类型" "multi_select" '[{"name":"论文阅读","color":"blue"}]'
bash scripts/add-property.sh <target_ds_id> "模态类型" "select" '[{"name":"arXiv","color":"blue"}]'
bash scripts/add-property.sh <target_ds_id> "状态" "status" '[{"name":"未开始","color":"default"}]'
bash scripts/add-property.sh <target_ds_id> "日期" "date"

# 7 个 property 一次性 (8 property 1:1 跟源库, 假设「页面」title 已存在)
DS="<target_ds_id>"
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

## §7. workspace-level database 必 UI 删 (API 限制)

```bash
# API 不能 archive, 必 UI 操作
ntn api /v1/databases/<id> -X PATCH -d '{"in_trash":true}'
# → error: Public API request failed (400 Bad Request validation_error):
#   Archiving workspace level pages via API not supported.

# UI 步骤: 打开 URL → 右上角 ··· → Delete → 确认
echo "https://app.notion.com/p/<page-id>"
```

## §8. 联动引用

- 起源 case: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714
- ADR: ADR-0057-c (v2.1 升级) / ADR-0057-b (v2.0) / ADR-0057 (v1.0)
- API model: `references/notion-schema-migration.md` (Notion 2025 data_source 模型速查)
- 配套 script: `scripts/add-property.sh` (跨 db 加 property 独立可用)
- 主 skill: SKILL.md v2.1 (frontmatter 4 字段全合规)
- 协议: §H.1 5 字段验收 / §C.3.1 worktree / §C.3.2 PR auto-merge / v2.6.30 §I self-evolution
