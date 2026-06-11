---

**v0.7.0 changelog (2026-06-11)**: H1-H4 编号标题 dot 后缀硬要求 (`1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`). 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **15 项 LLM 自检 (14 v0.6.0 + Check 15 编号 dot 后缀)**. 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废.
**v0.6.0 changelog (2026-06-11)**: H2 标题去装饰性 emoji 硬要求 (来源 13 docs × 5 H2 = 65 段统一清理, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). 14 项 LLM 自检 (新增 Check 14: H2 标题无装饰性 emoji). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; 保留 ✅❌⚠⭐🟢🟡🔴⛔🚨 等状态/信号类 (allowlist).
**v0.4.0 changelog (2026-06-10)**: Progressive disclosure refactor (Anthropic SKILL.md 500-line best practice). 1300 → 435 lines (-67%). 3 reference files: url-validation-rules.md (277) + paper-entry-v0.3.9.md (233) + output-schema-v0.3.9.md (413). v0.3.9 paper card demoted to reference (legacy), v0.4.0 紧凑 promoted to default. 13 项 LLM 自检强化 (新增 Check 13 Wiki Subject Author Verification).
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).

  **Generate**: user mentions researcher/advisor/老师/导师 and asks "调研/写一份报告/整理材料". Output: 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景). Triggers: "调研 XXX", "生成 XXX 老师的报告", "PhD advisor report for XXX".

  **Audit (v0.2.8+)**: user provides EXISTING docx (URL/doc_id) + asks "审计/检查/合规/review". Runs 12 compliance checks (title numbering, ① ②, block charts, TL;DR, 5-section, Persona footer), outputs pass/fail + fixes. Triggers: "审计一下 [URL]", "review teacher report compliance".

  **v0.4.0 (2026-06-10) 默认紧凑 + v0.3.9 完整版 fallback**: 4-dim paper taxonomy (大领域/中方向/小任务/子技术) per line, full author list with Chinese 括注, arXiv inline title (v0.4.0 紧凑默认) 或 arXiv + papers.cool URL (v0.3.9 完整版, ≤3 篇论文时), **15 项 LLM 自检 (14 v0.6.0 + Check 15 H3 编号 dot 后缀, 2026-06-11)**, verifiable claims (v0.2.9 anti-hallucination). See body §Paper Card v0.4.0 紧凑 + references/paper-entry-v0.3.9.md (legacy) + references/output-schema-v0.3.9.md (12 项自检) + §Anti-Hallucination Rules.
  **v0.7.0 (2026-06-11) H1-H4 编号标题 dot 后缀硬要求**: 编号标题必须以 `.<space>` 结尾, 即 `1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`. 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). Check 15: H3 编号 dot 后缀 (LLM 自检强化). 与 v0.2.5 旧规则 (h3 = `1.1` 无 dot) 冲突, 旧规则作废.
  **v0.6.0 (2026-06-11) H2 标题无装饰性 emoji 硬要求**: 5 大章节 H2 标题 (导师与课题组画像 / 申博匹配度评估 / 套磁与申请建议 / 论文产出全景 / 数据来源与说明) **禁止**使用装饰性图标 emoji (👤📊✉📚📖🎯ℹ 等); 允许状态/信号类 (✅❌⚠⭐🟢🟡🔴⛔🚨). 13 docs × 5 H2 = 65 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). Check 14: H2 标题无装饰性 emoji (LLM 自检强化).

  **v0.5.0 (2026-06-10) 申博实操增强**: 5 h2 框架不变, 8 新 h3 字段叠加: §1.3 招生偏好 (名额/竞争/卡本科) + §1.4 培养模式 (指导/组会/放羊/实习) + §1.5 科研资源 (GPU/经费/出国) + §2.2 团队氛围 (优点/缺点/矛盾说法) + §2.3 毕业去向 (年限/就业/留校) + §3.2 申请时间节点 (套磁/材料/考核/录取). 数据源扩到 L7 申博论坛 (mysupervisor.org + 学院 PDF + 知乎/小红书/博客园), L7 字段用 [社区来源] 标签与 L1 官网区分. 详见 §v0.5.0 申博实操增强 章节.

  Do NOT use for: batch processing many teachers (→ `phd-scout` Bitable), single paper deep-dive, lab summary.
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

> **🚨 飞书标准标题号硬要求(v0.7.0 升级, v0.2.5 旧规则作废, 违反 = skill 协议破坏)**:
> - **h1 / h2 / h3 / h4 编号标题**:`1.` `2.` `3.` / `1.` `2.` `3.` / **`1.1.` `2.1.` `3.2.` (h3 必须带 dot 后缀)** / `1.` `2.` `3.` (h4 同 h2)
> - **核心 v0.7.0 变更**: h3 编号标题从 v0.2.5 的 `1.1` (无 dot) 升级到 v0.7.0 的 `1.1.` (有 dot 后缀), 与 h2/h4 一致。**所有 5 大章节下的 H3 编号 (1.1/1.2/1.3/1.4/1.5/2.1/2.2/2.3/3.1/3.2/3.3/5.1/5.2/5.3) 末尾必须加 `.` 再接空格**
> - **示例**:
>   - v0.2.5 旧: `2.3 毕业要求与毕业去向` ❌
>   - v0.7.0 新: `2.3. 毕业要求与毕业去向` ✓
>   - h2 不变: `1. 导师与课题组画像` (已带 dot) ✓
>   - h4 不变: `1. xxx` (已带 dot) ✓
> - **禁止**手动 `(1) (2) (3)` 编号 — 飞书 outline 不识别,user 看不到大纲
> - **禁止**论文精读内联 `① ② ③` 字符 — 用 `<p><b>完整标题</b></p>` 即可,飞书 outline 通过 h4 定位
> - **禁止** `████████` 字符画 — 趋势表用 `<table>` + 精确数字(LLM-prompt §7)
> - **不混用** `1.` / `1.1.` / `(1)` / `①` 四种编号风格 (v0.7.0 后 h3 用 `1.1.`, paper card h3 用 `1.`)
> - **论文精读标题**:完整标题 + `(venue year)` + `⭐/📝/⚠️/🆕` 状态标记(无 arXiv id / 无作者列表)
> - **执行状态**: 13 docs × 11-12 H3 = 144 段已统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb, 2026-06-11), 0 doc 仍含无 dot 的 H3 编号
> - **详见**:`references/report-template.md §5` 论文精读模板 + `references/normalization-audit-2026-06-05.md`(4 文档规范化审计追踪)

Try sources in this order. Stop when a source yields enough signal; you do not need all four.

| Level | Source | How to query | What to extract |
|-------|--------|-------------|----------------|
| L1 | 学校/学院官网 | **`webfetch` 先试静态 HTML**;失败 / 明显是 SPA 框架(`<div id="app"></div>` 标记)→ **切 `playwright` MCP** `browser_navigate` + `browser_snapshot` 拿渲染后文本。ZJU common patterns: `person.zju.edu.cn/{pinyin}` (`{pinyin}` 是 LLM 不可猜的 slug — 见 §URL 验证硬规则), `mypage.zju.edu.cn/{pinyin}`, `cs.zju.edu.cn` faculty page | 基本信息、职称、行政职务、联系方式、研究方向、代表性工作 |
| L2 | Semantic Scholar API | `https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,affiliations,paperCount,hIndex,homepage` then `/author/{id}/papers?fields=title,year,venue,citationCount,authors&limit=100` | 论文清单（近 3 年）、h-index、合作者 |
| L3 | DBLP | `https://dblp.org/search/author/api?q={name}&format=json` then `/pid/{pid}.xml` for full paper list | 论文 venue 标准化(DBLP 提供的 venue 是规范名,不是缩写) |
| L4 | MiniMax Web Search (优先) | `mcp__MiniMax__web_search` MCP tool 搜 `"{name}" {university} site:arxiv.org` 或 `"{name}" personal homepage`. Mainland China 可用 | 论文全文(arXiv abs 页面)、个人 CV、学生名单、研究亮点 |
| L5 | Kimi WebBridge (浏览器兜底) | `kimi-webbridge` skill 调用真实 Chrome,打开 `arxiv.org/abs/{id}` 拿 abstract + 完整作者列表 + arXiv ID。SPA 渲染不下来的论文用这个 | arXiv abs 完整 HTML(渲染后)、下载图片/附件、个人主页 1-click 截图 |
| L6 | AnySearch (最后兜底) | `anysearch` skill 23 个垂直域 + 实时网页抽取,搜 `"{paper_title}"` 或 `"{name}" CV filetype:pdf` | 真实 PDF 链接、研究亮点汇总、跨平台交叉验证 |
| **L7** | **申博论坛 (v0.5.0 新增, 2026-06-10)** | `mysupervisor.org` 浙大CS学院导师 213 位 + 16 条评价/PI (适用性 100% 浙大CS, 985 高校类比) / 学院 PDF 招生意向信息表 (含意向学生需求数) / 知乎 1.4w 字长文 (浙大CS考研超详解 等) / 小红书 套磁经验贴 / 博客园 cnblogs 保研朝花夕拾 | **团队氛围** (mysupervisor 16 评价 → 优/缺点/矛盾说法) + **招生偏好** (名额/竞争度/卡本科) + **培养模式** (指导频率/组会/放羊) + **毕业去向** (年限/就业/留校) |

L2 (Google Scholar) is intentionally **skipped** in mainland-China network environments — go L2 Semantic Scholar → L3 DBLP → L4 MiniMax → L5 Kimi WebBridge → L6 AnySearch.

**v0.5.0 L7 数据源使用规则** (社区数据, 必须带标签):
- L1 官网字段 (学术身份/职务/email) → 无标签, 默认权威
- L7 论坛字段 (招生偏好/团队氛围/培养模式) → 必须显式标 `[社区来源]` 或 `[社区-多人共识]` (≥3 条独立帖子)
- L1 + L7 冲突 → 标 `[冲突: L1 vs L7]`, 让用户自己判断
- L7 抓不到 → `❓ 待补 (建议路径: 套磁时追问 / 学长咨询)`, 走 callout 占位
- **禁止**: 把 L7 字段写得像 L1 一样权威; 必须保留置信度信号

**v0.3.4 搜索链(vs 旧 L1→L2→L3→L4)**:
- L1 官网 → L2 S2 → L3 DBLP → **L4 MiniMax** (mcp__MiniMax__web_search, 优先用) → **L5 Kimi WebBridge** (浏览器兜底, SPA/动态渲染场景) → **L6 AnySearch** (23 域垂直 + 实时抽取, 最后兜底)
- 顺序逐级 fallback, 任一级成功即可停;失败时跳下一级
- 论文数据采集用 L4/L5 优先(覆盖 arxiv abs 完整内容),L6 做交叉验证
- 反例:不要一上来用 L6(anysearch 太宽泛),先用 L4/L5 精确抓 arxiv

**🚨 v0.1 CCF-A/B 限制 (2026-06-05)**:**本 skill 当前不在报告中标注 CCF 等级**。`LLM 估算` 的 "CCF-A 65" 数字不可信,容易被反例数据(LLM 把 ICLR submitted 当 CCF-A)污染。报告里**只写 venue 名**(NeurIPS / ICLR / ACL / KDD / TPAMI),**不写 CCF-A/B**。v0.2 实现方案见 `data-sources.md §CCF mapping (deferred)`。

If L1 fails (e.g., personal page 404 or 动态加载), continue to L2 — the data is still salvageable.


---

## 🚨 URL 验证硬规则 (2026-06-09 写入, 违反 = skill 协议破坏)

> 完整 URL 验证规则集（269 行）已下沉到 [`references/url-validation-rules.md`](references/url-validation-rules.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **必跑场景**: 准备生成 paper card 前 / 套磁信引用具体论文时 / 审计 docx 时对照。覆盖 arXiv 真实 ID 验证 / papers.cool URL 格式 / Wiki Subject Author Verification / 通讯作者交叉验证 等。

---
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
- **🚨 H2 标题无装饰性 emoji 硬要求 (2026-06-11 v0.6.0, 违反 = skill 协议破坏)**:
  - 5 大章节 H2 标题 (1. 导师与课题组画像 / 2. 申博匹配度评估 / 3. 套磁与申请建议 / 4. 论文产出全景 / 5. 数据来源与说明) **禁止**装饰性图标 emoji: 👤📊✉📚📖🎯ℹ 等
  - **保留** (allowlist, 状态/信号类, 不算装饰): ✅❌⚠⭐🟢🟡🔴⛔🚨
  - **Why**: 飞书 outline 节点树视觉一致, 避免乱图标; 与 §G audit 通讯作者 + §H 一作 inline 标记不冲突 (后者是 paper card 内部 `**...**(大老板)` 等, 不在 H2 标题)
  - **Template 实施**: LLM 生成 H2 标题时, 一律用纯中文 "1. 导师与课题组画像" (无前缀图标); 现有 13 docs × 5 H2 = 65 段已统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb, 2026-06-11)
  - **新 docx 模板生成前必跑**: `python3 ~/.agents/skills/teacher-report/scripts/check_h2_emoji.py {content}` → 0 decoration emoji 才输出
  - **Audit mode 必跑**: Check 14 列入 14 项 LLM 自检清单 (v0.6.0 强化)
- **🚨 论文条目 paper card 硬要求 (2026-06-08 v0.3.3 → 2026-06-10 v0.3.9 升级, 2026-06-10 v0.4.0 紧凑格式新增可选, 违反 = skill 协议破坏)**:
  - 所有论文 (§4 论文产出全景 / §2.2 论文举例 / §3 套磁信引用 任何位置) **必须**用以下 2 种 paper card 格式之一:
    - **v0.3.9 完整版** (15 行/paper, 单独标注行): 详见 `## Paper Entry Format (v0.3.9) — 硬要求` 章节
    - **v0.4.0 紧凑版** (7 行/paper, inline 标记): 详见 `## Paper Card v0.4.0 紧凑 (2026-06-10 新增)` 章节 + `references/paper-card-v0.4.0.md` 完整规范
  - **选型指南**:
    - 论文 ≤ 3 篇 → 优先 v0.3.9 完整版 (信息密度高)
    - 论文 ≥ 10 篇 → 优先 v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)
    - 同一 doc 中可混用 v0.3.9 和 v0.4.0, 但**同一论文不能同时用两种格式** (避免 reader 困惑)
  - **必须包含 4 维 taxonomy 4 行独立 <p> 块**(`大领域：` / `中方向：` / `小任务：` / `子技术：` 每行 1 字段)— **禁止** 4 列表格 (无论 v0.3.9 还是 v0.4.0)
  - **作者列表: 写完整 verbatim + 中文括注(全作者)**(v0.3.9 强化),禁止 `(末位/通讯)` 缩写 / `(通讯 PI 模式)` 描述 / `... 16 名作者` 省略 / 仅 `Fei Wu` 单独括注
  - **v0.3.9 标注行: 单独成行**: `通讯作者：`, `一作/共一：`, `学生：` 等独立 `<p>` 块
  - **v0.4.0 inline 标记**: 通讯 `(通讯)`, 大老板 `**(大老板)**`, 一作/共一 `(一作: X, Y)` 全部 inline 在 author 行
  - **禁止**简化为表内 1 行 / `<p><b>{标题} (venue year) ⭐</b></p>` 紧凑格式 / 省略作者列表 / 省略 taxonomy / 用 4 列表格 / 用缩写
  - LLM 必须自检 (无论 v0.3.9 还是 v0.4.0): 每篇论文均含 4 维 taxonomy 4 行 + 完整作者列表(全作者带中文括注) + §G 通讯作者真实 byline + `发表：` 1 字段 + `arXiv：` 1 字段 (v0.4.0 嵌入 title, v0.3.9 单独行)
  - v0.4.0 还需自检: arXiv ID 嵌入 `<h3>` title + arXiv URL 是 1-click 入口 + **15 项 v0.4.0 必跑 (14 项 v0.6.0 通用 + Check 15: H3 编号 dot 后缀, 2026-06-11)**, 详见 v0.4.0 章节 + `references/paper-card-v0.4.0.md §6`


---

## Paper Entry Format (v0.3.9 完整版) — 详见 references/

> 完整 15 行/paper paper card 规范 (224 行) 已下沉到 [`references/paper-entry-v0.3.9.md`](references/paper-entry-v0.3.9.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 起默认使用紧凑版 (7 行/paper, 详见 §Paper Card v0.4.0 紧凑 + references/paper-card-v0.4.0.md)**。v0.3.9 完整版仅在论文 ≤ 3 篇 / 套磁信深度引用 / 单篇 deep-dive 时使用。
>
> **选型指南**: 论文 ≤ 3 篇 → v0.3.9 完整版 (信息密度高) / 论文 ≥ 10 篇 → v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)。同一 doc 中可混用, 但**同一论文不能同时用两种格式**。

---
## Paper Card v0.4.0 紧凑 (2026-06-10 新增) — 替代 v0.3.9 完整版

> **背景**: v0.3.9 完整版 15 行/paper 对 ≥ 10 篇 paper 清单 (e.g. 邓舒敏 12 篇 / 刘泽民 30+ 篇) 太长. v0.4.0 紧凑版 7 行/paper, **不损失任何关键信息** (4 维 taxonomy / 完整作者 / §G audit 通讯 / §H 一作信号), 但视觉压缩 53%.
>
> **完整规范**: `references/paper-card-v0.4.0.md` (9 轮 grill-with-docs 问答定型, 9 项决策记录)
>
> **适用场景**:
> - 论文清单 ≥ 10 篇 (节省篇幅, Feishu outline 直接展开 12 h3 paper titles)
> - Reader 想要横向对比 (4 维 taxonomy 4 行对齐, scannable)
> - 飞书 outline 偏好 (h3 paper title 不嵌套 h4)
>
> **不适用场景**:
> - 论文 ≤ 3 篇 (e.g. 套磁信 1-2 篇深度引用) → 继续用 v0.3.9 完整版
> - 论文需要详细 abstract 摘要 → v0.4.0 不含 abstract 字段, 用 v0.3.9

### Paper Card v0.4.0 7-line 模板 (硬要求)

```xml
<h3>{N}. {TITLE} <a href="https://arxiv.org/abs/{ARXIV_ID}">[arXiv {ARXIV_ID}]</a></h3>
<p>{AUTHOR_LIST_WITH_INLINE_MARKERS}</p>
<p>{VENUE} {YEAR} ({ROLE})</p>
<p>大领域：{D}</p>
<p>中方向：{M}</p>
<p>小任务：{T}</p>
<p>子技术：{S}</p>
```

**严格 7 行 (加 1 空行) per paper card**. 任何 8-th line 禁止.

### v0.4.0 inline 标记规则 (author 行)

| 维度 | 规则 | 样例 |
|------|------|------|
| 通用作者 | `English Name（中文名）` 一律, 不区分师生 | `Xiaohan Wang（王晓晗）` |
| 外籍作者 | 保留英文, 不加中文括注 | `Bryan Hooi` |
| 通讯 | author 行末尾追加 `(通讯)` tag | `..., **Name（中文）**(大老板)(通讯)` |
| 大老板 | bold `**...**` + `(大老板)` tag | `**Huajun Chen（陈华钧）**(大老板)` |
| 共同末位 | 都 bold + `(大老板)`, 各自可能 (通讯) 或不 | `..., **Nanyun Peng（彭南云）**(通讯), **Huajun Chen（陈华钧）**(大老板)(通讯)` |
| 一作/共一 | author 行末尾追加 `(一作: X, Y)` (共一用括号分隔) | `(一作: Xiaohan Wang, Shengyu Mao)` |
| 一作 = 通讯 | 双重身份同时标 | `(大老板)(通讯) (一作: Name)` |

### v0.4.0 完整样例 (邓舒敏 12 papers 中 #11 Editing Conceptual Knowledge)

```xml
<h3>11. Editing Conceptual Knowledge for Large Language Models <a href="https://arxiv.org/abs/2403.06259">[arXiv 2403.06259]</a></h3>
<p>Xiaohan Wang（王晓晗）, Shengyu Mao（毛圣雨）, Ningyu Zhang（张宁豫）, Shumin Deng（邓舒敏）, Yunzhi Yao（姚蕴之）, Yue Shen（沈悦）, Lei Liang（梁磊）, Jinjie Gu（顾津锦）, **Huajun Chen（陈华钧）**(大老板)(通讯) (一作: Xiaohan Wang, Shengyu Mao)</p>
<p>EMNLP 2024 Findings (Findings)</p>
<p>大领域：自然语言处理</p>
<p>中方向：知识编辑</p>
<p>小任务：概念级知识编辑</p>
<p>子技术：ConceptEdit 数据集; 概念级知识; 知识更新</p>
```

### v0.3.9 vs v0.4.0 对比

| 维度 | v0.3.9 完整版 | v0.4.0 紧凑版 |
|------|--------------|--------------|
| 行数 per paper | 15 行 | 7 行 (-53%) |
| 标题级别 | `<p>` 段落 | `<h3>` heading (Feishu outline 可见) |
| 通讯作者 | 单独 `<p>通讯作者：X</p>` 行 | author 行内 `(通讯)` tag |
| 大老板 | 单独 `<p>作者角色：X</p>` 行 | author 行内 `**(大老板)**` bold + tag |
| 一作/共一 | 单独 `<p>一作/共一：X</p>` 行 | author 行末 `(一作: X, Y)` |
| arXiv URL | 单独 `<p>arXiv：URL</p>` 行 | 嵌入 title `[arXiv ID]` |
| paperscool URL | 单独 `<p>paperscool：URL</p>` 行 | (无, arXiv 1-click 入口替代) |
| 12 项 LLM 自检 | 必跑 | **必跑 (同样 100%)** |
| §G audit 通讯 | 必跑 | 必跑 (通讯 inline tag 数据源) |
| §I hallucination 检查 | 必跑 (4-index 0 results 标 ⚠️) | 必跑 |
| 数据完整性 | 100% 一致 | 100% 一致 |
| 主动丢弃 | — | paperscool URL / URL 类型行 / 作者角色行 / abstract |

### 15 项 v0.7.0 LLM 自检清单 (14 项 v0.6.0 通用 + **Check 15 H3 编号 dot 后缀**, 2026-06-11 加, 必跑)

| # | 检查项 | 通过条件 | 常见错误 |
|---|--------|---------|----------|
| 1 | 标题 verbatim | 完全从 arXiv abs 页复制 | ❌ 中途截断 / 错字字符 |
| 2 | 标题无 et al. 缩写 | 完整标题 | ❌ 缩写 |
| 3 | 标题 h3 + arXiv ID inline | `<h3>N. Title [arXiv X]</h3>` | ❌ 用 `<p>` 而非 h3 |
| 4 | 4 行 taxonomy 顺序 | 大领域→中方向→小任务→子技术 | ❌ 顺序错乱 |
| 5 | 4 行 taxonomy 无 table | 4 个 `<p>` 块 | ❌ 4 列表格 |
| 6 | taxonomy + 作者 无占位符 | 4 字段 + 作者列表均有具体值 | ❌ `[待补]` / `[未知]` |
| 7 | 作者完整 verbatim | 全部列出, 无 et al. | ❌ 省略 / 缩写 |
| 8 | 禁止 (末位/通讯) 缩写 | author 行无描述性缩写 | ❌ 缩写 |
| 9 | 全作者中文括注 | 100% 作者含 `Name（中文名）` | ❌ 部分漏标 |
| 10 | inline 标记齐全 | 通讯/大老板/一作 全部 inline | ❌ 缺一 |
| 11 | 真实 1-click URL | `<a href="...">[arXiv X]</a>` 嵌入 title | ❌ URL 缺失 |
| 12 | arXiv ID 真实 (v3.xxxx 格式) | placeholder 禁止 | ❌ `[待 L4/L5/L6 重抓]` |
| **13** | **Wiki Subject Author Verification (2026-06-10 新增, 来源 邓舒敏 v0.1.0→v0.3.5 EasyEdit/WISE 误归 case)** | **wiki subject 必须在 paper author list 里** | ❌ wiki subject NOT in author list → paper 误归, 必删除 (不允许"是导师组 paper 算 wiki subject 组"借口) |
| **14** | **H2 标题无装饰性 emoji (2026-06-11 v0.6.0 新增, 来源 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 5 H2 = 65 段清理)** | **5 大章节 H2 标题不含装饰性 emoji (👤📊✉📚📖🎯ℹ 等); 状态/信号类 (✅❌⚠⭐🟢🟡🔴⛔🚨) 允许** | ❌ "👤 1. 导师与课题组画像" / "📊 2. 申博匹配度评估" / "✉️ 3. 套磁与申请建议" / "📚 4. 论文产出全景" / "ℹ️ 5. 数据来源与说明" → 应改为 "1. 导师与课题组画像" / "2. 申博匹配度评估" 等纯中文标题 |
| **15** | **H1-H4 编号标题 dot 后缀 (2026-06-11 v0.7.0 新增, 来源 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 11-12 H3 = 144 段清理)** | **编号标题必须以 `.<space>` 结尾: h1=`1.`, h2=`1.`, h3=`1.1.`, h4=`1.1.1.`** | ❌ "2.3 毕业要求与毕业去向" → 应改为 "2.3. 毕业要求与毕业去向" (与 v0.2.5 `h3=1.1` 无 dot 旧规则作废, 13 docs 144 段已统一清理) |

### v0.4.0 适用位置 (全 docx 强制, 5 章均生效)

1. **§4 论文产出全景** — 每个 paper card 7 行
2. **§2.2 方向匹配度** — 引用具体论文时, 7 行 paper card
3. **§3 套磁信草稿** — 套磁信引用 1-2 篇论文时, 7 行 paper card
4. **§1.2 / §1.3 学生代表作** — 列每位博士代表作时, 7 行 paper card

### v0.3.9 → v0.4.0 迁移 (block-level 升级)

适用 `v0.3.6 §C 块级升级协议` (保留原内容, 只对 paper card blocks 用 `block_replace`):

```bash
# 对每个 paper card, block_replace 从 15 行换 7 行
lark-cli docs +update --api-version v2 --doc {DOC_ID} \
  --command block_replace --block-id {PAPER_CARD_BLOCK_ID} \
  --content @paper-card-v040-7lines.xml
```

**仅适用场景** (v0.3.6 §C 边界):
- 论文 ≥ 10 篇 (v0.4.0 节省 53% 篇幅值得)
- 现有 v0.3.9 doc 已合 §G audit (真实通讯作者, 不会因压缩丢信息)
- Reader 偏好 scannable 横向对比

**保留 v0.3.9 完整版场景**:
- 论文 ≤ 3 篇 (v0.3.9 完整版视觉更清晰)
- 论文需要 abstract 摘要
- 同一 doc 中混用 (e.g. §1 用 v0.3.9, §4 用 v0.4.0) — 但同一论文不能同时用两种格式

### v0.4.0 设计决策来源

详见 `references/paper-card-v0.4.0.md` §12:
- 9 轮 grill-with-docs 问答定型 (2026-06-10)
- 关键 trade-off: 视觉紧凑 vs 信息密度 (v0.4.0 选视觉)
- 关键 trade-off: 单独行 vs inline 标记 (v0.4.0 选 inline, 节省 8 行)
- 关键 trade-off: 学生识别 (v0.4.0 放弃, 减少数据成本)
- 关键 trade-off: 一作/共一 单独行 vs 行末 (v0.4.0 选行末)

---

## v0.5.0 申博实操增强 (2026-06-10 新增)

> **背景**: v0.4.0 论文导向 (5 h2 + 2-4 h3) 满足 "找方向" 阶段; 但 "申博可入度" 阶段需要 8 个**操作维度** (招生偏好/培养模式/科研资源/团队氛围/毕业去向/申请时间节点), v0.4.0 完全没覆盖. v0.5.0 保留 5 h2 框架, 在 §1/§2/§3 内部叠加 8 个新 h3, 总 h3 数 2 → 12.

### 8 新 h3 字段映射

| h2 | h3 | 内容 | 数据源 | 标签规则 |
|----|-----|------|--------|---------|
| **1. 导师与课题组画像** | **1.1 基本信息与学术身份** (扩) | 学术荣誉/兼职/职务/email | L1 官网 | 无标签 |
| | 1.2 研究方向与近年课题 (扩) | 子方向 + 近期 NSFC/重点研发 | L1 + S2 | 无标签 |
| | **1.3 招生偏好** (新) | 名额/竞争度/本科卡否/背景偏好 | L7 学院 PDF + mysupervisor + 知乎 | [社区来源] |
| | **1.4 培养模式** (新) | 指导频率/组会/放羊/实习允许度 | L7 mysupervisor + 知乎 + 学长 | [社区来源] |
| | **1.5 科研资源** (新) | GPU/经费/出国/实习 | L1 主页 + L7 知乎 | [社区来源] 混合 |
| **2. 申博匹配度评估** | 2.1 方向契合度 (existing) | 论文方向 × 用户方向 | L1 + L2 | 无标签 |
| | **2.2 团队氛围与学生评价** (新) | 优点/缺点/矛盾说法 (并列) | L7 mysupervisor 16 评价/PI | [社区-多人共识] 必有 |
| | **2.3 毕业要求与毕业去向** (新) | 年限/论文要求/就业/留校 | L7 知乎/小红书 + L1 alumni 页 | [社区来源] 混合 |
| **3. 套磁与申请建议** | 3.1 套磁信 (existing) | callout | L1 主页 | 无标签 |
| | **3.2 申请时间节点** (新) | 套磁/材料/考核/录取 timeline | L1 学院 + 浙大研招 | [官方时间] |
| | 3.3 风险点 (existing) | callout | 推断 | 无标签 |
| 4. 论文产出全景 (unchanged) | | | L1-L4 | 无标签 |
| 5. 数据来源与说明 (扩) | 5.1 L1-L4 数据源 (existing) | | | |
| | **5.2 L7 社区数据 (新)** | 列出 mysupervisor 抓取时间 / 知乎 URL / 学院 PDF URL | L7 | 显式标 [L7 社区] |

### v0.5.0 数据缺失策略 (3 选项, AskUserQuestion 2026-06-10 选 ❓ 待补 callout 占位)

每 h3 章节末**强制**附 ⚠️ callout 列出本节缺失字段 + 建议补充路径:
- 缺失字段: `❓ 2027 Fall 招生名额`, `❓ 实际带生者 (1v1 vs 团队)`, `❓ 学生毕业去向`
- 建议补充路径: 套磁时追问 / mysupervisor 新评价 / 知乎最新经验贴 / 课题组 alumni LinkedIn
- 与 §5 ❓ 待补机制对齐: 顶部 callout 集中汇总, 避免分散

### v0.5.0 L7 反幻觉协议

- **mysupervisor 1 条评价 ≠ 共识**: 必须 ≥3 条独立评价才能标 [社区-多人共识]; 1-2 条标 [社区-个别观点]
- **知乎长文 vs 单贴**: 长文 (>5000字) 标 [社区-长文], 单贴标 [社区-单贴]
- **学院 PDF vs 学院官网**: PDF 招生意向信息表**不是**招生计划 (招生计划以教育部下达为准), 标 [团队意向, 非官方计划]
- **矛盾说法强制呈现**: e.g. 1 条说 "push 放羊" + 1 条说 "push 严格" → 必须**并列展示**两段 quote, 禁止 AI 仲裁
- **冲突标注**: L1 官网说 "国家级青年学者" + L7 论坛说 "招生名额少" → 各自标源, 不合并

### v0.5.0 vs v0.4.0 决策对比

| 维度 | v0.4.0 (论文导向) | v0.5.0 (申博实操) |
|------|-------------------|-------------------|
| h2 总数 | 5 | 5 (不变) |
| h3 总数 | 2 (1.1/1.2) | 12 (扩 +10) |
| 数据源层 | L1-L6 论文类 | L1-L6 + **L7 论坛类** |
| 核心问题 | 老师做什么 | 怎么进 + 进去什么样 |
| 缺失数据处理 | 整段省略 | ❓ callout 占位 (强制保留章节) |
| 置信度标签 | 无 (默认权威) | [社区来源] / [社区-多人共识] / [冲突: L1 vs L7] |

### v0.5.0 适用场景

- 申博阶段用户 (已有论文 list, 需要决策 "跟谁/怎么申")
- v0.4.0 报告基础上叠加 (8 h3 增量, 不重写论文 card)
- 13 PIs 全覆盖 (含 v0.1.0 占位, 走完整 v0.5.0 generator)

### v0.5.0 升级路径 (block-level)

- 现有 v0.4.0 docx → 用 `block_insert` 在 §1.1 后插入 §1.2/§1.3/§1.4/§1.5 (4 个新 h3 block)
- 现有 §2/§3 同样 block_insert
- 论文 card (§4) **不重写**, 保留 v0.4.0 紧凑版
- §5 数据来源追加 L7 章节


---

## Output Schema (v0.3.9 strict, 12 项自检) — 详见 references/

> 完整 Output Schema + 12 项 LLM 自检清单 (404 行) 已下沉到 [`references/output-schema-v0.3.9.md`](references/output-schema-v0.3.9.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 增强**: 13 项自检 (新增 Check 13 Wiki Subject Author Verification, 详见 references/paper-card-v0.4.0.md §6)。每篇 paper card 必跑, 全通过才输出。
> **v0.6.0 增强 (2026-06-11)**: 14 项自检 (新增 Check 14: H2 无装饰性 emoji, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 5 H2 = 65 段清理落地). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; allowlist (✅❌⚠⭐🟢🟡🔴⛔🚨) 保留.
> **v0.7.0 增强 (2026-06-11)**: 15 项自检 (新增 Check 15: H3 编号 dot 后缀, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 11-12 H3 = 144 段清理落地). 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废, h3 统一为 `1.1.` 形式.

---

## 🚨 Paper-Set Diff 硬规则 (H1, 2026-06-10 写入)

> **触发场景**: 任何 teacher-report wiki 推 draft / migrate 任务, push 前**必须**做 paper-set 双向 diff。
>
> **来源 case**: [`~/.claude/knowledge/cases/wiki/CASE-V039-DRAFT-WIKI-MISMATCH-20260610.md`](../../knowledge/cases/wiki/CASE-V039-DRAFT-WIKI-MISMATCH-20260610.md)
> **背景**: 2026-06-10 6 teacher wikis 共有 44 papers, draft 36 papers, **仅 5 papers match (11%)**。两套 papers 来自不同检索 query 时段, 几乎不重叠。直接 push 36 cards 实际**无法命中任何 placeholder**, 浪费 1.5h 工作 + 暴露 2 个 migrate.py bug。

### 触发条件 (任一即触发)

- 推 /tmp/v039-cards-{teacher}.md 等 draft 到 wiki
- 跑 `migrate-to-v0.3.9.py --all` (会列 wikis 并 transform placeholder)
- 跨 session 推 v0.3.x 论文条目到 v0.4.0 doc
- 任何"我有 N 个 draft papers 要推"的批量操作

### 强制流程 (push 前必跑)

```bash
# Step 1: 列 wiki 实际 paper titles (注意用 24-char obj_token, 非 19-char prefix)
python3 -c "
import re, json
import subprocess
for tok in WIKI_TOKENS:  # 从 wiki +node-list --parent-node-token=P49mwGQU0iEh9CkXbCTcC418nPb 取
    out = subprocess.check_output(['lark-cli','docs','+fetch','--api-version=v2','--doc',tok,'--detail','with-ids','--format','json'])
    titles = re.findall(r'<p[^>]*><b>([^<]+)</b></p>', out.decode())
    print(f'{tok}: {titles}')
" > /tmp/wiki-titles.json

# Step 2: 列 draft paper titles
grep "^###" /tmp/v039-cards-*.md > /tmp/draft-titles.txt

# Step 3: 双向 diff (normalize: lowercase, strip punctuation, strip subtitle)
python3 -c "
import re
def norm(s): return re.sub(r'[:—].*$','',re.sub(r'[^\w\s]','',s.lower())).strip()
wiki = load_wiki()  # parse /tmp/wiki-titles.json
draft = load_draft()  # parse /tmp/draft-titles.txt
matched = set(wiki) & set(draft)
print(f'wiki={len(wiki)} draft={len(draft)} matched={len(matched)}')
print(f'wiki-only ({len(set(wiki)-set(draft))}):', sorted(set(wiki)-set(draft))[:5], '...')
print(f'draft-only ({len(set(draft)-set(wiki))}):', sorted(set(draft)-set(wiki))[:5], '...')
"
```

### 判定矩阵 (claudecode 强制 STOP 条件)

| 场景 | matched 比例 | 决策 |
|------|-------------|------|
| matched == wiki == draft | 100% | ✅ 直接 push |
| matched == draft (draft ⊂ wiki) | draft 100% | ⚠️ wiki 有 extras, 先**清理 wiki 残留 placeholder** 或**重抓 wiki-only** |
| matched == wiki (wiki ⊂ draft) | wiki 100% | ⚠️ draft 有 extras, **加 wiki slot** 或**保留 draft 备用** |
| matched < 50% max(wiki, draft) | **STOP** | 🛑 **整套 query 错了**, 回去对齐检索策略 (该 case 的真实状态) |
| matched == 0 | **STOP** | 🛑 推上去无意义, 重新对齐 source-of-truth |

### 同期暴露的 2 个 migrate.py bug (已修)

| Bug | 现象 | 修复 |
|-----|------|------|
| **Bug 1**: `transform_authors` regex 只匹配 `Last, First（中文）` 格式 | wiki 现有 v0.3.9 cards 用 `First Last（中文）` 无逗号格式, transform 永远 0 替换 | rewrite regex 改 split-on-comma 方案, 同时支持两种格式 (commit 推送中) |
| **Bug 2**: `transform_authors` 不处理 placeholder cards | placeholder 卡片是空 `<p>作者：</p>` + `<p>[完整作者列表待补]</p>`, 不是 author 行 | scope 推迟 (wiki 已 v0.4.0, placeholder 不存在) |

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
