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

# 1. verify mode: 检查 env
if [ "$MODE" = "verify" ]; then
    echo ""
    echo "[1] 检查环境变量:"
    for var in LARK_APP_ID LARK_APP_SECRET BAPP_TOKEN TABLE_ID_PAPER TABLE_ID_AUTHOR TABLE_ID_VENUE TABLE_ID_WEEKLY; do
        if [ -z "${!var}" ]; then
            echo -e "  ${RED}❌ $var 未设${NC}"
        else
            echo -e "  ${GREEN}✅ $var 已设${NC}"
        fi
    done

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

# 2. check env for daily/weekly
for var in LARK_APP_ID LARK_APP_SECRET BAPP_TOKEN TABLE_ID_PAPER TABLE_ID_WEEKLY; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ $var 未设, 跑 --verify 看 checklist 或填 templates/loop-protocol-feishu.md${NC}"
        exit 1
    fi
done

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

# 5. 真写 Bitable (claudecode 配好 feishu-base mcp 后, 这里用 mcp 调用)
# MVP: 占位, claudecode 跑时改成实际 mcp__feishu-base__create_record 调用

PAPERS=$(jq -s "sort_by(-.composite_score) | .[0:$TOP_N]" "$INPUT")
echo "$PAPERS" | jq -c '.[]' | while read -r paper; do
    TITLE=$(echo "$paper" | jq -r '.title')
    URL=$(echo "$paper" | jq -r '.url')
    COMPOSITE=$(echo "$paper" | jq -r '.composite_score')
    echo "  → $TITLE ($COMPOSITE) | $URL"
    # TODO: 用 mcp__feishu-base__create_record 真写 Paper 表
    # mcp__feishu-base__create_record --table_id "$TABLE_ID_PAPER" --fields "$paper"
done

WEEK_ID=$(date +%G-W%V)
echo ""
echo "📤 Weekly record (week_id: $WEEK_ID)"
# TODO: 用 mcp__feishu-base__create_record 真写 Weekly 表

echo ""
echo -e "${GREEN}✅ digest-publish 跑完${NC}"
echo ""
echo "下一步: 验证 Bitable 打开了 Paper / Weekly 表, 飞书消息推送自己 review"
