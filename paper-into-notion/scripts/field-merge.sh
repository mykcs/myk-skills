#!/usr/bin/env bash
# field-merge.sh — 字段级 merge 算法 (per ADR-0057 v1.2 修法 1 扩展到教育类型)
# 用法: bash field-merge.sh <TITLE> <MODAL> <KNOWLEDGE_TAGS_JSON> <EDUCATION_TAGS_JSON>
# 输出: ntn POST/PATCH 返的 page JSON {id, url, ...}
# 铁律 (per ADR-0057 v1.2):
#   - 新 page POST body 含: 3 auto 字段 + 知识点 + 教育类型 (LLM judge 自动填)
#   - 已有 page PATCH body 永远不含 multi_select (教育类型/标签/知识点) + rich_text (亮点)
#   - 上次编辑时间: Notion auto, 不传

set -euo pipefail
TITLE="${1:-}"
MODAL="${2:-其他}"
KNOWLEDGE_TAGS="${3:-}"     # JSON 数组字符串, 可选
EDUCATION_TAGS="${4:-}"     # JSON 数组字符串, 可选 (v1.2 新增)

# 加载 .env (NOTION_DATA_SOURCE_ID + NOTION_VERSION)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
elif [ -f "$SKILL_DIR/.env.example" ]; then
  set -a; . "$SKILL_DIR/.env.example"; set +a
fi

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

# Step 2: 0 条 → POST 新 page, body 含 3 auto 字段 + 知识点 + 教育类型 (per ADR-0057 v1.2 修法 1)
if [ "$COUNT" = "0" ]; then
  echo "→ POST 新 page (含 3 auto 字段 + 知识点 + 教育类型)" >&2
  # 构造知识点 properties 段 (可选, 来自 knowledge-tag-judge.sh)
  KNOWLEDGE_PROP=""
  if [ -n "$KNOWLEDGE_TAGS" ] && [ "$KNOWLEDGE_TAGS" != "[]" ]; then
    KNOWLEDGE_NAMES=$(echo "$KNOWLEDGE_TAGS" | python3 -c "
import json, sys
try:
    tags = json.loads(sys.stdin.read())
    if isinstance(tags, list) and len(tags) > 0:
        print(','.join([json.dumps({'name': t}) for t in tags]))
except: pass
")
    if [ -n "$KNOWLEDGE_NAMES" ]; then
      KNOWLEDGE_PROP=",\"知识点\":{\"multi_select\":[${KNOWLEDGE_NAMES}]}"
    fi
  fi
  # 构造教育类型 properties 段 (可选, 来自 education-type-judge.sh)
  EDUCATION_PROP=""
  if [ -n "$EDUCATION_TAGS" ] && [ "$EDUCATION_TAGS" != "[]" ]; then
    EDUCATION_NAMES=$(echo "$EDUCATION_TAGS" | python3 -c "
import json, sys
try:
    tags = json.loads(sys.stdin.read())
    if isinstance(tags, list) and len(tags) > 0:
        print(','.join([json.dumps({'name': t}) for t in tags]))
except: pass
")
    if [ -n "$EDUCATION_NAMES" ]; then
      EDUCATION_PROP=",\"教育类型\":{\"multi_select\":[${EDUCATION_NAMES}]}"
    fi
  fi
  POST_BODY=$(cat <<EOF
{
  "parent": {"type": "data_source_id", "data_source_id": "$DS_ID"},
  "properties": {
    "页面": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"select": {"name": "未开始"}},
    "模态类型": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}$KNOWLEDGE_PROP$EDUCATION_PROP
  }
}
EOF
)
  ntn api --method POST /v1/pages -d "$POST_BODY"
  exit 0
fi

# Step 3: 1 条 → PATCH 3 auto 字段, body 永远不含 知识点 (per ADR-0057 v1.1 修法 1)
if [ "$COUNT" = "1" ]; then
  PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id')
  echo "→ PATCH 已有 page $PAGE_ID (body 不含 multi_select, 包括知识点)" >&2
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