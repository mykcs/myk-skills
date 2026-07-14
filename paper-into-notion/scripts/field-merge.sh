#!/usr/bin/env bash
# field-merge.sh — 字段级 merge 算法 (per ADR-0057 v1.4)
# 用法:
#   默认 (修法 1, 安全):
#     bash field-merge.sh <TITLE> <MODAL> <SOURCE_URL> <KNOWLEDGE_TAGS_JSON> <EDUCATION_TAGS_JSON> <HIGHLIGHTS_TEXT>
#   --force (覆盖模式, 慎用):
#     bash field-merge.sh --force <PAGE_ID> <TITLE> <MODAL> <SOURCE_URL> <KNOWLEDGE_TAGS_JSON> <EDUCATION_TAGS_JSON> <HIGHLIGHTS_TEXT>
# 输出: ntn POST/PATCH 返的 page JSON {id, url, ...}
# 铁律 (per ADR-0057 v1.4, schema 8 字段: 页面/状态/模态/link/亮点/知识点/教育类型/上次编辑时间):
#   - 默认: 新 page POST body 含 全 7 auto 字段 (link 自动填 URL); 已有 page PATCH body 永远不含 multi_select + rich_text + url
#   - --force: 已有 page PATCH body 含 全 7 字段 (覆盖模式)
#   - 上次编辑时间: Notion auto, 不传

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
elif [ -f "$SKILL_DIR/.env.example" ]; then
  set -a; . "$SKILL_DIR/.env.example"; set +a
fi

DS_ID="${NOTION_DATA_SOURCE_ID:?NOTION_DATA_SOURCE_ID unset}"
VERSION="${NOTION_VERSION:-2026-03-11}"

# 解析 --force flag
FORCE=false
if [ "${1:-}" = "--force" ]; then
  FORCE=true
  shift
fi

PAGE_ID=""
if [ "$FORCE" = "true" ]; then
  PAGE_ID="${1:?--force 模式需 page_id}"
  shift
fi

TITLE="${1:-}"
MODAL="${2:-其他}"
SOURCE_URL="${3:-}"           # v1.4 新增: link url 字段
KNOWLEDGE_TAGS="${4:-}"      # JSON 数组字符串, 可选
EDUCATION_TAGS="${5:-}"      # JSON 数组字符串, 可选
HIGHLIGHTS="${6:-}"           # 纯文本, 可选

if [ -z "$TITLE" ]; then
  echo "用法 (默认 修法 1):" >&2
  echo "  bash field-merge.sh <TITLE> <MODAL> <SOURCE_URL> [KNOWLEDGE_TAGS] [EDUCATION_TAGS] [HIGHLIGHTS]" >&2
  echo "用法 (--force 覆盖, 慎用):" >&2
  echo "  bash field-merge.sh --force <PAGE_ID> <TITLE> <MODAL> <SOURCE_URL> [KNOWLEDGE_TAGS] [EDUCATION_TAGS] [HIGHLIGHTS]" >&2
  exit 1
fi

# === 公共: 构造 7 字段 properties 段 ===
build_auto_props() {
  local SOURCE_URL="$1"
  local KNOWLEDGE_TAGS="$2"
  local EDUCATION_TAGS="$3"
  local HIGHLIGHTS="$4"

  local LINK_PROP=""
  if [ -n "$SOURCE_URL" ]; then
    LINK_PROP=",\"link\":{\"url\":$(echo "$SOURCE_URL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}"
  fi

  local KNOWLEDGE_PROP=""
  if [ -n "$KNOWLEDGE_TAGS" ] && [ "$KNOWLEDGE_TAGS" != "[]" ]; then
    local KNOWLEDGE_NAMES
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

  local EDUCATION_PROP=""
  if [ -n "$EDUCATION_TAGS" ] && [ "$EDUCATION_TAGS" != "[]" ]; then
    local EDUCATION_NAMES
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

  local HIGHLIGHTS_PROP=""
  if [ -n "$HIGHLIGHTS" ]; then
    local HIGHLIGHTS_JSON
    HIGHLIGHTS_JSON=$(echo "$HIGHLIGHTS" | python3 -c "
import json, sys
text = sys.stdin.read().strip()
if text:
    print(json.dumps([{'text': {'content': text}}], ensure_ascii=False))
")
    if [ -n "$HIGHLIGHTS_JSON" ]; then
      HIGHLIGHTS_PROP=",\"亮点\":{\"rich_text\":${HIGHLIGHTS_JSON}}"
    fi
  fi

  echo "${LINK_PROP}${KNOWLEDGE_PROP}${EDUCATION_PROP}${HIGHLIGHTS_PROP}"
}

# === --force 路径 ===
if [ "$FORCE" = "true" ]; then
  echo "⚠️ --force 模式: PATCH 已有 page $PAGE_ID 全 7 字段 (覆盖你已有内容)" >&2
  AUTO_PROPS=$(build_auto_props "$SOURCE_URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS")
  PATCH_BODY=$(cat <<EOF
{
  "properties": {
    "页面": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"status": {"name": "未开始"}},
    "模态类型": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}$AUTO_PROPS
  }
}
EOF
)
  ntn api --method PATCH "/v1/pages/$PAGE_ID" -d "$PATCH_BODY"
  exit 0
fi

# === 默认路径: 修法 1 ===
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

if [ "$COUNT" = "0" ]; then
  echo "→ POST 新 page (含 7 字段: 3 auto + link + 知识点 + 教育类型 + 亮点)" >&2
  AUTO_PROPS=$(build_auto_props "$SOURCE_URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS")
  POST_BODY=$(cat <<EOF
{
  "parent": {"type": "data_source_id", "data_source_id": "$DS_ID"},
  "properties": {
    "页面": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"status": {"name": "未开始"}},
    "模态类型": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}$AUTO_PROPS
  }
}
EOF
)
  ntn api --method POST /v1/pages -d "$POST_BODY"
  exit 0
fi

if [ "$COUNT" = "1" ]; then
  EXISTING_PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id')
  echo "→ PATCH 已有 page $EXISTING_PAGE_ID (body 只含 3 auto 字段, 修法 1)" >&2
  PATCH_BODY=$(cat <<EOF
{
  "properties": {
    "页面": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"status": {"name": "未开始"}},
    "模态类型": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}
  }
}
EOF
)
  ntn api --method PATCH "/v1/pages/$EXISTING_PAGE_ID" -d "$PATCH_BODY"
  exit 0
fi

echo "❌ duplicate title: $TITLE (找到 $COUNT 条 page, 需 user 手动 dedup)" >&2
exit 1