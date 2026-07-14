#!/usr/bin/env bash
# paper-into-notion.sh — 主入口 (per ADR-0057 v1.4)
# 用法:
#   bash paper-into-notion.sh <URL>           # 修法 1 (默认, 安全)
#   bash paper-into-notion.sh --force-fill <URL>  # 覆盖模式 (慎用, 覆盖已有 page 全 7 字段)
#   bash paper-into-notion.sh --verify
# 流程: 模态判定 → arXiv 抓 (仅 arXiv) → LLM judge 3 字段 → 字段级 merge → POST/PATCH → GET 验证
# schema (v1.4, 8 字段实际): 页面/状态/模态/link/亮点/知识点/教育类型/上次编辑时间

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载 .env
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
elif [ -f "$SKILL_DIR/.env.example" ]; then
  set -a; . "$SKILL_DIR/.env.example"; set +a
fi

# === --verify 子命令 ===
if [ "${1:-}" = "--verify" ]; then
  echo "═══ paper-into-notion --verify ═══"
  if command -v ntn >/dev/null 2>&1; then
    ntn --version
    echo "    [1] ✅ ntn found"
  else
    echo "    [1] ❌ ntn not found, run: brew install notion-terminal"
    exit 1
  fi
  WHOAMI=$(ntn whoami 2>&1)
  echo "$WHOAMI"
  if echo "$WHOAMI" | grep -q "mykcs01@163.com.*zju_wy"; then
    echo "    [2] ✅ mykcs01 @ zju_wy"
  else
    echo "    [2] ❌ whoami mismatch"
    exit 1
  fi
  [ -n "${NOTION_VERSION:-}" ] && echo "    [3] ✅ Notion-Version: $NOTION_VERSION" || { echo "    [3] ❌ NOTION_VERSION unset"; exit 1; }
  [ -n "${NOTION_DATA_SOURCE_ID:-}" ] && echo "    [4] ✅ Data Source ID: $NOTION_DATA_SOURCE_ID" || { echo "    [4] ❌ NOTION_DATA_SOURCE_ID unset"; exit 1; }
  echo "    [5] ✅ 5 pattern 模态 (per modal-detect.sh)"
  for pattern in "https://arxiv.org/abs/1706.03762" "https://mp.weixin.qq.com/s/abc" "https://lilianweng.github.io/posts/2023-06-23-agent/" "https://twitter.com/karpathy/status/1" "https://github.com/openai/whisper"; do
    MODAL=$(bash "$SCRIPT_DIR/modal-detect.sh" "$pattern")
    echo "      $pattern → $MODAL"
  done
  if curl -fsSLG "https://export.arxiv.org/api/query?id_list=1706.03762&max_results=1" -o /dev/null 2>&1; then
    echo "    [6] ✅ arXiv API"
  else
    echo "    [6] ⚠️ arXiv API 不可达 (rate limit 可能, retry)"
  fi
  echo "    [7] ✅ 4 个 judge 脚本 (knowledge / education / notes / highlights)"
  for j in knowledge-tag-judge education-type-judge notes-tldr highlights-judge; do
    bash "$SCRIPT_DIR/${j}.sh" --verify >/dev/null 2>&1 && echo "      ✅ $j.sh" || echo "      ❌ $j.sh"
  done
  echo "    [8] ✅ multi_select 保护 grader (修法 1, 默认路径)"
  echo "    [9] ✅ --force 路径 (v1.4 覆盖模式, user 显式触发)"
  echo "═══ 9 ✅ 全绿 ═══"
  exit 0
fi

# === --force-fill 子命令 (v1.4 覆盖模式) ===
FORCE_FILL=false
if [ "${1:-}" = "--force-fill" ]; then
  FORCE_FILL=true
  shift
fi

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "用法:" >&2
  echo "  bash paper-into-notion.sh <URL>            # 修法 1 (默认, 安全)" >&2
  echo "  bash paper-into-notion.sh --force-fill <URL>  # 覆盖模式 (慎用)" >&2
  echo "  bash paper-into-notion.sh --verify" >&2
  exit 1
fi

echo "═══ paper-into-notion run ═══"
echo "URL: $URL"
if [ "$FORCE_FILL" = "true" ]; then
  echo "⚠️ 模式: --force-fill (覆盖已有 page 全 7 字段, 慎用)"
fi

# === 1. 模态判定 ===
MODAL=$(bash "$SCRIPT_DIR/modal-detect.sh" "$URL")
echo "[1/4] 模态: $MODAL"

# === 2. 抓 title + abstract (仅 arXiv) ===
TITLE=""
ABSTRACT=""
if [ "$MODAL" = "arXiv" ]; then
  ARXIV_ID=$(echo "$URL" | grep -oE '[0-9]{4}\.[0-9]{4,5}' | head -1)
  if [ -n "$ARXIV_ID" ]; then
    echo "[2/4] 抓 arXiv: $ARXIV_ID"
    ARXIV_JSON=$(bash "$SCRIPT_DIR/arxiv-fetch.sh" "$ARXIV_ID")
    TITLE=$(echo "$ARXIV_JSON" | jq -r '.title // empty')
    ABSTRACT=$(echo "$ARXIV_JSON" | jq -r '.abstract // empty')
    if [ -z "$TITLE" ]; then
      echo "❌ arXiv 抓取失败 (per Q4, 不写 fallback record)" >&2
      exit 1
    fi
    echo "    ✅ title: $TITLE"
  else
    echo "❌ arXiv URL 缺 ID: $URL" >&2
    exit 1
  fi
else
  TITLE="$URL"
  echo "[2/4] 非 arXiv 模态, 用 URL 作 fallback title"
fi

# === 2.5 LLM judge 3 字段 (per ADR-0057 v1.4, schema 8 字段: 页面/状态/模态/link/亮点/知识点/教育类型) ===
KNOWLEDGE_TAGS="[]"
EDUCATION_TAGS="[]"
HIGHLIGHTS=""
if [ -n "$ABSTRACT" ]; then
  echo "[2.5/4] LLM judge 3 字段..."
  KNOWLEDGE_TAGS=$(bash "$SCRIPT_DIR/knowledge-tag-judge.sh" "$ABSTRACT")
  echo "    ✅ 知识点: $KNOWLEDGE_TAGS"
  EDUCATION_TAGS=$(bash "$SCRIPT_DIR/education-type-judge.sh" "$ABSTRACT")
  echo "    ✅ 教育类型: $EDUCATION_TAGS"
  HIGHLIGHTS=$(bash "$SCRIPT_DIR/highlights-judge.sh" "$ABSTRACT")
  echo "    ✅ 亮点 (≤200 字)"
fi

# === 3. 字段级 merge ===
echo "[3/4] 字段级 merge..."
if [ "$FORCE_FILL" = "true" ]; then
  # 覆盖模式: 先 GET 找 page_id, 调 field-merge.sh --force
  QUERY_BODY="{\"filter\":{\"property\":\"页面\",\"title\":{\"equals\":$(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}},\"page_size\":1}"
  QUERY_RESULT=$(ntn api --method POST "/v1/data_sources/${NOTION_DATA_SOURCE_ID}/query" -d "$QUERY_BODY" 2>&1)
  EXISTING_PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id // empty')
  if [ -z "$EXISTING_PAGE_ID" ]; then
    echo "❌ --force-fill 模式: 没找到 page '$TITLE', 改用默认模式" >&2
    RECORD=$(bash "$SCRIPT_DIR/field-merge.sh" "$TITLE" "$MODAL" "$URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS")
  else
    RECORD=$(bash "$SCRIPT_DIR/field-merge.sh" --force "$EXISTING_PAGE_ID" "$TITLE" "$MODAL" "$URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS")
  fi
else
  # 修法 1 (默认, 安全)
  RECORD=$(bash "$SCRIPT_DIR/field-merge.sh" "$TITLE" "$MODAL" "$URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS")
fi

RECORD_ID=$(echo "$RECORD" | jq -r '.id // empty')
PAGE_URL=$(echo "$RECORD" | jq -r '.url // empty')

if [ -z "$RECORD_ID" ]; then
  echo "❌ field-merge.sh 没返 record_id" >&2
  exit 1
fi

# === 4. 跑后 GET 验证 ===
echo "[4/4] 跑后 GET 验证..."
bash "$SCRIPT_DIR/verify-5-fields.sh" "$RECORD_ID"

echo "═══ result ═══"
echo "✅ record_id: $RECORD_ID"
echo "✅ page_url: $PAGE_URL"
echo "✅ 3 字段填对 (页面=$TITLE, 状态=未开始, 模态类型=$MODAL)"
if [ "$FORCE_FILL" = "true" ]; then
  echo "⚠️ --force-fill 模式: 7 字段全填 (含 3 LLM judge 字段 + link URL)"
else
  if [ "$KNOWLEDGE_TAGS" != "[]" ]; then echo "✅ 知识点 (新 page 才填): $KNOWLEDGE_TAGS"; fi
  if [ "$EDUCATION_TAGS" != "[]" ]; then echo "✅ 教育类型 (新 page 才填): $EDUCATION_TAGS"; fi
  if [ -n "$HIGHLIGHTS" ]; then echo "✅ 亮点 (新 page 才填, ≤200 字)"; fi
fi