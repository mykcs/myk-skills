---
name: paper-into-notion
description: |
  URL → 自动填 3 字段 (页面 / 状态 / 模态类型) 到 Notion `论文` database. multi_select (教育类型/知识点/标签) + rich_text 亮点 **永不覆盖**已有值 (PATCH body 只含 select/title). 适用 arXiv / 公众号 / 博客 / Twitter / GitHub / bilibili / youtube / 小红书 / 知乎. 11 scripts + 6 templates + 6 references. weiying20260624 PhD 申请场景.
when_to_use: |
  Trigger when user says: "paper 进 Notion" / "论文入库" / "Notion 沉淀" / "写论文卡片" / "把这个 paper 加到 Notion" / "收藏这个 arXiv" / "收藏这个公众号" / "reading list 同步" / "沉淀 paper" / "把 URL 加到 Notion" / "把链接写到 Notion" / "把 paper 同步到 Notion" / "新 paper 提醒" / "我看了一篇 paper 想存下来" / "URL 写 Notion" / "跨 db 搬 schema" / "跨 db 同步" / "跨 db 搬运行记录" / "Notion URL 解读" / "Notion schema 变更" / "Notion cross-db 搬" / "Notion property 改名" / "Notion multi-db schema" / "skill 跑完自我总结" / "任务后总结" / "skill 经验教训内化" / "skill 自我升级" / "**skill 子句 grep 修复**" / "**skill 字面 drift 修复**" / "**skill ask window 守卫**" / "**用户 ADHD 节奏 + ask window**". Also: weekly-report-phd v0.7+ 跑周报时 paper card 联动 / Notion schema 变更 走 add-property.sh 独立入口 / Notion 修 bug 看 notion-fix-cheatsheet.md 4 决路径 / skill 跑完必跑 skill-self-summary.sh 4 段总结 + mem0 quota fallback 3 步 (per user 2026-07-14 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结，提升 skill") / v-bump 自动触发 (4 条件: 反模式 ≥ 4 / 流程变化 ≥ 1 / 触发词变化 ≥ 1, 任一满足立 v_new_version per v2.6.30 §I self-evolution) / **spawn subagent 验证前必 git pull + ff main** (避免 subagent 看到 stale main, per v2.2 + v2.4 累积第 2 次) / **3 dirty file 走 v-bump 闭环** (subagent 跑测试改 env var 触发 file dirty, 不删, 走 self-evolution 闭环 5 步) / **Step 0 ask window 守卫** (skill-self-summary.sh 7 keyword "顺手/直接跑/快做/拍板/帮我做/judge yourself/给我答案" 命中必 unset + AskUserQuestion 选项化决定, per v2.9 + CASE-CLAUDECODE-ADHD-RHYTHM-BYPASS-20260714). NOT: 查 Notion schema (用 Notion UI) / 批量导出 (用 Notion UI export) / 写 paper card 给老师 (用 teacher-report).
metadata:
  type: skill
  project_scope: cross-project
  skill_id: paper-into-notion
  version: v2.9-i (2026-07-14)
  changelog: |
    v2.9-i (2026-07-14) — ask window 守卫 (灵魂 v4/v6 + feedback-adhd-rhythm-ask-window-not-bypass + CASE-CLAUDECODE-ADHD-RHYTHM-BYPASS-20260714): scripts/skill-self-summary.sh 加 Step 0 守卫 (env ASW_PROMPTED_BY_USER 含 "顺手/直接跑/快做/拍板/帮我做/judge yourself/给我答案" 7 keyword 任一命中 → exit 1, 引导 unset + AskUserQuestion 选项化决定) + references/self-evolution-loop.md §0 立条 (ask window 4 条件判定: 跨仓/不可逆/user keyword 命中/Tier 1+2 白名单外, 任一满足走 ask window) + SKILL.md 反模式 #34 (顺手 X 自决跑) / #35 (X 幂等 ≠ user 已拍板) / #36 (v-bump 闭环漏 Step 0) (33 → 36) + 触发词 + 2 (skill ask window 守卫 / 用户 ADHD 节奏). 闭环 4 步 → 5 步 (Step 0 + 总结 + 内化 + commit + bump). 跟 v2.4/v2.5/v2.6/v2.7/v2.8/v2.9 协同不冲突. (sub-slot per ADR-0057-i, 跟 main v2.9 schema drift 区分)
    v2.8 (2026-07-14) — db schema 漂移检查 + 9 字段自检表 (含 link url + 机构 multi_select) + 2 反模式 (per《无矩阵乘法LLM》page 39dfedee-...afd8-e51e622da580 体检触发): SKILL.md §7 字段表 8 → 9 字段 (label property db 不存在) + db schema 实测表 (9 字段校对) + 反模式 #32 (schema 拍板跟 db 对不上) + #33 (亮点 url 跟 link 重复) + 跟 v2.7 mmx 三件套 + v2.5 multi-db 4 env 协同不冲突
    v2.7 (2026-07-14) — mmx v1.0.16 真子命令 + status 中文错乱 + .env 真值同步 (per TTHE paper 跑出来 '(需 mmx 翻译: ...)' 占位触发, user 反馈 '亮点直接写明, 不能这样'): 4 个 judge 脚本 (highlights / knowledge / education / notes-tldr) 修 mmx v1.0.16 真用法 = `mmx text chat --non-interactive --output json --message "<prompt>"` + python json 解析提取 text content (不是 `mmx chat` 也不是 `--quiet`, per `mmx --help`: text resource → chat subcommand) + paper-into-notion.sh:182 --force-fill 硬编码 "页面" → ${NOTION_TITLE_PROPERTY:-页面} env (跨 db 兼容) + .env + .env.example 双侧 status 真值同步 "初抓取" (db 实际 options, 旧 "初抓取-ai" 是合字错值, 跟 wiki 默认 "未开始" 不同) + v-bump 触发走 self-evolution 闭环 v2.4 ADR-0057-f + triggers 词 + 2 (skill 子句 grep 修复 / skill 字面 drift 修复, per CASE-PAPER-INTO-NOTION-V2-7-MMX-SUBCOMMAND-20260714). 跟 v2.5/v2.6 协同不冲突.
    v2.6 (2026-07-14) — subagent FAIL 反馈增量 + 字面 drift 跨 skill 协议位 (per user 2026-07-14 立 v2.5 之后增量): 加触发词 + 2 (skill 子句 grep 修复 / skill 字面 drift 修复) + 4 反模式表补 3 条 (28 → 31, 加 #25/26/27: spawn subagent 验证前不 pull main / 字面 drift 跨 skill 协议位 / self-evolution 闭环漏 subagent FAIL 反馈) + 新增 'subagent FAIL 反馈 + 修复' 段 + ADR-0057-h v2.6 + CASE-V2-6-SUBAGENT-FAIL-FEEDBACK-20260714. 跟 v2.5 (user multi-db schema 4 env) 协同不冲突.
    v2.5 (2026-07-14) — 多 db schema 适配 (4 env variables + 2 db property 差异表): field-merge.sh 3 处硬编码 页面 → $TITLE_PROP env + verify-5-fields.sh 1 处 → $TITLE_PROP env + status 默认 未开始 → $STATUS_DEFAULT env + .env.example 加 4 个 NOTION_*_PROPERTY/NOTION_STATUS_DEFAULT env + 新增 "多 db schema 适配" 段 (4 env table + 论文 wiki vs 信息 property 差异表) + 触发词 + 1 (Notion multi-db schema) + 4 反模式表补 4 条 (24 → 28) (per CASE-PAPER-INTO-NOTION-MULTI-DB-SCHEMA-20260714 + Notion 2025-09-03 → 2026-03-11 multi-source database 升级)
    v2.4 (2026-07-14) — 经验教训 → 提升 skill 闭环 + skill-self-summary 3 健壮性: 升级 scripts/skill-self-summary.sh v1.0 → v2.0 (session id 3 步 fallback / CLAUDE.local.md hot recall 段带 @v{version} / v-bump 自动触发 4 条件判定) + 新增 references/self-evolution-loop.md (4 步闭环: 总结 → 内化 → commit → bump version) + 触发词 + 2 + 4 反模式表补 5 条 (19 → 24)
    v2.3 (2026-07-14) — skill 跑完自我总结协议 + mem0 quota fallback: 新增 scripts/skill-self-summary.sh (跑完自动 4 段 + mem0 fallback 3 步) + references/self-summary-protocol.md (4 段模板 + fallback 决策树 + decision-stream schema) + 触发词 + 2 + 4 反模式表补 3 条 (16 → 19) + CLAUDE.local.md §19 段 hot recall
    v2.2 (2026-07-14) — Notion URL 解读 + 修哪一部分 4 决路径 + 6 残留踩坑沉淀: 新增 references/notion-url-parse.md (URL 4 类 + id 提取 + 4 决路径 + integration access 3 步判定) + templates/notion-fix-cheatsheet.md (4 类常见问题 + 1 跳决策树 + 4 决路径 quickref) + templates/cross-db-migrate-payload.md 加 §0 Notion URL 解读段 + 触发词 + 4 + 4 反模式表补 6 条 (10 → 16) + subagent 验证协议位
    v2.1 (2026-07-14) — 跨 Notion database 搬 schema 4 踩坑沉淀: 新增 scripts/add-property.sh (PATCH /v1/data_sources/{id} 加 property 独立可用) + templates/cross-db-migrate-payload.md (跨 db strip id 规则) + references/notion-schema-migration.md (Notion 2025 API model 速查 + 4 错误码) + 触发词 + 3 + 4 反模式表独立段
    v2.0 (2026-07-14) — description split-in-two + 触发词扩 15+ + 6 字段 → 8 字段 schema 文档 + frontmatter audit 4 字段全过
    v1.8 (2026-07-13) — 亮点 --highlight user override (claudecode 翻译)
    v1.7 (2026-07-13) — --knowledge user override + 状态 status type 修
    v1.6 (2026-07-13) — 亮点 3 层 fallback (mmx 主 + 翻译次 + 中文占位兜底)
    v1.5 (2026-07-13) — 修教育类型 PR 误判
    v1.4 (2026-07-13) — --force-fill + schema 8 字段对齐
    v1.3 (2026-07-13) — notes-tldr + highlights + arxiv backoff
    v1.2 (2026-07-13) — education-type-judge + 新 page 才填教育类型
    v1.1 (2026-07-13) — knowledge-tag-judge + 新 page 才填知识点
    v1.0 (2026-07-13) — 立 (per ADR-0057, 5 pattern 模态 + multi_select 字段级 merge)
  起源: user 2026-07-13 原话 "paper 进 Notion" 触发, 2026-07-14 升级 v2.0 (frontmatter 升级) → v2.1 (跨 db 搬 schema 4 踩坑) → v2.2 (Notion URL 解读 + 修哪一部分 4 决路径 + 6 残留踩坑) → v2.3 (skill 跑完自我总结 + mem0 quota fallback) → v2.4 (经验教训 → 提升 skill 闭环 + 3 健壮性 + v-bump 自动触发, per user 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结，提升 skill")
  关联 ADR: ADR-0057 (v1.0) / ADR-0057-b (v2.0) / ADR-0057-c (v2.1) / ADR-0057-d (v2.2) / ADR-0057-e (v2.3) / ADR-0057-f (v2.4) / ADR-0057-g (v2.5, user multi-db schema 4 env) / ADR-0057-h (v2.6) / ADR-0057-i (v2.7, mmx subcommand + status 真值同步, per TTHE paper user 反馈) / ADR-0026 (curl verify 必读 body) / ADR-0054 (Notion 严格层)
  关联 case: CASE-PAPER-INTO-NOTION-SKILL-V1-20260713 + CASE-PAPER-INTO-NOTION-V2-UPGRADE-20260714 + CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714 + CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714 + CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714 + CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714 + CASE-PAPER-INTO-NOTION-V2-4-SELF-EVOLUTION-20260714 + CASE-PAPER-INTO-NOTION-MULTI-DB-SCHEMA-20260714 (user v2.5) + CASE-PAPER-INTO-NOTION-V2-6-SUBAGENT-FAIL-FEEDBACK-20260714 + **CASE-PAPER-INTO-NOTION-V2-7-MMX-SUBCOMMAND-20260714** (本次, mmx 真子命令 + status 真值 + TTHE paper 修)
  适用 owner: mykcs (per ADR-0054 Notion 严格层 + 4 重保险)
---

# paper-into-notion v2.6

> **核心承诺**: 任何 URL 进来 → 自动写 Notion database 论文 → multi_select 字段 (教育类型/标签/知识点) 永不覆盖已有值 ✅
> **触发**: user 说 "paper 进 Notion" / "Notion 沉淀" / "把这个 paper 加到 Notion" / "写论文卡片" 时跑

---

## 何时用

| 触发场景 | 跑这个 skill |
|---|---|
| user 给 arXiv URL 要写 Notion | ✅ |
| user 给微信公众号 / 知乎 / 小红书 / bilibili / YouTube URL | ✅ |
| user 给技术博客 URL (medium / 官方 blog / GitHub README) | ✅ |
| user 说"加 paper 进 Notion" / "沉淀这个 paper" | ✅ |
| user 一次给多个 URL (≤ 5) | ✅ (循环跑主入口) |
| user 要跑 weekly-report-phd 周报 + paper card 写 Notion | ✅ (跟 weekly-report-phd §C.3 联动) |
| user 要查 Notion database schema / 改字段定义 | ❌ (手工到 Notion UI) |
| user 要批量导出 paper (反向操作) | ❌ (用 Notion UI export) |
| 写 paper card 给老师 (feishu docx) | ❌ (用 teacher-report) |

---

## 9 字段自检表 (核心铁律: multi_select 不覆盖, v2.7 修 v1.4 误写 8 字段为 9 字段)

> **v2.7 修正** (per CASE-PAPER-INTO-NOTION-V2-7-SCHEMA-DRIFT-20260714): v1.4 拍板 8 字段是错值, db 实测 9 字段 (含 `link` url + `机构` multi_select). page `39dfedee-...afd8-e51e622da580`《无矩阵乘法LLM》体检时 0 link + 0 模态类型发现, 修 SKILL.md schema 漂移.

| # | 字段 | 类型 | 自动填? | 保护机制 |
|---|---|---|---|---|
| 1 | 名称 | title | ✅ (抓 `<title>` / arXiv title) | 直接 PATCH 覆盖安全 (title 是单值). v2.5 起走 `$NOTION_TITLE_PROPERTY` env (论文 wiki 兼容老 db "页面" / 信息 db "名称") |
| 2 | 状态 | **status** | ✅ 默认 "初抓取" (per .env) | 单值安全。⚠️ status ≠ select: option 不能删,只能 UI Archive. PATCH 前必 GET data_source 拿真 options 比对 env 默认值 (per 反模式 #29) |
| 3 | 模态类型 | select | ✅ 5 pattern grep (arXiv / 微信公众号 / 博客 / Twitter / 其他) | 单值安全 |
| 4 | 教育类型 | **multi_select** | ❌ 后填 (新 page 才填) | **PATCH body 永远不含此字段** |
| 5 | 知识点 | **multi_select** | ❌ 后填 (新 page 才填) | **PATCH body 永远不含此字段** |
| 6 | 亮点 | rich_text | ❌ 后填 (新 page 才填) | **PATCH body 永远不含此字段** (你后填) |
| 7 | link | url | ✅ auto 填 source URL (per v1.4 字段级 merge) | 跟亮点分离 (老 v1.4 page 跟 url 写在亮点, v2.7 起 url 必填 link) |
| 8 | 机构 | **multi_select** | ❌ 后填 | **PATCH body 永远不含此字段** (新增 v2.7, db 实测有但 v1.4 schema 漏) |
| 9 | 日期 | created_time | ✅ auto (Notion set) | 永不传 (auto) |

**db schema 实测 (2026-07-14 GET data_source, per CASE-V2-7-SCHEMA-DRIFT)**:
- 名称 (title) / 状态 (status, 3 options) / 模态类型 (select, 5 options) / 教育类型 (multi_select, 1 option 论文阅读) / 知识点 (multi_select, 7 options) / 亮点 (rich_text) / link (url) / 机构 (multi_select, 2 options SZU+PolyU) / 日期 (created_time) = **9 字段**
- ❌ db 无 "标签" multi_select (v1.4 8 字段写错, 实际 db 没此 property)

**关键铁律** (per plan §核心铁律):
- multi_select 一旦传数组 = **完整新值覆盖** (Notion API 行为)
- 唯一安全方案 = **body 不传 multi_select 字段** → Notion 保持原值
- 新 page 没 multi_select 时 POST 只含 3 auto 字段 (页面/状态/模态类型)
- 已有 page 时 PATCH 只含 3 auto 字段 (含 title update) → multi_select / rich_text 保留

### status 字段 vs select 字段 (2026-07-14 补, per CASE-CROSS-DB-SCHEMA-MIGRATION §5)
- **API 差异**: select option 可 PATCH 加/删, status option **只能加不能删** (Notion API 限制, 2025-09 release 后仍如此)
- **UI 差异**: select option 可 Archive 隐藏, status option 在 database 视图 → 状态列下拉 → 3 点 Archive
- **batch page 改 status**: 先 PATCH schema 加新 option, 再 PATCH /v1/pages/{id} x N
- **残留旧 option 处理**: API 删不掉, 走 Notion UI 手动 Archive (browser 或 Claude in Chrome)

---

## 主入口用法 (5 行)

```bash
bash ~/.agents/skills/paper-into-notion/scripts/paper-into-notion.sh <URL>

# 例 1: arXiv
bash ~/.agents/skills/paper-into-notion/scripts/paper-into-notion.sh https://arxiv.org/abs/1706.03762

# 例 2: 微信公众号
bash ~/.agents/skills/paper-into-notion/scripts/paper-into-notion.sh "https://mp.weixin.qq.com/s/abc123"

# 例 3: 博客 (medium / 官方 blog)
bash ~/.agents/skills/paper-into-notion/scripts/paper-into-notion.sh "https://lilianweng.github.io/posts/2023-06-23-agent/"

# 期望输出:
# ✅ record_id: xxx-xxx-xxx
# ✅ page_url: https://www.notion.so/...
# ✅ 3 字段填对 (页面=Attention Is All You Need, 状态=未开始, 模态类型=arXiv)
```

### 子命令 flag (v2.6)

| Flag | 行为 | 用途 | 是否写 Notion |
|---|---|---|---|
| `<URL>` (默认) | 跑 4 步 + 写 Notion + verify-5-fields | 实际写 paper | ✅ 写 |
| `--verify` | 跑 9 步环境检查 | 部署前/装后 sanity check | ❌ 不写 |
| `--dry-run <URL>` | 跑 4 步 + 跳过 ntn api + 返 `DRY-RUN-PAGE-ID` | schema 验证 / 字段预览 | ❌ 不写 |
| `--force-fill <URL>` | 跑 4 步 + 覆盖已有 page 全 7 字段 | 已知 page 想重填 | ✅ 写 (慎用) |

**何时用 --dry-run**: ① 第一次给一个 db 跑, 验证 schema 适配 (per v2.5 multi-db) ② 改 SKILL.md 后想看 LLM judge 怎么判 ③ 给 user 预览会自动填什么字段. **永远不**用主入口 URL 形式做 schema 验证 — 会污染 Notion (per CASE-PAPER-INTO-NOTION-DRY-RUN-FLAG-20260714).

---

## 架构 (5 scripts + 4 templates + 2 references)

### 5 scripts

```
scripts/
├── paper-into-notion.sh        # 主入口: URL → 抓 → 写 → 返 record_id (含 --verify 子命令)
├── modal-detect.sh             # 5 pattern grep → 模态类型 (arxiv / 公众号 / 博客 / Twitter / 其他)
├── arxiv-fetch.sh              # curl + ElementTree + 重试 3 次 (等 3s) → title/authors/abstract
├── field-merge.sh              # GET 现有 properties → 字段级 merge 算法 (永远不写 multi_select)
├── check-notion-version.sh     # ntn doctor + Notion-Version: 2026-03-11 header 验证
└── verify-5-fields.sh          # §H.1 5 字段验收 + multi_select 保护 grader (跑后 GET 比对)
```

### 4 templates

```
templates/
├── paper-card.md               # 12 行 paper card (per teacher-report v0.13.6)
├── run-card.md                 # 启动卡片 (Phase 1-4 banner, 仿 auto-feishu-digest v0.2.2)
├── modal-detect.md             # 5 pattern 表 (URL → 模态)
└── flow-diagram.md             # ASCII 全流程图 (URL → 抓 → merge → POST/PATCH → GET)
```

### 2 references

```
references/
├── field-merge-algorithm.md    # 字段级 merge 算法详解 (GET 空形态 + PATCH 流程)
└── arxiv-fetch-protocol.md     # arXiv API + ElementTree 解析 + rate limit 1 req/3s
```

---

## 字段级 merge 算法 (核心 4 步, per Q2 严格模式)

```bash
# Step 1: GET 找 page (per Notion 0.18.1 OpenAPI 用 data source query, 旧 database query 已废)
RESULT=$(ntn api --method POST "/v1/data_sources/$DS_ID/query" \
  -H "Notion-Version: 2026-03-11" \
  -d "{\"filter\":{\"property\":\"页面\",\"title\":{\"equals\":\"$TITLE\"}}}")

# Step 2: 0 条 → POST 新 page, body 只含 3 auto 字段
if [ "$RESULT" = "[]" ]; then
  ntn api --method POST /v1/pages \
    -H "Notion-Version: 2026-03-11" \
    -d "{
      \"parent\": {\"type\": \"data_source_id\", \"data_source_id\": \"$DS_ID\"},
      \"properties\": {
        \"页面\": {\"title\": [{\"text\": {\"content\": \"$TITLE\"}}]},
        \"状态\": {\"select\": {\"name\": \"未开始\"}},
        \"模态类型\": {\"select\": {\"name\": \"$MODAL\"}}
      }
    }"
  # 新 page 没 multi_select, 无覆盖风险
fi

# Step 3: 1 条 → PATCH 3 auto 字段, body 永远不含 multi_select
if [ "$COUNT" = "1" ]; then
  PAGE_ID=$(echo "$RESULT" | jq -r '.[0].id')
  ntn api --method PATCH "/v1/pages/$PAGE_ID" \
    -H "Notion-Version: 2026-03-11" \
    -d "{
      \"properties\": {
        \"页面\": {\"title\": [{\"text\": {\"content\": \"$TITLE\"}}]},
        \"状态\": {\"select\": {\"name\": \"未开始\"}},
        \"模态类型\": {\"select\": {\"name\": \"$MODAL\"}}
      }
    }"
  # ⚠️ body 永远不包含: 教育类型 / 标签 / 知识点 (multi_select) + 亮点 (rich_text)
fi

# Step 4: 2+ 条 → exit 1 "duplicate title" (需 user 手动 dedup)
if [ "$COUNT" -ge "2" ]; then
  echo "❌ duplicate title: $TITLE (找到 $COUNT 条 page, 需 user 手动 dedup)" >&2
  exit 1
fi
```

**核心铁律** (per plan §核心铁律):
1. multi_select 空形态是 `[]`, 但 GET 返回的 `[]` 跟"未设置"不易区分 → 不要靠判空
2. PATCH 一旦传 multi_select 数组 = 字段的**新完整值** (覆盖)
3. 唯一安全方案 = **不传** → Notion 保持原值

---

## 5 pattern 模态判定 (per Q3 fallback "其他")

| Pattern | 模态类型 | URL 示例 |
|---|---|---|
| 1 | `arxiv` | `arxiv.org/abs/1706.03762` / `arxiv.org/pdf/1706.03762` |
| 2 | `微信公众号` | `mp.weixin.qq.com/s/...` |
| 3 | `博客` | `lilianweng.github.io/posts/...` / `medium.com/@...` / `*.blog.*` / `juejin.cn/post/...` / `zhuanlan.zhihu.com/p/...` |
| 4 | `Twitter` | `twitter.com/...` / `x.com/...` |
| 5 | `其他` | bilibili / youtube / 小红书 / github / 其他都 fallback 此项 (Notion schema 已含) |

**判定逻辑** (`scripts/modal-detect.sh`):
```bash
URL="$1"
case "$URL" in
  *arxiv.org*) echo "arXiv" ;;
  *mp.weixin.qq.com*) echo "微信公众号" ;;
  *twitter.com*|*x.com*) echo "Twitter" ;;
  *blog*|*medium.com*|*juejin.cn*|*zhuanlan.zhihu.com*|*github.io/posts*|*github.com/blog*) echo "博客" ;;
  *) echo "其他" ;;
esac
```

---

## arXiv 抓取 (重试 3 次 + exit 1, per Q4)

### Notion 2025-09-03 → 2026-03-11 multi-source database 升级背景

| 概念 | 2022-06-28 旧 | 2025-09-03+ 新 | paper-into-notion 现状 |
|---|---|---|---|
| **database** | 1 个 db = 1 个 schema | 1 个 db = N 个 data sources (容器) | 接受任一, 用 `GET /v1/databases/{id}` 反查 `data_sources[].id` |
| **data source** | 隐式 | 1 个 schema/table | DS_ID 必存, 用 `GET /v1/data_sources/{id}` 拿 schema |
| **URL segment** | 32-char db_id | 第 1 段 = database_id, 第 2 段 = view_id, data_source_id **不在 URL** | 必 introspect |
| **property schema** | per database | per data source (每个 ds 独立 property 名/类型) | introspect 模式待 v2.6, 当前 v2.5 env variable override |

**关键 URL 解读规则** (per CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714):
- 32-char UUID 不携带类型信息, 必跑 `ntn datasources resolve` 或 `GET /v1/databases/{id}` 反查
- `?v=` 后 32-char 是 **view_id**, 不是 data_source_id
- 用户 paste URL 时通常只 paste database_id, 没给 data_source_id

```bash
# scripts/arxiv-fetch.sh: curl + ElementTree + 重试 3 次 (等 3s)
# 输入: arXiv ID (e.g. 1706.03762)
# 输出: JSON {"title": "...", "authors": [...], "abstract": "..."}

ARXIV_ID="$1"
URL="https://export.arxiv.org/api/query?id_list=$ARXIV_ID&max_results=1"

for i in 1 2 3; do
  RESPONSE=$(curl -fsSLG "$URL" 2>&1) && break
  echo "retry $i failed, sleep 3s..." >&2
  sleep 3
done

# 3 次都失败 → exit 1 + 报错 + 不写 fallback record (per Q4)
if [ -z "$RESPONSE" ]; then
  echo "❌ arXiv 抓取失败 (3 次重试): $ARXIV_ID" >&2
  exit 1
fi

# ElementTree 解析 Atom XML
TITLE=$(echo "$RESPONSE" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'atom': 'http://www.w3.org/2005/Atom'}
root = ET.fromstring(sys.stdin.read())
entry = root.find('atom:entry', ns)
print(entry.find('atom:title', ns).text.strip())
")
```

---

## 6 反模式 (永久失效, per plan §5 + Q4 新增 #6)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 1 | **PATCH multi_select 覆盖已有** | Notion PATCH 数组 = 完整新值 | body **永远不含** 教育类型/标签/知识点 |
| 2 | **凭印象判模态类型** | URL pattern 没列全 | 5 pattern grep + fallback "其他" |
| 3 | **arXiv 抓失败不报** | rate limit / 网络 | exit 1 + 报错 + 不写 fallback record |
| 4 | **没 record_id 就算完成** | §C.2 deferred theater | 必须 ntn create 返 id + url |
| 5 | **跳过 verify agent** | 自检不可信 | spawn agent 跑 multi_select 保护 grader |
| 6 | **写 fallback 偷懒** (per Q4) | arXiv 失败留空 title 或写 fallback record | **重试 3 次 + 报错 + 不写 fallback** (per Q4 自修复) |

---

## 4 反模式 (跨 db 搬 schema 专属, v2.1 新增)

> 起源: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714, 4 真实踩坑

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 7 | **信任 docs "Notion API 不支持 add property"** (stale 知识) | 2025-09 API release 后 PATCH /v1/data_sources/{id} 加 property 实际支持 | **先试** PATCH, 失败再走 kimi-webbridge / UI |
| 8 | **跨 db 搬 multi_select / select / status option 复制 source id** | Notion 校验 `input id must = target existing id` | payload 永远 strip id 只留 `name` (per `templates/cross-db-migrate-payload.md` §2) |
| 9 | **PATCH data source `title` 想改 property name** | data source title ≠ property name, API 无 PATCH name endpoint | 接受 1 字段差异 / UI 改 property name |
| 10 | **workspace-level database 硬试 archive / delete** | Notion API 限制, 必 UI 操作 | 立即 AskUserQuestion 让 user UI 删, 不硬试 N 次 |

---

## 6 反模式 (Notion URL 解读 + 修哪一部分专属, v2.2 新增)

> 起源: CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714, 6 残留踩坑

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 11 | **把 Notion URL 当 1 类** (实际 4 类) | 32-char UUID 字符串本身不携带类型信息 | 必跑 `ntn datasources resolve` / `ntn pages get` 反查, 详见 `references/notion-url-parse.md` §1 |
| 12 | **`datasources query 200 = write access OK`** | read access 跟 write access 独立 | 3 步判定 (resolve + query + create test), 详见 `references/notion-url-parse.md` §4 |
| 13 | **`git worktree add` stdout "成功" = 真成功** | macOS bash 复合命令 + race condition, silent 失败 | 必跑 `git worktree list` 二次 verify + `ls <worktree>/<expected-dir>` 二次 verify |
| 14 | **kimi-webbridge 0 button 跟 Notion 2025** | Notion 2025 button 渲染为 `<div role=button>`, `querySelectorAll("button")` 返 0 | 改用 PATCH /v1/data_sources/{id} API 加 property (实测支持), 不走 UI 路径 |
| 15 | **测试 property 加到目标 db 不清理** | Notion API 没 delete property endpoint | 跑完测试必 UI 手动删, 不然污染目标 schema (1:1 搬失败) |
| 16 | **跨 db 搬 payload 字段名跟源 1:1** | Notion API 不支持 PATCH property name, 必有 1 字段差异 | 接受差异 (源「页面」→ 目标「名称」), 必 strip option id |

---

## 「修改哪一部分」4 决路径 (v2.2 新增, per user 原话)

> user v2.1 merge 后原话 "把这一路出现的问题经验教训都总结在 skill 里面，尤其是 notion 链接，怎么修改哪一部分"

**4 决路径表** (1 跳决策):

| 触发场景 | 修哪 | 工具 | endpoint |
|---|---|---|---|
| database 缺字段 / 类型不对 | **改 schema** (加 property / 改 type) | `scripts/add-property.sh` | PATCH /v1/data_sources/{id} |
| 单行 page 字段值错 | **改 page row** (cell value) | `scripts/paper-into-notion.sh` | PATCH /v1/pages/{id} |
| database 显示名错 | **改 database metadata** (title / icon) | ntn api | PATCH /v1/databases/{id} |
| page 内文字 / heading / list 错 | **改 page content** (block) | ntn pages edit | PATCH /v1/blocks/{id} |

**详细**: `references/notion-url-parse.md` §3 (4 决路径表 + 例子) / `templates/notion-fix-cheatsheet.md` §2 (1 跳决策树) / `templates/notion-fix-cheatsheet.md` §3 (4 决路径 quickref)

---

## 3 反模式 (skill 跑完自我总结 + mem0 quota fallback 专属, v2.3 新增)

> 起源: CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714 + CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714, per user 2026-07-14 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结"

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 17 | **skill 跑完 = 任务完成 (没自我总结)** | SKILL.md 没"跑完自我总结"协议位, §H.1 5 字段自检只验证 commit + push + CI, 缺"经验教训总结"类 | 必跑 `scripts/skill-self-summary.sh` (4 段: 做了什么 N / 修了什么 N / 踩坑 1-3 / 避坑 1-3) |
| 18 | **mem0 add_memory 撞墙无 fallback (浪费 17 天)** | mem0 收费计划 quota 10000/billing period 上限, 高频 add_memory 撞墙, 撞墙后**没有 fallback 协议位** | 3 步 fallback (本地 case + CLAUDE.local.md hot recall + decision-stream append), 不反问 user, 不重试 3+ 次 (per §C.3.6.1 no-stuck) |
| 19 | **总结落不落本地 (跨 session 失忆)** | 总结协议没指定"必须写文件路径", 默认 user 复制粘贴 = 卸给 user (违反 post-task-recommend §2 灵魂 v6) | 4 步必跑: ① chat 输出 + ② 写本地 case (per `~/.claude/knowledge/cases/wiki/`) + ③ CLAUDE.local.md hot recall + ④ decision-stream append |

---

## 「跑完自我总结协议」4 段模板 (v2.3 新增, per user 原话)

**触发条件** (满足任一就必跑):
- skill 升级 commit 后
- skill 跨 db 搬 / 跨 session 任务完成
- 任何 build + deploy + config 改动完成
- user 显式说 "总结" / "回顾" / "沉淀"

**4 段固定结构** (per post-task-recommend §2 硬规则 + 灵魂 v3/v6 自检):

```markdown
## 任务后建议

### 这次踩坑 (1-3 条)
- [踩坑现象] — 根因 / 当时为什么没识别
- 例: "改了 3 次才定位到 ADR-0027 v1.0 sub-slot 边界" — 根因: 没先 grep 现状

### 未来怎么避 (1-3 条)
- [可执行的避坑动作] — 为什么能避
- 例: "立新 ADR 前必跑 §3 现状 grep 6 件套" — per cross-session-grep-mandatory.md §1
```

**完整实现**: `scripts/skill-self-summary.sh` (4 步: chat + 本地 case + CLAUDE.local.md + decision-stream) + `references/self-summary-protocol.md` (4 段模板 + mem0 quota 决策树 + decision-stream schema + 案例)

**mem0 quota fallback** (per `references/self-summary-protocol.md` §2): 撞墙立即 3 步 fallback (本地 case + CLAUDE.local.md hot recall + decision-stream append), 不反问 user "要不要 add", 不重试 3+ 次

---

## 5 反模式 (skill 经验教训内化 + v-bump 自动触发专属, v2.4 新增)

> 起源: CASE-PAPER-INTO-NOTION-V2-4-SELF-EVOLUTION-20260714, per user 2026-07-14 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结，提升 skill"

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 20 | **session id 缺失走 unknown 字面** (实测) | `CLAUDE_SESSION_ID` env 未设, self-summary.sh 硬编码 fallback "unknown" | 3 步 fallback (env → `git rev-parse --short HEAD` → `date +%Y%m%d-%H%M%S`), 全缺失抛 exit 1 (per ADR-0057-f 残留 1) |
| 21 | **hot recall 段缺版本号 (多次跑同名段堆叠)** (实测) | 段标题只含 date + skill_name, 不含 skill version, 同日多次跑同名段堆叠, 难追溯 | 段标题含 `@v{version}`, e.g. `## §self-summary-2026-07-14-paper-into-notion@v2.4` (per ADR-0057-f 残留 2) |
| 22 | **v-bump 不自动 (经验教训不内化到 skill)** (实测) | self-summary.sh 缺 v-bump 自动触发逻辑, 只沉淀经验教训不内化到 SKILL.md changelog / 触发词 / 反模式 | 跑完自检 4 条件 (反模式 ≥ 4 / 流程变化 ≥ 1 / 触发词变化 ≥ 1), 任一满足触发立 v_new_version (per v2.6.30 §I self-evolution) |
| 23 | **总结不内化到 skill (跟 v2.6.30 §I self-evolution 反)** | 跑完 4 段总结只落本地 case + CLAUDE.local.md + decision-stream, 不更新 SKILL.md changelog / 触发词 / 反模式 | 4 步闭环 (总结 → 内化 → commit → bump version, per `references/self-evolution-loop.md` §1) |
| 24 | **跑完不验证 (subagent 跳过)** | 立协议不实测, 3 健壮性 (session id / 版本号 / v-bump) 实测才发现 | 立 skill 协议位必跑 1 轮实测 (per §C.1 verification gate), 实测失败立新 v-bump |

---

## 「经验教训 → 提升 skill」4 步闭环协议 (v2.4 新增, per user 原话 "提升 skill")

## 多 db schema 适配 (v2.5 新增, per user 2026-07-14 拍板 A 方案)

### --dry-run flag (v2.6 加成)

> **触发**: 任何 schema 验证 / 字段预览场景必跑 `--dry-run` 而不是主入口 URL 形式. 主入口会真写 Notion, 跟 verify 副作用污染.
> **行为**: 跑全 4 步 (模态 + arXiv + LLM judge + field-merge 算法), 但**不调 ntn api 写 Notion** + 跳过 verify-5-fields, 返 `DRY-RUN-PAGE-ID` 占位 + 输出 `[DRY-RUN] ⚠️ 不会真写 Notion` 提示.
> **修法起源 (CASE-PAPER-INTO-NOTION-DRY-RUN-FLAG-20260714)**: v2.5 我用 arXiv 1706.03762 (Transformer) 验证多 db schema adapter 是否生效, **实际真写了 1 条 paper 到 信息 db** — schema verify 副作用污染 Notion. 之后 trash + 立 P1 case + 立 --dry-run flag.

```bash
# 用法: 验证 schema 适配, 不污染 Notion
bash paper-into-notion.sh --dry-run "https://arxiv.org/abs/1706.03762"
# 期望输出: 4 步流程 + [DRY-RUN] 提示 + record_id=DRY-RUN-PAGE-ID + 跳过 verify-5-fields
```

> **触发**: user paste Notion URL, 目标 database 跟 skill 默认配置 (论文 wiki) 不同 (e.g. 信息 db property 叫 "名称" 不是 "页面", status 选项是 "初抓取-ai" 不是 "未开始")
> **v2.5 quick fix**: 4 env variables override 默认值, 兼容任一 Notion db
> **v2.6 follow-up**: introspect mode (auto-detect property name + status options, per Notion 2025-09-03+ 最佳实践)

### 4 env variables 表

| env | 默认 (论文 wiki) | 信息 db | 用途 |
|---|---|---|---|
| `NOTION_TITLE_PROPERTY` | `页面` | `名称` | 标题 property 名 |
| `NOTION_STATUS_DEFAULT` | `未开始` | `初抓取-ai` | 状态默认值 |
| `NOTION_LINK_PROPERTY` | `link` (可选) | `link` | 链接 property 名 (db 没此字段则跳过) |
| `NOTION_ORG_PROPERTY` | `机构` (可选) | `机构` | 机构 property 名 (db 没此字段则跳过) |

### 2 db property 差异表 (v2.5 实测)

| Property | 论文 wiki db | 信息 db |
|---|---|---|
| 标题 property 名 | `页面` | `名称` |
| 状态 property 名 | `状态` | `状态` (同) |
| 状态 options | `未开始` / `在读` / `已完成` | `初抓取-ai` / `ai补充` / `人类认证` |
| 模态类型 | `arXiv` / `微信公众号` / ... | 同 |
| 教育类型 | `论文阅读` | 同 |
| 知识点 | open | `llm` / `线性注意力` / `超声心动` (既有 tag) |
| 链接 | ❌ 无此字段 | ✅ `link` (url type) |
| 日期 | ❌ | ✅ `日期` (created_time auto) |
| 机构 | ❌ | ✅ `机构` (multi_select, SZU/PolyU) |

### 切换 db 操作 SOP

```bash
# 1. .env 改 4 env (paper-into-notion/.env)
NOTION_DATABASE_ID="<新 db id>"
NOTION_DATA_SOURCE_ID="<新 ds id>"  # GET /v1/databases/{db_id} 拿 data_sources[].id
NOTION_TITLE_PROPERTY="名称"
NOTION_STATUS_DEFAULT="初抓取-ai"

# 2. 跑 dry-run 验 (推荐先 --verify, 再跑一次实际 URL)
bash paper-into-notion.sh --verify
bash paper-into-notion.sh "https://arxiv.org/pdf/2607.08124"

# 3. bonus test: PATCH 已有 page 不覆盖 multi_select
# (脚本默认已含 multi_select 保护, 见 verify-5-fields.sh §4 字段级 merge)
```

### 3 反模式 (subagent FAIL 反馈 + 字面 drift 跨 skill 协议位, v2.6 新增)

> 起源: CASE-PAPER-INTO-NOTION-V2-6-SUBAGENT-FAIL-FEEDBACK-20260714, v2.4 subagent 验证 PARTIAL PASS 报 4 FAIL 修复 (跟 v2.2 字面 drift 同模式累积第 2 次)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 25 | **spawn subagent 验证前不 pull main (累积第 2 次)** | subagent 看到 stale main (v2.4 subagent 看到 v2.3 e760063, 看不到 v2.4 e2567d1), 报 false positive "commit 不存在" | spawn subagent 验证前必跑 `git pull + ff main`, 跟 v2.2 subagent 误判同模式 (累积第 2 次, 升级硬约束) |
| 26 | **字面 drift 跨 skill 协议位 (累积第 2 次)** | 注释跟实装字面不严格 (v2.4 self-summary.sh v-bump 注释写 "4 条件", 实装 "踩坑 ≥ 2 + 避坑 ≥ 1" 简化判定; v2.2 "integration access 3 步" → "integration share 3 步" 是同模式) | 写协议位注释必 grep 1 下实际代码, 注释跟实装字面必一致, 跨 skill 协议位必跑 sub-check 步骤 |
| 27 | **self-evolution 闭环漏"subagent FAIL 反馈" 1 步** | v2.4 立条时闭环 4 步 (总结 → 内化 → commit → bump version) 漏 1 步 "subagent FAIL 反馈修复", 3 dirty file 留在主仓等下次 commit | 5 步闭环 (总结 → 内化 → commit → bump version → **subagent FAIL 反馈修复**), v2.6 加最后 1 步 |

### 4 反模式 (永久失效, v2.5 新增)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 17 | **硬编码 property 名 "页面"** | 跨 db property 名不同 (页面 vs 名称) | 用 `$NOTION_TITLE_PROPERTY` env, 默认 "页面" 兼容老 db |
| 18 | **硬编码 status 默认 "未开始"** | 不同 db status options 不同 | 用 `$NOTION_STATUS_DEFAULT` env, 默认 "未开始" 兼容老 db |
| 19 | **Notion URL 反查失败就反复重试** | 32-char UUID 不携带类型信息, 重试无济于事 | 1 次 `GET /v1/databases/{id}` 拿 `data_sources[]` 即可, 失败用 kimi-webbridge |
| 20 | **多 db 切来切去但不复盘 schema 差异** | 每次切 db 都踩同一个 property 名不同的坑 | 立 CASE 沉淀 property 差异表 (如本段 §2) |

### 5 反模式 (永久失效, v2.7 新增 — mmx 子命令 + status 中文错乱 + judge fallback silent)

> 起源: CASE-PAPER-INTO-NOTION-V2-7-MMX-SUBCOMMAND-20260714 (TTHE paper《Test-Time Harness Evolution》arxiv 2607.08124 跑出'(需 mmx 翻译: ...)'占位 + 后续'初抓取-ai'也是错的, user 原话 '亮点直接写明, 不能这样')

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 28 | **mmx v1.0.16 子命令误写 `mmx chat`** | 跟 mmx 旧版本混淆 (mmx 0.x 用 `mmx chat "<prompt>"`); mmx 1.0.16 改 mmx `<resource> <command>` 模式, 真子命令 = `mmx text chat --message "<prompt>"` (per `mmx --help` Resources) | 凡引用 mmx CLI 子命令必跑 `mmx --help` 验证真名, **禁止凭印象写旧 `mmx chat` 兼容代码** |
| 29 | **status 中文错乱 (合字 "初抓取-ai") 跟 db 实际 3 选项 "初抓取/ai补充/人类认证" 不匹配** | .env + .env.example 默认值是 SKILL.md v1.4 拍板的 "未开始" (论文 wiki 老 db), .env 改 "初抓取-ai" 是 user 2026-07-14 v2.5 multi-db 适配但 db **没 "初抓取-ai" 选项** (合字错) | PATCH 任何 status 字段前必 `ntn api GET /v1/data_sources/{id}` 拿真实 options 比对, 不要凭 SKILL.md 拍板的默认值猜 db 选项 |
| 30 | **judge fallback 链隐藏真 bug 不暴露** | judge 脚本 (highlights/knowledge/education) 写 `mmx chat "..."` 失败 → fallback 关键词匹配 → 关键词命中 0 → 留 `(需 mmx 翻译: ...)` 中文占位 → 整条链路只 warn 一行, user 看 Notion page 才发现占位文本 | judge 脚本 fallback 链路必 1 段 stderr 输出 `⚠️ mmx CLI 调用失败: <stderr + exit code>`, 同步 4 fallback 触发段 (mmx 主 → mmx 翻译次 → 关键词次 → 中文占位兜底), 永不静默 silent 失败 |
| 31 | **--quiet + 没 --output json → mmx 走 TTY 流式纯文本, json.loads 失败** | `mmx text chat --quiet` 不带 `--output json` 时, TTY 路径走 plain text chat mode (`Hello! I'm here and ready...`), json.loads(plain text) 抛 → python pipe `or echo ""` 返空 → 看似 fallback silent 实际 mmx 是好的 | mmx text chat 在 bash 脚本里必 `--non-interactive --output json --message "<prompt>"` 三件套, **不要用 `--quiet`** (它走 TTY chat) |

### 6 反模式 (永久失效, v2.7 新增 — db schema 漂移)

> 起源: CASE-PAPER-INTO-NOTION-V2-7-SCHEMA-DRIFT-20260714 (page《无矩阵乘法LLM》`39dfedee-...afd8-e51e622da580` 体检发现 0 link + 0 模态类型 + db 无"标签" property, v1.4 拍板 8 字段是错值)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 32 | **SKILL.md schema 拍板跟 db 实际字段数对不上 (8 写错 9)** | v1.4 拍板 8 字段 (含"标签" multi_select), db 实测 9 字段 (含"机构" multi_select, 无"标签"); 文档跟 schema drift 后 user 决策 "全自动修" 时容易漏字段 | 任何 PATCH page 前必 `GET /v1/data_sources/{id}` 拿真 schema 跟 SKILL.md 校对, 漂移立 case + 改 SKILL.md |
| 33 | **亮点字段塞 url 跟 link url 字段重复** | 早期 page 手工创时, paper-into-notion.sh v1.4 还没自动写 link, user 只能把 url 塞进亮点 ("bilibili 视频 (2024-08-17 发布), URL: https://...") | PATCH 时 link url 跟 亮点拆开, link = URL, 亮点 = 1 句中文 takeaway. paper-into-notion.sh v1.4 改 mod-detect 输出 link 同时写 link + 亮点 |

### 3 反模式 (永久失效, v2.9 新增 — ask window 守卫, 灵魂 v6/v4 + feedback-adhd-rhythm-ask-window-not-bypass)

> 起源: CASE-CLAUDECODE-ADHD-RHYTHM-BYPASS-20260714 (claudecode 听到 user 说 "顺手 fetch --prune 跑一下" 直接跑不 ask, 违反灵魂 v4 + v6 + 灵魂 v3 主动铺 walk 但跳过询问) + feedback-adhd-rhythm-ask-window-not-bypass.md (立条)

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 34 | **user 说 "顺手 X / 直接跑 X / 快做 X" 自决跑 (本次返魂句)** | claudecode 把 "user 提议顺手" 误读为 "user 已拍板授权", 跳过 AskUserQuestion 直接跑; 跨仓动作 (push main / rm / reset / Notion API 写) 风险高, AD 不友好 | 必跑 AskUserQuestion (1-2 选项, A 跑 / B 等), 跑前先报 5 行 (动作 / 影响 / 验证). `scripts/skill-self-summary.sh` 加 Step 0 守卫 (env `ASW_PROMPTED_BY_USER` 含 keyword → exit 1) |
| 35 | **X 幂等 = 不需要 ask (错误前提)** | "git fetch --prune 幂等" != "user 已拍板", 幂等 ≠ 自决授权. 越权跑一次性副作用小, 但建立 "顺手 ≠ 拍板 = 跳过询问" 习惯后, 下次 X 不可逆 (`rm` / `--force push`) 会同样越权 | 副作用表求 = 0 (不触及 main / 远程 / 用户身份) 才能 "自决 + 事后告知"; 否则必跑 ask window (per §12 + §6 calm-flow 8 类必问) |
| 36 | **总结走 v-bump 闭环漏 ask window Step 0** | v2.4 4 步闭环 / v2.6 5 步闭环 没把 "user 用 keyword 提议" 当 1 步前置守卫; 结果 task 跑完剩 1 步自决残留, 跟 post-task-recommend §6 v3 清理 + 灵魂 v6 协议位 反 | 加 5 步闭环 Step 0 (ask window 4 条件判定), `references/self-evolution-loop.md` §0 立条, 字面跟 script Step 0 一致 (per 反模式 #26 字面 drift 协同) |

**触发条件** (满足任一就必跑):
- skill 升级 commit 后
- skill 跨 db 搬 / 跨 session 任务完成
- 任何 build + deploy + config 改动完成
- user 显式说 "总结" / "回顾" / "沉淀" / "提升 skill"

**4 步** (缺一不算 "提升 skill", 反 v2.6.30 §I self-evolution 协议位硬约束):

```text
1. 总结 (Summary)
   ↓ 跑 skill-self-summary.sh 4 段 (做了什么 N / 修了什么 N / 踩坑 1-3 / 避坑 1-3)
   ↓ 4 步 fallback: chat + 本地 case + CLAUDE.local.md (段带 @v{version}) + decision-stream
   ↓ mem0 quota 撞墙时, 3 步 fallback (本地 case + CLAUDE.local.md + decision-stream)
   ↓
2. 内化 (Internalize)
   ↓ 经验教训 → SKILL.md 5 类沉淀:
   ↓   - changelog 段 (新立 v_new_version entry)
   ↓   - 触发词 (扩 when_to_use 段)
   ↓   - 反模式 (扩 4 反模式表)
   ↓   - ADR (新立 sub-slot, per ADR-0027 v1.1)
   ↓   - case (新立 ~/.claude/knowledge/cases/wiki/CASE-*.md)
   ↓
3. Commit (Atomic)
   ↓ worktree 立新分支 (per §C.3.1, 必跑 verify 2 次: git worktree list + ls)
   ↓ atomic commit (5 file 单 commit, 1 unit 原则 per §C.3.2)
   ↓ commit message 含 changelog / 触发词 / 反模式 / 关联 ADR / 关联 case
   ↓
4. Bump version (v-bump)
   ↓ v2.x → v2.(x+1) bump (per v2.6.49 description split 触发条件)
   ↓ frontmatter 4 字段保留合规 (per v2.6.47 audit)
   ↓ changelog 段加 v_new_version entry
   ↓ 触发词 + N / 反模式 + N
   ↓ 5 步 (总结 → 内化 → commit → bump → push, per v2.6.30 §I.1)
```

**v-bump 自动触发 4 条件** (任一满足即触发, per `references/self-evolution-loop.md` §2):

| # | 条件 | 判定方法 | 触发 v-bump |
|---|------|---------|--------------|
| 1 | **反模式 ≥ 4** | 解析 SKILL.md 4 反模式表, 数条数 ≥ 4 | ✅ |
| 2 | **流程变化 ≥ 1** | git diff vs 上次 commit, 流程类代码 (scripts/ + run-card.md) 改 ≥ 1 文件 | ✅ |
| 3 | **触发词变化 ≥ 1** | 解析 frontmatter when_to_use, 跟上次 commit 字符串比对, diff ≥ 1 触发词 | ✅ |
| 4 | **hot recall 新增段** | CLAUDE.local.md 跑完 self-summary 后段数比跑前 +1 | ✅ |

**完整实现**: `scripts/skill-self-summary.sh` v2.0 (3 健壮性 + v-bump 触发判定) + `references/self-evolution-loop.md` (4 步闭环协议) + `references/self-summary-protocol.md` (4 段模板 + mem0 quota 决策树)

---

## 6 scripts 调用链

```
paper-into-notion.sh <URL>
  ├─→ modal-detect.sh <URL>          # 模态类型
  ├─→ arxiv-fetch.sh <ARXIV_ID>      # 仅 arXiv 抓 (其他模态用 URL 作 title)
  ├─→ check-notion-version.sh        # 跑前 ntn doctor + version header
  ├─→ field-merge.sh <TITLE> <MODAL> # 字段级 merge 算法
  │     ├─→ GET query data source
  │     ├─→ 0 条 → POST 3 字段
  │     ├─→ 1 条 → PATCH 3 字段 (不含 multi_select)
  │     └─→ 2+ 条 → exit 1 duplicate
  └─→ verify-5-fields.sh <PAGE_ID>   # 跑后 GET + multi_select 保护 grader
```

---

## §H.1 5 字段自检表 (run-end 必跑, per process.md §H.1)

| # | 字段 | 验证命令 | 期望 |
|---|---|---|---|
| 1 | path | `ls ~/.agents/skills/paper-into-notion/` | 1 SKILL + 1 .env.example + 1 USER-SETUP + 6 scripts + 4 templates + 2 references = 15 file |
| 2 | commit | `git -C ~/.agents/skills log -1 --oneline` | 新 commit (feat(skill): paper-into-notion v1.0) |
| 3 | push | `git -C ~/.agents/skills status -sb` | ahead=0 |
| 4 | CI | `gh api repos/mykcs/myk-skills/commits/HEAD/status` | green |
| 5 | record_id + multi_select 保护 | `ntn pages get $RECORD_ID` | 3 auto 字段填对 + multi_select 全空 (新建) 或保留 (更新) ✅ |

---

## 联动引用

- **Notion ntn CLI 用法**: `~/.agents/skills/weekly-report-phd/SKILL.md` (§C.3 5 字段自检 + Notion-Version header)
- **paper card 12 行格式**: `~/.agents/skills/teacher-report/SKILL.md` (v0.3.0 增强 h3 format)
- **3 scripts + .env 自含 + 4 阶段 banner 风格**: `~/.agents/skills/auto-feishu-digest/SKILL.md`
- **ntn 渲染坑**: `~/.claude/knowledge/cases/wiki/CASE-NOTION-NTN-MD-RENDER-FIX-20260708.md`
- **Notion ntn 协议位**: `~/.claude/docs/adr/0043-notion-ntn-md-render-protocol.md`
- **PR + Notion 严格层**: `~/.claude/docs/adr/0054-commit-pr-default-notion-feishu-strict.md`
- **§H.1 5 字段验收**: `~/.claude/rules/process.md §H.1`
- **worktree + PR**: `~/.claude/rules/process.md §C.3.1 + §C.3.2`
- **新 skill 跨 5 协议位**: `~/.claude/docs/adr/0057-paper-into-notion-skill.md` (本 skill 立条 ADR)

---

## 反模式 v3 灵魂自检 (per post-task-recommend §6)

- 任务完成时输出 ≤ 15 行
- 不写可推迟事项段 (per v3 清理, 2026-07-02)
- 关键证据直接 inline, 不卸给 user 复制粘贴