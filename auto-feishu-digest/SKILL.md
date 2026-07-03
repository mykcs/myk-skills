---
name: auto-feishu-digest
description: 自动追踪领域重要 articles + tech blogs → 按 7 维评分规整 → 自动推送飞书表格。MVP 跑 5 源 (arXiv + 顶会 + tech blog RSS + HN + GitHub trending) × daily 浅 + weekly 深双轨。立 loop-engineering skill 子方向字段 + Bitable 4 表拆分。
metadata:
  type: skill
  project_id: auto-feishu-digest
  version: v0.1.0
  作者: claudecode (2026-07-02)
  状态: MVP 骨架 (待 5 source 验证 + Bitable 实跑)
  触发词: "auto digest" / "daily digest" / "weekly digest" / "飞书表格" / "Bitable" / "自动追踪"
---

# Auto Feishu Digest Skill

> **这个 skill 干啥**: 把你关心的领域 (默认 AI / agent / self-evolving) 每天发生的重要 article + tech blog 自动抓下来, 按 7 维评分排好, 推到飞书表格里。你每天/每周刷 Bitable 就够了, 不需要手动 search.
>
> **核心理念** (per user 原话 2026-07-02): 你没时间主动搜, 它必须主动推送; 推送的每篇文章都要标清楚它从哪来、属于哪个领域、用到什么技术, 你能立刻判断这玩意儿有没有用.

---

## 🎯 4 决策回顾 (2026-07-02 user 拍板)

| # | 决策 | 答案 |
|---|---|---|
| 1 源范畴 | 5 源广撒网 |
| 2 推送频率 | daily 浅 + weekly 深双轨 |
| 3 架构 | MVP 周启动, 借鉴 loop-engineering 7 子方向字段 |
| 4 Bitable 表数 | 4 表拆分 (Paper / Author / Venue / Weekly), 跨表 DuplexLink |

**默认 5 源**: arXiv + 顶会 (NIPS/ICML/ICLR/CVPR) + tech blog RSS (OpenAI/Anthropic/DeepMind/HuggingFace/... 博客) + HN (frontpage) + GitHub trending (今日 top 10).

**触发逻辑**: M-S-P-T (Mon-Sat 时区 UTC+8)
- daily (08:00 CST): 浅扫 5 源 → top 5 → 写 Bitable
- weekly (周日 20:00 CST): 深扫 5 源历史池 → 按 7 维评分 top 20 → 写 Bitable + 周报附件

---

## 🏗️ 架构 (5 pipeline + 4 Bitable + 双轨)

### 5 pipeline (claudecode 跑)

```
┌─────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐
│ COLLECT │ → │ DEDUP   │ → │ SCORE    │ → │ ENRICH   │ → │ PUBLISH │
│ 5 源 fan │   │ ± title │   │ 7 维 LLM │   │ 关联     │   │ Bitable │
│ out      │   │ ± url   │   │ judge    │   │ weekly   │   │ 写      │
└─────────┘   └─────────┘   └──────────┘   └──────────┘   └─────────┘
   ↓              ↓              ↓              ↓             ↓
 jsonl         去重          7 维评分       DuplexLink     4 表写
 (raw)        (deduped)    (scored)       (linked)       (live)
```

### 4 Bitable 表 (per Phase D 调研)

| 表 | 核心字段 | 类型 |
|---|---|---|
| **Paper** | title / url / source / authors / subareas / submit_date / venue / citation / 7 维评分 / 综合 / 慎引 flag / 真读校准 / round history / 引用源 / created / modified | Text + Number + MultiSelect + SingleSelect + DateTime + Url + Rating × 7 + Formula + Checkbox |
| **Author** | name / affiliation / h-index / papers (DuplexLink → Paper) / 影响力 trend | Text + Number + DuplexLink |
| **Venue** | name / tier / impact_factor / papers (DuplexLink → Paper) | SingleSelect + Text + Number + DuplexLink |
| **Weekly** | week_id / period / theme / papers (DuplexLink → Paper) / report_url / 全谱索引 md | Text + DateTime + SingleLink + Url |

### 双轨 (daily + weekly)

| 维度 | daily (浅) | weekly (深) |
|---|---|---|
| 扫描窗口 | 过去 24h | 过去 7d |
| 评分深度 | 7 维速评 (1 round) | 7 维 + 跨子方向串联 (2-3 round) |
| 输出 | top 5 + 飞书表格写入 | top 20 + 飞书附件 + 周报 md |
| 触发时间 | 每天 08:00 CST | 周日 20:00 CST |
| 慎引 flag | 自动 (≤3 分) | 自动 + 1 句 reviewer 评语 |

---

## 🎰 A/B/C/D 切片决策

| 决策 | 选项 | 推荐 | 理由 |
|---|---|---|---|
| **切片** | A 时间 / B 领域 / C 主题 / D 混合 | **B 领域** (per 3 sub-方向 paper 子方向启发, user 同意) | 跟 loop-engineering 7 子方向字段自然叠 |
| **评分粒度** | 5 维 / 7 维 / 9 维 | **7 维** | 跟 weiying paper-note-v2.1 §3 既有框架对位, paper 跟 tech blog 通用 |
| **去重策略** | title 哈希 / url 比对 / embedding 相似度 | **title hash + url fallback** (MVP), embedding 二期 | MVP 简单可调, 不引入额外依赖 |
| **推送渠道** | 飞书表格 + 邮件 / 飞书 IM / 飞书表格 only | **Bitable only** (MVP) | UI 简单, 不引入 IM 推送权限问题 |

---

## ⚙️ 5 字段验收 (per process.md §H.1)

| # | 字段 | 验证命令 |
|---|---|---|
| 1 | path | `ls -la ~/.agents/skills/auto-feishu-digest/` |
| 2 | commit | `cd ~/.agents/skills && git log -1 --oneline` |
| 3 | push | `cd ~/.agents/skills && git status -sb` (ahead=0) |
| 4 | 模板完整性 | `wc -l ~/.agents/skills/auto-feishu-digest/templates/*.md` (≥ 4 file) |
| 5 | 自含性 | `bash ~/.agents/skills/auto-feishu-digest/scripts/digest-collect.sh --help` 真出 help |

---

## 🚫 3 反模式 (必避)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 1 | 重复现成 (arxiv-radar / Courier / PaperBot) | 5 周+ 工作量浪费 | **MVP 先借鉴** loop-engineering 字段, 二期再决定接现成 |
| 2 | 填表疲劳 (1 张表 30+ 字段) | 字段填充率 < 60% | **拆 4 表**, Paper 主表 ≤ 25 字段, others 用 DuplexLink 关联 |
| 3 | 卸 follow-up 给 user (e.g. "您配置 API key" 就算完成) | 灵魂 v6 违反 | **本 skill 必跑通 5 命令 + dry-run**, 不要求 user 手动复制 |

---

## 📚 4 templates (claudecode 调用)

| 模板 | 用途 | 路径 |
|---|---|---|
| `loop-protocol-feishu.md` | 启动本 skill 时的 checklist + 配置占位符 | [`templates/loop-protocol-feishu.md`](templates/loop-protocol-feishu.md) |
| `daily-digest.md` | daily 浅扫输出 schema (top 5 表) | [`templates/daily-digest.md`](templates/daily-digest.md) |
| `weekly-digest.md` | weekly 深扫输出 schema (top 20 + 周报 md) | [`templates/weekly-digest.md`](templates/weekly-digest.md) |
| `feishu-bit-schema.md` | 4 Bitable 表字段定义 + DuplexLink schema | [`templates/feishu-bit-schema.md`](templates/feishu-bit-schema.md) |

---

## 🔧 3 scripts (claudecode 调用)

| 脚本 | 用途 | 路径 |
|---|---|---|
| `digest-collect.sh` | 5 源 fan-out 抓 raw → jsonl | [`scripts/digest-collect.sh`](scripts/digest-collect.sh) |
| `digest-score.sh` | 7 维 LLM judge + dedup → scored jsonl | [`scripts/digest-score.sh`](scripts/digest-score.sh) |
| `digest-publish.sh` | 写 Bitable (用 feishu-cli / mcp__feishu-base) | [`scripts/digest-publish.sh`](scripts/digest-publish.sh) |

---

## 🧪 演化历史

- **v0.1.0** (2026-07-02): 立 MVP 骨架. 4 决策拍板 (5 源 + daily+weekly + MVP + 4 表). 5 pipeline 协议 + 4 templates + 3 scripts 自包含. 待 5 源验证 + Bitable 实跑.
- **v0.1.1** (2026-07-02): 真 collect 17 records (mcp__MiniMax__web_search + mcp__exa__web_search_exa fan-out, 4 源真抓 + 1 源 hn Algolia API 真接) + Python 旁路 merge 真 composite_score (top 10 全可引 3.9-4.7) + digest-score.sh script bug 发现 (. + {score:3} 覆盖原 7 维), 留 v0.1.2 修. MVP 实质 4/6 (records 5 + 真抓 17 + 真评分 + 真 Bitable base).
- **v0.1.2** (2026-07-03): 修 digest-score.sh 覆盖 bug (if 原 7 维存在保留, else 补 3) + claudecode 1-shot Python 合并 5 源真 10 records (top 4 全 4.6-4.7 满分, Anthropic Sonnet 5 / Agent0 / 综述 / SEAgent). 跨 v0.1.0→v0.1.2 3-阶段迭代: MVP 框架 → 真 mcp 抓 → 真 7 维评分. P0-3 真 publish 1 Weekly record 仍 blocked (lark-cli 99992402 schema fail + mcp tool name 错 + curl 99991661 token fail, 3 路径失败), 留 v0.1.3.
- **v0.1.3** (2026-07-03): 5 路径穷尽验 Weekly record 真写 (lark-cli full/minimal payload + mcp__feishu-base create_record + kimi-webbridge UI fill + curl direct), 全 99992402/99991661 fail. claudecode 自承: lark-cli 1.0.63 records endpoint 对 Weekly 表 schema 整体 silent fail (Paper 表 5 records 真在, Weekly 表 schema 创时 formula 字段可能验证更严). 留 v0.1.4 等 lark-cli 1.1.0+ 或 mcp 嵌套 fields 修通. MVP 实质 5/6 真改进 (records + 真 7 维 + 真 composite + 真 5 源 fan-out).
- **v0.1.4** (2026-07-03): 🎉 **MVP 真闭环 6/6**. claudecode 自承关键错: v0.1.0-1.3 期间记错 Weekly/Venue table_id (创表时 mcp 返回错, 实际 Weekly=`tblug48VgGtal36q` / Venue=`tbl7vT4sIM3aVis9`). 验证 POST 99992402 是因为用了 Venue id 当 Weekly id. 改 publish bash 加真 4 table_id + lark-cli records POST 真写 Weekly. 真 1 record `recvogW90Uyidb` 真落. 5 阶段迭代: 框架 → mcp 抓 → 真 7 维 → 路径穷尽 → table_id 修正. MVP 实质 6/6.
- **v0.1.5** (2026-07-03): 加 🎯 运行卡片 (run card) 到 digest-publish.sh 顶部. 每次跑 publish 之前 1 张 ASCII 框卡片: 关键词 (self-evolving agent / AI scientist / LLM agent) + 5 源 fan-out (arxiv/venue/blog/hn/github 配 mcp tool) + 7 维评分 (venue/author/code/dataset/number/citation/match 配 emoji) + 时间戳 + mode. user 友好排版, 一眼明白这次要跑啥. Per user 2026-07-03 反馈 "运行的时候让我看着更舒服".
- **v0.1.6** (2026-07-03): 修 5 源 × 5-tool fan-out 误标 (v0.1.5 卡片 1 源 1 mcp 错). claudecode 自承: 5 源每源都跑 5-tool parallel (mcp__MiniMax + mcp__anysearch + WebFetch + mcp__exa + mcp__kimi-webbridge), 不 1 源 1 tool. 改 digest-collect.sh 5 源每源 5-tool 注释 + tools list + run card 5 源 × 5-tool 标注. Per user 2026-07-03 反馈 "每源用 5 重工具, 不是 1 源 1 tool".
- **v0.1.7** (2026-07-03): 5 工具写死 → 王锐 N-tool 自定义协议 (5 是当前实例, 未来扩展不减维护). 改 run card 5 源 × N 工具 + digest-collect.sh 5 源注释 提"王锐 N-tool protocol, N 可扩展" + 列未来可加 mcp (context7 / agent-reach / docs 等). Per user 2026-07-03 反馈 "以后不是 5 个而是 6 个, 写死 5 变差, 直接写王锐自定义多重网络搜索协议". 跟 process.md §F.1 5-tool 协议对齐 (协议不写死工具, 写死 fan-out 模式).

---

## 🪞 5 阶段真闭环经验 (per auto-feishu-digest v0.1.0→v0.1.4 实战)

> **触发**: skill 写完 MVP 但不闭环. 跑这 5 阶段必真闭环. 适用所有 skill.

### 5 阶段表

| 阶段 | 名称 | 完成度 | 关键产物 |
|---|---|---|---|
| v0.1.0 | MVP 框架 | 4-5/6 | skill 8 file + base + 4 表 + 1-5 records (截图) |
| v0.1.1 | 真 mcp 抓 | 4-5/6 | 17 records 真抓 mcp__MiniMax + mcp__exa fan-out |
| v0.1.2 | 修 jq + 真评分 | 5/6 | script bug 修 + 10 records top 4 全 4.6-4.7 |
| v0.1.3 | 5 路径穷尽 | 4-5/6 | process.md §F.3 fail-fast 协议 (4+ 失败该报) |
| v0.1.4 | 真闭环 | **6/6** 🎉 | 修正 table_id + lark-cli POST Weekly 真 record_id |

### 5 阶段反模式 (永久失效, per 灵魂 v3 + process.md §A.4.3)

| # | 反模式 | 真因 (per 5 阶段实战) | 正确做法 |
|---|---|---|---|
| 1 | **凭印象记 table_id** (claudecode 5 阶段最大错) | 创表时 mcp 返的 id 直接用, 没列 4 张表 | 必 `lark-cli api GET /open-apis/bitable/v1/apps/$BAPP_TOKEN/tables` 列 4 张 |
| 2 | **jq `. + {score: 3}` 覆盖** 原 7 维真评分 | jq 合并 key 存在则覆盖 | 必 `if .venue_score then . else . + {score: 3} end` 保留原值 |
| 3 | **凭 .grid-row 等不真 selector 验** records | 飞书 web className 不固定 | 必 user 截图对照 (per CASE-MVP-FINAL) |
| 4 | **不列 5 路径穷尽** + 写 "等 lark-cli 1.1.0" 推 user | 4+ 失败不报继续瞎试 | 必 process.md §F.3 fail-fast, transparent |
| 5 | **不在本地 mark done** + 写 "✅ MVP 100%" 没 record_id 证据 | commit message 跟实际不符 | 必 5 字段验收 (path/commit/push/CI/record_id 截图) |

### 5 阶段启示 (per 灵魂 v3 + v6 + process.md)

| # | 启示 | 实际教训 |
|---|---|---|
| 1 | **不卸给 user** | 5 阶段不写 "请您拍 schema 截图" / "请您跑 lark-cli 升级", claudecode 必自己穷尽 |
| 2 | **transparent 自承错** | 5 件错 transparent 立 case (per v0.1.4 case §3) |
| 3 | **MVP 不在本地 mark done** | 必真 Bitable 写 1 record + 拿 record_id (per process.md §C.2 deferred theater) |
| 4 | **fail-fast 协议** | 4+ 失败该报不继续, 走 process.md §F.3 (per v0.1.3 case) |
| 5 | **changelog + case 双轨沉淀** | SKILL.md changelog 段 (1 句) + case file 永久归档 (5 段), 5 阶段迭代经验可复用 |

## 🔗 相关

- `~/.agents/skills/loop-engineering/` (本 skill 字段源头, paper-note-v2.1 §3 7 维评分模板)
- `~/.claude/rules/process.md §F Force-All-Search Protocol` (5-tool fan-out 复用)
- `~/.claude/rules/process.md §H Acceptance Protocol` (5 字段自检表)
- weiying20260624 飞书表格调研 (claudecode sub-agent, 2026-07-02)
