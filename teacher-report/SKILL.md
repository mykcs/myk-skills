---
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).
  
  **Generate mode**: use when the user mentions a specific researcher / advisor / 老师 / 导师 and asks to "调研 / 写一份报告 / 整理材料 / 看看这位老师" — output is a structured 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景) ready to share. Triggers on phrases like "调研一下 XXX", "生成 XXX 老师的报告", "看看张三是不是值得报", "写一份老师材料", "PhD advisor report for XXX".
  
   **Audit mode** (v0.2.8+): use when the user provides an EXISTING docx (URL or doc_id) and asks to "审计 / 检查 / 看看合不合规 / review" — fetches the doc, runs 12 compliance checks against v0.2.5+ rules (title numbering / ① ② / block charts / TL;DR callout / 5-section completeness / Persona footer etc), outputs a pass/fail report with fix suggestions. Triggers on phrases like "审计一下 [URL]", "看看 [老师] 报告合不合规", "review teacher report compliance", "teacher-report audit [doc_id]".

   **Anti-Hallucination Rules (v0.2.9, 2026-06-06)**: any paper status / year / author / title / 导师职务 / 学生身份 / 统计数字 claim must be verifiable against arXiv / OpenReview / 学校官网, not AI-inferred. See `## Anti-Hallucination Rules` section below for the 6-field matrix and 4 prohibition rules.

   **Paper Entry Format (v0.3.3, 2026-06-08) — 硬要求**: 所有论文条目 (§4 论文产出全景 / §2.2 方向匹配度 / §3 套磁信引用) **必须**用 paper card 格式 (**4 维 taxonomy 4 行** 大领域/中方向/小任务/子技术 每字段独立一行 + verbatim 标题 + 完整作者列表 + 吴飞显式标注 + 发表 venue/year/角色 + arXiv URL + papers.cool URL), 禁止简化为表内一行 / 4 列表格(用 4 个独立 <p> 块)。详见 `## Paper Entry Format (v0.3.2) — 硬要求` 章节。

   Do NOT use for: batch-processing many teachers (that's `phd-scout` which writes to Bitable), single paper deep-dive, lab research summary, or collecting a teacher into a structured Bitable row.
---

# Teacher Report

Generate a single-advisor PhD dossier in Feishu wiki doc format. Input: a researcher name (optionally with university / school). Output: a Feishu `docx` URL that the user can move to a wiki node.

## Inputs to collect

Before fetching, confirm or infer the following from the user's message:

1. **老师姓名** (required) — full Chinese name or Pinyin. If ambiguous (common name + university), ask the user.
2. **学校** (strongly recommended) — disambiguates homonyms and lets L1 (university site) work. If missing, infer from context or ask.
3. **学院 / 系** (optional) — narrows L1 search.
4. **用户的研究方向 / 匹配诉求** (optional) — used in the 方向匹配度 section to score fit. If user didn't say, write a generic "通用 CV/ML/Agent" profile and note "无特定方向假设" in the report.
5. **申博 wiki dashboard token** (recommended) — 飞书 wiki/docx token,代表用户的"申博候选池 dashboard"。提供时,生成的报告**自动 append 摘要**到这个 wiki(让用户在一个 wiki 节点看到所有候选老师)。不提供时,fallback 到 my_library(每个老师独立 docx)。
6. **申博 wiki parent token** (optional) — 飞书 folder/wiki 节点 token,生成的 docx **作为子页**放到这个 parent 下。和 (5) 配合:parent 是 wiki 树,dashboard 是顶层汇总。

If 1 + 2 are both missing, do NOT start fetching — ask the user.

### Disambiguation edge cases (must read)

- **同名老师跨校任职**:S2 affiliations 可能跨校混合(如老师从清华转浙大)。**先 L1 查现职学校官网**,若学校已变动,以**现职**为准;在报告 §5 数据来源标 "L2 论文列表含 2 单位混合数据(2024 前 X 校 / 2024 后 Y 校)"。
- **同名 + 同校 + 跨学院**:CS 学院有 "李明",医学院也有 "李明"。**用学院+研究方向的 L1 静态页或学院教师列表 grep** 二次定位。
- **拼音歧义**:"李伟" / "Li Wei" 在 S2 上可能匹配英文姓名写法 "Wei Li" (last-first)。**优先用中文名 + 学校搜 L1**,再 S2 验证。

### Step 0.5 — Confirm dashboard/parent token

> **⏰ 时机**:在 Step 1 抓取之前,先问 user 5/6 token 提供意愿,决定 Step 3 走模式 A / B / C。

如果 user 没有主动提供 §5/§6 token,使用 `AskUserQuestion` 给 3 个选项:

1. **两个 token 都有** → 模式 A(子页 + dashboard 摘要)
2. **只 dashboard** → 模式 B(my_library + dashboard 摘要)
3. **都没有 / 不在乎** → 模式 C(独立 docx,user 手动归档)

如果 user 在原始消息里**显式说过** token(从上下文提取),跳过询问直接用。

**为什么需要这个 step**:LLM-prompt.md 和 report-template.md §11 dashboard 摘要都假设 dashboard token 已提供,但实际 user 经常忘了。提前问一次,避免生成完 docx 后再问 "要不要加 dashboard"。

## Procedure

### Step 0 — Mode selection (v0.3.4+)

- **Generation mode (default)**:user 提供老师姓名 / 学校,生成新 docx
- **Audit mode**:user 提供 docx URL / doc_id,审计已有 docx 合规性
- **Rewrite mode (v0.3.4+ 新增)**:user 提供 docx URL / doc_id + 显式 "按 skill 模板重写 / 排版 / 规范化 / 升级到 v0.3.3" 指令 → fetch + 解析 + 按 v0.3.3 fixed-template 全量 regenerate + `overwrite`

**Rewrite 触发词** (任一即触发 Rewrite mode):
- "按 skill 模板重写" / "按 v0.3.3 重写" / "规范化 doc"
- "重排版" / "按模板排版" / "升级到最新格式"
- "fix this doc to match the skill"
- "regenerate according to skill template"

**Rewrite 不响应场景** (LLM 必须显式 user-confirm 才执行):
- 用户只说 "审计一下 [URL]" → 走 Audit mode, **不** 自动 rewrite
- 用户说 "看看 [老师] 报告合不合规" → 走 Audit mode
- 用户说 "fix this" 但没指明 docx URL → 反问 user 哪一篇, 不要随便 apply to 9 docs

**Mode 判定**:
- 触发词含 "审计 / audit / 检查 / 合规 / review" → Audit mode
- 触发词含 "调研 / 生成 / 写一份 / 看看这位老师" → Generation mode
- 显式提供 docx URL/doc_id 且无 Generation 触发词 → Audit mode
- 显式提供老师姓名 → Generation mode

### Step 1 — Data fetching (4-level fallback)

> **🚨 硬规则**(违反 = skill 协议破坏):
> - **L2 Semantic Scholar 失败时,只准 1 次 5s 重试,任何 5s/15s/30s/60s 指数退避 = 违反本 skill**。L4 web_search 聚合是 S2 字段的有效替代,直接跳。
> - **L3 DBLP pid 0 hits 时,不要无限重试**,直接走 L4 web_search。
> - **L1 抓到 SPA 锚点不全时,必须切 playwright**,不要只 webfetch。
> - **任何 L1-L4 抓取中,"导师本人一作顶会论文数"是必查字段**,0 → 风险灯号 🟡 中(见 Failure handling)。

> **🚨 飞书标准标题号硬要求(v0.2.5,违反 = skill 协议破坏)**:
> - **h2 / h3 / h4 标题**:`1.` `2.` `3.` / `1.1` `2.1` / `1.` `2.` `3.`(飞书自动识别为有序列表,显示在 outline)
> - **禁止**手动 `(1) (2) (3)` 编号 — 飞书 outline 不识别,user 看不到大纲
> - **禁止**论文精读内联 `① ② ③` 字符 — 用 `<p><b>完整标题</b></p>` 即可,飞书 outline 通过 h4 定位
> - **禁止** `████████` 字符画 — 趋势表用 `<table>` + 精确数字(LLM-prompt §7)
> - **不混用** `1.` / `(1)` / `①` 三种编号风格
> - **论文精读标题**:完整标题 + `(venue year)` + `⭐/📝/⚠️/🆕` 状态标记(无 arXiv id / 无作者列表)
> - **详见**:`references/report-template.md §5` 论文精读模板 + `references/normalization-audit-2026-06-05.md`(4 文档规范化审计追踪)

Try sources in this order. Stop when a source yields enough signal; you do not need all four.

| Level | Source | How to query | What to extract |
|-------|--------|-------------|----------------|
| L1 | 学校/学院官网 | **`webfetch` 先试静态 HTML**;失败 / 明显是 SPA 框架(`<div id="app"></div>` 标记)→ **切 `playwright` MCP** `browser_navigate` + `browser_snapshot` 拿渲染后文本。ZJU common patterns: `person.zju.edu.cn/{pinyin}`, `mypage.zju.edu.cn/{pinyin}`, `cs.zju.edu.cn` faculty page | 基本信息、职称、行政职务、联系方式、研究方向、代表性工作 |
| L2 | Semantic Scholar API | `https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,affiliations,paperCount,hIndex,homepage` then `/author/{id}/papers?fields=title,year,venue,citationCount,authors&limit=100` | 论文清单（近 3 年）、h-index、合作者 |
| L3 | DBLP | `https://dblp.org/search/author/api?q={name}&format=json` then `/pid/{pid}.xml` for full paper list | 论文 venue 标准化(DBLP 提供的 venue 是规范名,不是缩写) |
| L4 | MiniMax Web Search (优先) | `mcp__MiniMax__web_search` MCP tool 搜 `"{name}" {university} site:arxiv.org` 或 `"{name}" personal homepage`. Mainland China 可用 | 论文全文(arXiv abs 页面)、个人 CV、学生名单、研究亮点 |
| L5 | Kimi WebBridge (浏览器兜底) | `kimi-webbridge` skill 调用真实 Chrome,打开 `arxiv.org/abs/{id}` 拿 abstract + 完整作者列表 + arXiv ID。SPA 渲染不下来的论文用这个 | arXiv abs 完整 HTML(渲染后)、下载图片/附件、个人主页 1-click 截图 |
| L6 | AnySearch (最后兜底) | `anysearch` skill 23 个垂直域 + 实时网页抽取,搜 `"{paper_title}"` 或 `"{name}" CV filetype:pdf` | 真实 PDF 链接、研究亮点汇总、跨平台交叉验证 |

L2 (Google Scholar) is intentionally **skipped** in mainland-China network environments — go L2 Semantic Scholar → L3 DBLP → L4 MiniMax → L5 Kimi WebBridge → L6 AnySearch.

**v0.3.4 搜索链(vs 旧 L1→L2→L3→L4)**:
- L1 官网 → L2 S2 → L3 DBLP → **L4 MiniMax** (mcp__MiniMax__web_search, 优先用) → **L5 Kimi WebBridge** (浏览器兜底, SPA/动态渲染场景) → **L6 AnySearch** (23 域垂直 + 实时抽取, 最后兜底)
- 顺序逐级 fallback, 任一级成功即可停;失败时跳下一级
- 论文数据采集用 L4/L5 优先(覆盖 arxiv abs 完整内容),L6 做交叉验证
- 反例:不要一上来用 L6(anysearch 太宽泛),先用 L4/L5 精确抓 arxiv

**🚨 v0.1 CCF-A/B 限制 (2026-06-05)**:**本 skill 当前不在报告中标注 CCF 等级**。`LLM 估算` 的 "CCF-A 65" 数字不可信,容易被反例数据(LLM 把 ICLR submitted 当 CCF-A)污染。报告里**只写 venue 名**(NeurIPS / ICLR / ACL / KDD / TPAMI),**不写 CCF-A/B**。v0.2 实现方案见 `data-sources.md §CCF mapping (deferred)`。

If L1 fails (e.g., personal page 404 or 动态加载), continue to L2 — the data is still salvageable.

**Data the model should NOT make up**: student names, h-index, paper counts, CCF tier. If a fact is unverifiable from fetched sources, write `[待验证]` in the report and note it in `5. 数据来源`.

### Step 2 — LLM synthesis (in-conversation, not external API)

You are the LLM. Use the fetched data to produce a structured dossier. Read `references/llm-prompt.md` for the synthesis prompt and `references/report-template.md` for the target XML schema.

**Output of this step**: a single XML string (lark-doc v2 format) ready to pass to `lark-cli docs +create`.

**Synthesis rules**:
- **TL;DR callout** must be ≤ 6 lines per column. Numbers must come from L2/L3 data, not vibes.
- **方向匹配度** must reference the user's stated direction (or "通用 CV/ML/Agent" default). Score per direction with a one-line rationale.
- **套磁邮件草稿** must cite 1-2 specific papers from the fetched list (with venue + year). Generic flattery is forbidden.
- **风险点** must be fact-based: 方向变化、招生名额信息缺失、实际带生者不确定等可证伪的判断。
- If data is sparse, mark sections as `🟡 数据待补` rather than fabricating.

### Step 3 — Write to Feishu

**🚨 硬要求(2026-06-05 v0.2.4)**:每位老师报告**必须**出现在用户的"申博 wiki"里。三种模式,按用户输入(Inputs §5 §6)分支:

#### 模式 A — 提供 wiki parent + dashboard(完整 wiki 集成)
```bash
# 1. 创建子 docx(作为 wiki parent 的子页)
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "<skeleton>" \
  --parent-token {WIKI_PARENT_TOKEN}

# 2. append 章节到子 docx
lark-cli docs +update --command append --content "<section-X>" --doc {child_doc_id}

# 3. append 摘要到 dashboard wiki 节点(让 user 在一个地方看到所有候选老师)
lark-cli docs +update --command append --content "<dashboard-摘要>" --doc {WIKI_DASHBOARD_TOKEN}
```

#### 模式 B — 只提供 dashboard
```bash
# 1. 报告仍 create 到 my_library(独立 docx,user 可手动归档)
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "<skeleton>" \
  --parent-position my_library

# 2. append 章节
lark-cli docs +update --command append --content "<section-X>" --doc {child_doc_id}

# 3. append 摘要到 dashboard(让 user 在 dashboard 看到链接)
lark-cli docs +update --command append --content "<dashboard-摘要>" --doc {WIKI_DASHBOARD_TOKEN}
```

#### 模式 C — 都没提供(legacy 兼容)
```bash
# 直接 create 到 my_library,不 append 到 dashboard
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "<skeleton>" \
  --parent-position my_library

# append 章节(同上)
```

> 摘要模板见 `report-template.md` § 11 申博 wiki dashboard 摘要。

If the doc body is > 30 blocks, split: create with skeleton (title + headings + TL;DR callout only), then `lark-cli docs +update --api-version v2 --doc {doc_id} --command append` per section. This avoids the v2 single-call content-size limit and makes failures recoverable.

Capture the returned `data.document.url` — this is what the user gets.

### Step 4 — Return + handoff

Reply to the user with:
1. The docx URL
2. A 1-line "建议下一步": 套磁信草稿可直接 copy / 添加到知识库得 wiki 链接 / 等等
3. If any section was `🟡 数据待补`, list the specific gaps so the user can补

### Rewrite mode (v0.3.4+ 新增) — 详细流程

> **入参必填**:docx URL / token + user 显式指令(触发词匹配)
> **输出**:overwrite 后的新 docx URL + diff summary

**Step R1 — Fetch 现状**
```bash
lark-cli docs +fetch --api-version v2 --doc {doc_id} --detail with-ids
```
提取:
- docx content(完整 XML)
- revision_id(基线版本,后续用 --revision-id -1)
- 已知 paper cards 位置(用于 dedup)

**Step R2 — 解析当前内容**
按 section 拆解(基于 5 章结构):
- §1 TL;DR callout: 保留(若合规)
- §2 申博匹配度: 重写为 5 维度,每维度引用 paper card
- §3 套磁与行动建议: 重写套磁信,引用 1-2 篇 paper card
- §4 论文产出全景: **整段重写**——按 v0.3.3 paper card 格式重组,删除 v0.3.0 compact 残留
- §5 数据来源: 更新为 4-level 数据源(L1/L2/L3 + 新 L4 MiniMax / L5 Kimi / L6 AnySearch)

**Step R3 — 抓取真实论文数据**
对 §4 每篇论文:
1. L4 MiniMax: `mcp__MiniMax__web_search` 搜 `"{title}" arxiv`
2. L5 Kimi WebBridge(若 L4 失败):浏览器打开 arxiv.org/abs/{id} 拿完整 byline
3. L6 AnySearch(若 L4/L5 失败):搜 `"{title}" filetype:pdf` 拿 PDF 链接 + 摘要
4. fallback: 用现有数据 + 标注 `[待 L4/L5/L6 重抓]` (不直接用 placeholder,留 hook 供后续补)

**Step R4 — 生成 v0.3.3 全量 XML**
按 `Output Schema (v0.3.3 strict)` 章节的 fixed-template,11-12 个 block/论文,顺序固定。

**Step R5 — 跑 12 项 LLM 自检**
(详见 `Output Schema (v0.3.3 strict)` 章节)
- 任一 ❌ 必修正后重跑
- 全 ✅ 后才能 overwrite

**Step R6 — Overwrite**
```bash
lark-cli docs +update --api-version v2 --doc {doc_id} --command overwrite \
  --content @/tmp/rewrite-{doc_id_short}.xml
```

**Step R7 — Verify + Diff Summary**
```bash
lark-cli docs +fetch --api-version v2 --doc {doc_id} --scope outline
```
输出 diff summary:
- 5 章节是否齐全(各 1 个 <h2> 标题)
- paper card 数量(旧 vs 新)
- 4 行 taxonomy 覆盖率
- 完整作者列表覆盖率
- arXiv URL 真实率(目标:100%)

**Step R8 — Reply**
```
[X] 报告按 v0.3.3 fixed-template 重写完成:
- 删除了 N 条 v0.3.0 compact 残留
- 重写了 M 条 paper card(完整作者 + 单独标注行)
- L4 MiniMax 抓取 K 论文(arXiv 真实 URL 100%)
- L5 Kimi 补全 J 论文(完整 byline)
- L6 AnySearch 补全 L 论文(PDF 链接)

⚠️ [仍有 G 条占位,需手动补]: {title list}
🔗 新 docx URL: {url}
```

**Rewrite mode 风险控制**:
- **必先 user-confirm** 列出:"会删原 §4 重写,论文数据全部走 L4/L5/L6 重抓,4-5 分钟。OK 吗?" → user 回复"是"才执行
- 不 rewrite 不相关的 docx(只 rewrite user 提供的 URL)
- backup: rewrite 前先 `cp` 旧 docx 到 `/tmp/wiki-audit/backup-rewrite-{date}/`


### Audit mode (v0.2.8+) — 审计已有 docx

> **用途**:对**已发布**的 Feishu docx 跑 v0.2.5+ 合规检查,识别"(1) ② ████"等反模式 + TL;DR 缺失 + Persona 违规,输出修复建议。
>
> **不写飞书,只读飞书**。审计完成后,user 决定是否 overwrite 修复。

#### Audit 触发模式

| 用户输入 | 模式 |
|---------|------|
| `审计一下 https://xxx.feishu.cn/docx/MqEz...` | Audit mode |
| `看看 况琨 报告合不合规` + 已知 doc_id | Audit mode |
| `teacher-report audit MqEzdtwcso2AGyxUPuCcyQRAnwe` | Audit mode |
| `review teacher report compliance for MqEz...` | Audit mode |
| `调研一下 XXX 老师` | Generation mode(忽略 audit) |

#### Audit 流程(4 步)

**Step A1 — Fetch 现状**

```bash
lark-cli docs +fetch --api-version v2 --doc {doc_id}
```

提取 `data.document.content` (XML 字符串)。如果 fetch 失败:
- `LARK_USER_AUTH_REQUIRED` → 提示 user 跑 `lark-cli auth login`
- `404` / doc not found → 提示 user 检查 doc_id
- 其他错误 → 报原始错误,不要重试

**Step A2 — 跑 12 项合规检查**

详见 `references/audit-checklist.md`。每项输出 ✅ / ❌ + 失败时附原始片段。

| # | Check | Hard rule 引用 |
|---|-------|---------------|
| 1 | h2 章节为 5 个(顺序:TL;DR / 画像 / 匹配 / 套磁 / 论文 / 来源) | Output contract |
| 2 | h2 标题用 `1.` `2.` `3.` `4.` `5.` 风格 | SKILL.md 飞书标题号硬规则 |
| 3 | h3 标题用 `1.1` `1.2` 等子节风格 | 同上 |
| 4 | 无 h4 手动 `(1) (2) (3)` 编号 | 同上 |
| 5 | 无内联 `① ② ③` 字符 | 同上 |
| 6 | 无 `████████` 字符画趋势图 | 同上 |
| 7 | TL;DR 用 callout + grid | report-template.md §1 |
| 8 | §5 数据来源含检索时间 | report-template.md §9 |
| 9 | ≥ 3 个 callout(全文字段不算) | report-template.md 视觉丰富度 |
| 10 | table 用 `<table>` + `<colgroup>`(无 markdown table) | llm-prompt.md 反模式 |
| 11 | 论文精读含 arXiv/DOI link(无则降级) | llm-prompt.md §8 |
| 12 | Footer Persona = `claudecode teacher-report skill` | report-template.md §9 |

**Step A3 — 生成审计报告**

写到 `/tmp/teacher-report-audit-{name}-{doc_id_short}.md`,格式:

```markdown
# 审计报告 — {老师}({doc_id_short})
审计时间: {YYYY-MM-DD HH:MM}
docx URL: {url}

## 总览
- 12 项检查: ✅ X / ❌ Y / ⚠️ Z(降级)
- 合规度:{百分比}%

## 失败项详情

### ❌ Check 4: h4 手动 (1) 编号
**位置**:§2.3 论文精读
**原始片段**:`<h4>(1) 大模型 + 因果(3 篇)</h4>`
**修复建议**:改为 `<h4>1. 大模型 + 因果(3 篇)</h4>`

### ❌ Check 5: 内联 ① 字符
**位置**:§2.3 第 1 篇
**原始片段**:`<p><b>① Causality for LLMs...</b></p>`
**修复建议**:改为 `<p><b>Causality for LLMs...</b></p>`

## 修复命令(可选)

如需批量应用所有修复,user 跑:
\`\`\`bash
lark-cli docs +update --api-version v2 --doc {doc_id} --command overwrite \\
  --content "<v0.2.5-compliant XML>"
\`\`\`
```

**Step A4 — Reply to user**

1. 1 行总结:`{老师} 报告 12 项检查: ✅ 8 / ❌ 3 / ⚠️ 1,详情见 /tmp/audit-{name}.md`
2. 列出 ❌ 项(每项 1 行)
3. 提示:`如需修复,跑命令 ...`

#### Audit 模式限制

- **不直接 overwrite** — 审计完只报问题,user 决定是否修复(避免误覆盖已定制内容)
- **不抓新数据** — 只读现有 docx,不重新跑 L1-L4 数据源
- **不比对历史版本** — 单一快照,不做 diff
- **不验证内容正确性** — 只验证结构合规,内容真伪(数据来源)超出 audit 范围

## Output contract

- **Primary**: a Feishu `docx` URL (looks like `https://{tenant}.feishu.cn/docx/doxcn...`)
- **Document title**: `{学校} {老师姓名}` (e.g. "浙江大学 吴飞")
- **5 required sections in order**: TL;DR callout, 导师与课题组画像, 申博匹配度评估, 套磁与行动建议, 论文产出全景（按年）, 数据来源与说明
- **Visual elements required**: 1 TL;DR callout + 1 grid, ≥ 1 callout per section for non-text observations, all data tables formatted as `<table>` blocks (not markdown)
- **🚨 5 章节必含硬要求(2026-06-05 v0.2.6,违反 = skill 协议破坏)**:
  - 必须有 `<h2>1. ...</h2>` / `<h2>2. ...</h2>` / `<h2>3. ...</h2>` / `<h2>4. ...</h2>` / `<h2>5. ...</h2>` 5 个 h2 章节,顺序固定
  - **§2 申博匹配度评估 必须有 `<h2>2. ...</h2>` 标题**,**禁止**直接跳到 `<h3>2.1` 或 `<h4>(1)` (v0.2.3 残缺版踩过这个坑)
  - **§1 / §3 / §4 / §5 同理**必须有 `<h2>` 标题,不能缺
  - 模板生成后,LLM 必须自检:`grep -c '<h2>' content` ≥ 5
- **🚨 论文条目 paper card 硬要求 (2026-06-08 v0.3.3,违反 = skill 协议破坏)**:
  - 所有论文 (§4 论文产出全景 / §2.2 论文举例 / §3 套磁信引用 任何位置) **必须**用 `## Paper Entry Format (v0.3.3) — 硬要求` 章节定义的 paper card 格式
  - **必须包含 4 维 taxonomy 4 行独立 <p> 块**(`大领域：` / `中方向：` / `小任务：` / `子技术：` 每行 1 字段)— **禁止** 4 列表格
  - **作者列表: 写完整 verbatim**,禁止 `(末位/通讯)` 缩写 / `(通讯 PI 模式)` 描述 / `... 16 名作者` 省略
  - **标注行: 单独成行**: `通讯作者：`, `一作/共一：`, `学生：` 等独立 `<p>` 块
  - **Fei Wu 显式标 `Fei Wu（吴飞）`**(中文括号),即使排在第 1 位
  - **禁止**简化为表内 1 行 / `<p><b>{标题} (venue year) ⭐</b></p>` 紧凑格式 / 省略作者列表 / 省略 taxonomy / 用 4 列表格 / 用缩写
  - LLM 必须自检:每篇论文均含 4 维 taxonomy 4 行 + 完整作者列表 + 标注行 + `发表：` `arXiv：` `paperscool：` 3 个字段

## Paper Entry Format (v0.3.3, 2026-06-08) — 硬要求

> **背景**:v0.3.0 之前 docx 论文展示痛点:① 没法快速核对 author 完整性和通讯作者标注 ② 没法给 Fei Wu 显式高亮(通讯作者被埋没) ③ 没法直接跳到 arXiv 全文(用户必须自己搜) ④ 论文在 4 级研究 hierarchy(大领域→中方向→小任务→子技术)中的位置不可见,套磁信无法精准定位方向。
>
> **v0.3.0 → v0.3.1 → v0.3.2 → v0.3.3 升级**: 
> - **v0.3.1**: 在原 6 行 paper card 基础上,**追加 4 维 taxonomy** (大领域/中方向/小任务/子技术) — 但用 4 列表格
> - **v0.3.2 hotfix**: 4 维 taxonomy 改为 4 行独立 <p> 块(每字段一行,不是表格)
> - **v0.3.3 hotfix (2026-06-08)**:
>   1. **作者列表: 写完整 verbatim**。禁止 "(末位/通讯)" 或 "(通讯 PI 模式)" 描述性缩写 — 必须 verbatim 列出全部作者
>   2. **标注行: 单独成行**。作者身份/位置/学生身份等元信息(谁通讯、谁一作、谁是 Fei Wu)写独立 `<p>标注：</p>` 段,不混在作者列表里
>   3. **Fei Wu 显式标 `Fei Wu（吴飞）`**(中文括号),即使排在第 1 位
> - 原因: 表格形式在飞书 UI 里读起来割裂; 模板构造的"(末位/通讯)"缩写无法审计、可读性差

### Paper Card 模板(v0.3.3,每篇论文一份,无例外)

```
{论文完整标题 (verbatim, 不可改字/改序/省字)}
大领域：{大领域}    ← 1 行 1 字段,不是表格
中方向：{中方向}
小任务：{小任务}
子技术：{子技术}
作者：
{作者 1, 作者 2, 作者 3, ..., Fei Wu（吴飞）, ..., 末位作者}    ← 全部 verbatim 列出(无 et al. 无缩写),吴飞显式标 Fei Wu（吴飞）
标注：
通讯作者：{通讯 1, 通讯 2}    ← 单独成行;不混在作者列表里
一作/共一：{一作 1, 一作 2}    ← 第一作者(可多个,共一用括号)
学生：{学生 1, 学生 2}    ← 博士生/硕士生身份,标 (学生) 后缀
发表：{venue year (角色)}    ← 例: ACL 2025 (Oral) / ICLR 2026 (Spotlight) / KDD 2024 (Long Paper) / TPAMI 2024 (期刊) / arXiv preprint
arXiv：https://arxiv.org/abs/{arxiv-id}    ← 必须 arXiv ID;无 arXiv 用 DOI
paperscool：https://papers.cool/arxiv/{arxiv-id}    ← 必须,这是 user 1-click 阅读入口
```

#### v0.3.1 → v0.3.2 关键变化

- **4 维 taxonomy 从 4-列表格改为 4 行独立 <p> 块**(`大领域：` / `中方向：` / `小任务：` / `子技术：` 每行 1 字段)
- 表格形式在飞书 UI 里读起来割裂;4 行更清晰可读,可直接 grep/复制
- LLM 输出格式示例:
  ```html
  <p>大领域：人工智能</p>
  <p>中方向：强化学习</p>
  <p>小任务：探索策略</p>
  <p>子技术：状态启发式; 空间链接; 新颖性鼓励</p>
  ```

#### 4 维 taxonomy 填写规范

| 字段 | 说明 | 示例 |
|------|------|------|
| **大领域** | 最上层研究领域(2-5 个候选:CV / NLP / 图形学 / 多媒体 / 机器学习 / 具身智能) | 计算机视觉 / 自然语言处理 / 多模态 / 推荐系统 |
| **中方向** | 大领域下的细分方向(导师的主线方向,通常 5-15 个候选) | 多模态大模型 / GUI Agent / 视觉问答 / 端云协同 / 通用分割 |
| **小任务** | 中方向下的具体任务(论文直接解决的子问题) | 图像编辑 / 点云理解 / 视频问答 / 智能体规划 |
| **子技术** | 实现小任务的关键技术 / 方法(论文核心贡献) | 扩散模型 / 注意力机制 / RLHF / 思维链 / 世界模型 |

> 4 维 taxonomy 关系:**大领域 ⊃ 中方向 ⊃ 小任务 ⊃ 子技术**。每篇论文对应唯一的 4 元组。LLM 必须从论文 abstract + 引言 + 方法 章节判定,**禁止**用 placeholder(如"未知 / N/A")。
>
> **v0.3.2 强制输出格式**: 每字段 1 个独立 `<p>` 块,不是 1 个 4-列 `<table>`。例:见上方 Paper Card 模板。

### 字段规范(v0.3.1,共 9 字段)

| 字段 | 必填 | 规则 |
|------|------|------|
| **大领域** | ✅ | 4-列 taxonomy 第 1 列;最上层研究领域,5-10 候选 (CV / NLP / 多媒体 / 机器学习 / 具身智能 / 推荐系统) |
| **中方向** | ✅ | 4-列 taxonomy 第 2 列;大领域下细分方向,5-15 候选 (多模态大模型 / GUI Agent / 视觉问答 / 端云协同 / 通用分割) |
| **小任务** | ✅ | 4-列 taxonomy 第 3 列;中方向下具体任务,论文直接解决的子问题 (图像编辑 / 点云理解 / 视频问答 / 智能体规划) |
| **子技术** | ✅ | 4-列 taxonomy 第 4 列;实现小任务的关键技术,论文核心贡献 (扩散模型 / 注意力机制 / RLHF / 思维链 / 世界模型) |
| **标题** | ✅ | verbatim, 不可改字/改序/省字;**禁止**用缩写或 et al. 替代 |
| **作者** | ✅ | 全部列出(无 et al.), 用 `, ` 逗号+空格分隔; **Fei Wu 显式标 `Fei Wu（吴飞）`** (中文括号标注), 即使排在第 1 位 |
| **发表** | ✅ | `{venue} {year} ({角色})`, 角色可省: Oral / Spotlight / Poster / Long Paper / Short Paper / Findings / Track 1 / Invited Talk / Preprint |
| **arXiv** | ✅ | URL 必含 `https://arxiv.org/abs/{id}`;无 arXiv 用 `https://doi.org/{DOI}` 兜底 |
| **paperscool** | ✅ | URL 必含 `https://papers.cool/arxiv/{id}`;与 arXiv ID 一致;**禁止**漏 |

### 正确示例 (v0.3.3,完整作者列表 + 单独标注行)

```
OS Agents: A Survey on MLLM-based Agents for General Computing Devices Use
大领域：多模态
中方向：智能体 Agent
小任务：OS 操作
子技术：综述 + Benchmark
作者：
Xueyu Hu, Tao Xiong, Biao Yi, Zishu Wei, Ruixuan Xiao, Yurun Chen, Jiasheng Ye, Meiling Tao, Xiangxin Zhou, Ziyu Zhao, Yuhuai Li, Shengze Xu, Shenzhi Wang, Xinchen Xu, Shuofei Qiao, Zhaokai Wang, Kun Kuang, Tieyong Zeng, Liang Wang, Jiwei Li, Yuchen Eleanor Jiang, Wangchunshu Zhou, Guoyin Wang, Keting Yin, Zhou Zhao, Hongxia Yang, Fan Wu, Shengyu Zhang, Fei Wu（吴飞）
发表：ACL 2025 (Oral)
arXiv：https://arxiv.org/abs/2508.04482 
paperscool：https://papers.cool/arxiv/2508.04482
```

#### 4 维 taxonomy 反推流程 (从论文 abstract → 4 字段)

| 步骤 | 操作 | 工具/来源 |
|------|------|----------|
| 1. 读 abstract 末 2 句 | 提取"解决什么任务 / 用什么方法" 关键词 | paper abstract |
| 2. 查 venue 标签 | 标 ACL/NeurIPS/CVPR → 大领域候选 | arXiv abs 页 venue 字段 |
| 3. 标"小任务" | abstract 中"我们提出 X 用于 Y" 的 Y | abstract + 引言 |
| 4. 标"子技术" | abstract 中"基于 Z 改进 / 采用 Z" 的 Z | abstract + 方法章节 |
| 5. 标"中方向" | 综述论文 → 大领域 + 小任务聚合;否则 = 大领域下导师主线方向 | 课题组主页 + L1 |
| 6. 标"大领域" | 5 选 1:CV / NLP / 多模态 / 机器学习 / 具身智能 | 综述标题 + L1 |
| 7. 校验 hierarchy | 4 字段必须满足大领域 ⊃ 中方向 ⊃ 小任务 ⊃ 子技术 | LLM 自检 |

> **常见 taxonomy 错误**:
> - 大领域="Computer Vision" 错 → 应写"计算机视觉"(中文一致)
> - 子技术="提出新方法" 错 → 必须具体(扩散模型 / 注意力 / RLHF)
> - 中方向="深度学习" 错 → 太宽,应写"多模态大模型" 或 "端云协同"
> - 4 字段字数差异大(1 字 vs 20 字)→ 标准化为 4-8 字关键词

### 反例 (v0.3.0 全部禁止)

```
❌ OS Agents  ACL 2025, Hu et al.                          ← 1 行简化
❌ OS Agents (ACL 2025 Oral) ⭐                             ← 标题 + venue 1 行,无作者
❌ <p><b>OS Agents (ACL 2025 Oral) ⭐</b></p>               ← HTML 紧凑格式
❌ Xinyu: ... (Yiquan Wu, Bo Tang, ... 16 名作者)          ← 作者被压在标题括号里
❌ Wu et al. (2025) OS Agents ACL                          ← 缩写 + 顺序错乱
❌ arXiv: 2508.04482                                       ← arXiv 没给 URL
❌ paperscool (省略)                                       ← 缺 user 1-click 入口
❌ 大领域:CV | 中方向:Agent | 小任务:GUI | 子技术:RL      ← 单行 taxonomy 压平 (应 4 行)
❌ <table>大领域 中方向 小任务 子技术</table>                ← 4 列表格 (应 4 个 <p> 块)
❌ 作者：... (末位/通讯), Fei Wu                           ← (末位/通讯) 缩写 (应写完整 + 单独标注)
❌ 作者：... (通讯 PI 模式)                                 ← 模式描述 (应写完整作者 + 标注)
```

### 适用位置 (全 docx 强制,5 章均生效)

1. **§4 论文产出全景** — 每个分年表**上方或下方**列出该年所有论文的 paper cards (year ≥ 3 篇 → 列在表下; year 1-2 篇 → 可用 callout 装)
2. **§2.2 方向匹配度** — 引用具体论文举例时, 用 paper card 格式 (5 字段+作者)
3. **§3 套磁与行动建议** — 套磁信草稿引用具体论文时, paper card 块嵌入
4. **§1 TL;DR** — 提到"代表论文"时, paper card 列在 callout 下方
5. **§1.2 / §1.3 学生代表作** — 列每位博士代表作时, paper card

### 与 v0.2.5 旧"论文精读子段模板"的关系

| 维度 | v0.2.5 (旧) | v0.3.0 (新) |
|------|-------------|-------------|
| 论文展示形式 | 表内 1 行 / `<p><b>...</b></p>` 紧凑 | 6 行 paper card |
| 作者列表 | 禁止 (et al.) | 必须 (全名 + Fei Wu 中文标注) |
| arXiv 链接 | inline `<a href>` 在标题后 | 独立 `arXiv：` 行 |
| papers.cool | 无 | 必须 `paperscool：` 行 |
| 信息密度 | 低 (5 字段 UL 跟在标题后) | 高 (一篇一段,可独立打印) |

> **迁移指南**: 现有 v0.2.5-v0.2.9 的 docx 跑 audit mode (Check 13) 时,会标 ❌ "缺少 paperscool" / "缺少作者列表",给出修复建议。修复时用 `lark-cli docs +update --command block_replace` 把每个 `<p><b>{title} (venue year) ⭐</b></p>` 替换为对应 6 行 paper card block。
>
> **v0.3.0 → v0.3.1 迁移**: 现有 v0.3.0 docx 跑 audit mode (Check 14) 时,会标 ❌ "缺 4-列 taxonomy 分类表"。修复时:对每篇 paper card 跑 `block_insert_after` 在 `<p>{title}</p>` 后插入 4-列 table,然后 `block_replace` 改 taxonomy cell 值。LLM 需从 paper abstract 反推 4 维 taxonomy (参考 report-template §6.2 taxonomy 反推 prompt)。

### Audit Check 13 (2026-06-08 v0.3.0 6-行 paper card)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 13a | 论文条目 ≥ 6 行 (标题 + 5 字段) | 100% paper cards 符合 6 行结构 | ❌ 简化为 1 行 → 必须扩为 6 行 |
| 13b | 含 `作者：` `发表：` `arXiv：` `paperscool：` 4 个字段前缀 | 100% 4/4 | ❌ 缺任一字段 → 必须补 |
| 13c | `Fei Wu（吴飞）` 显式标注 | 100% Fei Wu 署名的论文 | ❌ 漏 `（吴飞）` → 必须补中文括号 |
| 13d | arXiv URL = `https://arxiv.org/abs/{id}` | 100% 链接规范 | ❌ 缺 URL / 用缩写 ID → 必须规范化 |
| 13e | paperscool URL = `https://papers.cool/arxiv/{id}` | 100% 链接规范 | ❌ 缺 papers.cool 入口 → 必须补 |

> Check 13 的 5 子项 (a-e) 全 ✅ 才算 Check 13 PASS;任一 ❌ = Check 13 FAIL (3 ❌ = 整体审计 fail, 降级为 🟡)。

### Audit Check 14 (2026-06-08 v0.3.1 新增 — 4 维 taxonomy)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 14a | 每篇 paper card 含 4 维 taxonomy 4 行独立 <p> 块(大领域/中方向/小任务/子技术) | 100% 论文含 4 行 | ❌ 缺 4 行 / 用了 4 列表格 → 必须改为 4 个 <p> 块 |
| 14b | taxonomy 4 字段均有具体值(无 `未知` / `N/A` / `待补` placeholder) | 100% 4/4 | ❌ placeholder → 必须从 abstract 抽取或 L1-L4 反查 |
| 14c | 4 维 hierarchy 一致性:大领域 ⊃ 中方向 ⊃ 小任务 ⊃ 子技术 | 100% 无逻辑冲突 | ❌ 跨级冲突(如"小任务=图像编辑"配"子技术=RLHF")→ 必须重判 |
| 14d | taxonomy 描述 ≤ 12 字(简洁,可对比) | ≥ 95% 论文满足 | ❌ 过长 → 截断为关键词 |

> Check 14 的 4 子项 (a-d) 全 ✅ 才算 Check 14 PASS;任一 ❌ = Check 14 FAIL (≥ 3 ❌ = 整体审计 fail, 降级为 🟡)。

### Audit Check 15 (2026-06-08 v0.3.3 新增 — 完整作者列表 + 单独标注行)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 15a | 作者列表 verbatim 全列 | 100% 论文完整列出全部作者,无 `et al.` / 无 `... N 名作者` 省略 / 无缩写 | ❌ 缩写 → 必须补全作者列表(查 arXiv abs 页) |
| 15b | 禁止 `(末位/通讯)` / `(通讯 PI 模式)` 等描述性缩写 | 100% 作者行无描述性缩写 | ❌ 缩写 → 必须 verbatim 复制 + 标注行单列 |
| 15c | 标注行: 通讯作者/一作/学生 独立成行 | 100% 论文含 `<p>标注：</p>` 段 | ❌ 缺标注行 → 必须从 arXiv byline 抽取并单列 |
| 15d | Fei Wu 显式标 `Fei Wu（吴飞）` 即使排第 1 | 100% Fei Wu 署名论文 | ❌ 漏 `（吴飞）` → 必须补中文括号 |

> Check 15 的 4 子项 (a-d) 全 ✅ 才算 Check 15 PASS;任一 ❌ = Check 15 FAIL (≥ 3 ❌ = 整体审计 fail, 降级为 🟡)。

## Output Schema (v0.3.3 strict, 2026-06-08)

> **背景**:v0.3.3 之前 skill 输出混乱(混 4 列表 + 4 行 + 缩写 + 占位符)。本节定义**严格的输出 schema**,LLM 写每篇 paper card 严格按 schema 走,自检 12 项通过才允许输出。

### 强制 Output Schema — v0.3.3 paper card block 结构

每篇论文 paper card **必须**由以下 11 个 block 顺序构成(顺序固定,不可调换):

```
1. <p>                          ← 标题 (verbatim,不可改字/改序/省字)
2. <p>大领域：{X}</p>             ← 4 行 taxonomy(每行 1 <p> 块,不是 table)
3. <p>中方向：{X}</p>
4. <p>小任务：{X}</p>
5. <p>子技术：{X}</p>
6. <p>作者：</p>                 ← 作者段头(空 <p>,下个 block 是作者列表)
7. <p>{完整作者列表}</p>           ← verbatim 完整作者,无 et al.,无缩写,Fei Wu 显式标（吴飞）
8. <p>标注：</p>                 ← 标注段头(空 <p>,下个 block 是标注)
9. <p>通讯作者：{X}</p>           ← 独立标注行(可选,无则整段省略)
10. <p>发表：{venue year (角色)}</p>  ← 发表信息
11. <p>arXiv：<a href="https://arxiv.org/abs/{id}">https://arxiv.org/abs/{id}</a></p>  ← **优先 arXiv URL**;若论文无 arXiv 预印本,改用原会议/期刊网址 (例: SIGMOD `https://dl.acm.org/doi/10.1145/{doi}`、 ASPLOS `https://dl.acm.org/doi/10.1145/{doi}`、 CVPR `https://openaccess.thecvf.com/content/CVPR{YEAR}/html/{paper}.html`、 NeurIPS `https://proceedings.neurips.cc/paper/{YEAR}/hash/{hash}-Abstract.html`、 期刊 `https://ieeexplore.ieee.org/document/{id}`)。禁止 `[待验证]` 占位符 — 必须有 1-click 入口
12. <p>URL 类型：arXiv 预印本</p>  ← 或 `<p>URL 类型：会议正式版 (SIGMOD/ASPLOS/CVPR/...)</p>` 标注 URL 来源类型,让用户一眼区分
```

### 12 项 LLM 自检清单(写完 paper card 必跑,任一 ❌ 必须修正后才能输出)

| # | 检查项 | 通过条件 | 常见错误 |
|---|--------|---------|---------|
| 1 | 标题 verbatim | 完全从 arXiv abs 页复制,无改字/改序/省字 | ❌ "OS Agents: Survey" (缺 "A Survey on MLLM-based Agents for General Computing Devices Use") |
| 2 | 标题无 et al. 缩写 | 完整标题,无 "et al." 替代 | ❌ "Xinyu: ... (Yiquan Wu et al., 16 authors)" |
| 3 | 4 行 taxonomy 顺序 | 顺序固定:大领域→中方向→小任务→子技术,每行独立 `<p>` 块 | ❌ 单行 "大领域:CV\|中方向:Agent\|小任务:GUI" 压平 |
| 4 | 4 行 taxonomy 无 table | **禁止** 4 列表格 `<table>`,**必须** 4 个 `<p>` 块 | ❌ `<table>大领域 中方向 小任务 子技术</table>` |
| 5 | taxonomy 无占位符 | 4 字段均有具体值,无 "未知" / "N/A" / "待补" | ❌ `<p>大领域：待补</p>` |
| 6 | 作者完整 verbatim | 全部列出,无 "... N 名作者" 省略,无 et al. | ❌ "Xueyu Hu, Tao Xiong, ... 27 名作者, Fei Wu" |
| 7 | 禁止 (末位/通讯) 缩写 | 作者行无 "(末位/通讯)" / "(通讯 PI 模式)" 描述 | ❌ "作者：..., (末位/通讯), Fei Wu" |
| 8 | 禁止 (通讯 PI 模式) 描述 | 作者行无 "通讯 PI 模式" 等描述性短语 | ❌ "作者：... (通讯 PI 模式)" |
| 9 | Fei Wu 显式标 (吴飞) | 100% Fei Wu 署名论文含 `Fei Wu（吴飞）`(中文括号) | ❌ "Fei Wu" 漏中文括号 |
| 10 | 标注行单独成行 | 通讯作者/一作/学生 独立 `<p>标注：</p>` 段,不混作者列表 | ❌ "作者：..., (通讯), ..., 一作 Xueyu" |
| 11 | 真实 1-click URL (arXiv 优先 / 会议期刊兜底) | 100% 论文有 1-click 入口 URL;有 arXiv 用 arxiv.org,无 arXiv 用 dl.acm.org/openaccess.thecvf.com/proceedings.neurips.cc/ieeexplore.ieee.org,**禁止** `[待验证]` 占位符 | ❌ `<p>arXiv：待 arXiv 验证</p>` (应填会议 doi) / ❌ 缺 URL |
| 12 | paperscool 真实 URL | `<a href="https://papers.cool/arxiv/{id}">...</a>` 完整 URL,非占位 | ❌ `<p>paperscool：待 arXiv 验证</p>` |

> 12 项全 ✅ 才能输出 paper card;任一 ❌ 必须修正后重跑自检

### v0.3.3 fixed-template (LLM 输出时直接 fill)

```xml
<p>{TITLE}</p>
<p>大领域：{D}</p>
<p>中方向：{M}</p>
<p>小任务：{T}</p>
<p>子技术：{S}</p>
<p>作者：</p>
<p>{A1}, {A2}, {A3}, ..., Fei Wu（吴飞）, ..., {An}</p>
<p>标注：</p>
<p>通讯作者：{CORR1}, {CORR2}</p>
<p>一作/共一：{FIRST1}, {FIRST2}</p>
<p>学生：{STU1} (学生), {STU2} (学生)</p>
<p>发表：{VENUE} {YEAR} ({ROLE})</p>
<p>arXiv：<a href="https://arxiv.org/abs/{ARXIV_ID}">https://arxiv.org/abs/{ARXIV_ID}</a></p>  ← 优先 arXiv
<p>URL 类型：arXiv 预印本</p>  ← 或 "URL 类型：{VENUE_ABBR} 正式版"
<p>paperscool：<a href="https://papers.cool/arxiv/{ARXIV_ID}">https://papers.cool/arxiv/{ARXIV_ID}</a></p>  ← arXiv 才有 paperscool;无 arXiv 跳过此行

--- v0.3.5 无 arXiv 兜底模板 (e.g. SIGMOD/ASPLOS/CVPR 正式版) ---

<XML><![CDATA[
<p>arXiv：无预印本</p>
<p>URL 类型：{VENUE_ABBR} 正式版</p>
<p>论文网址：<a href="{VENUE_URL}">{VENUE_URL}</a></p>  ← dl.acm.org/doi/... 或 openaccess.thecvf.com 或 proceedings.neurips.cc
]]></XML>
```

### 完整文档规则(v0.3.5+ 必须遵守)

每篇生成的 doc **必须**是一份完整、自包含、可独立阅读的文档。**禁止**以下"画蛇添足"meta-描述:

```
❌ "本次重写以 §4 论文产出 v0.3.3 规范化为重点"
❌ "详细画像见原报告 §1"
❌ "v0.3.3 重写版 (2026-06-08)"
❌ "本次调研以 [某] 方向为重点"
❌ "本节仅作为 v0.3.3 重写标记"
❌ "更多论文见原 doc 表格"
❌ 任何"以...为标记/重点/版本"元描述
```

**正确做法**:5 章节全部填实,§1 画像完整,§2 匹配度具体,§3 套磁信有 call-to-action,§4 论文全列,§5 数据源标检索时间。**不要告诉用户"省略了 X"或"见原报告"**。

### §C 块级升级协议(v0.3.6+ 必须遵守)

**禁止**用 `docs +update --command overwrite` 重写整个 doc(v0.3.5 我犯过这错,删了原 200+ KB 内容)。

正确做法:**保留所有原内容**,只对不规范的元素用块级操作升级:

| 操作 | 适用场景 | 命令 |
|------|---------|------|
| `block_insert_after` | 在某 block 后插入新 block(如 4 行 taxonomy) | `lark-cli docs +update --api-version v2 --doc X --command block_insert_after --block-id <h4_id> --content @4tax.xml` |
| `block_replace` | 替换某 block(如 4 列表格换 4 行) | `lark-cli docs +update --api-version v2 --doc X --command block_replace --block-id <table_id> --content @4lines.xml` |
| `block_delete` | 删除冗余 block(如重复 paper card) | `lark-cli docs +update --api-version v2 --doc X --command block_delete --block-id <id>` |
| `str_replace` | 局部文字替换(如 删 "(末位/通讯)" 缩写) | `lark-cli docs +update --api-version v2 --doc X --command str_replace --pattern "..." --content "..."` |

**overwrite 的使用边界**(极严格):
- **仅**当用户**显式**说"按 v0.3.5 模板完整重写"+提供完整新数据(新论文清单 + 完整作者列表 + 真实 arXiv ID)
- **绝不**在"重写 / 规范化 / 升级"等模糊指令下用 overwrite
- overwrite 前必先 `cp` 备份原 docx 到 `/tmp/wiki-audit/backup-overwrite-{date}/`
- 备份内容保留 ≥ 7 天

**块级升级的优先级清单**(按 v0.3.5/3.6 升级):
1. 4 列表格 → 4 行 p blocks (Check 14a)
2. paper card 缺 4 行 taxonomy → block_insert_after
3. paper card 缺完整作者 → 抓 arXiv 补 + block_replace
4. paper card 缺标注行 → block_insert_after
5. 全文 "(末位/通讯)" 缩写 → str_replace
6. 全文 "v0.3.3 重写版" framing → str_replace

### §D 备份要求(v0.3.6+ 强制)

**任何块级操作前必先 backup 当前 doc 全文**到 `/tmp/wiki-audit/backup-{date}-{teacher}/`:

```bash
TOKEN="EFlmwpPgKiUARAkTplIcoOqrn3w"
DATE=$(date +%Y%m%d)
TEACHER="wufei"
mkdir -p /tmp/wiki-audit/backup-$DATE-$TEACHER
lark-cli docs +fetch --api-version v2 --doc $TOKEN --detail with-ids --format json \
  > /tmp/wiki-audit/backup-$DATE-$TEACHER/original.xml
```

如果发现"删太多",从 backup 恢复:
```bash
cd /tmp/wiki-audit/backup-$DATE-$TEACHER
lark-cli docs +update --api-version v2 --doc $TOKEN --command overwrite --content @original.xml
```

### "脏"输出反例 (v0.3.3 全部禁止)

```
❌ <table>大领域 中方向 小任务 子技术</table>          ← 4 列表格
❌ <p>大领域:CV|中方向:Agent|小任务:GUI|子技术:RL</p>  ← 单行压平
❌ 作者: ..., (末位/通讯), Fei Wu                     ← 缩写
❌ 作者: ..., (通讯 PI 模式)                            ← 模式描述
❌ Xinyu: ... (Yiquan Wu, Bo Tang, ... 16 authors)      ← 省略
❌ arXiv: 2508.04482                                    ← 不是 URL
❌ arXiv: 待 arXiv 验证                                  ← 占位符
❌ paperscool (省略)                                     ← 缺 user 1-click 入口
❌ Wu et al. (2025) OS Agents ACL                       ← 缩写 + 顺序错乱
```

### Output Schema 强制流程(LLM 必须按此顺序执行)

```
1. 写完论文 abstract 后 → 反推 4 维 taxonomy (从 abstract + 引言 + 方法)
2. 抓 arXiv abs 页 → 复制完整标题 + 完整作者列表 + arXiv ID + venue/year/role
3. 标注 (通讯作者/一作/学生) → 从论文 byline + 课题组主页查
4. 按 v0.3.3 fixed-template 顺序填 11-12 个 block
5. 跑 12 项 LLM 自检清单 → 任一 ❌ 必须修正后重跑
6. 全 ✅ 后才能进 1v1 block 写入
```

### v0.3.3 + 后续清理路径

- **新生成的 doc**(teacher-report --mode generate):严格按 v0.3.3 schema + 12 项自检
- **已有 v0.3.0/3.1/3.2 的 doc**:跑 audit mode Check 13+14+15,会标 ❌ "未用 v0.3.3 schema"
- **修复方法**:`overwrite` 整篇 doc,重写时用 v0.3.3 fixed-template

---

## Anti-Hallucination Rules (v0.2.9, 2026-06-06)

> **背景**:v0.2.8 之前的 teacher-report 曾出现系统性幻觉 —— 5 字段(论文状态/年份/作者/学生身份/职务)直接从 AI 推断而非平台校验,5 篇 ICLR 2026 论文"已撤稿"标注全部错误,行政职务滞后 2 个时间点。**后续 v0.2.9+ 必须强制走以下规则**。

### 6 类事实主张的强制校验矩阵

| 字段 | 必查源 | 不允许的来源 | 失败处理 |
|------|--------|-------------|---------|
| **论文发表状态**(Withdrawn/Accepted/Rejected/Submitted) | OpenReview API (`openreview.net/forum?id=...`) **OR** arXiv 摘要页 | ❌ AI 推断、❌ 二手数据库快照、❌ 课题组主页文字 | 查不到 → 标"❓状态未核 (OpenReview/arXiv 未公开)"，不写"已撤稿"或"已接收" |
| **发表年/月** | arXiv 首次提交时间戳 OR DOI 公布时间 | ❌ 论文里写"2025"但实际 arXiv 提交"2024"的情况 | 必须给出 arXiv ID 或 DOI 作为锚点 |
| **论文标题 + 作者** | arXiv abs 页 `Title:` `Authors:` 字段 | ❌ 凭印象写(中文名常错字,如"叶鑫海"vs"叶昕海") | 标题必须 verbatim 复制,作者必须 verbatim 复制 |
| **导师行政职务** | 现任学校官网"现任职务"页(注意时间戳) | ❌ 旧版缓存、❌ 3 年前的新闻稿、❌ 维基类聚合页 | 必须给出官网 URL,注意区分"曾任"(过去)vs"现任" |
| **学生身份归属** | 论文 byline + 课题组主页"组内成员"页 | ❌ "高频合作 = 学生"(合作者也可能是同事) | 论文里 byline + 合作频率 ≥ 5 篇 + 推断"<推断>"前缀 |
| **统计数字**(104 篇、CCF-A ~65 等) | L1-L4 抓取后**实际计数**,不预估值 | ❌ "估算"、"约" | 必须给精确数字(自报"+"多少待补充) |

### 3 个生成层 + 1 个使用层防御

#### 生成前(L1-L4 抓取阶段)

- 任何 L1-L4 抓取后,关键字段(year/status/author/title)必须有可追溯的 URL/arXiv ID
- L1 抓到 SPA 不全时,必须切 playwright 渲染,不要只 webfetch(见 Failure handling)
- 优先使用 **OpenReview API** (`https://api.openreview.net/notes`) 批量查 ICLR/NeurIPS 等会议的状态(撤回/接受/审稿中),不要靠搜索结果拼凑

#### 生成中(LLM synthesis 阶段)

- **关键字段不预填**:LLM 写论文清单时,状态列如果 L1-L4 没明确给出,留空 + 标"待核",**不**凭"看起来像 Withdrawn"就填 Withdrawn
- **数字必精确**:统计 "104 篇" 这种,必须是 L1-L4 实际抓到的论文数,**不**用"约 100"或"估算"
- **名字 verbatim**:作者中文名必须从 arXiv abs 页 verbatim 复制,AI 不要"纠正"看起来错的中文字(常因 OCR/转写污染)

#### 生成后(LLM 自检阶段)

- **5 字段抽样自检**:写完 docx 后,LMM 必须**随机抽 5 篇**论文,逐条在 arXiv/OpenReview 上核对(year + status + authors),不通过 → 重写该字段
- **可信度标签**:每篇论文的 status 列后必须可加 `[v: arxiv:2512.09396]` 或 `[v: openreview:xxx]` 标签(可选用),让用户能看到哪些字段被实时核过

#### 使用时(用户使用 / 后续 agent 复用)

- **AI-to-AI 不免责**:后续 agent 拿到本 skill 生成的 docx 做编辑/审计/补强时,**任何事实主张必须重新核**,不允许"原文写的所以照搬"
- **抽样校验 ≥ 10%**:用户拿到 docx 后,使用前应至少抽样 10% 的论文在 arXiv/OpenReview 上验证;**不验证 = 接受幻觉风险**
- **"AI 整理"红线**:文档底部如有"整理人:AI"字样,后续使用者必须降低置信度,优先复核关键决策字段(导师职务/招生状态/论文状态)

### 4 类绝对禁止(违反 = skill 协议破坏)

1. **❌ 禁止**"凭印象 / 估算 / 大约"写论文状态 → 必须可追溯到 arXiv / OpenReview
2. **❌ 禁止**照搬前任 AI 输出不做事实复核 → AI-to-AI 链式污染
3. **❌ 禁止**用"高置信度模板"装饰不确凿的事实(例如把未核的"导师职务"放在 TL;DR callout 高亮框里,会被用户当作可信结论)
4. **❌ 禁止**把"未核"状态字段(❓)藏在大段表格里,必须显式标黄/标红/单独成行,让用户能一眼看到哪些是"待补"

## Failure handling

| Failure | What to do |
|---------|------------|
| L1-L4 all return nothing | Stop, tell the user "信息黑洞 — 五级抓取都失败,建议手动提供主页 URL 或姓名 + 单位"。Do not fabricate. |
| L1 成功 + L2/L3/L4 部分失败(半失败):L2 抓到的近 3 年论文 < 5 篇,或 venue 验证不全 | 🟡 中。报告顶部 ⚠️ callout 必须显式标"**数据稀疏 — 套磁信引文可能不准确**",**禁止**在套磁信里引用 L2 没验证过的论文。 |
| L1 成功 + 近 3 年署名论文 ≥ 30 篇,但**本人一作 / 共一论文 = 0** | 🟡 中。典型"通讯/末位 PI 模式",实际带生者高度疑为青年教师。报告中必须显式标红 + 套磁信必须追问 1v1 带生安排。 |
| 课题组定位"双核心 / 三核心"硬塞给学生代笔模式 | ⛔ **禁止**(见 `report-template.md §3` 反模式段)。如果导师是末位/通讯 PI、实际带生者疑为青年教师,**必须**用 ⚠️ callout 显式标"实际带生者高度疑似 X,导师时间投入 < 50%,需邮件确认 1v1 带生安排"——不可包装成"X-Y 双核心"或"X-Y-Z 三核心" callout(那是把"学生代笔"美化成"团队结构")。 |
| User asks for many teachers at once (≥ 3 位) | **Out of scope, redirect to `phd-scout --mode batch`**。回复模板:"`teacher-report` 一次只处理一位老师(深度报告)。如需批量调研多位老师,请告诉我 — 我会切换到 `phd-scout --mode batch` 写 Bitable 表,之后再对感兴趣的字段再做深度 `teacher-report`。" |
| Personal page exists but is JS-rendered SPA | Use `playwright` MCP `browser_navigate` → `browser_snapshot` to get rendered text. Avoid `webfetch` on SPAs. |
| L2 Semantic Scholar rate-limited (429) | 1 次重试 (5s),仍 429 跳 L3。**不要指数退避** — 5s/15s/30s/60s 在已知失败的端点上浪费 ≥2 分钟。L4 web_search 聚合是 S2 字段的有效替代。 |
| User has not enabled lark-cli auth | The `docs +create` call will return `LARK_USER_AUTH_REQUIRED`. Tell the user to run `lark-cli auth login` and retry. |
| LLM output exceeds `--content` size limit | Split into skeleton + appends per Step 3. |
| Same teacher fetched twice with different results | Trust L2 (Semantic Scholar) h-index + paperCount over L1 self-claimed numbers. Note both in `5. 数据来源`. |

## Examples

### Example 1 — single, full data
- Input: "调研一下浙江大学计算机学院的吴飞老师,看适不适合申博"
- Fetch: L1 (ZJU 主页) → L2 (S2 API 50+ papers) → L3 (DBLP) → L4 (kunkuang.github.io for 况琨 context)
- Output: docx URL with 5 sections, TL;DR shows 🟢 高匹配, 论文按 2023-2026 分年展示

### Example 2 — sparse data
- Input: "看看清华的 XXX 副教授"
- Fetch: L1 404, L2 returns 12 papers, L3 returns 8 (overlap with L2), L4 returns a stale personal page from 2019
- Output: docx URL with TL;DR showing 🟡 数据待补, `5. 数据来源` explicitly says "L1 抓取失败,依赖 L2+L3 共 8 篇去重论文"

### Example 3 — Audit mode pass (v0.2.8+)
- Input: "审计一下 MqEzdtwcso2AGyxUPuCcyQRAnwe"
- Action: Step A1 fetch → A2 12 项 check → A3 写 `/tmp/teacher-report-audit-况琨-MqEzdtwcso.md`
- Output: 1 行总结 "况琨 v0.2.4 子节点: ✅ 12/12,完全合规" + 完整报告路径

### Example 4 — Rewrite mode (v0.3.4+)

- Input: "按 skill 模板重写 https://lxpii9q8vy0.feishu.cn/wiki/P49mwGQU0iEh9CkXbCTcC418nPb"
- Action: R1 fetch → R2 解析 → R3 L4/L5/L6 重抓 → R4 11-12 block/论文 → R5 12 项自检 → R6 overwrite → R7 验证
- Output: 新 docx URL + diff summary

### Example 5 — Audit mode fail
- Input: "审计一下 [URL]" 指向 v0.2.3 模板的旧 doc
- Action: Check 4 (h4 (1) 编号) + Check 5 (① 字符) + Check 6 (████ 字符画) 失败
- Output: "吴飞 wiki: ✅ 8 / ❌ 3 / ⚠️ 1,失败项 Check 4/5/6,详见 /tmp/audit-吴飞.md;跑 overwrite 命令可修复"

## References

- `references/report-template.md` — 飞书 docx XML 模板 (TL;DR callout / 5 章节结构)
- `references/data-sources.md` — L1-L4 抓取细节 + ZJU URL 模式 + S2 API 字段
- `references/llm-prompt.md` — 总结 prompt (synthesis rules + 章节填充指引)
- `references/audit-checklist.md` — 12 项合规检查 (Audit mode 跑这份 checklist)
- `references/normalization-audit-2026-06-05.md` — 4 docx 飞书标题号规范化审计追踪(v0.2.5 → v0.2.7 重跑记录)
