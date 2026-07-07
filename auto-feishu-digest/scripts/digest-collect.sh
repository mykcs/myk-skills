#!/bin/bash
# digest-collect.sh — 3 大类信息源 fan-out 抓 raw article (v0.1.12)
# v0.1.12: 按 user 2026-07-07 反馈, 重定义为 3 大类 (替代 v0.1.9 的 5 源 arxiv/venue/blog/hn/github)
#
# 第 1 大类: 论文 / 会议类 (academic)
#   - arxiv RSS API (cs.AI / cs.LG, 实时论文)
#   - OpenReview API (NIPS / ICML / ICLR / CVPR 最近 accepted papers, 机器学习三大会议)
#   - N mcp (MiniMax / anysearch / exa / kimi-webbridge) 兜底
#
# 第 2 大类: 国内博客 (domestic-blogger, 中文社群)
#   - 晓辉博士 (小红书 ID, AI 产品实战)
#   - 冰瓶子 (Kimi 产品经理, 小红书 profile URL)
#   - Anthropic 中文 (WebFetch + RSS, 如有)
#   - OpenAI 中文 (WebFetch + RSS, 如有)
#   - HuggingFace 中文 (WebFetch, 如有)
#   - N mcp (anysearch query="中文 AI 博客", MiniMax) 兜底
#
# 第 3 大类: 国外博主 (global-blogger)
#   - Codex 产品负责人播客 (xiaoyuzhoufm.com episode URL)
#   - Stratechery (Ben Thompson)
#   - Latent Space (swyx.ai)
#   - Simon Willison's blog
#   - Andrej Karpathy blog
#   - N mcp 兜底
#
# 王锐 N-tool 自定义多重网络搜索协议 (per process.md §F.1, N 可扩展, 5 是当前实例)
# 1 类 = 1 类专属源 (RSS/API/curl 直抓) + N 工具都跑 + dedup by url
#
# 用法:
#   bash digest-collect.sh --source=academic          # 仅论文会议类
#   bash digest-collect.sh --source=domestic-blogger # 仅国内博客
#   bash digest-collect.sh --source=global-blogger   # 仅国外博主
#   bash digest-collect.sh --source=all              # 3 大类全跑
#   bash digest-collect.sh --source=all --dry-run    # 仅打印计划
# 输出: ~/.cache/digest/<class>-<YYYY-MM-DD>.jsonl (一行一 article)

set -e
# v0.1.8: auto-load 7 env from .env
set -a
. "$(dirname "$0")/../.env" 2>/dev/null || . "$(dirname "$0")/.env" 2>/dev/null || true
set +a

SOURCE="all"
DRY_RUN="false"
CACHE="${HOME}/.cache/digest"
TODAY=$(date +%Y-%m-%d)
QUERY="${QUERY:-self-evolving agent OR AI scientist OR LLM agent OR agentic system OR reasoning}"

mkdir -p "$CACHE/log"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 写 JSON 行 (escape 引号)
j() { python3 -c "import json,sys; print(json.dumps(dict(sys.argv[1:])))" "$@"; }

# ╔═══════════════════════════════════════════════════════════════╗
# ║  第 1 大类: 论文 / 会议类 (academic)                          ║
# ║  源: arxiv RSS + OpenReview API + N mcp 兜底                  ║
# ╚═══════════════════════════════════════════════════════════════╝

# ----- arxiv RSS API (cs.AI / cs.LG / cs.CL) -----
collect_arxiv_rss() {
    local out="$CACHE/academic-arxiv-${TODAY}.jsonl"
    echo -e "${GREEN}▶ academic-arxiv (cs.AI/LG/CL)${NC} → $out"
    [ "$DRY_RUN" = "true" ] && { echo "  (dry-run) 跳过"; return 0; }

    : > "$out"
    local rss
    rss=$(curl -sL --max-time 20 "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending" 2>/dev/null || true)
    if [ -z "$rss" ] || ! echo "$rss" | grep -q "<entry>"; then
        echo -e "  ${RED}❌ arxiv RSS empty (network?)${NC}"
        echo "{\"source\":\"academic-arxiv\",\"query\":\"$QUERY\",\"fetched_at\":\"$(date -Iseconds)\",\"error\":\"empty rss\"}" > "$out"
        return 1
    fi

    echo "$rss" | python3 -c "
import sys, json
from xml.etree import ElementTree as ET
ns = {'a':'http://www.w3.org/2005/Atom'}
root = ET.fromstring(sys.stdin.read())
for entry in root.findall('a:entry', ns):
    title = entry.find('a:title', ns).text.strip()
    link  = entry.find('a:id', ns).text.strip()
    auth  = [a.find('a:name', ns).text.strip() for a in entry.findall('a:author', ns)]
    pub   = entry.find('a:published', ns).text[:10]
    summ  = entry.find('a:summary', ns).text.strip().replace('\n',' ')[:300]
    rec = {
        'source':'academic-arxiv','category':'academic','query':'$QUERY',
        'title':title,'url':link,'authors':auth,'submit_date':pub,'abstract':summ,
        'fetched_at':'$(date -Iseconds)',
    }
    print(json.dumps(rec, ensure_ascii=False))
" >> "$out" 2>/dev/null || true

    local lines=$(grep -c '^{' "$out" 2>/dev/null || echo 0)
    [ "$lines" -eq 0 ] && lines=0
    echo "  ✓ $lines 行"
}

# ----- OpenReview (NIPS / ICML / ICLR / CVPR 最近 accepted) -----
collect_openreview() {
    local out="$CACHE/academic-openreview-${TODAY}.jsonl"
    echo -e "${GREEN}▶ academic-openreview (NIPS+ICML+ICLR+CVPR)${NC} → $out"
    [ "$DRY_RUN" = "true" ] && { echo "  (dry-run) 跳过"; return 0; }

    : > "$out"
    local OR_DATA=""
    for venue_id in "NeurIPS.cc/2025/Conference" "ICML.cc/2025/Conference" "ICLR.cc/2025/Conference" "CVPR.cc/2025/Conference"; do
        local resp
        resp=$(curl -sL --max-time 15 "https://api2.openreview.net/notes/search?term=self-evolving+agent+OR+LLM+agent&group=$venue_id&limit=10" 2>/dev/null || true)
        OR_DATA="${OR_DATA}${resp}"
    done

    if [ -n "$OR_DATA" ] && echo "$OR_DATA" | grep -q '"notes"'; then
        echo "$OR_DATA" | python3 -c "
import sys, json
data = sys.stdin.read()
notes = []
try:
    d = json.loads(data)
    if isinstance(d, dict) and 'notes' in d:
        notes = d['notes']
except json.JSONDecodeError:
    pass
for n in notes[:30]:
    c = n.get('content', {})
    title_raw = c.get('title', '')
    title = title_raw.get('value','') if isinstance(title_raw, dict) else str(title_raw or '')
    if not title:
        continue
    auth_raw = c.get('authors', {})
    if isinstance(auth_raw, dict):
        auth = auth_raw.get('value', [])
    else:
        auth = auth_raw if isinstance(auth_raw, list) else []
    venue = ''
    if n.get('invitations'):
        first_inv = n['invitations'][0]
        venue = first_inv.split('/')[1] if '/' in first_inv else first_inv
    rec = {
        'source':'academic-openreview','category':'academic','query':'$QUERY',
        'title':title[:200],'url':f\"https://openreview.net/forum?id={n.get('id','')}\",
        'authors':auth[:10],'venue':venue,
        'fetched_at':'$(date -Iseconds)',
    }
    print(json.dumps(rec, ensure_ascii=False))
" >> "$out" 2>/dev/null || true
    fi

    local lines=$(grep -c '^{' "$out" 2>/dev/null || echo 0)
    if [ "$lines" -eq 0 ]; then
        echo -e "  ${YELLOW}⚠️ OpenReview 0 行, 留待 N mcp 兜底 (claudecode 主进程跑)${NC}"
        echo "{\"source\":\"academic-openreview\",\"category\":\"academic\",\"query\":\"$QUERY\",\"fetched_at\":\"$(date -Iseconds)\",\"note\":\"OpenReview 0 hit, 等 claudecode N mcp 抓 NIPS/ICML/ICLR/CVPR\"}" > "$out"
        lines=1
    fi
    echo "  ✓ $lines 行"
}

# ╔═══════════════════════════════════════════════════════════════╗
# ║  第 2 大类: 国内博客 (domestic-blogger, 中文社群)              ║
# ║  源: N mcp 抓 + WebFetch 直抓                                 ║
# ║  晓辉博士 (小红书), 冰瓶子 (Kimi PM, 小红书),                ║
# ║  Anthropic 中文/OpenAI 中文/HuggingFace 中文                   ║
# ╚═══════════════════════════════════════════════════════════════╝

# ----- 国内博客专属源 (per user 2026-07-07 配置) -----
# 晓辉博士: 小红书 ID + 主理 AI 产品实战文章
# 冰瓶子: Kimi 产品经理 (Moonshot AI), 小红书 profile
# Note: 留 N mcp 兜底 (claudecode 跑 anysearch query="AI 博客")
collect_domestic_brokers() {
    local out="$CACHE/domestic-broker-${TODAY}.jsonl"
    echo -e "${GREEN}▶ domestic-blogger (晓辉博士 + 冰瓶子 + 中文 AI 社群)${NC} → $out"
    [ "$DRY_RUN" = "true" ] && { echo "  (dry-run) 跳过"; return 0; }

    : > "$out"
    # N mcp 兜底 (留 claudecode 跑):
    #   mcp__anysearch__web_search: "AI 产品实战 晓辉博士 OR 冰瓶子 Kimi 产品经理"
    #   mcp__MiniMax__web_search:    "中文 AI 博客"
    #   WebFetch: 小红书 profile, RSS feed 等
    # MVP 默认 0 行, 留 N mcp 兜底 (claudecode 主进程跑)
    echo "{\"source\":\"domestic-broker\",\"category\":\"domestic\",\"sub_sources\":[\"晓辉博士(小红书)\",\"冰瓶子(Kimi PM,小红书)\",\"中文 AI 博客 N mcp 兜底\"],\"query\":\"$QUERY\",\"fetched_at\":\"$(date -Iseconds)\",\"note\":\"N mcp 兜底等 claudecode\"}" > "$out"

    # 尝试 WebFetch 抓公开内容 (如博客 RSS)
    local resp
    resp=$(curl -sL --max-time 10 -A "Mozilla/5.0" "https://api.xiaohongshu.com/api/sns/v2/comment/page?note_id=&cursor=" 2>/dev/null || true)
    # 小红书 API 反爬, 大概率空, 不 fail
    if [ -n "$resp" ] && echo "$resp" | grep -q '"data"'; then
        echo "$resp" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    items = d.get('data',{}).get('comments',[]) or d.get('data',{}).get('notes',[]) or []
    for item in items[:10]:
        title = item.get('title') or item.get('content','')[:80]
        link = item.get('url') or f\"https://www.xiaohongshu.com/explore/{item.get('note_id','')}\"
        rec = {
            'source':'domestic-broker','category':'domestic','query':'$QUERY',
            'title':title,'url':link,
            'author':item.get('user',{}).get('nickname',''),'platform':'xiaohongshu',
            'fetched_at':'$(date -Iseconds)',
        }
        print(json.dumps(rec, ensure_ascii=False))
except (json.JSONDecodeError, KeyError):
    pass
" >> "$out" 2>/dev/null || true
    fi

    local lines=$(grep -c '^{' "$out" 2>/dev/null || echo 0)
    echo "  ✓ $lines 行 (N mcp 兜底待 claudecode)"
}

# ----- 中文 AI 公司博客 RSS + WebFetch (Anthropic 中文等) -----
collect_chinese_blog() {
    local out="$CACHE/domestic-blog-cn-${TODAY}.jsonl"
    echo -e "${GREEN}▶ domestic-blog (中文 AI 社群里 RSS feed: Anthropic 中文等)${NC} → $out"
    [ "$DRY_RUN" = "true" ] && { echo "  (dry-run) 跳过"; return 0; }

    : > "$out"
    local lines=0
    # HuggingFace 中文博客 (有 RSS)
    local HF_RSS
    HF_RSS=$(curl -sL --max-time 10 -A "Mozilla/5.0" "https://huggingface.co/blog/feed.xml" 2>/dev/null || true)
    if [ -n "$HF_RSS" ] && echo "$HF_RSS" | grep -q "<item"; then
        echo "$HF_RSS" | python3 -c "
import sys, json
from xml.etree import ElementTree as ET
ns = {'a':'http://www.w3.org/2005/Atom'}
data = sys.stdin.read()
try:
    root = ET.fromstring(data)
    for item in root.findall('.//item'):
        t = item.find('title')
        l = item.find('link')
        d = item.find('pubDate')
        desc = item.find('description')
        rec = {
            'source':'domestic-blog-cn','category':'domestic','sub_source':'HuggingFace',
            'title':(t.text or '').strip()[:200],'url':(l.text or '').strip(),
            'pub_date':(d.text or '')[:10],'summary':(desc.text or '')[:300] if desc is not None else '',
            'fetched_at':'$(date -Iseconds)',
        }
        print(json.dumps(rec, ensure_ascii=False))
except ET.ParseError:
    pass
" >> "$out" 2>/dev/null || true
    fi

    lines=$(grep -c '^{' "$out" 2>/dev/null || echo 0)
    if [ "$lines" -eq 0 ]; then
        echo "{\"source\":\"domestic-blog-cn\",\"category\":\"domestic\",\"sub_source\":\"N mcp 兜底\",\"query\":\"$QUERY\",\"fetched_at\":\"$(date -Iseconds)\",\"note\":\"N mcp (Anthropic 中文 / OpenAI 中文 / HuggingFace / 极客公园 / 机器之心) 等 claudecode 跑\"}" > "$out"
        lines=1
    fi
    echo "  ✓ $lines 行 (中文博客 + RSS 兜底)"
}

# ╔═══════════════════════════════════════════════════════════════╗
# ║  第 3 大类: 国外博主 (global-blogger)                          ║
# ║  源: codex 产品负责人播客 + Stratechery + Latent Space +     ║
# ║       Simon Willison + Karpathy + N mcp 兜底                  ║
# ╚═══════════════════════════════════════════════════════════════╝

# ----- 国外博主专属 (per user 2026-07-07 配置: codex PM 播客) -----
collect_global_bloggers() {
    local out="$CACHE/global-blogger-${TODAY}.jsonl"
    echo -e "${GREEN}▶ global-blogger (codex PM 播客 + Stratechery + Latent Space + 5 个)${NC} → $out"
    [ "$DRY_RUN" = "true" ] && { echo "  (dry-run) 跳过"; return 0; }

    : > "$out"
    # 留 N mcp 兜底 (claudecode 跑 WebFetch + mcp__MiniMax__web_search):
    #   codex 产品负责人播客: https://www.xiaoyuzhoufm.com/episode/6a43a9699d2f574368405276
    #   Stratechery (Ben Thompson): https://stratechery.com
    #   Latent Space (swyx.ai): https://latent.space
    #   Simon Willison: https://simonwillison.net
    #   Andrej Karpathy: https://karpathy.ai
    #   Lilian Weng (智能体博客): https://lilianweng.github.io
    echo "{\"source\":\"global-blogger\",\"category\":\"global\",\"sub_sources\":[\"codex PM 播客(xiaoyuzhoufm.com)\",\"Stratechery\",\"Latent Space\",\"Simon Willison\",\"Karpathy\",\"Lilian Weng\"],\"query\":\"$QUERY\",\"fetched_at\":\"$(date -Iseconds)\",\"note\":\"WebFetch + N mcp 兜底等 claudecode\"}" > "$out"

    local lines=$(grep -c '^{' "$out" 2>/dev/null || echo 0)
    echo "  ✓ $lines 行 (国外博主 WebFetch + N mcp 兜底)"
}

# ----- main -----
echo "═══════════════════════════════════════════════════════════"
echo "🌀 Digest Collect — 3 大类信息源 fan-out (v0.1.12)"
echo "═══════════════════════════════════════════════════════════"
echo "Date:   $TODAY"
echo "Cache:  $CACHE"
echo "Query:  $QUERY"
echo "Source: $SOURCE  | dry_run: $DRY_RUN"
echo ""

# v0.1.12: 重定义为 3 大类信息源
case "$SOURCE" in
    academic)
        echo -e "${GREEN}▶ 第 1 大类: 论文 / 会议类${NC}"
        echo ""
        echo -e "${YELLOW}  1.1 academic-arxiv (cs.AI/LG/CL)${NC}"
        collect_arxiv_rss
        echo -e "${YELLOW}  1.2 academic-openreview (NIPS+ICML+ICLR+CVPR + N mcp 兜底)${NC}"
        collect_openreview
        ;;
    domestic-blogger)
        echo -e "${GREEN}▶ 第 2 大类: 国内博客 (中文 AI 社群)${NC}"
        echo ""
        echo -e "${YELLOW}  2.1 domestic-broker (晓辉博士 + 冰瓶子 + N mcp 兜底)${NC}"
        collect_domestic_brokers
        echo -e "${YELLOW}  2.2 domestic-blog-cn (Anthropic 中文等 RSS feed)${NC}"
        collect_chinese_blog
        ;;
    global-blogger)
        echo -e "${GREEN}▶ 第 3 大类: 国外博主${NC}"
        echo ""
        echo -e "${YELLOW}  3.1 global-blogger (codex PM 播客 + Stratechery + 5 大博主 + N mcp 兜底)${NC}"
        collect_global_bloggers
        ;;
    all)
        echo -e "${GREEN}▶ 第 1 大类: 论文 / 会议类${NC}"
        echo ""
        echo -e "${YELLOW}  1.1 academic-arxiv (cs.AI/LG/CL)${NC}"
        collect_arxiv_rss
        echo -e "${YELLOW}  1.2 academic-openreview (NIPS+ICML+ICLR+CVPR + N mcp 兜底)${NC}"
        collect_openreview
        echo ""
        echo -e "${GREEN}▶ 第 2 大类: 国内博客 (中文 AI 社群)${NC}"
        echo ""
        echo -e "${YELLOW}  2.1 domestic-broker (晓辉博士 + 冰瓶子 + N mcp 兜底)${NC}"
        collect_domestic_brokers
        echo -e "${YELLOW}  2.2 domestic-blog-cn (Anthropic 中文等 RSS feed)${NC}"
        collect_chinese_blog
        echo ""
        echo -e "${GREEN}▶ 第 3 大类: 国外博主${NC}"
        echo ""
        echo -e "${YELLOW}  3.1 global-blogger (codex PM 播客 + Stratechery + 5 大博主 + N mcp 兜底)${NC}"
        collect_global_bloggers
        ;;
    *)
        echo "用法: $0 [--source=academic|domestic-blogger|global-blogger|all] [--dry-run] [--query='...']"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 抓源完成, 下一步: bash digest-score.sh${NC}"
echo "  或 dry-run 自检: bash digest-score.sh --dry-run"
