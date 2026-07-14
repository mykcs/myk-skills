---
name: paper-into-notion
description: |
  URL → 自动填 3 字段 (页面 / 状态 / 模态类型) 到 Notion `论文` database. multi_select (教育类型/知识点/标签) + rich_text 亮点 **永不覆盖**已有值 (PATCH body 只含 select/title). 适用 arXiv / 公众号 / 博客 / Twitter / GitHub / bilibili / youtube / 小红书 / 知乎. 6 scripts + 4 templates + 2 references. weiying20260624 PhD 申请场景.
when_to_use: |
  Trigger when user says: "paper 进 Notion" / "论文入库" / "Notion 沉淀" / "写论文卡片" / "把这个 paper 加到 Notion" / "收藏这个 arXiv" / "收藏这个公众号" / "reading list 同步" / "沉淀 paper" / "把 URL 加到 Notion" / "把链接写到 Notion" / "把 paper 同步到 Notion" / "新 paper 提醒" / "我看了一篇 paper 想存下来" / "URL 写 Notion". Also: weekly-report-phd v0.7+ 跑周报时 paper card 联动. NOT: 查 Notion schema (用 Notion UI) / 批量导出 (用 Notion UI export) / 写 paper card 给老师 (用 teacher-report).
metadata:
  type: skill
  project_scope: cross-project
  skill_id: paper-into-notion
  version: v2.0 (2026-07-14)
  changelog: |
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
  起源: user 2026-07-13 原话 "paper 进 Notion" 触发, 2026-07-14 升级为 v2.0
  关联 ADR: ADR-0057
  关联 case: CASE-PAPER-INTO-NOTION-SKILL-V1-20260713 + CASE-PAPER-INTO-NOTION-V2-20260714
  关联 skill: weekly-report-phd (ntn CLI) / teacher-report (paper card) / auto-feishu-digest (3 scripts 风格)
  适用 owner: mykcs (per ADR-0054 Notion 严格层 + 4 重保险)
---

# paper-into-notion v1.0

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
| 2 | 状态 | select | ✅ 固定 "未开始" | 单值安全 |
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