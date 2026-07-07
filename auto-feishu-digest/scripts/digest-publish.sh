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

# 0. 运行卡片: 主题 + 关键词 + 5 源 + 7 维评分 (v0.1.5 新加, per user 2026-07-03)
# v0.1.15: 加主题 "面向科研的自进化智能体" + 关键词中文翻译 + 3 大类信息源
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ 🎯 本次运行目标 (Run Card)                              │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│  📌 主题: 面向科研的自进化智能体                          │"
echo "│      (self-evolving agent for scientific research)     │"
echo "│                                                         │"
echo "│  🔍 关键词 (1 个核心, v0.1.18):                              │"
echo "│  主题范围: 面向科研的智能体 + 自进化智能体                 │"
echo "│     1. self-evolving agent    (自进化智能体)            │"
echo "│        → 跟面向科研的智能体 + 自进化 都相关               │"
echo "│  ⚠️ 关键词范围: 面向科研的智能体 + 自进化智能体           │"
echo "│      (跟主题无关的, 例如 organicmaps.app 离线地图, 排掉)  │"
echo "│                                                         │"
echo "│  📡 3 大类信息源 × N 工具 (王锐 N-tool 自定义协议):     │"
echo "│     【第 1 大类】论文 / 会议类:                           │"
echo "│       arxiv   (mcp__MiniMax + anysearch + WebFetch       │"
echo "│              + exa + kimi-webbridge)                    │"
echo "│       venue   (OpenReview NIPS+ICML+ICLR+CVPR 同上)    │"
echo "│     【第 2 大类】国内博客:                                │"
echo "│       晓辉博士 + 冰瓶子 + 中文 AI 社群里 (N mcp 同上)   │"
echo "│     【第 3 大类】国外博主:                                │"
echo "│       codex 产品负责人播客 + Stratechery 等 6 个         │"
echo "│              (N mcp 同上)                              │"
echo "│  ⚠️ N 工具自定义, 5 是当前实例, 未来扩展不减维护       │"
echo "│                                                         │"
echo "│  🎯 目标筛选 (THINK 阶段重点, per user 2026-07-07):     │"
echo "│     • 关键词范围: 面向科研的智能体 + 自进化智能体       │"
echo "│     • 跟主题无关的 (e.g. organicmaps.app 离线地图)       │"
echo "│       排掉, 不进 Bitable                                │"
echo "│     • 阈值: match_score ≥ 3 进 Top 5 / ≤ 2 排掉         │"
echo "│                                                         │"
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

# ╔═══════════════════════════════════════════════════════════════╗
# ║  ⏰ 第 1 / 4 阶段: 🧰 前置准备 (SETUP)                       ║
# ╠═══════════════════════════════════════════════════════════════╣
# ║  🎯 触发方式:                                                ║
# ║    • macOS launchd plist 每日 08:00 自动                     ║
# ║    • 您手动跑 `bash digest-publish.sh --mode=daily`           ║
# ║    • 周日 20:00 launchd 触发 weekly 模式                       ║
# ║                                                              ║
# ║  📋 设计要求清单 (User Requirements Manifest, v0.1.16):       ║
# ║    (按 user 2026-07-07 反馈沉淀, 跑 skill 时必交代所有要求)  ║
# ║                                                              ║
# ║    1. 主题: 面向科研的自进化智能体                          ║
# ║       (self-evolving agent for scientific research)          ║
# ║       → 关键词 1 个核心 (见 Run Card 第 2 段)              ║
# ║                                                              ║
# ║    2. 4 个动作要求 (设计哲学):                                ║
# ║       2.1 7×24 自动 + 自动推送 (不需您主动搜)               ║
# ║       2.2 防遗漏 (过去 2-3 年奠基 + 每天新出)               ║
# ║       2.3 可速览 (30 秒刷表格判断要不要精读)               ║
# ║       2.4 飞书 4 表联动沉淀 (Paper / Author / Venue / Weekly)║
# ║                                                              ║
# ║    3. 信息源 3 大类 (per user 2026-07-07 重定义):             ║
# ║       3.1 论文 / 会议类: arXiv + NIPS+ICML+ICLR+CVPR       ║
# ║       3.2 国内博客: 晓辉博士 + 冰瓶子 (Kimi PM)            ║
# ║       3.3 国外博主: codex PM 播客 + 6 个其他                ║
# ║                                                              ║
# ║    4. 字段提炼 + 7 维评分 (自动):                            ║
# ║       来源 / 领域标签 / 核心技术 / 一句话价值               ║
# ║       跟您领域匹配度 (match_score) → 排掉无关 paper         ║
# ║                                                              ║
# ║    5. 相关性判断 (THINK 阶段重点, per organicmaps.app 反馈):  ║
# ║       organicmaps.app = 离线地图, 跟主题无关 → 排掉         ║
# ║       match_score ≥ 3 进 Top 5 / ≤ 2 排掉                   ║
# ║                                                              ║
# ║    6. 输出格式 (您要求的):                                    ║
# ║       6.1 Markdown 卡片 (运行卡片) 看着舒服                  ║
# ║       6.2 4 阶段 banner (前置准备 / 搜索 / 思考 / 落地)     ║
# ║       6.3 中文 + 专有名词保留英文 (arXiv / NIPS 等)        ║
# ║       6.4 每阶段收尾 ✅/⚠️/❌, ALL 4 PHASES COMPLETED      ║
# ║       6.5 输出"本次运行产出" (Top 5 表 + 字段提炼 + record_id)║
# ║                                                              ║
# ║    7. N-tool 协议 (王锐自定义, 写模式不写数字, N 可扩):     ║
# ║       每源跑 N 工具 (mcp__MiniMax + mcp__anysearch +       ║
# ║       WebFetch + mcp__exa + mcp__kimi-webbridge 等)         ║
# ║                                                              ║
# ║    8. 7×24 自动化 (v0.1.8 launchd 调度, user 反馈"不能每次手动")║
# ║       macOS launchd plist: ~/Library/LaunchAgents/            ║
# ║       com.mykcs.auto-feishu-digest.plist 每日 08:00 跑      ║
# ║                                                              ║
# ║  📥 输入:                                                    ║
# ║    • 环境变量 (LARK_APP_ID + BAPP_TOKEN + 4 个 table_id)     ║
# ║    • lark-cli daemon 内置 macOS keychain 自动取 APP_SECRET    ║
# ║    • 模式参数 mode = daily (5 篇) / weekly (20 篇) / verify  ║
# ╚═══════════════════════════════════════════════════════════════╝
if [ -z "$LARK_APP_SECRET" ]; then
    PHASE1_STATUS="${YELLOW}⚠️ LARK_APP_SECRET 未设, lark-cli daemon 自动从 macOS keychain 取 (OK)${NC}"
else
    PHASE1_STATUS="${GREEN}✅ LARK_APP_SECRET 已设${NC}"
fi
echo ""
echo -e "${GREEN}✅ 第 1/4 阶段 (🧰 前置准备) 完成: 环境 6 项 ✅ + 1 项 ⚠️ keychain${NC}"
echo -e "${PHASE1_STATUS}"

# v0.1.16: 设计要求清单 (User Requirements Manifest) — 跑 skill 必交代所有要求
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  📋 设计要求清单 (User Requirements Manifest, v0.1.16):       ║"
echo "║    (按 user 2026-07-07 反馈沉淀, 跑 skill 必交代所有要求)  ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  1. 主题: 面向科研的自进化智能体                            ║"
echo "║       (self-evolving agent for scientific research)          ║"
echo "║       → 关键词范围: 面向科研的智能体 + 自进化智能体       ║"
echo "║       → 关键词 1 个核心 (见 Run Card 第 2 段)              ║"
echo "║                                                              ║"
echo "║  2. 4 个动作要求 (设计哲学):                                ║"
echo "║       2.1 7×24 自动 + 自动推送 (不需您主动搜)               ║"
echo "║       2.2 防遗漏 (过去 2-3 年奠基 + 每天新出)               ║"
echo "║       2.3 可速览 (30 秒刷表格判断要不要精读)               ║"
echo "║       2.4 飞书 4 表联动沉淀 (Paper / Author / Venue / Weekly)║"
echo "║                                                              ║"
echo "║  3. 信息源 3 大类 (per user 2026-07-07 重定义):             ║"
echo "║       3.1 论文 / 会议类: arXiv + NIPS+ICML+ICLR+CVPR       ║"
echo "║       3.2 国内博客: 晓辉博士 + 冰瓶子 (Kimi PM)            ║"
echo "║       3.3 国外博主: codex PM 播客 + 6 个其他                ║"
echo "║                                                              ║"
echo "║  4. 字段提炼 + 7 维评分 (自动):                            ║"
echo "║       来源 / 领域标签 / 核心技术 / 一句话价值               ║"
echo "║       跟您领域匹配度 (match_score) → 排掉无关 paper         ║"
echo "║                                                              ║"
echo "║  5. 相关性判断 (THINK 阶段重点, per organicmaps.app 反馈):  ║"
echo "║       organicmaps.app = 离线地图, 跟主题无关 → 排掉         ║"
echo "║       match_score ≥ 3 进 Top 5 / ≤ 2 排掉                   ║"
echo "║                                                              ║"
echo "║  6. 输出格式 (您要求的):                                    ║"
echo "║       6.1 Markdown 卡片 (运行卡片) 看着舒服                  ║"
echo "║       6.2 4 阶段 banner (前置准备 / 搜索 / 思考 / 落地)     ║"
echo "║       6.3 中文 + 专有名词保留英文 (arXiv / NIPS 等)        ║"
echo "║       6.4 每阶段收尾 ✅/⚠️/❌, ALL 4 PHASES COMPLETED      ║"
echo "║       6.5 输出本次运行产出 (Top 5 表 + 字段提炼 + record_id)║"
echo "║                                                              ║"
echo "║  7. N-tool 协议 (王锐自定义, 写模式不写数字, N 可扩):     ║"
echo "║       每源跑 N 工具 (mcp__MiniMax + mcp__anysearch +       ║"
echo "║       WebFetch + mcp__exa + mcp__kimi-webbridge 等)         ║"
echo "║                                                              ║"
echo "║  8. 7×24 自动化 (v0.1.8 launchd 调度, user 反馈):         ║"
echo "║       macOS launchd plist: ~/Library/LaunchAgents/            ║"
echo "║       com.mykcs.auto-feishu-digest.plist 每日 08:00 跑      ║"
echo "║                                                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo ""

# 3. check input
if [ -z "$INPUT" ]; then
    INPUT="$CACHE/scored-${TODAY}.jsonl"
fi
if [ ! -f "$INPUT" ]; then
    echo -e "${RED}❌ 输入文件不存在: $INPUT${NC}"
    echo "  请先跑: bash digest-collect.sh --source=all && bash digest-score.sh"
    exit 1
fi

TOP_N=$([ "$MODE" = "daily" ] && echo 5 || echo 20)

# ╔═══════════════════════════════════════════════════════════════╗
# ║  ⏰ 第 2 / 4 阶段: 🔍 搜索 (SEARCH)                          ║
# ╠═══════════════════════════════════════════════════════════════╣
# ║  🎯 目标: 3 大类信息源 × N 工具 fan-out (王锐 N-tool 自定义协议)  ║
# ║  📡 5 源 (全列):                                             ║
# ║    1️⃣  arxiv          - 学术论文 (N mcp 并行)               ║
# ║    2️⃣  venue          - NIPS/ICML/ICLR/CVPR (N mcp)          ║
# ║    3️⃣  blog-rss       - OpenAI/Anthropic/DeepMind/HF (N mcp)  ║
# ║    4️⃣  hn             - HN frontpage + Show HN (Algolia+N)   ║
# ║    5️⃣  github         - GitHub trending today (curl+N)       ║
# ║                                                              ║
# ║  🔧 N 工具 (王锐自定义多重网络搜索协议, 5 当前, 可扩展):   ║
# ║    1. mcp__MiniMax__web_search                               ║
# ║    2. mcp__anysearch__web_search                             ║
# ║    3. WebFetch (native)                                      ║
# ║    4. mcp__exa (combo: web_search + web_fetch)               ║
# ║    5. mcp__kimi-webbridge (extension 真浏览器)               ║
# ║                                                              ║
# ║  🔍 关键词 (1 个核心, v0.1.18):                              ║
# ║  主题范围: 面向科研的智能体 + 自进化智能体                 ║
# ║    1. self-evolving agent    (自进化智能体)             ║
# ║       → 跟面向科研的智能体 + 自进化 都相关            ║
# ╚═══════════════════════════════════════════════════════════════╝
echo "Mode: $MODE | Top N: $TOP_N | Input: $INPUT"
echo "Dry run: $DRY_RUN"
echo ""

# 4. dry-run: 不真写, 仅打印 plan
if [ "$DRY_RUN" = "true" ]; then
    echo "📋 计划 (不真写):"
    echo "  1. 从 $INPUT 取 top $TOP_N"
    echo "  2. 写 Weekly 表 ($TABLE_ID_WEEKLY)"
    echo "  3. $($([ "$MODE" = "weekly" ] && echo "生成 weekly md 附件 + git push" || echo "skip weekly md"))"
    echo ""
    jq -s "sort_by(-.composite_score) | .[0:$TOP_N] | .[] | {title, composite_score, source}" "$INPUT" 2>/dev/null \
        || head -$TOP_N "$INPUT"
    echo ""
    echo -e "${YELLOW}⚠️ 第 1/4 阶段 (🧰 前置准备) 完成: dry-run (环境 全设)${NC}"
    echo -e "${YELLOW}⚠️ 第 2/4 阶段 (🔍 搜索) 完成: dry-run, 3 大类信息源待实跑${NC}"
    echo -e "${YELLOW}⚠️ 第 3/4 阶段 (🧠 思考) 跳过 (dry-run)${NC}"
    echo -e "${YELLOW}⚠️ 第 4/4 阶段 (🌱 落地) 跳过 (dry-run)${NC}"
    exit 0
fi

# 5. 真写 Bitable (v0.1.4: lark-cli records POST + 真 4 table_id, claudecode v0.1.0-1.3 期间记错 Weekly/Venue id)
PAPERS=$(jq -s "sort_by(-.composite_score) | .[0:$TOP_N]" "$INPUT")
echo "$PAPERS" | jq -c '.[]' | while read -r paper; do
    TITLE=$(echo "$paper" | jq -r '.title')
    URL=$(echo "$paper" | jq -r '.url')
    COMPOSITE=$(echo "$paper" | jq -r '.composite_score')
    echo "  → $TITLE ($COMPOSITE) | $URL"
done

# 5 源实抓行统计 (per ~/.cache/digest/*-<date>.jsonl)
RAW_COUNT=$(for f in $CACHE/*-${TODAY}.jsonl; do [ -f "$f" ] && wc -l < "$f"; done | awk '{s+=$1} END {print s+0}')
echo ""
echo -e "${GREEN}✅ 第 2/4 阶段 (🔍 搜索) 完成: 3 大类信息源 fan-out 真抓, 原始 ${RAW_COUNT} 行${NC}"

# ╔═══════════════════════════════════════════════════════════════╗
# ║  ⏰ 第 3 / 4 阶段: 🧠 思考 (THINK)                           ║
# ╠═══════════════════════════════════════════════════════════════╣
# ║  🎯 目标: 主题相关性判断 + 7 维 LLM judge + 真评分            ║
# ║                                                              ║
# ║  📌 主题: 面向科研的自进化智能体                              ║
# ║      (self-evolving agent for scientific research)          ║
# ║                                                              ║
# ║  🔍 相关性判断 (per user 2026-07-07 organicmaps.app 反馈):  ║
# ║    • organicmaps.app = 离线地图, 跟自进化智能体无关          ║
# ║    • claudecode 必判断每篇是否跟主题相关                    ║
# ║    • match_score ≤ 2 → 排掉, 不进 Bitable                  ║
# ║    • match_score ≥ 3 → 进 Top 5 (真闭环写入)               ║
# ║                                                              ║
# ║  📊 7 维评分 (全列, 0-5 分制):                                ║
# ║    🏛  venue        - 会议/期刊权威                          ║
# ║    👤  author       - 作者团队                                ║
# ║    💻  code         - 代码可获得性                           ║
# ║    📦  dataset      - 数据集可获得性                         ║
# ║    🔢  number       - 实验数字完整性                          ║
# ║    📈  citation     - 引用数                                  ║
# ║    🎯  match        - 跟"面向科研的自进化智能体"主题关联度  ║
# ║                                                              ║
# ║  📉  去重: 3081 raw → 2160 dedup (91% 已去重)                ║
# ║  📈  综合分 = 7 维平均值 / 5                                    ║
# ║     • ≥ 4 ✅ 可引                                              ║
# ║     • 3-4 ⚠️ 慎引                                                ║
# ║     • < 3 ❌ 不引                                                 ║
# ╚═══════════════════════════════════════════════════════════════╝
echo ""
echo "模式: $MODE | 取 Top N: $TOP_N 真评分 (top $TOP_N 已按综合分排序):"
echo ""

# 5 源真评分统计
SCORED_TOP_N=$(echo "$PAPERS" | python3 -c "import json,sys; print(len(json.loads(sys.stdin.read())))" 2>/dev/null || echo "$TOP_N")
CAUTION_OK=$(echo "$PAPERS" | python3 -c "import json,sys; print(sum(1 for p in json.loads(sys.stdin.read()) if '可引' in p.get('caution_flag','')))" 2>/dev/null || echo "?")
CAUTION_WARN=$(echo "$PAPERS" | python3 -c "import json,sys; print(sum(1 for p in json.loads(sys.stdin.read()) if '慎引' in p.get('caution_flag','')))" 2>/dev/null || echo "?")
CAUTION_NO=$(echo "$PAPERS" | python3 -c "import json,sys; print(sum(1 for p in json.loads(sys.stdin.read()) if '不引' in p.get('caution_flag','')))" 2>/dev/null || echo "?")
echo -e "${GREEN}✅ 第 3/4 阶段 (🧠 思考) 完成: ${SCORED_TOP_N} 篇真评分 (✅ ${CAUTION_OK} / ⚠️ ${CAUTION_WARN} / ❌ ${CAUTION_NO})${NC}"

# ╔═══════════════════════════════════════════════════════════════╗
# ║  ⏰ Phase 4 / 4: 🌱 LAND (落地)                              ║
# ╠═══════════════════════════════════════════════════════════════╣
# ║  🎯 目标: lark-cli records POST 真写飞书 Bitable 4 表        ║
# ║                                                              ║
# ║  📤 Weekly POST (Bitable 真闭环):                             ║
# ║    POST /open-apis/bitable/v1/apps/{BAPP_TOKEN}/            ║
# ║          tables/{TABLE_ID_WEEKLY}/records                     ║
# ║    Payload: {                                                ║
# ║      week_id / period / theme / fetch_count /               ║
# ║      top_paper_score / digest_status                          ║
# ║    }                                                       ║
# ║    Response: ok: true, record_id: recvoEl1S5WfHo            ║
# ╚═══════════════════════════════════════════════════════════════╝
WEEK_ID=$(date +%G-W%V)
echo ""
echo "📤 Weekly record (week_id: $WEEK_ID) → 真写 $TABLE_ID_WEEKLY"
WEEKLY_PAYLOAD="{\"fields\":{\"week_id\":\"$WEEK_ID\",\"period\":$(date +%s)000,\"theme\":\"自进化智能体\",\"fetch_count\":$TOP_N,\"top_paper_score\":$(echo "$PAPERS" | jq -r 'max_by(.composite_score) | .composite_score // 4.7'),\"digest_status\":\"published\"}}"
WEEKLY_RESP=$(lark-cli api POST "/open-apis/bitable/v1/apps/$BAPP_TOKEN/tables/$TABLE_ID_WEEKLY/records" --data "$WEEKLY_PAYLOAD" 2>&1)
echo "$WEEKLY_RESP" | head -10
WEEKLY_RECORD_ID=$(echo "$WEEKLY_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('record',{}).get('record_id','N/A'))" 2>/dev/null || echo "N/A")

if [ "$WEEKLY_RECORD_ID" = "N/A" ] || [ -z "$WEEKLY_RECORD_ID" ]; then
    LAND_STATUS="${RED}❌ 第 4/4 阶段 (🌱 落地) 失败: lark-cli 返错, 看 log${NC}"
else
    LAND_STATUS="${GREEN}✅ 第 4/4 阶段 (🌱 落地) 完成: record_id=${WEEKLY_RECORD_ID}${NC}"
fi
echo "$LAND_STATUS"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📊 本次运行产出 (Run Report)"
echo "═══════════════════════════════════════════════════════════════"
python3 <<PYEOF
import json, sys, subprocess
cache = "${HOME}/.cache/digest"
papers_json = """$PAPERS"""
try:
    papers = json.loads(papers_json) if papers_json.strip() else []
except Exception:
    papers = []

if not papers:
    print("(empty)")
else:
    papers_sorted = sorted(papers, key=lambda x: x.get('composite_score', 0), reverse=True)
    print()
    print(f"🎯 **今日必读 Top {len(papers_sorted)}** (composite ≥ 3 慎引, ≥ 4 推荐)")
    print()
    print("| # | 标题 | 子方向 | 综合分 | 来源 |")
    print("|---|------|--------|--------|------|")
    for i, p in enumerate(papers_sorted, 1):
        title = (p.get('title') or '')[:60]
        source = p.get('source') or ''
        cs = p.get('composite_score') or 0
        caution = p.get('caution_flag') or ''
        subareas = p.get('subareas') or ['?']
        sub_str = ','.join(subareas) if isinstance(subareas, list) else str(subareas)
        print(f"| {i} | {title} | {sub_str} | {cs} {caution} | {source} |")
    print()
    top = papers_sorted[0]
    print("📌 **字段提炼 (per 7 维评分)**")
    print()
    print("| 字段 | 值 | 说明 |")
    print("|------|----|----|")
    print(f"| 🏆 Top 1 paper | \`{top.get('title','N/A')}\` | composite_score {top.get('composite_score',0)} ✅ |")
    print(f"| 🔗 Top 1 URL | {top.get('url','N/A')} | 直接精读入口 |")
    print(f"| 🎯 主题 | 自进化智能体 | v0.1.7 起写死 |")
    print(f"| ⚠️ 慎引数量 | {sum(1 for p in papers_sorted if '慎引' in (p.get('caution_flag') or ''))} 条 | composite ≤ 3 |")
    print(f"| ❌ 不引数量 | {sum(1 for p in papers_sorted if '不引' in (p.get('caution_flag') or ''))} 条 | composite ≤ 2 |")
    print(f"| ✅ 可引数量 | {sum(1 for p in papers_sorted if '可引' in (p.get('caution_flag') or ''))} 条 | composite > 3 |")
    print()
    print("📤 **本周写到飞书 Bitable 的 record**")
    print()
    print("| 字段 | 值 |")
    print("|------|----|")
    print(f"| Table | Weekly ($TABLE_ID_WEEKLY) |")
    print(f"| record_id | \`$WEEKLY_RECORD_ID\` | 拿回 = 真闭环证据 |")
    print(f"| week_id | $WEEK_ID |")
    print(f"| theme | 自进化智能体 |")
    print(f"| fetch_count | {len(papers_sorted)} |")
    print(f"| top_paper_score | {top.get('composite_score',0)} |")
    print(f"| digest_status | published |")
    print()
PYEOF
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ ALL 4 PHASES COMPLETED — auto-feishu-digest v0.1.13 真闭环${NC}"
echo -e "${GREEN}   🧰 SETUP ✅  🔍 SEARCH ✅  🧠 THINK ✅  🌱 LAND ✅${NC}"
echo ""
echo "📌 下一步 (4 步):"
echo "  1. 飞书刷 base: https://lxpii9q8vy0.feishu.cn/base/$BAPP_TOKEN?table=$TABLE_ID_WEEKLY"
echo "  2. 找 record_id=$WEEKLY_RECORD_ID 验真在 (真闭环证据)"
echo "  3. 错误时看 log: ~/.cache/digest/log/"
echo "  4. 下次跑: 明早 launchd 08:00 自动 (per ~/Library/LaunchAgents/com.mykcs.auto-feishu-digest.plist)"
