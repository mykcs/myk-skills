#!/usr/bin/env bash
# patch-block-direct.sh — Notion 块级 PATCH (改单 block / table_row 子 cell, v11 新走法)
# 用法: patch-block-direct.sh <block_id> <body_json_file>
# 例: patch-block-direct.sh 58ccc819-dace-4e71-964a-dc37197da6fb /tmp/block-body.json
#
# 基于 Notion 2026-03-11 API: PATCH /v1/blocks/{id}
# 不经 markdown endpoint, 不经 patch-markdown-block.sh
# 详见 weiying-notion-MASTER.md v11 §5.2 + CASE-NOTION-BLOCK-PATCH-TABLE-CELL-20260716
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "用法: $0 <block_id> <body_json_file>" >&2
  echo "  block_id: 32-char 无 dash (e.g. 58ccc819dace4e71964adc37197da6fb)" >&2
  echo "            或 36-char UUID 含 dash (e.g. 58ccc819-dace-4e71-964a-dc37197da6fb)" >&2
  echo "  body_json_file: 含 block body JSON, 例:" >&2
  echo '    {"numbered_list_item":{"rich_text":[{"type":"text","text":{"content":"new text"}}]}}' >&2
  echo '    {"table_row":{"cells":[cell1, cell2, ...]}} (改 table_row 子 cell, cells 必传完整数组)' >&2
  exit 2
fi

BLOCK_ID="$1"
BODY_FILE="$2"

if [ ! -f "$BODY_FILE" ]; then
  echo "❌ body_json_file 不存在: $BODY_FILE" >&2
  exit 2
fi

# 0. 规范化 block_id (strip dashes, 32-char)
BLOCK_ID_NODASH=$(echo "$BLOCK_ID" | tr -d '-')

# 1. 必跑 v7.2 §7.1 UUID 格式校验 (per CASE-PAGE-ID-DASHES-FORMAT-20260716)
if ! echo "$BLOCK_ID_NODASH" | grep -qE '^[0-9a-f]{32}$'; then
  echo "❌ block_id 格式错: $BLOCK_ID (期望 32-char no-dash 或 36-char UUID)" >&2
  echo "   例: 58ccc819dace4e71964adc37197da6fb 或 58ccc819-dace-4e71-964a-dc37197da6fb" >&2
  exit 2
fi

# 2. 必跑 body 顶层 key 白名单校验 (per v11 §3, 防 user 写错块类型)
ALLOWED_KEYS="paragraph|numbered_list_item|bulleted_list_item|table_row|to_do|heading_1|heading_2|heading_3|quote|code"
TOP_KEY=$(jq -r 'keys[0]' "$BODY_FILE" 2>/dev/null || echo "")
if [ -z "$TOP_KEY" ] || ! echo "$TOP_KEY" | grep -qE "^($ALLOWED_KEYS)$"; then
  echo "❌ body 顶层 key 错: '$TOP_KEY' (期望: paragraph | numbered_list_item | table_row | ...)" >&2
  echo "   例: {\"paragraph\":{...}} 或 {\"table_row\":{...}}" >&2
  exit 2
fi

# 3. table_row 必传完整 cells 数组 (per v11 §4 IF...THEN #2)
if [ "$TOP_KEY" = "table_row" ]; then
  CELLS_LEN=$(jq -r '.table_row.cells | length' "$BODY_FILE" 2>/dev/null || echo "0")
  if [ "$CELLS_LEN" = "0" ]; then
    echo "❌ table_row.cells 必传完整数组 (不能 partial update)" >&2
    echo "   例: {\"table_row\":{\"cells\":[[{type:\"text\",...}],[{type:\"text\",...}]]}}" >&2
    exit 2
  fi
  echo "📋 table_row 含 $CELLS_LEN 个 cell (全替换, 不可 partial)"
fi

# 4. PATCH (3 retry + 60s timeout, per ntn-cli.md §1.1)
echo "🔨 PATCH /v1/blocks/$BLOCK_ID_NODASH ..."
TASK_ID=""
RESP=""
for attempt in 1 2 3; do
  set +e
  RESP=$(curl -sS -X PATCH "https://api.notion.com/v1/blocks/${BLOCK_ID_NODASH}" \
    -H "Authorization: Bearer ${NOTION_TOKEN:-}" \
    -H "Notion-Version: 2026-03-11" \
    -H "Content-Type: application/json" \
    --data @"$BODY_FILE" 2>&1)
  CURL_RC=$?
  set -e

  # Notion API 200 = success, 4xx = client error (don't retry), 5xx = server error (retry)
  HTTP_CODE=""
  if echo "$RESP" | jq -e '.id' >/dev/null 2>&1; then
    HTTP_CODE="200"
  elif echo "$RESP" | jq -r '.code // .status // empty' 2>/dev/null | grep -qE '^(400|401|403|404|409|422)$'; then
    HTTP_CODE=$(echo "$RESP" | jq -r '.code // .status' 2>/dev/null)
  fi

  if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" = "200" ]; then
    NEW_ID=$(echo "$RESP" | jq -r '.id')
    NEW_TYPE=$(echo "$RESP" | jq -r '.type')
    echo "✅ PATCH 成功 (attempt $attempt): id=$NEW_ID type=$NEW_TYPE"
    break
  fi

  if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" != "200" ]; then
    echo "❌ HTTP $HTTP_CODE 永久失败, 不 retry:" >&2
    echo "$RESP" | jq . 2>/dev/null >&2 || echo "$RESP" >&2
    exit 1
  fi

  echo "⚠️ attempt $attempt 失败 (curl_rc=$CURL_RC), retry in 8s..."
  sleep 8
done

if [ -z "${NEW_ID:-}" ]; then
  echo "❌ PATCH 3 次都失败, 最后响应:" >&2
  echo "$RESP" | jq . 2>/dev/null >&2 || echo "$RESP" >&2
  exit 1
fi

# 5. verify (HTTP GET, per rule #8 + weiying-notion-MASTER.md §6)
echo ""
echo "🔍 verify: GET /v1/blocks/$BLOCK_ID_NODASH ..."
VERIFY_RESP=$(curl -sS "https://api.notion.com/v1/blocks/${BLOCK_ID_NODASH}" \
  -H "Authorization: Bearer ${NOTION_TOKEN:-}" \
  -H "Notion-Version: 2026-03-11" 2>&1)

if echo "$VERIFY_RESP" | jq -e . >/dev/null 2>&1; then
  # 提取新内容 (top_key 决定读哪字段)
  if [ "$TOP_KEY" = "table_row" ]; then
    NEW_TEXT=$(echo "$VERIFY_RESP" | jq -r '.table_row.cells | map(map(.plain_text) | join("")) | join(" | ")')
  else
    NEW_TEXT=$(echo "$VERIFY_RESP" | jq -r --arg key "$TOP_KEY" '.[$key].rich_text | map(.plain_text) | join("")')
  fi
  echo "  new content: ${NEW_TEXT:0:200}$([ ${#NEW_TEXT} -gt 200 ] && echo "...")"
  echo "✅ verify 通过 (HTTP GET 200 + content 可读)"
  echo ""
  echo "📝 后续手动核验: 跑 grep 独特字串确认内容真改 (per rule #8)"
else
  echo "⚠️ verify GET 失败, 必手动 re-GET 确认 (per §6 验证信源唯一性)" >&2
  echo "$VERIFY_RESP" | jq . 2>/dev/null >&2 || echo "$VERIFY_RESP" >&2
  exit 1
fi

# 6. cleanup (临时文件由 caller 管)
echo ""
echo "✅ 全部 done. block_id=$BLOCK_ID_NODASH type=$TOP_KEY"