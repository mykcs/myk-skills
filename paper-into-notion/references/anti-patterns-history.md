## 6 反模式 (永久失效, per plan §5 + Q4 新增 #6)

| #   | 反模式                          | 真因                                      | 正确做法                                             |
| --- | ------------------------------- | ----------------------------------------- | ---------------------------------------------------- |
| 1   | **PATCH multi_select 覆盖已有** | Notion PATCH 数组 = 完整新值              | body **永远不含** 教育类型/标签/关键词               |
| 2   | **凭印象判模态类型**            | URL pattern 没列全                        | 5 pattern grep + fallback "其他"                     |
| 3   | **arXiv 抓失败不报**            | rate limit / 网络                         | exit 1 + 报错 + 不写 fallback record                 |
| 4   | **没 record_id 就算完成**       | §C.2 deferred theater                     | 必须 ntn create 返 id + url                          |
| 5   | **跳过 verify agent**           | 自检不可信                                | spawn agent 跑 multi_select 保护 grader              |
| 6   | **写 fallback 偷懒** (per Q4)   | arXiv 失败留空 title 或写 fallback record | **重试 3 次 + 报错 + 不写 fallback** (per Q4 自修复) |

---

## 4 反模式 (跨 db 搬 schema 专属, v2.1 新增)

> 起源: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714, 4 真实踩坑

| #   | 反模式                                                            | 真因                                                                    | 正确做法                                                                           |
| --- | ----------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 7   | **信任 docs "Notion API 不支持 add property"** (stale 知识)       | 2025-09 API release 后 PATCH /v1/data_sources/{id} 加 property 实际支持 | **先试** PATCH, 失败再走 kimi-webbridge / UI                                       |
| 8   | **跨 db 搬 multi_select / select / status option 复制 source id** | Notion 校验 `input id must = target existing id`                        | payload 永远 strip id 只留 `name` (per `templates/cross-db-migrate-payload.md` §2) |
| 9   | **PATCH data source `title` 想改 property name**                  | data source title ≠ property name, API 无 PATCH name endpoint           | 接受 1 字段差异 / UI 改 property name                                              |
| 10  | **workspace-level database 硬试 archive / delete**                | Notion API 限制, 必 UI 操作                                             | 立即 AskUserQuestion 让 user UI 删, 不硬试 N 次                                    |

---

## 6 反模式 (Notion URL 解读 + 修哪一部分专属, v2.2 新增)

> 起源: CASE-PAPER-INTO-NOTION-NOTION-URL-FIX-20260714, 6 残留踩坑

| #   | 反模式                                        | 真因                                                                             | 正确做法                                                                                        |
| --- | --------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 11  | **把 Notion URL 当 1 类** (实际 4 类)         | 32-char UUID 字符串本身不携带类型信息                                            | 必跑 `ntn datasources resolve` / `ntn pages get` 反查, 详见 `references/notion-url-parse.md` §1 |
| 12  | **`datasources query 200 = write access OK`** | read access 跟 write access 独立                                                 | 3 步判定 (resolve + query + create test), 详见 `references/notion-url-parse.md` §4              |
| 13  | **`git worktree add` stdout "成功" = 真成功** | macOS bash 复合命令 + race condition, silent 失败                                | 必跑 `git worktree list` 二次 verify + `ls <worktree>/<expected-dir>` 二次 verify               |
| 14  | **kimi-webbridge 0 button 跟 Notion 2025**    | Notion 2025 button 渲染为 `<div role=button>`, `querySelectorAll("button")` 返 0 | 改用 PATCH /v1/data_sources/{id} API 加 property (实测支持), 不走 UI 路径                       |
| 15  | **测试 property 加到目标 db 不清理**          | Notion API 没 delete property endpoint                                           | 跑完测试必 UI 手动删, 不然污染目标 schema (1:1 搬失败)                                          |
| 16  | **跨 db 搬 payload 字段名跟源 1:1**           | Notion API 不支持 PATCH property name, 必有 1 字段差异                           | 接受差异 (源「页面」→ 目标「名称」), 必 strip option id                                         |

---

## 「修改哪一部分」4 决路径 (v2.2 新增, per user 原话)

> user v2.1 merge 后原话 "把这一路出现的问题经验教训都总结在 skill 里面，尤其是 notion 链接，怎么修改哪一部分"

**4 决路径表** (1 跳决策):

| 触发场景                        | 修哪                                    | 工具                           | endpoint                    |
| ------------------------------- | --------------------------------------- | ------------------------------ | --------------------------- |
| database 缺字段 / 类型不对      | **改 schema** (加 property / 改 type)   | `scripts/add-property.sh`      | PATCH /v1/data_sources/{id} |
| 单行 page 字段值错              | **改 page row** (cell value)            | `scripts/paper-into-notion.sh` | PATCH /v1/pages/{id}        |
| database 显示名错               | **改 database metadata** (title / icon) | ntn api                        | PATCH /v1/databases/{id}    |
| page 内文字 / heading / list 错 | **改 page content** (block)             | ntn pages edit                 | PATCH /v1/blocks/{id}       |

**详细**: `references/notion-url-parse.md` §3 (4 决路径表 + 例子) / `templates/notion-fix-cheatsheet.md` §2 (1 跳决策树) / `templates/notion-fix-cheatsheet.md` §3 (4 决路径 quickref)

---

## 3 反模式 (skill 跑完自我总结 + mem0 quota fallback 专属, v2.3 新增)

> 起源: CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714 + CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714, per user 2026-07-14 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结"

| #   | 反模式                                           | 真因                                                                                                 | 正确做法                                                                                                                                |
| --- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 17  | **skill 跑完 = 任务完成 (没自我总结)**           | SKILL.md 没"跑完自我总结"协议位, §H.1 5 字段自检只验证 commit + push + CI, 缺"经验教训总结"类        | 必跑 `scripts/skill-self-summary.sh` (4 段: 做了什么 N / 修了什么 N / 踩坑 1-3 / 避坑 1-3)                                              |
| 18  | **mem0 add_memory 撞墙无 fallback (浪费 17 天)** | mem0 收费计划 quota 10000/billing period 上限, 高频 add_memory 撞墙, 撞墙后**没有 fallback 协议位**  | 3 步 fallback (本地 case + CLAUDE.local.md hot recall + decision-stream append), 不反问 user, 不重试 3+ 次 (per §C.3.6.1 no-stuck)      |
| 19  | **总结落不落本地 (跨 session 失忆)**             | 总结协议没指定"必须写文件路径", 默认 user 复制粘贴 = 卸给 user (违反 post-task-recommend §2 灵魂 v6) | 4 步必跑: ① chat 输出 + ② 写本地 case (per `~/.claude/knowledge/cases/wiki/`) + ③ CLAUDE.local.md hot recall + ④ decision-stream append |

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

| #   | 反模式                                                   | 真因                                                                                                        | 正确做法                                                                                                                   |
| --- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 20  | **session id 缺失走 unknown 字面** (实测)                | `CLAUDE_SESSION_ID` env 未设, self-summary.sh 硬编码 fallback "unknown"                                     | 3 步 fallback (env → `git rev-parse --short HEAD` → `date +%Y%m%d-%H%M%S`), 全缺失抛 exit 1 (per ADR-0057-f 残留 1)        |
| 21  | **hot recall 段缺版本号 (多次跑同名段堆叠)** (实测)      | 段标题只含 date + skill_name, 不含 skill version, 同日多次跑同名段堆叠, 难追溯                              | 段标题含 `@v{version}`, e.g. `## §self-summary-2026-07-14-paper-into-notion@v2.4` (per ADR-0057-f 残留 2)                  |
| 22  | **v-bump 不自动 (经验教训不内化到 skill)** (实测)        | self-summary.sh 缺 v-bump 自动触发逻辑, 只沉淀经验教训不内化到 SKILL.md changelog / 触发词 / 反模式         | 跑完自检 4 条件 (反模式 ≥ 4 / 流程变化 ≥ 1 / 触发词变化 ≥ 1), 任一满足触发立 v_new_version (per v2.6.30 §I self-evolution) |
| 23  | **总结不内化到 skill (跟 v2.6.30 §I self-evolution 反)** | 跑完 4 段总结只落本地 case + CLAUDE.local.md + decision-stream, 不更新 SKILL.md changelog / 触发词 / 反模式 | 4 步闭环 (总结 → 内化 → commit → bump version, per `references/self-evolution-loop.md` §1)                                 |
| 24  | **跑完不验证 (subagent 跳过)**                           | 立协议不实测, 3 健壮性 (session id / 版本号 / v-bump) 实测才发现                                            | 立 skill 协议位必跑 1 轮实测 (per §C.1 verification gate), 实测失败立新 v-bump                                             |

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

| #   | 条件                  | 判定方法                                                                 | 触发 v-bump |
| --- | --------------------- | ------------------------------------------------------------------------ | ----------- |
| 1   | **反模式 ≥ 4**        | 解析 SKILL.md 4 反模式表, 数条数 ≥ 4                                     | ✅          |
| 2   | **流程变化 ≥ 1**      | git diff vs 上次 commit, 流程类代码 (scripts/ + run-card.md) 改 ≥ 1 文件 | ✅          |
| 3   | **触发词变化 ≥ 1**    | 解析 frontmatter when_to_use, 跟上次 commit 字符串比对, diff ≥ 1 触发词  | ✅          |
| 4   | **hot recall 新增段** | CLAUDE.local.md 跑完 self-summary 后段数比跑前 +1                        | ✅          |

**完整实现**: `scripts/skill-self-summary.sh` v2.0 (3 健壮性 + v-bump 触发判定) + `references/self-evolution-loop.md` (4 步闭环协议) + `references/self-summary-protocol.md` (4 段模板 + mem0 quota 决策树)

---

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

| env                     | 默认 (论文 wiki) | 信息 db     | 用途                                 |
| ----------------------- | ---------------- | ----------- | ------------------------------------ |
| `NOTION_TITLE_PROPERTY` | `页面`           | `名称`      | 标题 property 名                     |
| `NOTION_STATUS_DEFAULT` | `未开始`         | `初抓取-ai` | 状态默认值                           |
| `NOTION_LINK_PROPERTY`  | `link` (可选)    | `link`      | 链接 property 名 (db 没此字段则跳过) |
| `NOTION_ORG_PROPERTY`   | `机构` (可选)    | `机构`      | 机构 property 名 (db 没此字段则跳过) |

### 2 db property 差异表 (v2.5 实测)

| Property         | 论文 wiki db                 | 信息 db                                      |
| ---------------- | ---------------------------- | -------------------------------------------- |
| 标题 property 名 | `页面`                       | `名称`                                       |
| 状态 property 名 | `状态`                       | `状态` (同)                                  |
| 状态 options     | `未开始` / `在读` / `已完成` | `初抓取-ai` / `ai补充` / `人类认证`          |
| 模态类型         | `arXiv` / `微信公众号` / ... | 同                                           |
| 教育类型         | `论文阅读`                   | 同                                           |
| 关键词           | open                         | `llm` / `线性注意力` / `超声心动` (既有 tag) |
| 链接             | ❌ 无此字段                  | ✅ `link` (url type)                         |
| 日期             | ❌                           | ✅ `日期` (created_time auto)                |
| 机构             | ❌                           | ✅ `机构` (multi_select, SZU/PolyU)          |

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

---

### 3 反模式 (subagent FAIL 反馈 + 字面 drift 跨 skill 协议位, v2.6 新增)

> 起源: CASE-PAPER-INTO-NOTION-V2-6-SUBAGENT-FAIL-FEEDBACK-20260714, v2.4 subagent 验证 PARTIAL PASS 报 4 FAIL 修复 (跟 v2.2 字面 drift 同模式累积第 2 次)

| #   | 反模式                                              | 真因                                                                                                                                                                        | 正确做法                                                                                              |
| --- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 25  | **spawn subagent 验证前不 pull main (累积第 2 次)** | subagent 看到 stale main (v2.4 subagent 看到 v2.3 e760063, 看不到 v2.4 e2567d1), 报 false positive "commit 不存在"                                                          | spawn subagent 验证前必跑 `git pull + ff main`, 跟 v2.2 subagent 误判同模式 (累积第 2 次, 升级硬约束) |
| 26  | **字面 drift 跨 skill 协议位 (累积第 2 次)**        | 注释跟实装字面不严格 (v2.4 self-summary.sh v-bump 注释写 "4 条件", 实装 "踩坑 ≥ 2 + 避坑 ≥ 1" 简化判定; v2.2 "integration access 3 步" → "integration share 3 步" 是同模式) | 写协议位注释必 grep 1 下实际代码, 注释跟实装字面必一致, 跨 skill 协议位必跑 sub-check 步骤            |
| 27  | **self-evolution 闭环漏"subagent FAIL 反馈" 1 步**  | v2.4 立条时闭环 4 步 (总结 → 内化 → commit → bump version) 漏 1 步 "subagent FAIL 反馈修复", 3 dirty file 留在主仓等下次 commit                                             | 5 步闭环 (总结 → 内化 → commit → bump version → **subagent FAIL 反馈修复**), v2.6 加最后 1 步         |

### 4 反模式 (永久失效, v2.5 新增)

| #   | 反模式                                 | 真因                                      | 正确做法                                                                      |
| --- | -------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------- |
| 17  | **硬编码 property 名 "页面"**          | 跨 db property 名不同 (页面 vs 名称)      | 用 `$NOTION_TITLE_PROPERTY` env, 默认 "页面" 兼容老 db                        |
| 18  | **硬编码 status 默认 "未开始"**        | 不同 db status options 不同               | 用 `$NOTION_STATUS_DEFAULT` env, 默认 "未开始" 兼容老 db                      |
| 19  | **Notion URL 反查失败就反复重试**      | 32-char UUID 不携带类型信息, 重试无济于事 | 1 次 `GET /v1/databases/{id}` 拿 `data_sources[]` 即可, 失败用 kimi-webbridge |
| 20  | **多 db 切来切去但不复盘 schema 差异** | 每次切 db 都踩同一个 property 名不同的坑  | 立 CASE 沉淀 property 差异表 (如本段 §2)                                      |

### 5 反模式 (永久失效, v2.7 新增 — mmx 子命令 + status 中文错乱 + judge fallback silent)

> 起源: CASE-PAPER-INTO-NOTION-V2-7-MMX-SUBCOMMAND-20260714 (TTHE paper《Test-Time Harness Evolution》arxiv 2607.08124 跑出'(需 mmx 翻译: ...)'占位 + 后续'初抓取-ai'也是错的, user 原话 '亮点直接写明, 不能这样')

| #   | 反模式                                                                                   | 真因                                                                                                                                                                                                                | 正确做法                                                                                                                                                                              |
| --- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 28  | **mmx v1.0.16 子命令误写 `mmx chat`**                                                    | 跟 mmx 旧版本混淆 (mmx 0.x 用 `mmx chat "<prompt>"`); mmx 1.0.16 改 mmx `<resource> <command>` 模式, 真子命令 = `mmx text chat --message "<prompt>"` (per `mmx --help` Resources)                                   | 凡引用 mmx CLI 子命令必跑 `mmx --help` 验证真名, **禁止凭印象写旧 `mmx chat` 兼容代码**                                                                                               |
| 29  | **status 中文错乱 (合字 "初抓取-ai") 跟 db 实际 3 选项 "初抓取/ai补充/人类认证" 不匹配** | .env + .env.example 默认值是 SKILL.md v1.4 拍板的 "未开始" (论文 wiki 老 db), .env 改 "初抓取-ai" 是 user 2026-07-14 v2.5 multi-db 适配但 db **没 "初抓取-ai" 选项** (合字错)                                       | PATCH 任何 status 字段前必 `ntn api GET /v1/data_sources/{id}` 拿真实 options 比对, 不要凭 SKILL.md 拍板的默认值猜 db 选项                                                            |
| 30  | **judge fallback 链隐藏真 bug 不暴露**                                                   | judge 脚本 (highlights/knowledge/education) 写 `mmx chat "..."` 失败 → fallback 关键词匹配 → 关键词命中 0 → 留 `(需 mmx 翻译: ...)` 中文占位 → 整条链路只 warn 一行, user 看 Notion page 才发现占位文本             | judge 脚本 fallback 链路必 1 段 stderr 输出 `⚠️ mmx CLI 调用失败: <stderr + exit code>`, 同步 4 fallback 触发段 (mmx 主 → mmx 翻译次 → 关键词次 → 中文占位兜底), 永不静默 silent 失败 |
| 31  | **--quiet + 没 --output json → mmx 走 TTY 流式纯文本, json.loads 失败**                  | `mmx text chat --quiet` 不带 `--output json` 时, TTY 路径走 plain text chat mode (`Hello! I'm here and ready...`), json.loads(plain text) 抛 → python pipe `or echo ""` 返空 → 看似 fallback silent 实际 mmx 是好的 | mmx text chat 在 bash 脚本里必 `--non-interactive --output json --message "<prompt>"` 三件套, **不要用 `--quiet`** (它走 TTY chat)                                                    |

### 6 反模式 (永久失效, v2.7 新增 — db schema 漂移)

> 起源: CASE-PAPER-INTO-NOTION-V2-7-SCHEMA-DRIFT-20260714 (page《无矩阵乘法LLM》`39dfedee-...afd8-e51e622da580` 体检发现 0 link + 0 模态类型 + db 无"标签" property, v1.4 拍板 8 字段是错值)

| #   | 反模式                                                      | 真因                                                                                                                                                                                       | 正确做法                                                                                                                                              |
| --- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 32  | **SKILL.md schema 拍板跟 db 实际字段数对不上 (8 写错 9)**   | v1.4 拍板 8 字段 (含"标签" multi_select), db 实测 9 字段 (含"机构" multi_select, 无"标签"); 文档跟 schema drift 后 user 决策 "全自动修" 时容易漏字段                                       | 任何 PATCH page 前必 `GET /v1/data_sources/{id}` 拿真 schema 跟 SKILL.md 校对, 漂移立 case + 改 SKILL.md                                              |
| 33  | **亮点字段塞 url 跟 link url 字段重复**                     | 早期 page 手工创时, paper-into-notion.sh v1.4 还没自动写 link, user 只能把 url 塞进亮点 ("bilibili 视频 (2024-08-17 发布), URL: https://...")                                              | PATCH 时 link url 跟 亮点拆开, link = URL, 亮点 = 1 句中文 takeaway. paper-into-notion.sh v1.4 改 mod-detect 输出 link 同时写 link + 亮点             |
| 34  | **僵尸 property 误填 (type=None, options=空 字段还往里写)** | v1.4 拍板的 "模态类型" select 实际 type=None, options=空 (db schema 留壳), 真实数据走新建的 "平台" 字段. 写字段 PATCH 时如果硬编码 "模态类型" → Notion API 返 200 但实际不存 (silent loss) | PATCH 前必 GET data_source 拿真 schema, 跳过 type=None 字段. 任何 property 引用必走 env (per v2.9 $NOTION_MODAL_PROPERTY=平台), 禁止硬编码 "模态类型" |

### 3 反模式 (永久失效, v2.9-i 新增 — ask window 守卫, 灵魂 v4/v6 + feedback-adhd-rhythm-ask-window-not-bypass)

> 起源: CASE-CLAUDECODE-ADHD-RHYTHM-BYPASS-20260714 (claudecode 听到 user 说 "顺手 fetch --prune 跑一下" 直接跑不 ask, 违反灵魂 v4 + v6 + 灵魂 v3 主动铺 walk 但跳过询问) + feedback-adhd-rhythm-ask-window-not-bypass.md (立条). 编号 #35-37 (避撞 v2.9 #34 僵尸 property).

| #   | 反模式                                                       | 真因                                                                                                                                                                       | 正确做法                                                                                                                                                                          |
| --- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 35  | **user 说 "顺手 X / 直接跑 X / 快做 X" 自决跑 (本次返魂句)** | claudecode 把 "user 提议顺手" 误读为 "user 已拍板授权", 跳过 AskUserQuestion 直接跑; 跨仓动作 (push main / rm / reset / Notion API 写) 风险高, AD 不友好                   | 必跑 AskUserQuestion (1-2 选项, A 跑 / B 等), 跑前先报 5 行 (动作 / 影响 / 验证). `scripts/skill-self-summary.sh` 加 Step 0 守卫 (env `ASW_PROMPTED_BY_USER` 含 keyword → exit 1) |
| 36  | **X 幂等 = 不需要 ask (错误前提)**                           | "git fetch --prune 幂等" != "user 已拍板", 幂等 ≠ 自决授权. 越权跑一次性副作用小, 但建立 "顺手 ≠ 拍板 = 跳过询问" 习惯后, 下次 X 不可逆 (`rm` / `--force push`) 会同样越权 | 副作用表求 = 0 (不触及 main / 远程 / 用户身份) 才能 "自决 + 事后告知"; 否则必跑 ask window (per §12 + §6 calm-flow 8 类必问)                                                      |
| 37  | **总结走 v-bump 闭环漏 ask window Step 0**                   | v2.4 4 步闭环 / v2.6 5 步闭环 没把 "user 用 keyword 提议" 当 1 步前置守卫; 结果 task 跑完剩 1 步自决残留, 跟 post-task-recommend §6 v3 清理 + 灵魂 v6 协议位 反            | 加 5 步闭环 Step 0 (ask window 4 条件判定), `references/self-evolution-loop.md` §0 立条, 字面跟 script Step 0 一致 (per 反模式 #26 字面 drift 协同)                               |

### 5 反模式 (永久失效, v3.x-v4.5 新增 — introspect cache + 字面 drift + modal-detect 镜像)

> 起源: CASE-PAPER-INTO-NOTION-MODAL-PROP-DRIFT-20260714 + CASE-PAPER-INTO-NOTION-PAPERS-COOL-MIRROR-20260717 + PR #51 retro + ADR-0057-o. 编号 #42+ 避撞前面.

| #   | 反模式                                                                                                                                               | 真因                                                                                                                                                                                                                                                                                                                                                         | 正确做法                                                                                                                                                                                                                                                                                                            |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 42  | **multi_select "改为 N 项" 默认臆断合成还是拆分**                                                                                                    | user 说 "关键词改为 X 进阶技巧" 时, "X 进阶技巧" 可能是 1 个合成项也可能是《X》《进阶技巧》2 个拆分项 (TTHE page 2 轮才澄清); claudecode 默认按字面写 1 项 = 猜错语义 = 返工                                                                                                                                                                                 | multi_select "改为 N 项" 先 `AskUserQuestion` 确认 "合成 1 项" vs "拆 N 项" (2 选项各 1 行人话), 别默认; 改后二次 `ntn pages get` 验证                                                                                                                                                                              |
| 44  | **修缮已有 page 跳过 grill 直接改**                                                                                                                  | 对已存在的 page 改字段时, 若不先确认改动语义 (覆盖 vs 追加 / 合成 vs 拆分) 就 PATCH, 易改错已有值                                                                                                                                                                                                                                                            | 修缮 page 前先 GET 现值 + AskUserQuestion 确认改动语义, 再 PATCH + 二次 GET 验证                                                                                                                                                                                                                                    |
| 45  | **查 page 用 URL 当 title 搜 → PATCH 后找不到**                                                                                                      | 用 URL slug 里的标题去 query db 搜 page, PATCH 改了 property 后 slug 不变但搜索逻辑可能错位; URL 32-char segment 是 page id 不是 title                                                                                                                                                                                                                       | 查 page 优先用 URL 尾部 32-char page id 直接 `ntn pages get <id>`, 不用 title 模糊搜                                                                                                                                                                                                                                |
| 46  | **property 改名后脚本硬编码字面 drift**                                                                                                              | Notion property 改名 (`ntn api PATCH /v1/data_sources`) 后, 脚本里硬编码的旧 property 名 (如 field-merge.sh `,\"知识点\":{...}`) 仍写旧名 → PATCH 静默失败 (写入丢失, HTTP 200 但字段没填)                                                                                                                                                                   | property 名一律走 env var (NOTION_KEYWORD_PROPERTY 等), 脚本读 `${KEYWORD_PROP:-默认名}`, 不硬编码; 改名后 grep 全仓字面确认 0 残留                                                                                                                                                                                 |
| 47  | **worktree 中途被后台清掉, 编辑丢失 + main 被别 session 推进**                                                                                       | 手动 `git worktree add` 后, 编辑到一半 worktree 目录被 background/hook 清掉 (`worktree list` 只剩主仓), 已改文件全丢; 且期间别的 session 把 origin/main 推进 → 白干 + 基于 stale main                                                                                                                                                                        | (1) 每次编辑前先 `git worktree list` 确认 worktree 还在; (2) worktree 建好后**尽快** commit + push (缩短窗口, 别攒一大批改动); (3) worktree 若丢, 先 `git fetch origin main` + `git log origin/main -3` 看是否被别 session 推进, 基于最新 main 重建                                                                 |
| 50  | **introspect cache 静默推断字段名 → silent loss**                                                                                                    | v2.9 case 写"平台" 字段, db 后来 user UI 改名"平台形式", introspect cache (24h) 推断没 verify 旧值, POST 400 silent loss (HTTP 200 但字段没填)                                                                                                                                                                                                               | (1) introspect 默认关闭 (`NOTION_INTROSPECT=false`), 走 .env 优先; (2) cache 写入前必 query 1 个 page 拿真 property 名 verify, 不匹配 exit 1 不写; (3) db schema 改后跑 paper-into-notion.sh 必先 `rm .introspect-cache.json`                                                                                       |
| 51  | **build_auto_props 函数签名漏第 8 参数 GROWTH_TAGS**                                                                                                 | v3.7 changelog 承诺"GROWTH_TAGS 第 8 参数写 知识等级形态 multi_select", 但 `build_auto_props()` 签名只接 5 positional (URL/KNOWLEDGE/EDUCATION/HIGHLIGHTS/ORG), PATCH body 从来没 build `知识等级形态` 字段 (verify 显示空)                                                                                                                                  | (1) `build_auto_props` 重构 kwargs dict (`local props=$(build_auto_props SOURCE_URL=... KNOWLEDGE=... GROWTH=...)`), IDE 能查 + 漏参数 SyntaxError 早暴露; (2) 任何字段级 merge 函数加 ≥ 1 unit test 必含此字段的 PATCH body 验证                                                                                   |
| 52  | **verify-5-fields.sh 硬编码字段名 drift**                                                                                                            | verify 脚本 echo `平台 (旧:模态类型)` 硬编码字段名 "平台", .env `NOTION_MODAL_PROPERTY="平台形式"` 改了但 verify 没改 → 实际写对 (平台形式=arXiv) 但 verify 报 ❌, 误导判断                                                                                                                                                                                  | (1) verify 脚本所有字段名从 .env 读 (`MODAL_PROP="${NOTION_MODAL_PROPERTY:-平台形式}"`), 跟 v2.5 multi-db 4 env override 协同; (2) 改 .env 后 grep verify-5-fields.sh 确认 0 硬编码字段名残留                                                                                                                       |
| 53  | **跑完 page 字段漏填不报警**                                                                                                                         | user 2026-07-15 反馈 "page 里所有字段都应该填上" (v4 留空关键词/知识等级形态). 跑完 verify 只查 title/status/modal/link, 不查 multi_select/rich_text 漏填 → user 必须手动看 page 才知漏. (per v4 fix #49 触发)                                                                                                                                               | (1) 加 `verify_all_fields.py` (paper-into-notion.py main 跑后必调, exit 1 if missing); (2) 严格必填字段 = 名称/状态/平台/link/亮点/关键词/知识等级形态 (LLM 必给 1+ 项); (3) 允许空字段 = 机构/其他 multi_select (LLM 0 候选合理). 跟反模式 #1 (multi_select 保护) 协同反转: v3.x 一律不传, v4 必填 + verify 兜底.  |
| 54  | **v4 用户偏好 "多_select 全填" 未立为 skill 默认行为**                                                                                               | v4 design 默认 multi_select 全填, 但 SKILL.md 没明文写"默认策略: 全部填", 后续 contributor 看到旧文档 (#1 反模式 multi_select 保护) 可能误解回退                                                                                                                                                                                                             | (1) SKILL.md changelog v4.1 立条 "策略反转" 段; (2) 反模式 #53 锁定 "必填" 行为; (3) CLAUDE.local.md hot recall 加 @v4.1 锚点提示                                                                                                                                                                                   |
| 55  | **v3.x introspect MODAL_PROP substring filter 误排含"形式"字段** (per PR #51 introspect.py:42-43 + CASE-PAPER-INTO-NOTION-MODAL-PROP-DRIFT-20260714) | v3.7 introspect 设计 `"形式" not in k` filter 想跳过"展现形式"留壳 select, 但 db 真字段叫"平台形式"被自己过滤掉 → fallback 走 "平台" 字面 → POST 400 "平台 is not a property that exists" silent loss                                                                                                                                                        | (1) introspect.py 选 select field whose `options[].name == "arXiv"` (canonical modal source); (2) 退化 substring match; (3) 退化首 select; (4) 字面兜底 "平台形式" 替 "平台". 跟 v4 schema.py `FieldMap.from_page()` query page 自动反推 5min TTL 协同, v3.x scripts/ 标 legacy 不删                                |
| 56  | **v3.x shell fallback 硬编码字段名 + POST body 引用废弃字段** (per PR #51 + ADR-0057-o)                                                              | v3.x 残留 5 处 stale-site: (1) `.env.example` NOTION_MODAL_PROPERTY="平台" 模板错; (2) field-merge.sh:35 fallback "平台" 错; (3) get-page-props.sh:39 fallback "平台" 错; (4) paper-into-notion.sh POST body 引用 "展现形式" (db 已删 per v3.7 FORM_PROP 弃用); (5) verify-5-fields.sh 硬编码 "平台" + label "旧:模态类型" 误导. 任意一处单独触发即 POST 400 | (1) .env.example 改 "平台形式"; (2)+(3) fallback 全部改 "平台形式"; (4) POST body 删所有 "展现形式" 引用 (v3.7 已弃用); (5) verify 改 dynamic `${MODAL_PROP:-平台形式}` env 解析. **根除路径**: 跑 v4 paper-into-notion.py 单入口 (不走 v3.x scripts), v4 schema.py 自动 query page 反推字段名, 不依赖字面 fallback |
| 57  | **modal-detect 5 pattern grep 漏 arxiv 镜像域名** (per CASE-PAPER-INTO-NOTION-PAPERS-COOL-MIRROR-20260717, arXiv 2607.13104 实测踩坑)                | case pattern 只写 `*arxiv.org*`, 漏 arxiv 镜像 (`papers.cool/arxiv/*` / `huggingface.co/papers/*` / `alphaxiv.org/*` / `arxiv-vanity.com/*` 等). 用户分享常见走镜像 (公众号 / 卡片美观), fallback "其他" → 标题写 URL → LLM judge 拿不到 title/abstract → 整条 paper card 失败 (5 字段 verify 全 0)                                                          | (1) modal-detect.sh case pattern 加 papers.cool/arxiv 分支 (v4.3 立); (2) 镜像域名扩 grep 用 `_arxiv_                                                                                                                                                                                                               | _papers.cool/arxiv_` 字面 + 后续扩 huggingface/alphaxiv 等; (3) modal-detect fallback "其他" 必须 LLM-judge 之前 warn "title=URL 风险", 强制走 canonical arxiv.org 重抓 |
