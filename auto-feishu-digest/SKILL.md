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

## 🔗 相关

- `~/.agents/skills/loop-engineering/` (本 skill 字段源头, paper-note-v2.1 §3 7 维评分模板)
- `~/.claude/rules/process.md §F Force-All-Search Protocol` (5-tool fan-out 复用)
- `~/.claude/rules/process.md §H Acceptance Protocol` (5 字段自检表)
- weiying20260624 飞书表格调研 (claudecode sub-agent, 2026-07-02)
