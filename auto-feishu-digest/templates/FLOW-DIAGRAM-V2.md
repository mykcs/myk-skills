# auto-feishu-digest skill — 流程图 v2 (4 阶段生命周期)

> **claudecode 自承**: 用户要 "Life → Search → Think → Land" 4 阶段, 每阶段 banner + 完成 ✅/⚠️/❌. 跑 publish 时 4 段清晰呈现.

## 启动流程 (life → search → think → land)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    🌀 LIFE CYCLE: auto-feishu-digest                       │
│                                                                          │
│   ╔══════════════════════════════════════════════════════════════╗      │
│   ║  ⏰ Phase 1 / 4: 🌱 LIFE (生活)                              ║      │
│   ║                                                              ║      │
│   ║  🎯 触发:                                                    ║      │
│   ║    • launchd plist 每日 08:00 自动                          ║      │
│   ║    • user 手动 `bash digest-publish.sh --mode=daily`        ║      │
│   ║    • 每周日 20:00 launchd weekly 模式                       ║      │
│   ║                                                              ║      │
│   ║  📥 输入:                                                    ║      │
│   ║    • env (LARK_APP_ID + BAPP_TOKEN + 4 table_id)            ║      │
│   ║    • lark-cli daemon 内置 macOS keychain 自动取 APP_SECRET  ║      │
│   ║    • mode = daily (5 篇) / weekly (20 篇) / verify         ║      │
│   ║                                                              ║      │
│   ║  ⚙ 准备:                                                    ║      │
│   ║    • bash set -a; . ../.env; set +a (env 自动)              ║      │
│   ║    • dry-run 检查 (mode != verify)                          ║      │
│   ╚══════════════════════════════════════════════════════════════╝      │
│                                                                          │
│   ╔══════════════════════════════════════════════════════════════╗      │
│   ║  ⏰ Phase 2 / 4: 🔍 SEARCH (搜索)                            ║      │
│   ║                                                              ║      │
│   ║  🎯 目标: 5 源 × N 工具 fan-out (王锐 N-tool protocol)     ║      │
│   ║                                                              ║      │
│   ║  📡 5 源 (列出全部):                                         ║      │
│   ║    1. arxiv          - 学术论文 (N mcp 并行)               ║      │
│   ║    2. venue          - NIPS/ICML/ICLR/CVPR (N mcp)          ║      │
│   ║    3. blog-rss       - OpenAI/Anthropic/DeepMind/HF (N mcp)  ║      │
│   ║    4. hn             - HN frontpage + Show HN (Algolia+N)   ║      │
│   ║    5. github         - GitHub trending today (curl+N)       ║      │
│   ║                                                              ║      │
│   ║  🔧 N 工具 (当前 N=5, 可扩展, 王锐协议):                   ║      │
│   ║    1. mcp__MiniMax__web_search                              ║      │
│   ║    2. mcp__anysearch__web_search                            ║      │
│   ║    3. WebFetch (native)                                     ║      │
│   ║    4. mcp__exa (combo: web_search + web_fetch)              ║      │
│   ║    5. mcp__kimi-webbridge (extension 真浏览器)              ║      │
│   ║                                                              ║      │
│   ║  🔍 关键词 (列出全部):                                       ║      │
│   ║    • self-evolving agent (主)                               ║      │
│   ║    • AI scientist                                            ║      │
│   ║    • LLM agent                                               ║      │
│   ║    • agentic system                                          ║      │
│   ║    • reasoning                                               ║      │
│   ║                                                              ║      │
│   ║  📊 输出: ~/.cache/digest/*-YYYY-MM-DD.jsonl (5 文件)     ║      │
│   ║    • arxiv: 30 行                                            ║      │
│   ║    • venue: 10 行                                            ║      │
│   ║    • blog-rss: 20 行                                         ║      │
│   ║    • hn: 30 行                                               ║      │
│   ║    • github: 20 行                                           ║      │
│   ╚══════════════════════════════════════════════════════════════╝      │
│                                                                          │
│   ╔══════════════════════════════════════════════════════════════╗      │
│   ║  ⏰ Phase 3 / 4: 🧠 THINK (思考)                             ║      │
│   ║                                                              ║      │
│   ║  🎯 目标: 7 维 LLM judge + dedup + 真评分                  ║      │
│   ║                                                              ║      │
│   ║  📊 7 维评分 (列全部):                                       ║      │
│   ║    🏛  venue       - 会议/期刊权威                          ║      │
│   ║    👤  author      - 作者团队                                ║      │
│   ║    💻  code        - 代码可获得性                           ║      │
│   ║    📦  dataset     - 数据集可获得性                         ║      │
│   ║    🔢  number      - 实验数字完整性                          ║      │
│   ║    📈  citation    - 引用数                                  ║      │
│   ║    🎯  match       - 跟您领域匹配度                         ║      │
│   ║                                                              ║      │
│   ║  📉  dedup: 5 源 → dedup by id (3081 raw / 2160 dedup)    ║      │
│   ║                                                              ║      │
│   ║  📈  composite_score: avg(7 维) / 5                           ║      │
│   ║     • ≥ 4 ✅ 可引                                            ║      │
│   ║     • 3-4 ⚠️ 慎引                                             ║      │
│   ║     • < 3 ❌ 不引                                              ║      │
│   ║                                                              ║      │
│   ║  📊 输出: scored-YYYY-MM-DD.jsonl (top 5 / 20 真评分)      ║      │
│   ╚══════════════════════════════════════════════════════════════╝      │
│                                                                          │
│   ╔══════════════════════════════════════════════════════════════╗      │
│   ║  ⏰ Phase 4 / 4: 🌱 LAND (落地)                             ║      │
│   ║                                                              ║      │
│   ║  🎯 目标: lark-cli records POST 真写飞书 Bitable 4 表       ║      │
│   ║                                                              ║      │
│   ║  📤 Weekly POST (Bitable 真闭环):                            ║      │
│   ║    • POST /open-apis/bitable/v1/apps/{BAPP_TOKEN}/         ║      │
│   ║      tables/{TABLE_ID_WEEKLY}/records                      ║      │
│   ║    • Payload: {                                              ║      │
│   ║        week_id: "2026-W28",                                 ║      │
│   ║        period: <ms>,                                        ║      │
│   ║        theme: "自进化智能体",                              ║      │
│   ║        fetch_count: 5,                                      ║      │
│   ║        top_paper_score: 4.7,                                ║      │
│   ║        digest_status: "published"                          ║      │
│   ║      }                                                     ║      │
│   ║    • Response: ok: true, record_id: recvoEl1S5WfHo          ║      │
│   ║                                                              ║      │
│   ║  📊 本次运行产出 (Run Report):                               ║      │
│   ║    🎯 Top 5 真表 (composite 4.1-4.7 全 ✅ 可引)            ║      │
│   ║    🏆 Top 1 paper + 🔗 URL                                  ║      │
│   ║    📌 字段提炼 (慎引/不引/可引统计)                          ║      │
│   ║    📤 本周写到 Bitable 的 record_id                          ║      │
│   ║    ✅ digest-publish 跑完                                    ║      │
│   ║                                                              ║      │
│   ╚══════════════════════════════════════════════════════════════╝      │
└──────────────────────────────────────────────────────────────────────────┘
                                      ▼
                          您 30 sec 刷 Bitable 看 top records
```

## 4 阶段 banner 协议 (后续要加进 skill)

```bash
# Phase 1/4: LIFE (生活)
╔══════════════════════════════════════════════════════╗
║  ⏰ Phase 1 / 4: 🌱 LIFE (生活)                       ║
║  🎯 触发: launchd 08:00 / manual / weekly            ║
║  📥 输入: env + mode (daily/weekly/verify)           ║
║  ⚙ 准备: set -a; . ../.env                          ║
╚══════════════════════════════════════════════════════╝

# 阶段结束 ✅/⚠️/❌
✅ Phase 1 完成: env 全设 (6 ✅ + 1 ⚠️ keychain OK)

# Phase 2/4: SEARCH (搜索) - **5 源全部列出 + N 工具全部列出 + 关键词全部列出**
╔══════════════════════════════════════════════════════╗
║  ⏰ Phase 2 / 4: 🔍 SEARCH (搜索)                     ║
║  📡 5 源 fan-out (全部):                              ║
║    1. arxiv    2. venue    3. blog-rss                ║
║    4. hn       5. github                              ║
║  🔧 N 工具并行 (王锐 N-tool protocol):                ║
║    1. MiniMax    2. anysearch    3. WebFetch         ║
║    4. exa        5. kimi-webbridge                  ║
║  🔍 关键词 (全部):                                    ║
║    • self-evolving agent    • AI scientist           ║
║    • LLM agent               • agentic system         ║
║    • reasoning                                       ║
╚══════════════════════════════════════════════════════╝

# 阶段结束 ✅/⚠️/❌
✅ Phase 2 完成: 5 源抓取 110 行 (1 源 ⚠️ HuggingFace 网络 404)

# Phase 3/4: THINK (思考)
╔══════════════════════════════════════════════════════╗
║  ⏰ Phase 3 / 4: 🧠 THINK (思考)                      ║
║  📊 7 维评分 (全部):                                  ║
║    🏛 venue / 👤 author / 💻 code / 📦 dataset /   ║
║    🔢 number / 📈 citation / 🎯 match                ║
║  📉 dedup: 3081 → 2160                               ║
╚══════════════════════════════════════════════════════╝

# 阶段结束
✅ Phase 3 完成: 10 真记录, top 5 全 4.1-4.7 ✅ 可引

# Phase 4/4: LAND (落地)
╔══════════════════════════════════════════════════════╗
║  ⏰ Phase 4 / 4: 🌱 LAND (落地)                       ║
║  📤 Weekly POST: record_id=recvoEl1S5WfHo            ║
║  📊 Run Report: top 5 + 真 record_id                  ║
╚══════════════════════════════════════════════════════╝

# 最终关闭
✅ ALL 4 PHASES COMPLETED — auto-feishu-digest v0.1.10 真闭环
```

## 跨 link (auto-feishu-digest skill)

```
       ┌─ auto-feishu-digest v0.1.10 (主)
       │
       ▼
   4 阶段生命体 (Life → Search → Think → Land)
       │
       ├─→ Phase 1: env (claudecode 主进程 read ~/.agents/skills/auto-feishu-digest/.env)
       ├─→ Phase 2: 5 源 × N 工具 (王锐 N-tool, N=5 当前)
       ├─→ Phase 3: 7 维评分 + dedup + 真 composite
       └─→ Phase 4: lark-cli records POST + 真 record_id 拿回
                       │
                       ▼
              真闭环: 您刷飞书 Bitable, 30 sec 看 top records
```
