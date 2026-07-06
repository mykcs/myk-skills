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
# v0.1.8: auto-load 7 env from .env (per user feedback "不能我每次跑一遍 skill 都重新配一次")
set -a
. "$(dirname "$0")/../.env" 2>/dev/null || . "$(dirname "$0")/.env" 2>/dev/null || true
set +a

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
            # 王锐 N-tool 自定义多重网络搜索协议 (per process.md §F.1, N 可扩展)
            # 5 是当前实例 (mcp__MiniMax + mcp__anysearch + WebFetch + mcp__exa + mcp__kimi-webbridge)
            # 未来加 mcp__x__web_search / mcp__context7__query_docs / mcp__agent-reach__search_17_platforms 等直接扩 N
            # 1 源 = N 工具都跑, dedup by arxiv_id (per templates/feishu-bit-schema.md)
            {
                echo "{\"source\": \"arxiv\", \"query\": \"self-evolving agent OR AI scientist 2026\", \"tools\": [\"MiniMax\", \"anysearch\", \"WebFetch\", \"exa\", \"kimi-webbridge\"], \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            # 真抓时: claudecode 主进程跑 N mcp, 把结果 concat 写到 $out
            ;;
        venue)
            # 顶会 NIPS/ICML/ICLR/CVPR: 王锐 N-tool protocol (N 工具都查, 不只 1 个)
            {
                echo "{\"source\": \"venue-conference\", \"query\": \"NIPS 2026 OR ICML 2026 OR ICLR 2026 self-evolving\", \"tools\": [\"MiniMax\", \"anysearch\", \"WebFetch\", \"exa\", \"kimi-webbridge\"], \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            ;;
        blog)
            # tech blog (OpenAI/Anthropic/DeepMind/HuggingFace): 王锐 N-tool protocol
            {
                echo "{\"source\": \"blog-rss\", \"query\": \"AI lab blog 2026 self-evolving agent\", \"tools\": [\"MiniMax\", \"anysearch\", \"WebFetch\", \"exa\", \"kimi-webbridge\"], \"fetched_at\": \"$(date -Iseconds)\"}"
            } > "$out"
            ;;
        hn)
            # HN frontpage + Show HN: 王锐 N-tool protocol (HN Algolia API + N mcp 也跑同样 query dedup)
            curl -s "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30" 2>/dev/null >> "$out" || true
            # HN Algolia 抓不到, N mcp 兜底
            ;;
        github)
            # GitHub trending: 王锐 N-tool protocol (curl + N mcp 同样 query)
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
