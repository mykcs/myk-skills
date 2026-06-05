---
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).
  
  **Generate mode**: use when the user mentions a specific researcher / advisor / 老师 / 导师 and asks to "调研 / 写一份报告 / 整理材料 / 看看这位老师" — output is a structured 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景) ready to share. Triggers on phrases like "调研一下 XXX", "生成 XXX 老师的报告", "看看张三是不是值得报", "写一份老师材料", "PhD advisor report for XXX".
  
  **Audit mode** (v0.2.8+): use when the user provides an EXISTING docx (URL or doc_id) and asks to "审计 / 检查 / 看看合不合规 / review" — fetches the doc, runs 12 compliance checks against v0.2.5+ rules (title numbering / ① ② / block charts / TL;DR callout / 5-section completeness / Persona footer etc), outputs a pass/fail report with fix suggestions. Triggers on phrases like "审计一下 [URL]", "看看 [老师] 报告合不合规", "review teacher report compliance", "teacher-report audit [doc_id]".
  
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

### Step 0 — Mode selection (v0.2.8+)

- **Generation mode (default)**:user 提供老师姓名 / 学校,生成新 docx
- **Audit mode**:user 提供 docx URL / doc_id,审计已有 docx 合规性

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
| L4 | 个人主页 / 知乎 / Google Scholar | `web_search` for `"{name}" {university} site:{personal_domain}` or `"{name}" scholar profile` | 个人 CV、学生名单、研究亮点 |

L2 (Google Scholar) is intentionally **skipped** in mainland-China network environments — go L2 Semantic Scholar → L3 DBLP → L4 directly.

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

### Example 4 — Audit mode fail
- Input: "审计一下 [URL]" 指向 v0.2.3 模板的旧 doc
- Action: Check 4 (h4 (1) 编号) + Check 5 (① 字符) + Check 6 (████ 字符画) 失败
- Output: "吴飞 wiki: ✅ 8 / ❌ 3 / ⚠️ 1,失败项 Check 4/5/6,详见 /tmp/audit-吴飞.md;跑 overwrite 命令可修复"

## References

- `references/report-template.md` — 飞书 docx XML 模板 (TL;DR callout / 5 章节结构)
- `references/data-sources.md` — L1-L4 抓取细节 + ZJU URL 模式 + S2 API 字段
- `references/llm-prompt.md` — 总结 prompt (synthesis rules + 章节填充指引)
- `references/audit-checklist.md` — 12 项合规检查 (Audit mode 跑这份 checklist)
- `references/normalization-audit-2026-06-05.md` — 4 docx 飞书标题号规范化审计追踪(v0.2.5 → v0.2.7 重跑记录)
