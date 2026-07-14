---
name: paper-into-notion
description: |
  URL → 自动填 3 字段 (页面 / 状态 / 模态类型) 到 Notion `论文` database. multi_select (教育类型/知识点/标签) + rich_text 亮点 **永不覆盖**已有值 (PATCH body 只含 select/title). 适用 arXiv / 公众号 / 博客 / Twitter / GitHub / bilibili / youtube / 小红书 / 知乎. 11 scripts + 6 templates + 6 references. weiying20260624 PhD 申请场景.
when_to_use: |
  Trigger when user says: "paper 进 Notion" / "论文入库" / "Notion 沉淀" / "写论文卡片" / "把这个 paper 加到 Notion" / "收藏这个 arXiv" / "收藏这个公众号" / "reading list 同步" / "沉淀 paper" / "把 URL 加到 Notion" / "把链接写到 Notion" / "把 paper 同步到 Notion" / "新 paper 提醒" / "我看了一篇 paper 想存下来" / "URL 写 Notion" / "跨 db 搬 schema" / "跨 db 同步" / "跨 db 搬运行记录" / "Notion URL 解读" / "Notion schema 变更" / "Notion cross-db 搬" / "Notion property 改名" / "skill 跑完自我总结" / "任务后总结" / "**skill 经验教训内化**" / "**skill 自我升级**". Also: weekly-report-phd v0.7+ 跑周报时 paper card 联动 / Notion schema 变更 走 add-property.sh 独立入口 / Notion 修 bug 看 notion-fix-cheatsheet.md 4 决路径 / **skill 跑完必跑 skill-self-summary.sh 4 段总结 + mem0 quota fallback 3 步** (per user 2026-07-14 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结，提升 skill") / **v-bump 自动触发** (4 条件: 反模式 ≥ 4 / 流程变化 ≥ 1 / 触发词变化 ≥ 1, 任一满足立 v_new_version per v2.6.30 §I self-evolution). NOT: 查 Notion schema (用 Notion UI) / 批量导出 (用 Notion UI export) / 写 paper card 给老师 (用 teacher-report).
metadata:
  type: skill
  project_scope: cross-project
  skill_id: paper-into-notion
  version: v2.4 (2026-07-14)
  changelog: |
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
  关联 ADR: ADR-0057 (v1.0) / ADR-0057-b (v2.0) / ADR-0057-c (v2.1) / ADR-0057-d (v2.2) / ADR-0057-e (v2.3) / ADR-0057-f (v2.4) / ADR-0026 (curl verify 必读 body) / ADR-0054 (Notion 严格层)
  关联 case: CASE-PAPER-INTO-NOTION-SKILL-V1-20260713 + CASE-PAPER-INTO-NOTION-V2-UPGRADE-20260714 + CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714 + CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714 + CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714 + CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714 + CASE-PAPER-INTO-NOTION-V2-4-SELF-EVOLUTION-20260714
  关联 skill: weekly-report-phd (ntn CLI) / teacher-report (paper card) / auto-feishu-digest (3 scripts 风格)
  适用 owner: mykcs (per ADR-0054 Notion 严格层 + 4 重保险)
---

# paper-into-notion v2.4

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

## 7 字段自检表 (核心铁律: multi_select 不覆盖)

| # | 字段 | 类型 | 自动填? | 保护机制 |
|---|---|---|---|---|
| 1 | 页面 | title | ✅ (抓 `<title>` / arXiv title) | 直接 PATCH 覆盖安全 (title 是单值) |
| 2 | 状态 | **status** | ✅ 固定 "未开始" | 单值安全。⚠️ status ≠ select: option 不能删,只能 UI Archive |
| 3 | 模态类型 | select | ✅ 5 pattern grep | 单值安全 |
| 4 | 教育类型 | **multi_select** | ❌ 后填 | **PATCH body 永远不含此字段** |
| 5 | 知识点 | **multi_select** | ❌ 后填 | **PATCH body 永远不含此字段** |
| 6 | 标签 | **multi_select** | ❌ 后填 | **PATCH body 永远不含此字段** |
| 7 | 亮点 | rich_text | ❌ 后填 | **PATCH body 永远不含此字段** (你后填) |

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