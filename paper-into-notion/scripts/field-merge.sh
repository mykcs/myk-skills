#!/usr/bin/env bash
# field-merge.sh — 字段级 merge 算法 (per Q2 严格模式 + Q4 自修复)
# 用法: bash field-merge.sh <TITLE> <MODAL>
# 输出: ntn POST/PATCH 返的 page JSON {id, url, ...}
# 铁律: PATCH body 永远不包含 multi_select (教育类型/标签/知识点) + rich_text (亮点)
#       新 page POST body 也只含 3 auto 字段, 多选字段后填

set -euo pipefail
TITLE="${1:-}"
MODAL="${2:-其他}"
DS_ID="${NOTION_DATA_SOURCE_ID:?NOTION_DATA_SOURCE_ID unset}"
VERSION="${NOTION_VERSION:-2026-03-11}"

if [ -z "$TITLE" ]; then
  echo "用法: bash field-merge.sh <TITLE> <MODAL>" >&2
  exit 1
fi

# Step 1: GET 找 page (POST data source query, 旧 database query 已废)
QUERY_BODY=$(cat <<EOF
{
  "filter": {
    "property": "页面",
    "title": {"equals": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}
  },
  "page_size": 2
}
EOF
)

QUERY_RESULT=$(ntn api --method POST "/v1/data_sources/$DS_ID/query" -d "$QUERY_BODY" 2>&1)

COUNT=$(echo "$QUERY_RESULT" | jq '.results | length' 2>/dev/null || echo "0")

# Step 2: 0 条 → POST 新 page, body 只含 3 auto 字段
if [ "$COUNT" = "0" ]; then
  echo "→ POST 新 page (multi_select 全空, body 只含 3 auto 字段)" >&2
  POST_BODY=$(cat <<EOF
{
  "parent": {"type": "data_source_id", "data_source_id": "$DS_ID"},
  "properties": {
    "页面": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"select": {"name": "未开始"}},
    "模态类型": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}
  }
}
EOF
)
  ntn api --method POST /v1/pages -d "$POST_BODY"
  exit 0
fi

# Step 3: 1 条 → PATCH 3 auto 字段, body 永远不含 multi_select
if [ "$COUNT" = "1" ]; then
  PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id')
  echo "→ PATCH 已有 page $PAGE_ID (body 不含 multi_select)" >&2
  PATCH_BODY=$(cat <<EOF
{
  "properties": {
    "页面": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"select": {"name": "未开始"}},
    "模态类型": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}
  }
}
EOF
)
  ntn api --method PATCH "/v1/pages/$PAGE_ID" -d "$PATCH_BODY"
  exit 0
fi

# Step 4: 2+ 条 → exit 1 "duplicate title" (需 user 手动 dedup)
echo "❌ duplicate title: $TITLE (找到 $COUNT 条 page, 需 user 手动 dedup)" >&2
exit 1