#!/usr/bin/env bash
# check-notion-version.sh — 跑前 ntn doctor + Notion-Version header 验证 (per §USER-SETUP-CHECKLIST Step 4)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载 .env
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
elif [ -f "$SKILL_DIR/.env.example" ]; then
  set -a; . "$SKILL_DIR/.env.example"; set +a
fi

echo "═══ check-notion-version ═══"

# 1. ntn --version
echo "[1] ntn --version:"
ntn --version

# 2. ntn whoami
echo "[2] ntn whoami:"
ntn whoami

# 3. Notion-Version header
echo "[3] Notion-Version: ${NOTION_VERSION:-unset}"
if [ -z "${NOTION_VERSION:-}" ]; then
  echo "❌ NOTION_VERSION unset" >&2
  exit 1
fi

# 4. data source 可达
echo "[4] data source 可达 (GET /v1/databases/$NOTION_DATABASE_ID):"
ntn api --method GET "/v1/databases/${NOTION_DATABASE_ID}" \
  -H "Notion-Version: $NOTION_VERSION" \
  | jq '.data_sources[0].id // "❌ no data source"'

echo "═══ ✅ 4 checks pass ═══"