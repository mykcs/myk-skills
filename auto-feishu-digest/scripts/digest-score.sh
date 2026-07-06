#!/bin/bash
# digest-score.sh — 5 jsonl dedup + 7 维 LLM judge → scored jsonl
# 7 维 (per loop-engineering paper-note-v2.1 §3):
#   venue / author / code / dataset / number / citation / match
# 用法:
#   bash digest-score.sh                              # 默认吃 ~/.cache/digest/*.jsonl
#   bash digest-score.sh --in=*.jsonl --dry-run       # 不调用 LLM, mock score
#   bash digest-score.sh --top-n=5                    # 限制输出数量
# 输出: ~/.cache/digest/scored-<YYYY-MM-DD>.jsonl

set -e
# v0.1.8: auto-load 7 env from .env (per user feedback "不能我每次跑一遍 skill 都重新配一次")
set -a
. "$(dirname "$0")/../.env" 2>/dev/null || . "$(dirname "$0")/.env" 2>/dev/null || true
set +a

INPUT_GLOB="${HOME}/.cache/digest/*-*.jsonl"
OUTPUT=""
TOP_N="0"
DRY_RUN="false"
CACHE="${HOME}/.cache/digest"
TODAY=$(date +%Y-%m-%d)

while [[ $# -gt 0 ]]; do
    case $1 in
        --in=*) INPUT_GLOB="${1#*=}" ;;
        --out=*) OUTPUT="${1#*=}" ;;
        --top-n=*) TOP_N="${1#*=}" ;;
        --dry-run) DRY_RUN="true" ;;
        --cache=*) CACHE="${1#*=}" ;;
        *) echo "用法: $0 [--in=GLOB] [--out=PATH] [--top-n=N] [--dry-run]"; exit 1 ;;
    esac
    shift
done

OUTPUT="${OUTPUT:-$CACHE/scored-${TODAY}.jsonl}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "═══════════════════════════════════════════════════════════"
echo "🎯 Digest Score — 7 维 LLM judge + dedup"
echo "═══════════════════════════════════════════════════════════"
echo "Input:   $INPUT_GLOB"
echo "Output:  $OUTPUT"
echo "Top N:   $TOP_N  | dry_run: $DRY_RUN"
echo ""

# 1. 收集所有候选
PAPERS_TMP="$CACHE/.tmp-papers-$$.jsonl"
trap "rm -f $PAPERS_TMP" EXIT

> "$PAPERS_TMP"
INPUT_FILES=$(ls $INPUT_GLOB 2>/dev/null || true)
if [ -z "$INPUT_FILES" ]; then
    echo -e "${YELLOW}⚠️ 无 input jsonl, 跑过 digest-collect.sh 了吗?${NC}"
    exit 1
fi

for f in $INPUT_FILES; do
    cat "$f" >> "$PAPERS_TMP"
done
RAW_COUNT=$(wc -l < "$PAPERS_TMP")
echo "✓ Raw 输入: $RAW_COUNT 行"

# 2. dedup (按 arxiv_id or url or title hash)
DEDUP_TMP="$CACHE/.tmp-dedup-$$.jsonl"
sort -u "$PAPERS_TMP" > "$DEDUP_TMP"  # MVP: 简单 unique by line, 实际应该 jq dedup by key
DEDUP_COUNT=$(wc -l < "$DEDUP_TMP")
echo "✓ Dedup 后: $DEDUP_COUNT 行 (去重 $((RAW_COUNT - DEDUP_COUNT)) 条)"

# 3. 7 维 LLM judge (MVP: mock score, 真跑要接 opus / claude API)
SCORED_TMP="$CACHE/.tmp-scored-$$.jsonl"
> "$SCORED_TMP"

if [ "$DRY_RUN" = "true" ]; then
    # mock: 所有 paper 同分 (演示流程)
    # v0.1.2 修: if 原 7 维有值, 保留; else 补 3
    jq -c '
        if .venue_score then .
        else . + {venue_score: 3, author_score: 3, code_score: 3, dataset_score: 3, number_score: 3, citation_score: 3, match_score: 3}
        end |
        . + {composite_score: (((.venue_score // 3) + (.author_score // 3) + (.code_score // 3) + (.dataset_score // 3) + (.number_score // 3) + (.citation_score // 3) + (.match_score // 3)) / 7.0 | . * 10 | round / 10), caution_flag: (if (((.venue_score // 3) + (.author_score // 3) + (.code_score // 3) + (.dataset_score // 3) + (.number_score // 3) + (.citation_score // 3) + (.match_score // 3)) / 7.0) <= 3 then "⚠️ 慎引" else "✅ 可引" end), scored_at: (now | todate)}
    ' "$DEDUP_TMP" > "$SCORED_TMP" 2>/dev/null || cat "$DEDUP_TMP" > "$SCORED_TMP"
    echo "  (dry-run) LLM judge 已 mock 全部 3 分 (v0.1.2 if-then 保留原 7 维)"
else
    # 真 LLM judge (claudecode 执行时补全)
    # v0.1.2 修: if 原 7 维有值, 保留; else 补 3 (跟 dry-run 同 logic)
    jq -c '
        if .venue_score then .
        else . + {venue_score: 3, author_score: 3, code_score: 3, dataset_score: 3, number_score: 3, citation_score: 3, match_score: 3}
        end |
        . + {composite_score: (((.venue_score // 3) + (.author_score // 3) + (.code_score // 3) + (.dataset_score // 3) + (.number_score // 3) + (.citation_score // 3) + (.match_score // 3)) / 7.0 | . * 10 | round / 10), caution_flag: (if (((.venue_score // 3) + (.author_score // 3) + (.code_score // 3) + (.dataset_score // 3) + (.number_score // 3) + (.citation_score // 3) + (.match_score // 3)) / 7.0) <= 3 then "⚠️ 慎引" else "✅ 可引" end), scored_at: (now | todate)}
    ' "$DEDUP_TMP" > "$SCORED_TMP" 2>/dev/null || cp "$DEDUP_TMP" "$SCORED_TMP"
    echo "  ⚠️ 真 LLM judge 需 claudecode 跑 (MVP 占位, v0.1.2 if-then 保留原 7 维)"
fi

# 4. 按 composite_score 降序
if [ "$TOP_N" -gt 0 ]; then
    jq -s 'sort_by(-.composite_score) | .[0:'"$TOP_N"']' "$SCORED_TMP" > "$OUTPUT"
else
    jq -s 'sort_by(-.composite_score) | .[]' "$SCORED_TMP" > "$OUTPUT"
fi

FINAL_COUNT=$(wc -l < "$OUTPUT")
echo ""
echo -e "${GREEN}✅ scored 输出: $OUTPUT ($FINAL_COUNT 行)${NC}"
echo ""
echo "📊 评分分布:"
jq -r '.composite_score' "$OUTPUT" 2>/dev/null | sort -n | uniq -c | head -10
echo ""
echo "下一步: bash digest-publish.sh --mode=daily (top 5) 或 --mode=weekly (top 20)"
