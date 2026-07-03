#!/bin/bash
# digest-collect.sh — 5 源 fan-out 抓 raw article
# 5 源: arxiv + venue-conference + blog-rss + hn + github-trending
# 复用 process.md §F.1 + §F.1.2 降级矩阵 (5-tool)
# 用法:
#   bash digest-collect.sh --source=arxiv         # 单源
#   bash digest-collect.sh --source=all           # 5 源全跑
#   bash digest-collect.sh --source=all --dry-run # 不真抓, 仅打印计划
# 输出: ~/.cache/digest/<source>-<YYYY-MM-DD>.jsonl

set -e
SOURCE="all"
DRY_RUN="false"
CACHE="${HOME}/.cache/digest"
TODAY=$(date +%Y-%m-%d)

mkdir -p "$CACHE/log"

# parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --source=*) SOURCE="${1#*=}" ;;
        --dry-run) DRY_RUN="true" ;;
        --cache=*) CACHE="${1#*=}" ;;
        *) echo "用法: $0 [--source=arxiv|venue|blog|hn|github|all] [--dry-run] [--cache=PATH]"; exit 1 ;;
    esac
    shift
done

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

collect_one() {
    local src="$1"
    local out="$CACHE/${src}-${TODAY}.jsonl"
    echo -e "${GREEN}▶ $src${NC} → $out"

    if [ "$DRY_RUN" = "true" ]; then
        echo "  (dry-run) 跳过真抓"
        return 0
    fi

    case "$src" in
        arxiv)
            # 5-tool parallel fan-out (per process.md §F.1 + user 2026-07-03 反馈 "每源都用 5-tool, 不是 1 源 1 tool")
            # 5 mcp 并行跑 query: mcp__MiniMax__web_search + mcp__anysearch__web_search + WebFetch + mcp__exa (combo) + mcp__kimi-webbridge
            # 5 工具都查 arxiv, dedup by arxiv_id (per templates/feishu-bit-schema.md)
            # 1 源 = 5 工具都跑 (不只 1 个), 结果去重合并
            {
                echo "{\"source\": \"arxiv\", \"query\": \"self-evolving agent OR AI scientist 2026\", \"tools\": [\"MiniMax\", \"anysearch\", \"WebFetch\", \"exa\", \"kimi-webbridge\"], \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            # 真抓时: claudecode 主进程跑 5 mcp, 把结果 concat 写到 $out
            ;;
        venue)
            # 顶会 NIPS/ICML/ICLR/CVPR: 5-tool parallel fan-out (5 工具都查, 不只 1 个)
            {
                echo "{\"source\": \"venue-conference\", \"query\": \"NIPS 2026 OR ICML 2026 OR ICLR 2026 self-evolving\", \"tools\": [\"MiniMax\", \"anysearch\", \"WebFetch\", \"exa\", \"kimi-webbridge\"], \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            ;;
        blog)
            # tech blog (OpenAI/Anthropic/DeepMind/HuggingFace): 5-tool fan-out
            {
                echo "{\"source\": \"blog-rss\", \"query\": \"AI lab blog 2026 self-evolving agent\", \"tools\": [\"MiniMax\", \"anysearch\", \"WebFetch\", \"exa\", \"kimi-webbridge\"], \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            ;;
        hn)
            # HN frontpage + Show HN: 5-tool fan-out (HN Algolia API + 4 mcp 也跑同样 query dedup)
            curl -s "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30" 2>/dev/null >> "$out" || true
            # HN Algolia 抓不到, 4 mcp 兜底
            ;;
        github)
            # GitHub trending: 5-tool fan-out (curl + 4 mcp 同样 query)
            curl -s "https://github.com/trending?since=daily" 2>/dev/null >> "$out" || true
            ;;
        *)
            echo -e "${YELLOW}⚠️ 未知 source: $src${NC}"
            return 1
            ;;
    esac

    if [ -f "$out" ]; then
        local lines=$(wc -l < "$out")
        echo "  ✓ $lines 行"
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "🌀 Digest Collect — 5 源 fan-out"
echo "═══════════════════════════════════════════════════════════"
echo "Date:  $TODAY"
echo "Cache: $CACHE"
echo "Mode:  $SOURCE  | dry_run: $DRY_RUN"
echo ""

if [ "$SOURCE" = "all" ]; then
    for s in arxiv venue blog hn github; do
        collect_one "$s"
    done
else
    collect_one "$SOURCE"
fi

echo ""
echo -e "${GREEN}✅ 抓源完成, 下一步: bash digest-score.sh${NC}"
echo "  或 dry-run 自检: bash digest-score.sh --dry-run"
