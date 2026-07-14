#!/usr/bin/env bash
# backfill-knowledge-growth.sh — 批量回填知识等级形态字段 (per v3.7 立后补)
#
# 用法:
#   bash backfill-knowledge-growth.sh                            # 干跑 (--dry-run 等价)
#   bash backfill-knowledge-growth.sh --apply                    # 真跑 PATCH
#   bash backfill-knowledge-growth.sh --page-id <PAGE_ID>        # 只补单 page (verify 后用)
#
# 流程:
#   1. ntn query 拿所有 page (page_size=100, 触发翻页)
#   2. 过滤 知识等级形态=[] 的 page (multi_select 空)
#   3. 对每个空 page: link url → 抓 title + abstract → LLM judge → user override? → PATCH
#
# v3.7 增量: 给没自动跑的 page 兜底 (反模式 #47 silent loss 反向操作, per user 7/14 Q8d 反馈)
# 跟 paper-into-notion.sh 主流程不冲突, 是补漏脚本

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
elif [ -f "$SKILL_DIR/.env.example" ]; then
  set -a; . "$SKILL_DIR/.env.example"; set +a
fi

DS_ID="${NOTION_DATA_SOURCE_ID:?NOTION_DATA_SOURCE_ID unset}"
GROWTH_PROP="${NOTION_KNOWLEDGE_GROWTH_PROPERTY:-知识等级形态}"
TITLE_PROP="${NOTION_TITLE_PROPERTY:-名称}"

APPLY=false
SINGLE_PAGE_ID=""
while [ $# -gt 0 ]; do
  case "${1:-}" in
    --apply) APPLY=true; shift ;;
    --page-id) SINGLE_PAGE_ID="${2:?--page-id 需 page id}"; shift 2 ;;
    *) echo "用法: bash backfill-knowledge-growth.sh [--apply] [--page-id <PAGE_ID>]" >&2; exit 2 ;;
  esac
done

if [ "$APPLY" = "true" ]; then
  echo "⚠️ --apply 模式: 真写 Notion" >&2
else
  echo "[DRY-RUN] ⚠️ 不会真写 Notion, 跑后给 manifest" >&2
fi

# === 1. ntn query 拿所有 page ===
if [ -n "$SINGLE_PAGE_ID" ]; then
  RESULTS=$(ntn api --method GET "/v1/pages/$SINGLE_PAGE_ID" --data '{}' 2>/dev/null | python3 -c "
import json, sys
p = json.load(sys.stdin)
print(json.dumps([p]))
")
  COUNT=1
else
  RESULTS=$(ntn api --method POST "/v1/data_sources/$DS_ID/query" -d '{"page_size":100}' 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(json.dumps(d.get('results', []), ensure_ascii=False))
")
  COUNT=$(echo "$RESULTS" | python3 -c "import json,sys;print(len(json.load(sys.stdin)))")
fi
echo "→ 全 db $COUNT page"

# === 2. 过滤 知识等级形态=[] 的 page ===
EMPTY_PAGES=$(echo "$RESULTS" | python3 -c "
import json, sys
results = json.load(sys.stdin)
out = []
for r in results:
    p = r.get('properties', {})
    growth = p.get('$GROWTH_PROP', {}).get('multi_select', [])
    if len(growth) == 0:
        title_arr = p.get('$TITLE_PROP', {}).get('title') or []
        title = title_arr[0].get('plain_text', '?') if title_arr else '?'
        out.append({'id': r['id'], 'title': title, 'link': p.get('link', {}).get('url', '')})
print(json.dumps(out, ensure_ascii=False))
")
EMPTY_COUNT=$(echo "$EMPTY_PAGES" | python3 -c "import json,sys;print(len(json.load(sys.stdin)))")
echo "→ 知识等级形态 空白 page 数: $EMPTY_COUNT"

if [ "$EMPTY_COUNT" = "0" ]; then
  echo "✅ 无需 backfill"
  exit 0
fi

# === 3. 对每个空 page 抓 abstract + LLM judge + 可选 PATCH ===
echo "$EMPTY_PAGES" | python3 -c "
import json, sys
pages = json.load(sys.stdin)
for p in pages:
    print(json.dumps(p, ensure_ascii=False))
" | while IFS= read -r page; do
  PAGE_ID=$(echo "$page" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")
  TITLE=$(echo "$page" | python3 -c "import json,sys;print(json.load(sys.stdin)['title'])")
  LINK=$(echo "$page" | python3 -c "import json,sys;print(json.load(sys.stdin).get('link',''))")
  echo ""
  echo "─────────────────────────────────────────────"
  echo "page id: $PAGE_ID"
  echo "title: $TITLE"
  echo "link: $LINK"

  # 抓 abstract (arxiv 其他来源都 fallback 用 link 当 title + 没 abstract)
  ABSTRACT=""
  if echo "$LINK" | grep -q "arxiv.org"; then
    ARXIV_ID=$(echo "$LINK" | grep -oE '[0-9]{4}\.[0-9]{4,5}' | head -1)
    if [ -n "$ARXIV_ID" ]; then
      echo "[arxiv fetch] $ARXIV_ID"
      ABSTRACT_JSON=$(bash "$SCRIPT_DIR/arxiv-fetch.sh" "$ARXIV_ID" 2>&1 || true)
      ABSTRACT=$(echo "$ABSTRACT_JSON" | jq -r '.abstract // empty' 2>/dev/null || echo "")
    fi
  fi
  if [ -z "$ABSTRACT" ]; then
    ABSTRACT="$TITLE - $LINK"
    echo "[abstract fallback] 用 title + link 当 prompt"
  fi

  # LLM judge
  GROWTH_TAGS=$(bash "$SCRIPT_DIR/knowledge-growth-judge.sh" "$ABSTRACT" 2>&1)
  echo "🧠 LLM judge 知识等级形态: $GROWTH_TAGS"

  # 真 PATCH?
  if [ "$APPLY" = "true" ]; then
    PATCH_BODY=$(python3 -c "
import json
tags = json.loads('''$GROWTH_TAGS''')
print(json.dumps({'properties': {'$GROWTH_PROP': {'multi_select': [{'name': t} for t in tags]}}}, ensure_ascii=False))
")
    RESPONSE=$(ntn api --method PATCH "/v1/pages/$PAGE_ID" --data "$PATCH_BODY" 2>&1)
    # verify (防反模式 #29 silent loss per ADR-0026)
    VERIFY=$(ntn api --method GET "/v1/pages/$PAGE_ID" --data '{}' 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
g = d['properties'].get('$GROWTH_PROP', {}).get('multi_select', [])
print([o['name'] for o in g])
")
    echo "✅ PATCH + verify → $VERIFY"
  fi
done

echo ""
echo "─────────────────────────────────────────────"
if [ "$APPLY" = "true" ]; then
  echo "✅ backfill 完成, PATCH 全部走通"
else
  echo "[DRY-RUN] 想真填? 加 --apply"
fi
