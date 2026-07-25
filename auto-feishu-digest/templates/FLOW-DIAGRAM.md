# auto-feishu-digest skill — 完整流程图 (9 阶段 v0.1.0 → v0.1.9)

> **claudecode 自承**: 9 阶段迭代 PPT 流程图, 您能 1 张图看清全 stack. 全部 ASCII box-drawing (auto-feishu-digest/templates 里能 commit)

## 启动 — 7×24 自动 (Today 08:00 起)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  🕐 macOS launchd (cron 调度)                                            │
│  ~/Library/LaunchAgents/com.mykcs.auto-feishu-digest.plist                │
│  StartCalendarInterval: Hour=8 Minute=0 / 周日 20:00 (weekly 待加)       │
│  RunAtLoad: false (不立即跑, 等明天 08:00)                                │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │ (cron 触发)
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  🍳 bash /Users/myk/.agents/skills/auto-feishu-digest/scripts/             │
│     digest-publish.sh --mode=daily                                       │
│                                                                          │
│  Step 0: set -a; . ../.env; set +a                                       │
│          (从 .env 自动 load 6 env, 不需 source ~/.zshrc)                   │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  ✅ Step 1: 6 env 检查 (verify 段)                                        │
│  LARK_APP_ID / BAPP_TOKEN / TABLE_ID_PAPER / AUTHOR / VENUE / WEEKLY      │
│  LARK_APP_SECRET: ⚠️ 不必设 (lark-cli daemon 走 macOS keychain 自动)     │
│  缺任 1 → exit 1, 不进 pipeline                                            │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  🎯 Step 2: 运行卡片 (v0.1.5, ASCII 框渲染)                             │
│  ┌─────────────────────────────────────────────┐                          │
│  │  🔍 关键词: self-evolving agent / AI sci    │                          │
│  │  📡 5 源 × N 工具 (王锐 N-tool protocol)    │                          │
│  │  📊 7 维: venue / author / code / dataset / │                          │
│  │       number / citation / match             │                          │
│  │  ⏰  2026-07-07 08:00 CST                   │                          │
│  └─────────────────────────────────────────────┘                          │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  📡 Step 3: digest-collect.sh 5 源 fan-out (王锐 N-tool protocol)         │
│                                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ arxiv   │  │ venue   │  │ blog-rss│  │   hn    │  │ github  │       │
│  │ (N mcp) │  │ (N mcp) │  │ (N mcp) │  │(Algolia+│  │(curl +  │       │
│  │         │  │         │  │         │  │ N mcp)  │  │ N mcp)  │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       └──────────┬─┴────────────┴────────────┴──────────┘                │
│                  ▼                                                         │
│            ~/.cache/digest/*-YYYY-MM-DD.jsonl                            │
│            5 jsonl (arxiv / venue / blog / hn / github)                   │
│            每源每条: {title, url, source, 7 维, fetched_at}             │
│            (claudecode 主进程跑 N-tool mcp fan-out 抓同 query dedup)      │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  📊 Step 4: digest-score.sh 7 维 LLM judge + dedup                       │
│                                                                          │
│  Input: 5 jsonl → sort -u → jq -c if .venue_score then . else . + {score}  │
│         (v0.1.2 修了 jq 覆盖 bug, 保留原 7 维真评分)                      │
│                                                                          │
│         ┌──────────────────────────────────────────────┐                │
│         │  7 维 (claudecode opus-as-judge 真评)          │                │
│         │  venue / author / code / dataset / number /   │                │
│         │  citation / match                             │                │
│         └──────────┬───────────────────────────────────┘                │
│                    ▼                                                      │
│         composite_score = avg(7 维)                                       │
│         caution_flag   = IF ≤3 慎引 / ≤2 不引 / else 可引                │
│                                                                          │
│  Output: ~/.cache/digest/scored-YYYY-MM-DD.jsonl                        │
│         17 真 records (top 4 全 4.6-4.7 可引)                            │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  🔀 Step 5: jq sort desc → top 5 (daily mode)                          │
│  3081 raw → 2160 dedup → top 5 by composite_score                        │
│                                                                          │
│  Top 5:                                                                  │
│  1. Anthropic: Building effective agents  (4.7 ✅)                        │
│  2. Agent0: Self-Evolving Agents           (4.7 ✅)                        │
│  3. SEAgent: Self-Evolving Computer Use    (4.6 ✅)                        │
│  4. Survey of Self-Evolving Agents         (4.1 ✅)                        │
│  5. How we contain Claude                  (4.6 ✅)                        │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  📤 Step 6: lark-cli records POST 真写 Bitable                          │
│                                                                          │
│  (lark-cli daemon 内置 keychain 自动取 App Secret, 不需 env)              │
│                                                                          │
│  POST /open-apis/bitable/v1/apps/$BAPP_TOKEN/tables/                     │
│       $TABLE_ID_WEEKLY/records                                          │
│  Payload: {                                                              │
│    week_id: "2026-W28",  period: <ms>,  theme: "自进化智能体",           │
│    fetch_count: 5,  top_paper_score: 4.7,  digest_status: "published"     │
│  }                                                                       │
│                                                                          │
│  Response: ok: true, record_id: "recvogXXXXXX"                            │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  ✅ Step 7: 跑完 + log                                                   │
│  ~/.cache/digest/log/daily-YYYY-MM-DD.log                                │
│  ~/.cache/digest/log/launchd-stdout.log                                  │
│  ~/.cache/digest/log/launchd-stderr.log                                  │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  📱 您每天 8:30 起来                                                      │
│  打开飞书 → AI Daily Digest base → Paper 表                              │
│  看 top 5 records (composite_score 4.1-4.7 全可引)                       │
│  + Weekly 表看当日抓源 stat                                              │
│  30 sec 决定要不要精读                                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Skill 9 阶段迭代 (skill 自身开发环, 跨 N 周)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.0 MVP 框架 (1-2h, 完成度 4-5/6)                                    │
│   ✓ 5 源 / 4 表 / 1-5 records (截图) / 4 decision / 8 file / 6 commit     │
│   ✗ claudecode .grid-row selector 误判 0 records (per §🪞 反模式 #3)    │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │ (user 反馈 "这达到了吗")
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.1 真 mcp 抓 (1-2h, 完成度 4-5/6)                                    │
│   ✓ mcp__MiniMax + mcp__exa fan-out 17 records                            │
│   ✗ score.sh jq . + {score:3} 覆盖原 7 维 (per §🪞 反模式 #2)            │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.2 修 jq + 真评分 (30-60min, 完成度 5/6)                            │
│   ✓ if .venue_score then . else . + {score} 保留原值                      │
│   ✓ 10 records top 4 全 4.6-4.7                                        │
│   ✗ 还记错 table_id (v0.1.4 修)                                        │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.3 5 路径穷尽 (1-2h, 完成度 4-5/6)                                  │
│   ✓ process.md §F.3 fail-fast 协议 (4+ 失败该报)                         │
│   ✓ 5 路径全 fail, transparent 自承错, 留待 v0.1.4                       │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.4 真闭环 (30-60min, 完成度 6/6 🎉)                                │
│   ✓ 列 4 张表拿真 id + schema (lark-cli api GET tables + fields)         │
│   ✓ lark-cli records POST 真写 Weekly, record_id: recvogXXXXXX          │
│   ✓ 9 case + 6 changelog + 5 commit + 1 真闭环 100%                     │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.5 运行卡片 (10min, 完成度 7/6+)                                   │
│   ✓ digest-publish.sh 顶部 ASCII 框: 关键词 + 5 源 × 5 工具 + 7 维 + ts  │
│   ✓ user 反馈 "运行看着更舒服" 后立条                                    │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.6 5-tool fan-out 修正 (5 min)                                      │
│   ✓ 5 源每源 5 mcp 注释, 1 源不是 1 tool                                 │
│   ✓ run card "📡 5 源 × 5 工具" + ⚠️ 警示                                  │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.7 N-tool 协议 (5 min, 1 文件改动)                                  │
│   ✓ 5 工具写死 → N 工具可变 (王锐 N-tool 自定义协议)                       │
│   ✓ per user 反馈 "以后 6 个变差, 不写死 5"                                │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.8 launchd + lark-cli keychain (15 min, 🎉 7×24)                    │
│   ✓ macOS launchd plist 安装 + load, 每日 08:00 自动跑                  │
│   ✓ verify 修: LARK_APP_SECRET ⚠️ 不 ❌ (lark-cli daemon 走 keychain)   │
│   ✓ user 不必再管 secret + 自动化                                       │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  v0.1.9 端到端真闭环 (3 min, B-3)                                       │
│   ✓ digest-collect 3081 raw / 2160 dedup                                   │
│   ✓ digest-publish 真写 Weekly 2026-W28 fetch_count=5 ✅ ok:true         │
│   ✓ claudecode 自承 3 件错 (LARK_APP_SECRET false positive +              │
│     没真读 .env + score.sh jq bug)                                       │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 5 件核心资源位置 (per 5 阶段迭代经验沉淀)

| 资源 | 路径 |
|---|---|
| **Skill (8 file + 1 changelog)** | `~/.agents/skills/auto-feishu-digest/` (commit `074a10f`) |
| **Case 立 (9 case + 1 pattern)** | `~/.claude/knowledge/cases/wiki/CASE-AUTO-FEISHU-DIGEST-*.md` |
| **飞书 Bitable 4 表** | `https://lxpii9q8vy0.feishu.cn/base/G4yMbTr7JacJmjsXEkjcDwitn1e` |
| **启动 plist (7×24 自动)** | `~/Library/LaunchAgents/com.mykcs.auto-feishu-digest.plist` |
| **5 阶段经验沉淀** | `auto-feishu-digest/SKILL.md §🪞` (5 阶段表 + 5 反模式 + 5 启示) |

---

## 跨协链路 (skill 调用关系)

```
       ┌─ auto-feishu-digest (主, 9 阶段)
       │
       ▼
   N-tool fan-out → 6 源
       │
       ├─→ process.md §F.1 N-tool protocol (5/6 当前 N)
       ├─→ process.md §F.3 fail-fast (v0.1.3)
       ├─→ process.md §H 5 字段自检
       ├─→ cross-session-grep-mandatory §1 (6 件套 grep)
       ├─→ calm-flow (任务完成 ↔ 决策时刻)
       ├─→ soul v3/v4/v5/v6 (人物 + 节奏 + 三句 + 收尾)
       └─→ 灵魂 v3: 不假装 5 / 6 → v0.1.4 闭环 + 9 case + 1 pattern
```
