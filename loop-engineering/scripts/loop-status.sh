#!/bin/bash
# loop-status.sh — 看当前 loop 跑到哪 / 下一步是什么
# 用途: loop protocol 跑到一半接续, 看进度
# 用法: bash loop-status.sh [project_root]
#      默认 project_root = 当前目录

set -e
PROJECT_ROOT="${1:-$PWD}"
LOOP_STATE="$PROJECT_ROOT/00-meta/loop-state.json"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 找 loop-protocol
PROTOCOL=$(find "$PROJECT_ROOT" -name "loop-protocol*.md" -type f 2>/dev/null | head -1)
if [ -z "$PROTOCOL" ]; then
    echo -e "${RED}❌ 未找到 loop-protocol*.md${NC}"
    echo "请确认: cd <your-project> && bash loop-status.sh"
    exit 1
fi
PROTOCOL_REL="${PROTOCOL#$PROJECT_ROOT/}"

# 2. 找 agents-output
AGENT_OUT=$(find "$PROJECT_ROOT" -path "*/04-artifacts/agents-output/*" -name "*.jsonl" -o -path "*/04-artifacts/agents-output/*" -name "filtered-*.md" 2>/dev/null | sort)
NOTE_DIR=$(find "$PROJECT_ROOT" -path "*/03-research/01-reading-notes/*" -name "*.md" -not -name "_template*" -not -name "v*-paper-note*" 2>/dev/null | head -200)

# 3. 统计
SEARCH_COUNT=$(echo "$AGENT_OUT" | grep -c "search-C.*\.jsonl" || echo 0)
FILTER_COUNT=$(echo "$AGENT_OUT" | grep -c "filtered-" || echo 0)
NOTE_COUNT=$(echo "$NOTE_DIR" | grep -vc "^$" || echo 0)
REPORT_COUNT=$(echo "$AGENT_OUT" | grep -c "report-\|full-canvas" || echo 0)

echo "═══════════════════════════════════════════════════════════"
echo "🌀 Loop Engineering — Status"
echo "═══════════════════════════════════════════════════════════"
echo "Project: $PROJECT_ROOT"
echo "Protocol: $PROTOCOL_REL"
echo ""
echo -e "  ${GREEN}Stage 1 SEARCH${NC}:  $SEARCH_COUNT / 7 子方向 jsonl"
echo -e "  ${GREEN}Stage 2 FILTER${NC}:  $FILTER_COUNT / 1 通过清单"
echo -e "  ${GREEN}Stage 3 NOTE${NC}:    $NOTE_COUNT 篇"
echo -e "  ${GREEN}Stage 4 REPORT${NC}:  $REPORT_COUNT 篇"
echo ""
echo "───────────────────────────────────────────────────────────"
echo "📁 最新产物"
echo "───────────────────────────────────────────────────────────"
ls -lat "$PROJECT_ROOT/04-artifacts/agents-output/" 2>/dev/null | head -10 || echo "  (空)"
echo ""
echo "───────────────────────────────────────────────────────────"
echo "🎯 下一步"
echo "───────────────────────────────────────────────────────────"
if [ "$SEARCH_COUNT" -lt 7 ]; then
    NEXT_SUB=$((SEARCH_COUNT + 1))
    echo -e "  ${YELLOW}→ 起 Stage 1 SEARCH sub-agent C$NEXT_SUB${NC}"
    echo "    prompt: 见 SKILL.md §Stage 1 + templates/loop-protocol.md §2"
elif [ "$FILTER_COUNT" -lt 1 ]; then
    echo -e "  ${YELLOW}→ 起 Stage 2 FILTER-AGENT (7 jsonl → 通过清单)${NC}"
    echo "    prompt: 见 SKILL.md §Stage 2 + templates/filtered-papers.md"
elif [ "$NOTE_COUNT" -lt 30 ]; then
    echo -e "  ${YELLOW}→ 起 Stage 3 NOTE-AGENT (通过清单 → paper notes)${NC}"
    echo "    prompt: 见 SKILL.md §Stage 3 + templates/paper-note-v2.1.md"
elif [ "$REPORT_COUNT" -lt 1 ]; then
    echo -e "  ${YELLOW}→ 起 Stage 4 REPORT-AGENT (全谱索引 + html)${NC}"
    echo "    prompt: 见 SKILL.md §Stage 4 + templates/report-index.md"
else
    echo -e "  ${GREEN}✅ 4 stage 全跑完, 跑 §H.1 5 字段验收: bash verify-5fields.sh${NC}"
fi
echo ""
echo "───────────────────────────────────────────────────────────"
echo "🔗 5 命令快速看仓状态"
echo "───────────────────────────────────────────────────────────"
git -C "$PROJECT_ROOT" status --short 2>/dev/null || echo "  (非 git 仓)"
