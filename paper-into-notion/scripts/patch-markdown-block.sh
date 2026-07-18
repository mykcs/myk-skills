#!/usr/bin/env bash
# patch-markdown-block.sh — 改 Notion page body 单段内容 (推荐 default)
# 用法: patch-markdown-block.sh <page_id> <old_str_file> <new_str_file>
# 例: patch-markdown-block.sh 39efedee62678086a384cd6114c7d8c3 /tmp/old.txt /tmp/new.txt
#
# 基于 Notion 2026-03-11 API: PATCH /v1/pages/{id}/markdown + update_content payload
# 详见 ADR-0057-p + CASE-NOTION-MARKDOWN-PATCH-VS-BLOCK-API-20260716
set -euo pipefail

if [ $# -ne 3 ]; then
  echo "用法: $0 <page_id> <old_str_file> <new_str_file>" >&2
  echo "  page_id: 32-char 无 dash (e.g. 39efedee62678086a384cd6114c7d8c3)" >&2
  echo "  old_str_file / new_str_file: 含 exact 文本 (含 mention-page closed form)" >&2
  exit 2
fi

PAGE_ID="$1"
OLD_STR_FILE="$2"
NEW_STR_FILE="$3"

if [ ! -f "$OLD_STR_FILE" ]; then
  echo "❌ old_str_file 不存在: $OLD_STR_FILE" >&2
  exit 2
fi
if [ ! -f "$NEW_STR_FILE" ]; then
  echo "❌ new_str_file 不存在: $NEW_STR_FILE" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq 必装: brew install jq" >&2
  exit 2
fi

# 1. 写 JSON payload (避免 shell quoting hell)
PAYLOAD_FILE="/tmp/patch-payload-$$.json"
jq -n \
  --arg old "$(cat "$OLD_STR_FILE")" \
  --arg new "$(cat "$NEW_STR_FILE")" \
  '{allow_async: true, type: "update_content", update_content: {content_updates: [{old_str: $old, new_str: $new}]}}' \
  > "$PAYLOAD_FILE"
trap "rm -f $PAYLOAD_FILE" EXIT

# 2. PATCH (用 short id 无前导 slash, ntn 自动 normalize)
RESP=$(ntn api --method PATCH "v1/pages/${PAGE_ID}/markdown" \
  --notion-version 2026-03-11 --data "$(cat "$PAYLOAD_FILE")" 2>&1)

# 3. capture task_id (allow_async=true 立即返 task)
TASK_ID=$(echo "$RESP" | jq -r '.id // empty' 2>/dev/null || echo "")
if [ -z "$TASK_ID" ]; then
  echo "❌ PATCH 失败, 响应:" >&2
  echo "$RESP" >&2
  exit 1
fi
echo "task_id: $TASK_ID"

# 4. wait 异步任务 (Notion async task 跑完时间不定, poll async_tasks endpoint
#    实测 ntn api path 解析 bug 跟 /v1/blocks/... 同源, 改用 sleep + GET 验证)
sleep 8

# 5. GET 验证 (new_str 在 md 里 + old_str 不在) - 加 60s + 3 retry (per ntn-cli.md §1.1)
NEW_STR_CONTENT="$(cat "$NEW_STR_FILE")"
OLD_STR_CONTENT="$(cat "$OLD_STR_FILE")"
VERIFY=""
for attempt in {1..3}; do
  VERIFY=$(ntn api "v1/pages/${PAGE_ID}/markdown" --notion-version 2026-03-11 2>&1) || true
  if echo "$VERIFY" | grep -qF "$NEW_STR_CONTENT"; then
    break
  fi
  echo "verify attempt $attempt: new_str not in page, retry..."
  sleep 3
done

if echo "$VERIFY" | grep -qF "$NEW_STR_CONTENT"; then
  if echo "$VERIFY" | grep -qF "$OLD_STR_CONTENT"; then
    echo "⚠️ new_str + old_str 都在 (可能 Notion 渲染了不同 form, 手动 verify)"
    exit 1
  fi
  echo "✅ patch verified (new_str in md, old_str not in md)"
  exit 0
else
  echo "❌ patch failed: new_str not in page after 3 retries"
  echo "  task_id: $TASK_ID (status_url 可查 https://api.notion.com/v1/async_tasks/$TASK_ID)" >&2
  exit 1
fi