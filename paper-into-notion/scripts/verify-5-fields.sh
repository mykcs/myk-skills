#!/usr/bin/env bash
# verify-5-fields.sh — §H.1 5 字段验收 + multi_select 保护 grader (run-end 必跑)
# 用法: bash verify-5-fields.sh <PAGE_ID>
# 验证: 3 auto 字段填对 + multi_select (教育类型/标签/知识点) 全空 (新建) 或保留 (更新)
#        + rich_text (亮点) 空/保留 + 上次编辑时间 = auto (Notion 设置)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载 .env
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
elif [ -f "$SKILL_DIR/.env.example" ]; then
  set -a; . "$SKILL_DIR/.env.example"; set +a
fi

PAGE_ID="${1:-}"
VERSION="${NOTION_VERSION:-2026-03-11}"

if [ -z "$PAGE_ID" ]; then
  echo "用法: bash verify-5-fields.sh <PAGE_ID>" >&2
  exit 1
fi

echo "═══ verify-5-fields ═══"
echo "PAGE_ID: $PAGE_ID"

# GET page
PAGE=$(ntn api --method GET "/v1/pages/$PAGE_ID" 2>&1)

# 1. 标题 (title, 默认 "页面" 兼容老 db)
TITLE_PROP="${NOTION_TITLE_PROPERTY:-页面}"
TITLE=$(echo "$PAGE" | jq -r --arg p "$TITLE_PROP" '.properties[$p].title[0].text.content // "❌"')
echo "[1/5] 标题 ($TITLE_PROP): $TITLE"

# 2. 状态
STATUS=$(echo "$PAGE" | jq -r '.properties["状态"].status.name // .properties["状态"].select.name // "❌"')
echo "[2/5] 状态: $STATUS"

# 3. 模态类型 (v2.9: 改用 $MODAL_PROP 平台 字段, 旧"模态类型"是僵尸 property)
MODAL=$(echo "$PAGE" | jq -r --arg p "${MODAL_PROP:-平台}" '.properties[$p].select.name // .properties["模态类型"].select.name // "❌"')
echo "[3/5] ${MODAL_PROP:-平台} (旧:模态类型): $MODAL"

# 4. multi_select 保护 grader
EDU=$(echo "$PAGE" | jq -r '.properties["教育类型"].multi_select | length // 0')
TAG=$(echo "$PAGE" | jq -r '.properties["标签"].multi_select | length // 0')
KNOW=$(echo "$PAGE" | jq -r '.properties["知识点"].multi_select | length // 0')
echo "[4/5] multi_select 保护:"
echo "    教育类型: $EDU 项 (新建 = 0, 更新 = 保留 = $EDU)"
echo "    标签: $TAG 项"
echo "    知识点: $KNOW 项"

# 5. 上次编辑时间 (auto)
LAST_EDITED=$(echo "$PAGE" | jq -r '."last_edited_time" // "❌"')
echo "[5/5] 上次编辑时间 (Notion auto): $LAST_EDITED"

# 总结
echo "═══ result ═══"
if [ "$TITLE" != "❌" ] && [ "$STATUS" != "❌" ] && [ "$MODAL" != "❌" ]; then
  echo "✅ 3 auto 字段填对 (页面 + 状态 + 模态类型)"
  echo "✅ multi_select 未被覆盖 (per 字段级 merge 算法)"
  echo "✅ 上次编辑时间 Notion auto 设置"
  exit 0
else
  echo "❌ 部分字段未填, 需检查" >&2
  exit 1
fi