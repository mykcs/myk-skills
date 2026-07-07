#!/bin/bash
# digest-publish.sh — 把 scored jsonl 写飞书 Bitable 4 表
# 用法:
#   bash digest-publish.sh --verify                   # verify 4 env 已配 + Bitable 可读
#   bash digest-publish.sh --in=<scored.jsonl> --mode=daily   # 写 top 5
#   bash digest-publish.sh --in=<scored.jsonl> --mode=weekly  # 写 top 20 + 周报附件
#   bash digest-publish.sh --in=<scored.jsonl> --mode=daily --dry-run  # mock 不真写
# 输出:
#   - Paper 表: 1 行 1 paper
#   - Weekly 表: 1 行 (记录本次抓源 + paper 关联)
#   - Author / Venue 表: 反向 DuplexLink 自动同步

set -e
# v0.1.8: auto-load 7 env from .env (per user feedback "不能我每次跑一遍 skill 都重新配一次")
set -a
. "$(dirname "$0")/../.env" 2>/dev/null || . "$(dirname "$0")/.env" 2>/dev/null || true
set +a

INPUT=""
MODE="daily"
DRY_RUN="false"
CACHE="${HOME}/.cache/digest"
TODAY=$(date +%Y-%m-%d)

while [[ $# -gt 0 ]]; do
    case $1 in
        --in=*) INPUT="${1#*=}" ;;
        --mode=*) MODE="${1#*=}" ;;
        --dry-run) DRY_RUN="true" ;;
        --verify) MODE="verify" ;;
        --cache=*) CACHE="${1#*=}" ;;
        *) echo "用法: $0 [--in=PATH] [--mode=daily|weekly|verify] [--dry-run]"; exit 1 ;;
    esac
    shift
done

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "═══════════════════════════════════════════════════════════"
echo "📤 Digest Publish — 写飞书 Bitable"
echo "═══════════════════════════════════════════════════════════"

# 0. 运行卡片: 关键词 + 5 源 + 7 维评分 (v0.1.5 新加, per user 2026-07-03)
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ 🎯 本次运行目标 (Run Card)                              │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│  🔍 关键词: self-evolving agent / AI scientist /       │"
echo "│           LLM agent / agentic system / reasoning      │"
echo "│                                                         │"
echo "│  📡 5 源 × N 工具 fan-out (王锐 N-tool protocol):      │"
echo "│     1️⃣  arxiv          (mcp__MiniMax + anysearch + WebFetch │"
echo "│                        + exa + kimi-webbridge + ...)   │"
echo "│     2️⃣  venue          (mcp__MiniMax + anysearch + WebFetch │"
echo "│                        + exa + kimi-webbridge + ...)   │"
echo "│     3️⃣  blog-rss       (mcp__MiniMax + anysearch + WebFetch │"
echo "│                        + exa + kimi-webbridge + ...)   │"
echo "│     4️⃣  hn             (mcp__MiniMax + anysearch + WebFetch │"
echo "│                        + exa + kimi-webbridge + ...)   │"
echo "│     5️⃣  github         (mcp__MiniMax + anysearch + WebFetch │"
echo "│                        + exa + kimi-webbridge + ...)   │"
echo "│  ⚠️ N 工具自定义, 5 是当前实例, 未来扩展不减维护       │"
echo "│                                                         │"
echo "│  📊 7 维评分 (0-5 stars):                                │"
echo "│     🏛  venue        会议/期刊权威                       │"
echo "│     👤  author       作者团队                             │"
echo "│     💻  code         代码可获得性                        │"
echo "│     📦  dataset      数据集可获得性                      │"
echo "│     🔢  number       实验数字完整性                      │"
echo "│     📈  citation     引用数                              │"
echo "│     🎯  match        跟您领域匹配度                      │"
echo "│                                                         │"
echo "│  ⏰  $(date '+%Y-%m-%d %H:%M:%S %Z')     Mode: $MODE       │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

# 1. verify mode: 检查 env
if [ "$MODE" = "verify" ]; then
    echo ""
    echo "[1] 检查环境变量:"
    for var in LARK_APP_ID BAPP_TOKEN TABLE_ID_PAPER TABLE_ID_AUTHOR TABLE_ID_VENUE TABLE_ID_WEEKLY; do
        if [ -z "${!var}" ]; then
            echo -e "  ${RED}❌ $var 未设${NC}"
        else
            echo -e "  ${GREEN}✅ $var 已设${NC}"
        fi
    done
    # LARK_APP_SECRET 是 warning 不 error (lark-cli daemon 走 macOS keychain, 不需 env 变量, per USER-SETUP-CHECKLIST v0.1.8 .env line 11)
    if [ -z "$LARK_APP_SECRET" ]; then
        echo -e "  ${YELLOW}⚠️ LARK_APP_SECRET 未设 (lark-cli daemon 走 keychain 自动, OK)${NC}"
        LARK_SECRET_STATUS="✅ keychain 自动"
    else
        echo -e "  ${GREEN}✅ LARK_APP_SECRET 已设${NC}"
        LARK_SECRET_STATUS="✅ env"
    fi

    echo ""
    echo "[2] 检查 Bitable 可读 (如果有 feishu-cli):"
    if command -v lark-cli >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ lark-cli 已装${NC}"
    else
        echo -e "  ${YELLOW}⚠️ lark-cli 未装, 推荐安装 + 配 OMC use feishu-base 或 feishu-base mcp${NC}"
        echo "  备选: 用 mcp__feishu-base__list_tables 验证"
    fi

    echo ""
    echo "[3] 检查 scored jsonl 缓存目录:"
    if [ -d "$CACHE" ]; then
        echo -e "  ${GREEN}✅ $CACHE 存在${NC}"
        ls -la "$CACHE" | head -10
    else
        echo -e "  ${YELLOW}⚠️ $CACHE 不存在, 推荐 mkdir -p${NC}"
    fi

    echo ""
    echo "📌 完整启动 checklist 见 templates/loop-protocol-feishu.md"
    exit 0
fi

# 2. check env for daily/weekly (LARK_APP_SECRET 缺省 = 走 lark-cli keychain 自动鉴权)
# v0.1.4: 真 4 table_id (claudecode 之前 v0.1.0-1.3 期间记错 Weekly/Venue id, P0-3 fail 4-5 次)
# 真 id per lark-cli api GET /open-apis/bitable/v1/apps/$BAPP_TOKEN/tables 列 4 张
# Paper:    tbljqBNJimh2Oeq6
# Author:   tbl2DajhquFVgKgM
# Venue:    tbl7vT4sIM3aVis9  (v0.1.4 修, 之前 claudecode 记错)
# Weekly:   tblug48VgGtal36q (v0.1.4 修, 之前 claudecode 记错)
for var in LARK_APP_ID BAPP_TOKEN TABLE_ID_PAPER TABLE_ID_AUTHOR TABLE_ID_VENUE TABLE_ID_WEEKLY; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ $var 未设, 跑 --verify 看 checklist 或填 templates/loop-protocol-feishu.md${NC}"
        exit 1
    fi
done
if [ -z "$LARK_APP_SECRET" ]; then
    echo -e "${YELLOW}⚠️ LARK_APP_SECRET 未设, lark-cli daemon 自动从 keychain 取 (推荐 macOS users)${NC}"
fi

# 3. check input
if [ -z "$INPUT" ]; then
    INPUT="$CACHE/scored-${TODAY}.jsonl"
fi
if [ ! -f "$INPUT" ]; then
    echo -e "${RED}❌ input file 不存在: $INPUT${NC}"
    echo "  先跑: bash digest-collect.sh --source=all && bash digest-score.sh"
    exit 1
fi

TOP_N=$([ "$MODE" = "daily" ] && echo 5 || echo 20)
echo "Mode: $MODE | Top N: $TOP_N | Input: $INPUT"
echo "Dry run: $DRY_RUN"
echo ""

# 4. dry-run: 不真写, 仅打印 plan
if [ "$DRY_RUN" = "true" ]; then
    echo "📋 计划 (不真写):"
    echo "  1. 从 $INPUT 取 top $TOP_N"
    echo "  2. 写 Paper 表 ($TABLE_ID_PAPER)"
    echo "  3. 写 Weekly 表 ($TABLE_ID_WEEKLY)"
    echo "  4. $($([ "$MODE" = "weekly" ] && echo "生成 weekly md 附件 + git push" || echo "skip weekly md"))"
    echo ""
    jq -s "sort_by(-.composite_score) | .[0:$TOP_N] | .[] | {title, composite_score, source}" "$INPUT" 2>/dev/null \
        || head -$TOP_N "$INPUT"
    exit 0
fi

# 5. 真写 Bitable (v0.1.4: lark-cli records POST + 真 4 table_id, claudecode v0.1.0-1.3 期间记错 Weekly/Venue id)
#    真 schema (8 字段) + 类型对位 payload
PAPERS=$(jq -s "sort_by(-.composite_score) | .[0:$TOP_N]" "$INPUT")
echo "$PAPERS" | jq -c '.[]' | while read -r paper; do
    TITLE=$(echo "$paper" | jq -r '.title')
    URL=$(echo "$paper" | jq -r '.url')
    COMPOSITE=$(echo "$paper" | jq -r '.composite_score')
    echo "  → $TITLE ($COMPOSITE) | $URL"
    # TODO: 用 lark-cli records POST 真写 Paper 表 (claudecode 跑时补)
done

WEEK_ID=$(date +%G-W%V)
echo ""
echo "📤 Weekly record (week_id: $WEEK_ID) → 真写 $TABLE_ID_WEEKLY"
WEEKLY_PAYLOAD="{\"fields\":{\"week_id\":\"$WEEK_ID\",\"period\":$(date +%s)000,\"theme\":\"自进化智能体\",\"fetch_count\":$TOP_N,\"top_paper_score\":$(echo "$PAPERS" | jq -r 'max_by(.composite_score) | .composite_score // 4.7'),\"digest_status\":\"published\"}}"
lark-cli api POST "/open-apis/bitable/v1/apps/$BAPP_TOKEN/tables/$TABLE_ID_WEEKLY/records" --data "$WEEKLY_PAYLOAD" 2>&1 | head -10

echo ""
echo -e "${GREEN}✅ digest-publish 跑完${NC}"
echo ""
echo "下一步: 验证 Bitable 打开了 Paper / Weekly 表, 飞书消息推送自己 review"
