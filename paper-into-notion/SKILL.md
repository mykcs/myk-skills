---
name: paper-into-notion
description: |
  URL → 自动填 3 字段 (页面 / 状态 / 模态类型) 到 Notion `论文` database. multi_select (教育类型/关键词/标签) + rich_text 亮点 **永不覆盖**已有值 (PATCH body 只含 select/title). 适用 arXiv / 公众号 / 博客 / Twitter / GitHub / bilibili / youtube / 小红书 / 知乎. 11 scripts + 6 templates + 6 references. weiying20260624 PhD 申请场景.
  v4.7 (2026-07-25): body 拆 1 references/ 1 层深 (per Anthropic best-practices + deep-research P0 #3). SKILL.md body 624 → < 500 行.
when_to_use: |
  Trigger when user says: "paper 进 Notion" / "论文入库" / "Notion 沉淀" / "写论文卡片" / "把这个 paper 加到 Notion" / "收藏这个 arXiv" / "收藏这个公众号" / "reading list 同步" / "沉淀 paper" / "把 URL 加到 Notion" / "把链接写到 Notion" / "把 paper 同步到 Notion" / "新 paper 提醒" / "我看了一篇 paper 想存下来" / "URL 写 Notion". 高级触发词见 references/triggers-advanced.md。
  NOT: 查 Notion schema (用 Notion UI) / 批量导出 (用 Notion UI export) / 写 paper card 给老师 (用 teacher-report).
metadata:
  type: skill
  project_scope: cross-project
  skill_id: paper-into-notion
  version: v4.7 (2026-07-25)
  changelog: |
    v4.7 (2026-07-25) — body 拆 1 references/ 1 层深 (per Anthropic best-practices + deep-research P0 #3). SKILL.md body 624 → ~450 行 (< 500 cap). references/anti-patterns-history.md (反模式 #1-#57 + 「修改哪一部分」4 决路径 + 「跑完自我总结」4 段模板 + 「经验教训 → 提升 skill」5 步闭环 + v-bump 自动触发 4 条件 + 多 db schema 适配 + 4 env + 2 db property 差异表).
    v4.6 (2026-07-19) — PER Workflow 统一抽象；新增 PER Workflow 总览节；frontmatter 触发词拆分；高级触发词下沉到 references/triggers-advanced.md；技能版本号与 frontmatter 对齐为 v4.6。
    v4.5 (2026-07-18) — keyword abstract 命中检查 + highlights 80 字 + 必含 4 组件 (per CASE-PAPER-INTO-NOTION-V4-5-KEYWORD-OBJECTIVITY-20260718 + arXiv 2607.13104 实测): 关键词 0 命中 abstract 是 silent loss 经典反模式 (LLM judge 凭 general knowledge 瞎填 "llm/机器学习/深度学习", abstract 全无这 3 词); 新增 verify_all_fields.check_keyword_objective() 拿 abstract 跟 page 关键词比对, 3 个 keyword 中至少 2 个必须在 abstract 出现 ≥ 1 次否则 FAIL + exit 1.
    v4.4 (2026-07-18) — arxiv-affiliations Layer 0 + 反作者名 post-filter (per CASE-PAPER-INTO-NOTION-V4-3-5-AFFILIATIONS-20260718 + arXiv 2607.13104 实测): 新增 fetch_arxiv_affiliations() 调 scripts/arxiv-affiliations.py 抓 sup 标 1-N 真实机构 (per v3.4 ADR-0057), Layer 0 成功覆盖 LLM judge org.
    v4.3 (2026-07-17) — modal-detect 加 papers.cool/arxiv 镜像分支 (per CASE-PAPER-INTO-NOTION-PAPERS-COOL-MIRROR-20260717, arXiv 2607.13104《Self-Improvements in Modern Agentic Systems: A Survey》实测踩坑): modal-detect.sh case pattern 从 5 加到 6 (`*arxiv.org*|*papers.cool/arxiv*` → arXiv).
    v4.2 (2026-07-16) — Notion block 布局 + verify 协议位抽离 (per weekly-report-phd v1.1 §X + §9, 周报项目 30+ 次反馈累积): 新增 2 个 references/notion-*.md (notion-block-layout.md 元素位置 + 分隔线 + h1 层级 + IF...THEN 6 + 反模式 5; notion-content-verify.md 5 类逐项 grep + 5 步流程 + 4 类触发协议 + 8 条反模式).
    v4.1.1 (2026-07-16) — v3.x shell 残留子集 introspect MODAL_PROP 修复 + 5 处 stale-site 闭环 (per PR #51 retro + ADR-0057-o).
    v4.1 (2026-07-15) — 全字段必填 verify 兜底 (per user 2026-07-15 "page 里所有字段都应该填上" 反馈 2 次, v4.0 + fix #49 没根治): 新增 verify_all_fields.py (~80 行, GET page 全 properties 检查 + LLM 必填 vs 允许空分类判定) + paper-into-notion.py main 跑后必调 (exit 1 if missing, 返缺字段名 list).
    v4.0 (2026-07-14) — Python 单入口重写 (替代 v3.x 11 shell + 4 env), per user 2026-07-14 原话 "为什么这么困难 重新设计 skill 更优雅达成我的目的".
    v3.8 (2026-07-14) — introspect cache pin 守卫 + 教育类型 default fallback + MODAL_PROP stale 修复 (per CASE-PAPER-INTO-NOTION-MODAL-PROP-DRIFT-20260714 + arXiv 2603.26188 (OSA) 实测).
    v3.7 (2026-07-14) — 知识等级形态 multi_select 6 项 (开创新领域/综述/增量/反驳/进阶技巧/基础知识), 旧 展现形式 select user UI 删, FORM_PROP 完全弃用.
    v3.6 (2026-07-14) — Notion property「知识点」改名「关键词」+ 硬编码换 env var.
    v3.5 (2026-07-14) — 补 v3.4 changelog 谎报的缺失反模式表格行 (per CASE-PAPER-INTO-NOTION-SELF-SUMMARY-2026-07-14 + 灵魂 v6 self-summary 内化).
    v3.4 (2026-07-14) — 合并 sub-agent 半成品 (institutions-judge.sh 加 whitelist 注释 + v3-3 反模式 #42 multi_select 拆 N 项歧义 + llm-fill 反模式 #44/#45 修缮 page + 字段填全).
    v3.2 (2026-07-14) — LLM 默认自动写入 + institutions judge + get-page-props 工具.
    v3.1 (2026-07-14) — introspect mode + self-evolution 闭环 v3.0 self-summary 内化.
    v2.9-i (2026-07-14) — ask window 守卫 (灵魂 v4/v6 + feedback-adhd-rhythm-ask-window-not-bypass + CASE-CLAUDECODE-ADHD-RHYTHM-BYPASS-20260714).
    v2.9 (2026-07-14) — db schema 改 教育类型 multi → 展现形式 select 6 选项 + 平台 字段.
    v2.8 (2026-07-14) — db schema 漂移检查 + 9 字段自检表 (含 link url + 机构 multi_select) + 2 反模式.
    v2.7 (2026-07-14) — mmx v1.0.16 真子命令 + status 中文错乱 + .env 真值同步.
    v2.6 (2026-07-14) — subagent FAIL 反馈增量 + 字面 drift 跨 skill 协议位.
    v2.5 (2026-07-14) — 多 db schema 适配 (4 env variables + 2 db property 差异表).
    v2.4 (2026-07-14) — 经验教训 → 提升 skill 闭环 + skill-self-summary 3 健壮性.
    v2.3 (2026-07-14) — skill 跑完自我总结协议 + mem0 quota fallback.
    v2.2 (2026-07-14) — Notion URL 解读 + 修哪一部分 4 决路径 + 6 残留踩坑沉淀.
    v2.1 (2026-07-14) — 跨 Notion database 搬 schema 4 踩坑沉淀.
    v2.0 (2026-07-14) — description split-in-two + 触发词扩 15+ + 6 字段 → 8 字段 schema 文档 + frontmatter audit 4 字段全过.
    v1.0 (2026-07-13) — 立 (per ADR-0057, 5 pattern 模态 + multi_select 字段级 merge).
  起源: user 2026-07-13 原话 "paper 进 Notion" 触发.
  关联 ADR: ADR-0057 (v1.0) / ADR-0057-b (v2.0) / ADR-0057-c (v2.1) / ADR-0057-d (v2.2) / ADR-0057-e (v2.3) / ADR-0057-f (v2.4) / ADR-0057-g (v2.5) / ADR-0057-h (v2.6) / ADR-0057-i (v2.7) / ADR-0057-k (v2.9) / ADR-0026 / ADR-0054.
  关联 case: 16 CASE 文件 (v1.0 → v4.5), per `~/.claude/knowledge/cases/wiki/CASE-PAPER-INTO-NOTION-*`.
  适用 owner: mykcs (per ADR-0054 Notion 严格层 + 4 重保险).
  自我进化协议: v2.6.30 §I 8 步循环 (per ADR-0057-f v2.4 + v2.6.30).
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-25"
triggers:
  - paper 进 Notion
  - 论文入库
  - /paper-into-notion
  - Notion 沉淀
  - 写论文卡片
  - 收藏 arXiv
  - 收藏公众号
  - paper card

---

# paper-into-notion v4.7

> **核心承诺**: 任何 URL 进来 → 自动写 Notion database 论文 → multi_select 字段 (教育类型/标签/关键词) 永不覆盖已有值 ✅
> **触发**: user 说 "paper 进 Notion" / "Notion 沉淀" / "把这个 paper 加到 Notion" / "写论文卡片" 时跑
>
> **v4.7 body 拆 1 references/** (per Anthropic best-practices + deep-research P0 #3): SKILL.md body 624 → ~450 行. 引用 1 层深, 禁嵌套.

| references/ 段             | 内容                                                                                                                                                                                | 引用原因                                                         |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `anti-patterns-history.md` | 反模式 #1-#57 + 「修改哪一部分」4 决路径 + 「跑完自我总结」4 段模板 + 「经验教训 → 提升 skill」5 步闭环 + v-bump 自动触发 4 条件 + 多 db schema 适配 + 4 env + 2 db property 差异表 | 反模式表 60+ 条跨 v2.1-v4.5 累积, schema + self-evolution 协议位 |

---

## 何时用

| 触发场景                                                   | 跑这个 skill                        |
| ---------------------------------------------------------- | ----------------------------------- |
| user 给 arXiv URL 要写 Notion                              | ✅                                  |
| user 给微信公众号 / 知乎 / 小红书 / bilibili / YouTube URL | ✅                                  |
| user 给技术博客 URL (medium / 官方 blog / GitHub README)   | ✅                                  |
| user 说"加 paper 进 Notion" / "沉淀这个 paper"             | ✅                                  |
| user 一次给多个 URL (≤ 5)                                  | ✅ (循环跑主入口)                   |
| user 要跑 weekly-report-phd 周报 + paper card 写 Notion    | ✅ (跟 weekly-report-phd §C.3 联动) |
| user 要查 Notion database schema / 改字段定义              | ❌ (手工到 Notion UI)               |
| user 要批量导出 paper (反向操作)                           | ❌ (用 Notion UI export)            |
| 写 paper card 给老师 (feishu docx)                         | ❌ (用 teacher-report)              |

高级触发词见 `references/triggers-advanced.md`。

---

## PER Workflow

> 统一 workflow 抽象见 `~/.agents/skills/website-improve/references/per-workflow-framework.md`（Source of truth）。本 skill 所有复杂任务默认按 Plan → Execute → Verify 三段执行，artifact 文件 handoff，禁止口头传话。

### 角色映射

| 角色         | 职责                                                                                                                                                                                                                                        | 产出 artifact                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| **Planner**  | 解析 user URL / 自然语言；跑 `modal-detect.sh` 判定模态（arXiv / 公众号 / 博客 / Twitter / 其他）；根据目标 db 选 Notion db/page；识别 schema drift / multi-db 风险；输出 scope + acceptance criteria + risk list                           | `plan.json` / `plan.md`         |
| **Executor** | 按 plan 执行：arXiv 抓 metadata → LLM judge 5 字段 → `field-merge.sh` 字段级 merge → `ntn api` POST/PATCH page；必要时在写 Notion 后触发 Executor-stage 可选子流 `scripts/skill-self-summary.sh`（4 段总结 + mem0 fallback）；输出 exec log | `exec-log.json` / `exec-log.md` |
| **Verifier** | 读 plan + exec log；跑 `verify-5-fields.sh` / `verify_all_fields.py` 5 字段自检；检查 Notion block layout（`references/notion-block-layout.md`）；patch recovery 验证（GET page 二次确认）；FAIL 则 reject 回 Executor 重做                 | `verdict.json` / `verdict.md`   |

### 3 条核心反模式（来自 PER 框架）

- ❌ 1 个 sub-agent 跑完 3 角色。
- ❌ Executor 自己标 done。
- ❌ Verifier FAIL 还强行 ship。

完整反模式列表见 `~/.agents/skills/website-improve/references/per-workflow-framework.md` §反模式。

### Executor-stage 可选子流：跑完自我总结

当任务满足以下任一条件时，Executor 在 Notion 写入后应调用 `scripts/skill-self-summary.sh`：

- skill 升级 / config 改动后
- 跨 db / 跨 session 任务完成
- user 显式说 "总结" / "回顾" / "沉淀"

完整闭环协议见 `references/self-evolution-loop.md` + `references/anti-patterns-history.md` (反模式 #17-#24 + 「经验教训 → 提升 skill」5 步闭环 + v-bump 自动触发 4 条件)。

---

## 9 字段自检表 (核心铁律: multi_select 不覆盖, v2.7 修 v1.4 误写 8 字段为 9 字段)

> **v2.7 修正** (per CASE-PAPER-INTO-NOTION-V2-7-SCHEMA-DRIFT-20260714): v1.4 拍板 8 字段是错值, db 实测 9 字段 (含 `link` url + `机构` multi_select). page `39dfedee-...afd8-e51e622da580`《无矩阵乘法LLM》体检时 0 link + 0 模态类型发现, 修 SKILL.md schema 漂移.

| #   | 字段     | 类型             | 自动填?                                                        | 保护机制                                                                                                                              |
| --- | -------- | ---------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 名称     | title            | ✅ (抓 `<title>` / arXiv title)                                | 直接 PATCH 覆盖安全 (title 是单值). v2.5 起走 `$NOTION_TITLE_PROPERTY` env (论文 wiki 兼容老 db "页面" / 信息 db "名称")              |
| 2   | 状态     | **status**       | ✅ 默认 "初抓取" (per .env)                                    | 单值安全。⚠️ status ≠ select: option 不能删,只能 UI Archive. PATCH 前必 GET data_source 拿真 options 比对 env 默认值 (per 反模式 #29) |
| 3   | 模态类型 | select           | ✅ 5 pattern grep (arXiv / 微信公众号 / 博客 / Twitter / 其他) | 单值安全                                                                                                                              |
| 4   | 教育类型 | **multi_select** | ❌ 后填 (新 page 才填)                                         | **PATCH body 永远不含此字段**                                                                                                         |
| 5   | 关键词   | **multi_select** | ❌ 后填 (新 page 才填)                                         | **PATCH body 永远不含此字段**                                                                                                         |
| 6   | 亮点     | rich_text        | ❌ 后填 (新 page 才填)                                         | **PATCH body 永远不含此字段** (你后填)                                                                                                |
| 7   | link     | url              | ✅ auto 填 source URL (per v1.4 字段级 merge)                  | 跟亮点分离 (老 v1.4 page 跟 url 写在亮点, v2.7 起 url 必填 link)                                                                      |
| 8   | 机构     | **multi_select** | ❌ 后填                                                        | **PATCH body 永远不含此字段** (新增 v2.7, db 实测有但 v1.4 schema 漏)                                                                 |
| 9   | 日期     | created_time     | ✅ auto (Notion set)                                           | 永不传 (auto)                                                                                                                         |

**db schema 实测 (2026-07-14 GET data_source, per CASE-V2-7-SCHEMA-DRIFT + V2-9-SCHEMA-CHANGE 累积第 3 次 schema 漂移, 9 → 12 字段)**:

- 名称 (title) / 状态 (status, 3 options 初抓取/ai补充/人类认证) / **平台** (select, 6 options arXiv/博客/微信公众号/bilibili/Twitter/其他, v2.9 新建替代 v1.4 "模态类型" 僵尸 property) / 教育类型 (multi_select, 1 option 论文阅读) / 关键词 (multi_select, 7 options) / 亮点 (rich_text) / link (url) / 机构 (multi_select, 2 options SZU+PolyU) / 日期 (created_time) / 创建时间 (created_time) / 上次编辑时间 (last_edited_time) / **展现形式** (select, 6 options 课程/论文/工具/基础知识/博客/帖子, v2.9 新建替代 v1.2 教育类型 multi) = **12 字段实测**
- ❌ db 无 "标签" multi_select (v1.4 8 字段写错, 实际 db 没此 property)
- ⚠️ 模态类型 select 是僵尸 property (type=None, options=空), 写 PATCH 时不要往里写 (per 反模式 #34)

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

| Flag                 | 行为                                          | 用途                     | 是否写 Notion |
| -------------------- | --------------------------------------------- | ------------------------ | ------------- |
| `<URL>` (默认)       | 跑 4 步 + 写 Notion + verify-5-fields         | 实际写 paper             | ✅ 写         |
| `--verify`           | 跑 9 步环境检查                               | 部署前/装后 sanity check | ❌ 不写       |
| `--dry-run <URL>`    | 跑 4 步 + 跳过 ntn api + 返 `DRY-RUN-PAGE-ID` | schema 验证 / 字段预览   | ❌ 不写       |
| `--force-fill <URL>` | 跑 4 步 + 覆盖已有 page 全 7 字段             | 已知 page 想重填         | ✅ 写 (慎用)  |

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
├── ntn-call.sh                 # 公共 client (GET/POST/PATCH), 修 ntn 0 字节 + 参数顺序 bug (per CASE-NTN-CLI-SILENT-BUFFER-20260719)
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

### 10 references (v4.7 加 1)

```
references/
├── field-merge-algorithm.md    # 字段级 merge 算法详解 (GET 空形态 + PATCH 流程)
├── arxiv-fetch-protocol.md     # arXiv API + ElementTree 解析 + rate limit 1 req/3s
├── notion-schema-migration.md  # Notion 2025 API model 速查 + 4 错误码
├── notion-url-parse.md         # Notion URL 4 类 + id 提取 + 4 决路径
├── gh-worktree-cwd-compat.md   # git worktree + cwd 兼容 (sub-agent 不踩坑)
├── institution-canonical.md    # 机构名 canonical 化 (arXiv affiliation)
├── self-evolution-loop.md      # skill self-evolution 4 步闭环 + 5 步闭环
├── self-summary-protocol.md    # 跑完自我总结 4 段模板 + mem0 quota fallback
├── notion-block-layout.md      # v4.2 Notion 元素位置 + 分隔线 + h1 层级 + IF...THEN 6 + 反模式 5
├── notion-content-verify.md    # v4.2 Notion 5 类逐项 verify + 4 类触发协议 + 8 条反模式
└── anti-patterns-history.md    # v4.7 反模式 #1-#57 + 修改哪一部分 + 跑完自我总结 + 经验教训 → 提升 skill + 多 db schema 适配
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
 # ⚠️ body 永远不包含: 教育类型 / 标签 / 关键词 (multi_select) + 亮点 (rich_text)
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

| Pattern | 模态类型     | URL 示例                                                                                                              |
| ------- | ------------ | --------------------------------------------------------------------------------------------------------------------- |
| 1       | `arxiv`      | `arxiv.org/abs/1706.03762` / `arxiv.org/pdf/1706.03762` / **v4.3 加**: `papers.cool/arxiv/*` (镜像)                   |
| 2       | `微信公众号` | `mp.weixin.qq.com/s/...`                                                                                              |
| 3       | `博客`       | `lilianweng.github.io/posts/...` / `medium.com/@...` / `*.blog.*` / `juejin.cn/post/...` / `zhuanlan.zhihu.com/p/...` |
| 4       | `Twitter`    | `twitter.com/...` / `x.com/...`                                                                                       |
| 5       | `其他`       | bilibili / youtube / 小红书 / github / 其他都 fallback 此项 (Notion schema 已含)                                      |

**判定逻辑** (`scripts/modal-detect.sh`):

```bash
URL="$1"
case "$URL" in
  *arxiv.org*|*papers.cool/arxiv*) echo "arXiv" ;;
  *mp.weixin.qq.com*) echo "微信公众号" ;;
  *twitter.com*|*x.com*) echo "Twitter" ;;
  *blog*|*medium.com*|*juejin.cn*|*zhuanlan.zhihu.com*|*github.io/posts*|*github.com/blog*) echo "博客" ;;
  *) echo "其他" ;;
esac
```

---

## arXiv 抓取 (重试 3 次 + exit 1, per Q4)

### Notion 2025-09-03 → 2026-03-11 multi-source database 升级背景

| 概念                | 2022-06-28 旧         | 2025-09-03+ 新                                                        | paper-into-notion 现状                                         |
| ------------------- | --------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------- |
| **database**        | 1 个 db = 1 个 schema | 1 个 db = N 个 data sources (容器)                                    | 接受任一, 用 `GET /v1/databases/{id}` 反查 `data_sources[].id` |
| **data source**     | 隐式                  | 1 个 schema/table                                                     | DS_ID 必存, 用 `GET /v1/data_sources/{id}` 拿 schema           |
| **URL segment**     | 32-char db_id         | 第 1 段 = database_id, 第 2 段 = view_id, data_source_id **不在 URL** | 必 introspect                                                  |
| **property schema** | per database          | per data source (每个 ds 独立 property 名/类型)                       | introspect 模式待 v2.6, 当前 v2.5 env variable override        |

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

| #   | 字段                          | 验证命令                                            | 期望                                                                                       |
| --- | ----------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1   | path                          | `ls ~/.agents/skills/paper-into-notion/`            | 1 SKILL + 1 .env.example + 1 USER-SETUP + 6 scripts + 4 templates + 2 references = 15 file |
| 2   | commit                        | `git -C ~/.agents/skills log -1 --oneline`          | 新 commit (feat(skill): paper-into-notion v1.0)                                            |
| 3   | push                          | `git -C ~/.agents/skills status -sb`                | ahead=0                                                                                    |
| 4   | CI                            | `gh api repos/mykcs/myk-skills/commits/HEAD/status` | green                                                                                      |
| 5   | record_id + multi_select 保护 | `ntn pages get $RECORD_ID`                          | 3 auto 字段填对 + multi_select 全空 (新建) 或保留 (更新) ✅                                |

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
- **weiying 域 Notion 主入口 (verify 协议位 SSOT)**: `~/.claude/memory/weiying20260624-notion-operations-master.md` §2 rule #8 (verify 必 HTTP GET Notion API, 不可信 backup). 适用 introspect.py / verify_all_fields.py / patch-markdown-block.sh 等所有 verify 场景, 不复制内容, 1 行 pointer.
- **跨域 verify ground truth 通则 (rule #8 起源)**: `~/.claude/knowledge/cases/wiki/CASE-VERIFY-TRUST-GROUND-TRUTH-NOT-CACHE-20260716.md` + `~/.claude/rules/claudecode-verify-before-act.md` §4 IF...THEN (verify 改完必拿 ground truth, 不依赖 cache/backup/snapshot, 2026-07-16 立)

---

## 反模式 v3 灵魂自检 (per post-task-recommend §6)

- 任务完成时输出 ≤ 15 行
- 不写可推迟事项段 (per v3 清理, 2026-07-02)
- 关键证据直接 inline, 不卸给 user 复制粘贴

> **反模式总表 (60+ 条跨 v2.1-v4.5) 见 `references/anti-patterns-history.md`** — 本 SKILL.md body 已拆该引用, 1 层深不嵌套.
