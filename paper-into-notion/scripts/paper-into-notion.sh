#!/usr/bin/env bash
# paper-into-notion.sh — 主入口 (per ADR-0057 v1.8)
# 用法:
#   bash paper-into-notion.sh <URL>                                                        # 修法 1 (默认, 安全)
#   bash paper-into-notion.sh --force-fill <URL>                                          # 覆盖模式 (慎用)
#   bash paper-into-notion.sh --force-fill <URL> --knowledge "tag1 tag2"                  # user override 知识点
#   bash paper-into-notion.sh --force-fill <URL> --highlight "中文 takeaway"              # user override 亮点 (claudecode 自己翻)
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

# === --dry-run 子命令 (v2.6 验证模式, 不写 Notion) ===
DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
  shift
fi

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "用法:" >&2
  echo "  bash paper-into-notion.sh <URL>                                            # 修法 1 (默认, 安全)" >&2
  echo "  bash paper-into-notion.sh --force-fill <URL>                              # 覆盖模式 (慎用)" >&2
  echo "  bash paper-into-notion.sh --force-fill <URL> --knowledge \"tag1 tag2\"      # user override 知识点" >&2
  echo "  bash paper-into-notion.sh --dry-run <URL>                                 # 验证模式, 不写 Notion" >&2
  echo "  bash paper-into-notion.sh --verify                                       # 环境检查" >&2
  exit 1
fi
shift  # shift URL

# === --knowledge "tag1 tag2" 参数 (v1.7, user override 知识点, 在 URL 之后位置) ===
USER_KNOWLEDGE=""
if [ "${1:-}" = "--knowledge" ]; then
  shift
  # 合并所有非 --flag 起始的 arg, 遇 --xxx 停 (跟 --highlight 互不干扰)
  USER_KNOWLEDGE=""
  while [ $# -gt 0 ] && [ "${1#--}" = "${1}" ]; do
    if [ -n "$USER_KNOWLEDGE" ]; then USER_KNOWLEDGE+=" "; fi
    USER_KNOWLEDGE+="$1"
    shift
  done
fi

# === --highlight "中文 takeaway" 参数 (v1.8, claudecode 自己翻) ===
USER_HIGHLIGHT=""
if [ "${1:-}" = "--highlight" ]; then
  shift
  USER_HIGHLIGHT=""
  while [ $# -gt 0 ] && [ "${1#--}" = "${1}" ]; do
    if [ -n "$USER_HIGHLIGHT" ]; then USER_HIGHLIGHT+=" "; fi
    USER_HIGHLIGHT+="$1"
    shift
  done
fi

echo "═══ paper-into-notion run ═══"
echo "URL: $URL"
if [ "$FORCE_FILL" = "true" ]; then
  echo "⚠️ 模式: --force-fill (覆盖已有 page 全 7 字段, 慎用)"
fi
if [ -n "$USER_KNOWLEDGE" ]; then
  echo "👤 user override 知识点: $USER_KNOWLEDGE"
fi
if [ -n "$USER_HIGHLIGHT" ]; then
  echo "👤 user override 亮点: $USER_HIGHLIGHT"
fi

# === 1. 模态判定 ===
MODAL=$(bash "$SCRIPT_DIR/modal-detect.sh" "$URL")
echo "[1/4] 模态: $MODAL"

# === 2. 抓 title + abstract + authors (仅 arXiv) ===
TITLE=""
ABSTRACT=""
AUTHORS_LINE=""
if [ "$MODAL" = "arXiv" ]; then
  ARXIV_ID=$(echo "$URL" | grep -oE '[0-9]{4}\.[0-9]{4,5}' | head -1)
  if [ -n "$ARXIV_ID" ]; then
    echo "[2/4] 抓 arXiv: $ARXIV_ID"
    ARXIV_JSON=$(bash "$SCRIPT_DIR/arxiv-fetch.sh" "$ARXIV_ID")
    TITLE=$(echo "$ARXIV_JSON" | jq -r '.title // empty')
    ABSTRACT=$(echo "$ARXIV_JSON" | jq -r '.abstract // empty')
    AUTHORS_LINE=$(echo "$ARXIV_JSON" | jq -r '.authors // [] | join("; ") // empty')
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

# === 2.5 LLM judge 4 字段 (per ADR-0057 v3.1, schema 8 字段: 页面/状态/平台/link/亮点/知识点/展现形式/机构) ===
KNOWLEDGE_TAGS="[]"
EDUCATION_TAGS="[]"
HIGHLIGHTS=""
INSTITUTIONS="[]"
if [ -n "$ABSTRACT" ]; then
  echo "[2.5/4] LLM judge 4 字段..."
  EDUCATION_TAGS=$(bash "$SCRIPT_DIR/education-type-judge.sh" "$ABSTRACT")
  echo "    ✅ 教育类型: $EDUCATION_TAGS"
  # 亮点: user override (claudecode 翻译) > LLM judge (v1.8)
  if [ -n "$USER_HIGHLIGHT" ]; then
    HIGHLIGHTS="$USER_HIGHLIGHT"
    echo "    ✅ 亮点 (user override / claudecode 翻译): $HIGHLIGHTS"
  else
    HIGHLIGHTS=$(bash "$SCRIPT_DIR/highlights-judge.sh" "$ABSTRACT")
    echo "    ✅ 亮点: $HIGHLIGHTS"
  fi

  # 知识点: user override > LLM judge (v1.7)
  if [ -n "$USER_KNOWLEDGE" ]; then
    # 把 user 关键词空格分隔 → JSON 数组
    KNOWLEDGE_TAGS=$(echo "$USER_KNOWLEDGE" | python3 -c "
import json, sys
tags = sys.stdin.read().strip().split()
print(json.dumps(tags, ensure_ascii=False))
")
    echo "    ✅ 知识点 (user override): $KNOWLEDGE_TAGS"
  else
    KNOWLEDGE_TAGS=$(bash "$SCRIPT_DIR/knowledge-tag-judge.sh" "$ABSTRACT")
    echo "    ✅ 知识点: $KNOWLEDGE_TAGS"
  fi

  # 机构: v3.1 新增 (per user 反馈"很多字段没填"), 走 email grep + LLM fallback
  INSTITUTIONS=$(bash "$SCRIPT_DIR/institutions-judge.sh" "$ABSTRACT" "$AUTHORS_LINE")
  echo "    ✅ 机构: $INSTITUTIONS"
fi

# === 3. 字段级 merge ===
echo "[3/4] 字段级 merge..."
if [ "$FORCE_FILL" = "true" ]; then
  # 覆盖模式: 先 GET 找 page_id, 调 field-merge.sh --force
  if [ "$DRY_RUN" = "true" ]; then
    echo "[DRY-RUN] ⚠️ 不会真写 Notion, 仅模拟完整流程"
    echo "[DRY-RUN]   会调: ntn api POST /v1/data_sources/\$DS/query (查 page)"
    echo "[DRY-RUN]   会调: field-merge.sh --force <page_id> (PATCH)"
    RECORD='{"id":"DRY-RUN-PAGE-ID","url":"https://app.notion.com/p/DRY-RUN"}'
  else
    QUERY_BODY="{\"filter\":{\"property\":\"${NOTION_TITLE_PROPERTY:-页面}\",\"title\":{\"equals\":$(echo "$TITLE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}},\"page_size\":1}"
    QUERY_RESULT=$(ntn api --method POST "/v1/data_sources/${NOTION_DATA_SOURCE_ID}/query" -d "$QUERY_BODY" 2>&1)
    EXISTING_PAGE_ID=$(echo "$QUERY_RESULT" | jq -r '.results[0].id // empty')
    if [ -z "$EXISTING_PAGE_ID" ]; then
      echo "❌ --force-fill 模式: 没找到 page '$TITLE', 改用默认模式" >&2
      RECORD=$(bash "$SCRIPT_DIR/field-merge.sh" "$TITLE" "$MODAL" "$URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS" "$INSTITUTIONS")
    else
      RECORD=$(bash "$SCRIPT_DIR/field-merge.sh" --force "$EXISTING_PAGE_ID" "$TITLE" "$MODAL" "$URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS" "$INSTITUTIONS")
    fi
  fi
else
  # 修法 1 (默认, 安全)
  if [ "$DRY_RUN" = "true" ]; then
    echo "[DRY-RUN] ⚠️ 不会真写 Notion, 仅模拟完整流程"
    echo "[DRY-RUN]   会调: field-merge.sh (POST 新 page 或 PATCH 已有)"
    echo "[DRY-RUN]   title: $TITLE"
    echo "[DRY-RUN]   modal: $MODAL"
    echo "[DRY-RUN]   source_url: $URL"
    RECORD='{"id":"DRY-RUN-PAGE-ID","url":"https://app.notion.com/p/DRY-RUN"}'
  else
    RECORD=$(bash "$SCRIPT_DIR/field-merge.sh" "$TITLE" "$MODAL" "$URL" "$KNOWLEDGE_TAGS" "$EDUCATION_TAGS" "$HIGHLIGHTS" "$INSTITUTIONS")
  fi
fi

RECORD_ID=$(echo "$RECORD" | jq -r '.id // empty')
PAGE_URL=$(echo "$RECORD" | jq -r '.url // empty')

if [ -z "$RECORD_ID" ]; then
  echo "❌ field-merge.sh 没返 record_id" >&2
  exit 1
fi

# === 4. 跑后 GET 验证 ===
echo "[4/4] 跑后 GET 验证..."
if [ "$DRY_RUN" = "true" ]; then
  echo "[DRY-RUN] 跳过 verify-5-fields.sh (无真 page ID 可验)"
else
  bash "$SCRIPT_DIR/verify-5-fields.sh" "$RECORD_ID"
fi

echo "═══ result ═══"
echo "✅ record_id: $RECORD_ID"
echo "✅ page_url: $PAGE_URL"
echo "✅ 3 字段填对 (页面=$TITLE, 状态=未开始, ${MODAL_PROP:-平台}=$MODAL)"
if [ "$FORCE_FILL" = "true" ]; then
  echo "⚠️ --force-fill 模式: 7 字段全填 (含 3 LLM judge 字段 + link URL)"
else
  if [ "$KNOWLEDGE_TAGS" != "[]" ]; then echo "✅ 知识点 (新 page 才填): $KNOWLEDGE_TAGS"; fi
  if [ "$EDUCATION_TAGS" != "[]" ]; then echo "✅ 教育类型 (新 page 才填): $EDUCATION_TAGS"; fi
  if [ -n "$HIGHLIGHTS" ]; then echo "✅ 亮点 (新 page 才填, ≤200 字)"; fi
  if [ "$INSTITUTIONS" != "[]" ]; then echo "✅ 机构 (新 page 才填, v3.1): $INSTITUTIONS"; fi
fi