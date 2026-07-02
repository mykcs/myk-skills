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
            # 5-tool parallel fan-out (per process.md §F.1)
            # 优先 MiniMax, fallback exa + WebFetch
            {
                echo "{\"source\": \"arxiv\", \"query\": \"self-evolving agent OR AI scientist\", \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            # 真抓时: mcp__MiniMax__web_search + mcp__exa__web_search_exa + WebFetch (parallel)
            # MVP: 占位, user 配好 API 后由 claudecode 补全
            ;;
        venue)
            # 抓 NIPS/ICML/ICLR/CVPR 最新 accepted papers
            # 用 OpenReview API + WebFetch
            {
                echo "{\"source\": \"venue-conference\", \"query\": \"NIPS 2026 OR ICML 2026 OR ICLR 2026\", \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            ;;
        blog)
            # RSS: OpenAI / Anthropic / DeepMind / HuggingFace 等
            # 用 WebFetch 抓 RSS feed 或 reader 类 API
            {
                echo "{\"source\": \"blog-rss\", \"query\": \"AI lab blog 2026\", \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            ;;
        hn)
            # HackerNews frontpage + Show HN
            # 用 HN Algolia API: https://hn.algolia.com/api/v1/search?tags=front_page
            curl -s "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30" 2>/dev/null >> "$out" || true
            ;;
        github)
            # GitHub trending (today)
            # curl https://github.com/trending + parser
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
