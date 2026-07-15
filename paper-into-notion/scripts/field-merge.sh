#!/usr/bin/env bash
# field-merge.sh — 字段级 merge 算法 (per ADR-0057 v3.1)
# 用法:
#   默认 (修法 1, 安全):
#     bash field-merge.sh <TITLE> <MODAL> <SOURCE_URL> <KNOWLEDGE_TAGS_JSON> <EDUCATION_TAGS_JSON> <HIGHLIGHTS_TEXT> [INSTITUTIONS_JSON] [KNOWLEDGE_GROWTH_TAGS_JSON]
# 输出: ntn POST/PATCH 返的 page JSON {id, url, ...}
# v3.7 增量: KNOWLEDGE_GROWTH_TAGS (第 8 参数) 写 知识等级形态 multi_select, Q8B user 拍板: scripts 不读旧值 (字段新建无历史值), LLM judge 输出直接 PATCH
#             FORM_PROP 完全弃用 (旧 展现形式 select user UI 删了, 不要再读)

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

# === v3.0 introspect mode (v3.7+ disabled by default, .env wins, cache stale risk) ===
INTROSPECT_OUT=""
if [ "${NOTION_INTROSPECT:-false}" = "true" ]; then
  INTROSPECT_OUT=$(python3 "$SCRIPT_DIR/introspect.py" "$DS_ID" "$SKILL_DIR/.introspect-cache.json" 2>/dev/null || true)
  if [ -n "$INTROSPECT_OUT" ]; then
    eval "$INTROSPECT_OUT"
  fi
fi

TITLE_PROP="${NOTION_TITLE_PROPERTY:-${TITLE_PROP:-页面}}"
STATUS_DEFAULT="${NOTION_STATUS_DEFAULT:-${STATUS_DEFAULT:-未开始}}"
LINK_PROP="${NOTION_LINK_PROPERTY:-link}"
ORG_PROP="${NOTION_ORG_PROPERTY:-机构}"
MODAL_PROP="${NOTION_MODAL_PROPERTY:-${MODAL_PROP:-平台形式}}"
KEYWORD_PROP="${NOTION_KEYWORD_PROPERTY:-${KEYWORD_PROP:-关键词}}"   # v3.6
GROWTH_PROP="${NOTION_KNOWLEDGE_GROWTH_PROPERTY:-${KNOWLEDGE_GROWTH_PROP:-知识等级形态}}"   # v3.7

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
EDUCATION_TAGS="${5:-}"      # JSON 数组字符串, 可选 (v3.7 已弃用, scripts 不读)
HIGHLIGHTS="${6:-}"           # 纯文本, 可选
INSTITUTIONS="${7:-}"         # v3.1 新增: JSON 数组字符串 (机构 multi_select)
GROWTH_TAGS="${8:-}"          # v3.7 新增: JSON 数组字符串 (知识等级形态 multi_select)

if [ -z "$TITLE" ]; then
  echo "用法 (默认 修法 1):" >&2
  echo "  bash field-merge.sh <TITLE> <MODAL> <SOURCE_URL> [KNOWLEDGE_TAGS] [EDUCATION_TAGS] [HIGHLIGHTS] [INSTITUTIONS] [GROWTH_TAGS]" >&2
  echo "用法 (--force 覆盖, 慎用):" >&2
  echo "  bash field-merge.sh --force <PAGE_ID> <TITLE> <MODAL> <SOURCE_URL> [KNOWLEDGE_TAGS] [EDUCATION_TAGS] [HIGHLIGHTS] [INSTITUTIONS] [GROWTH_TAGS]" >&2
  exit 1
fi

# === 公共: 构造 8 字段 properties 段 (含 v3.1 INSTITUTIONS) ===
build_auto_props() {
  local SOURCE_URL="$1"
  local KNOWLEDGE_TAGS="$2"
  local EDUCATION_TAGS="$3"
  local HIGHLIGHTS="$4"
  local INSTITUTIONS="$5"

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
      KNOWLEDGE_PROP=",\"${KEYWORD_PROP}\":{\"multi_select\":[${KNOWLEDGE_NAMES}]}"
    fi
  fi

  local EDUCATION_PROP=""
  # v3.7: FORM_PROP 弃用 (旧 展现形式 select user UI 删, scripts 不再 POST 该字段)
  # EDUCATION_TAGS 参数保留兼容, 但不写入 PATCH body

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

  # v3.1: 机构 multi_select (per ADR-0057 v3.3: 不写死 whitelist, auto-add option to schema)
  # v3.3 增量: PATCH 前 sync 缺失的 institution options 到 schema (否则 Notion API 400 option not found)
  local INSTITUTIONS_PROP=""
  if [ -n "$INSTITUTIONS" ] && [ "$INSTITUTIONS" != "[]" ]; then
    local INSTITUTIONS_NAMES
    INSTITUTIONS_NAMES=$(echo "$INSTITUTIONS" | python3 -c "
import json, sys
try:
    tags = json.loads(sys.stdin.read())
    if isinstance(tags, list) and len(tags) > 0:
        print(','.join([json.dumps({'name': t}) for t in tags]))
except: pass
")
    if [ -n "$INSTITUTIONS_NAMES" ]; then
      # v3.3: sync 缺失 options 到 schema (auto-add, 不报错, 调独立 Python 脚本)
      python3 "$SCRIPT_DIR/sync-institution-options.py" "$DS_ID" "$INSTITUTIONS" 2>/dev/null || true
      INSTITUTIONS_PROP=",\"${ORG_PROP:-机构}\":{\"multi_select\":[${INSTITUTIONS_NAMES}]}"
    fi
  fi

  echo "${LINK_PROP}${KNOWLEDGE_PROP}${EDUCATION_PROP}${HIGHLIGHTS_PROP}${INSTITUTIONS_PROP}"
}

TITLE_PROP="${NOTION_TITLE_PROPERTY:-页面}"
LINK_PROP="${NOTION_LINK_PROPERTY:-link}"
ORG_PROP="${NOTION_ORG_PROPERTY:-机构}"

# === --force 路径 ===
if [ "$FORCE" = "true" ]; then
  echo "⚠️ --force 模式: PATCH 已有 page $PAGE_ID 全 8 字段 (覆盖你已有内容)" >&2
  AUTO_PROPS=$(build_auto_props "$SOURCE_URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS" "$INSTITUTIONS")
  PATCH_BODY=$(cat <<EOF
{
  "properties": {
    "$TITLE_PROP": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"status": {"name": "$STATUS_DEFAULT"}},
    "$MODAL_PROP": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}$AUTO_PROPS
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
    "property": "$TITLE_PROP",
    "title": {"equals": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}
  },
  "page_size": 2
}
EOF
)
QUERY_RESULT=$(ntn api --method POST "/v1/data_sources/$DS_ID/query" -d "$QUERY_BODY" 2>&1)
COUNT=$(echo "$QUERY_RESULT" | jq '.results | length' 2>/dev/null || echo "0")

if [ "$COUNT" = "0" ]; then
  echo "→ POST 新 page (含 7 字段: 3 auto + link + 关键词 + 知识等级形态 + 亮点 + 机构)" >&2
  AUTO_PROPS=$(build_auto_props "$SOURCE_URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS" "$INSTITUTIONS")
  POST_BODY=$(cat <<EOF
{
  "parent": {"type": "data_source_id", "data_source_id": "$DS_ID"},
  "properties": {
    "$TITLE_PROP": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"status": {"name": "$STATUS_DEFAULT"}},
    "$MODAL_PROP": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}$AUTO_PROPS
  }
}
EOF
)
  ntn api --method POST /v1/pages -d "$POST_BODY"
  exit 0
fi

if [ "$COUNT" = "1" ]; then
  EXISTING_PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id')
  echo "→ PATCH 已有 page $EXISTING_PAGE_ID (v3.1 空才填: title/status/modal/link 永远写; knowledge/education/highlights/org 空才填)" >&2
  # v3.0: GET page 字段空判定 → body 包不包 LLM 字段
  PROP_STATUS=$(bash "$SCRIPT_DIR/get-page-props.sh" "$EXISTING_PAGE_ID" 2>/dev/null || echo "")
  LINK_EMPTY=false; KNOWLEDGE_EMPTY=false; EDUCATION_EMPTY=false; HIGHLIGHTS_EMPTY=false; ORG_EMPTY=false
  if [ -n "$PROP_STATUS" ]; then
    grep -q '^link=empty$' <<<"$PROP_STATUS" && LINK_EMPTY=true
    grep -q '^knowledge=empty$' <<<"$PROP_STATUS" && KNOWLEDGE_EMPTY=true
    grep -q '^education=empty$' <<<"$PROP_STATUS" && EDUCATION_EMPTY=true
    grep -q '^highlights=empty$' <<<"$PROP_STATUS" && HIGHLIGHTS_EMPTY=true
    grep -q '^org=empty$' <<<"$PROP_STATUS" && ORG_EMPTY=true
  fi

  PATCH_LLM_PROPS=""
  if [ -n "$SOURCE_URL" ] && [ "$LINK_EMPTY" = "true" ]; then
    PATCH_LLM_PROPS+=",\"link\":{\"url\":$(echo "$SOURCE_URL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}"
  fi
  if [ -n "$KNOWLEDGE_TAGS" ] && [ "$KNOWLEDGE_TAGS" != "[]" ] && [ "$KNOWLEDGE_EMPTY" = "true" ]; then
    KNOWLEDGE_NAMES=$(echo "$KNOWLEDGE_TAGS" | python3 -c "
import json, sys
try:
    tags = json.loads(sys.stdin.read())
    if isinstance(tags, list) and len(tags) > 0:
        print(','.join([json.dumps({'name': t}) for t in tags]))
except: pass
")
    if [ -n "$KNOWLEDGE_NAMES" ]; then
      PATCH_LLM_PROPS+=",\"${KEYWORD_PROP}\":{\"multi_select\":[${KNOWLEDGE_NAMES}]}"
    fi
  fi
  # v3.7: FORM_PROP 弃用 (旧 展现形式 select user UI 删), EDUCATION_TAGS 不写入 PATCH body
  if [ -n "$HIGHLIGHTS" ] && [ "$HIGHLIGHTS_EMPTY" = "true" ]; then
    HIGHLIGHTS_JSON=$(echo "$HIGHLIGHTS" | python3 -c "
import json, sys
text = sys.stdin.read().strip()
if text:
    print(json.dumps([{'text': {'content': text}}], ensure_ascii=False))
")
    if [ -n "$HIGHLIGHTS_JSON" ]; then
      PATCH_LLM_PROPS+=",\"亮点\":{\"rich_text\":${HIGHLIGHTS_JSON}}"
    fi
  fi
  # v3.1: 机构 multi_select (SZU/PolyU)
  if [ -n "$INSTITUTIONS" ] && [ "$INSTITUTIONS" != "[]" ] && [ "$ORG_EMPTY" = "true" ]; then
    INST_NAMES=$(echo "$INSTITUTIONS" | python3 -c "
import json, sys
try:
    tags = json.loads(sys.stdin.read())
    if isinstance(tags, list) and len(tags) > 0:
        print(','.join([json.dumps({'name': t}) for t in tags]))
except: pass
")
    if [ -n "$INST_NAMES" ]; then
      PATCH_LLM_PROPS+=",\"${ORG_PROP:-机构}\":{\"multi_select\":[${INST_NAMES}]}"
    fi
  fi

  PATCH_BODY=$(cat <<EOF
{
  "properties": {
    "$TITLE_PROP": {"title": [{"text": {"content": $(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}]},
    "状态": {"status": {"name": "$STATUS_DEFAULT"}},
    "$MODAL_PROP": {"select": {"name": $(echo "$MODAL" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}}$PATCH_LLM_PROPS
  }
}
EOF
)
  FILLED_COUNT=$(echo "$PATCH_LLM_PROPS" | grep -oE ',"(link|'"${KEYWORD_PROP:-关键词}"'|'"${GROWTH_PROP:-知识等级形态}"'|亮点|'"${ORG_PROP:-机构}"')"' | wc -l | tr -d ' ')
  echo "    [v3.1] 字段空判定: link=$LINK_EMPTY knowledge=$KNOWLEDGE_EMPTY education=$EDUCATION_EMPTY highlights=$HIGHLIGHTS_EMPTY org=$ORG_EMPTY" >&2
  echo "    [v3.0] 本次 fill-empty 实际填 $FILLED_COUNT LLM 字段 (非空保留)" >&2
  ntn api --method PATCH "/v1/pages/$EXISTING_PAGE_ID" -d "$PATCH_BODY"
  exit 0
fi

echo "❌ duplicate title: $TITLE (找到 $COUNT 条 page, 需 user 手动 dedup)" >&2
exit 1