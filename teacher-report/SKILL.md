---

**v0.8.0 changelog (2026-06-11)**: 深度+1 编号重构. h2 = `1.X.` (5 章 → 1.1./1.2./1.3./1.4./1.5.), h3 章节 = `1.X.Y.` (原 1.1./2.1./3.2./5.3. → 1.1.1./1.2.1./1.3.2./1.5.3.). paper card h3 (N. Title) 不变. 13 docs × 5 h2 + 11-12 h3 = 65 + 144 = 209 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **16 项 LLM 自检 (15 v0.7.0 + Check 16 深度+1 编号)**. 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废.
**v0.7.0 changelog (2026-06-11)**: H1-H4 编号标题 dot 后缀硬要求 (`1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`). 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **15 项 LLM 自检 (14 v0.6.0 + Check 15 编号 dot 后缀)**. 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废.
**v0.6.0 changelog (2026-06-11)**: H2 标题去装饰性 emoji 硬要求 (来源 13 docs × 5 H2 = 65 段统一清理, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). 14 项 LLM 自检 (新增 Check 14: H2 标题无装饰性 emoji). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; 保留 ✅❌⚠⭐🟢🟡🔴⛔🚨 等状态/信号类 (allowlist).
**v0.4.0 changelog (2026-06-10)**: Progressive disclosure refactor (Anthropic SKILL.md 500-line best practice). 1300 → 435 lines (-67%). 3 reference files: url-validation-rules.md (277) + paper-entry-v0.3.9.md (233) + output-schema-v0.3.9.md (413). v0.3.9 paper card demoted to reference (legacy), v0.4.0 紧凑 promoted to default. 13 项 LLM 自检强化 (新增 Check 13 Wiki Subject Author Verification).
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).

  **Generate**: user mentions researcher/advisor/老师/导师 and asks "调研/写一份报告/整理材料". Output: 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景). Triggers: "调研 XXX", "生成 XXX 老师的报告", "PhD advisor report for XXX".

  **Audit (v0.2.8+)**: user provides EXISTING docx (URL/doc_id) + asks "审计/检查/合规/review". Runs 12 compliance checks (title numbering, ① ②, block charts, TL;DR, 5-section, Persona footer), outputs pass/fail + fixes. Triggers: "审计一下 [URL]", "review teacher report compliance".

  **v0.4.0 (2026-06-10) 默认紧凑 + v0.3.9 完整版 fallback**: 4-dim paper taxonomy (大领域/中方向/小任务/子技术) per line, full author list with Chinese 括注, arXiv inline title (v0.4.0 紧凑默认) 或 arXiv + papers.cool URL (v0.3.9 完整版, ≤3 篇论文时), **16 项 LLM 自检 (15 v0.7.0 + Check 16 深度+1 编号, 2026-06-11)**, verifiable claims (v0.2.9 anti-hallucination). See body §Paper Card v0.4.0 紧凑 + references/paper-entry-v0.3.9.md (legacy) + references/output-schema-v0.3.9.md (12 项自检) + §Anti-Hallucination Rules.
  **v0.7.0 (2026-06-11) H1-H4 编号标题 dot 后缀硬要求**: 编号标题必须以 `.<space>` 结尾, 即 `1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`. 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). Check 15: H3 编号 dot 后缀 (LLM 自检强化). 与 v0.2.5 旧规则 (h3 = `1.1` 无 dot) 冲突, 旧规则作废.
  **v0.8.0 (2026-06-11) 深度+1 编号重构**: heading 级别 + 1 段编号. h2 = `1.X.` (5 章统一在 doc parent `1` 下: 1.1./1.2./1.3./1.4./1.5.), h3 章节 = `1.X.Y.` (3 段: 1.1.1./1.2.1./1.3.2./1.5.3.). 13 docs × 5 h2 + 11-12 h3 = 209 段统一清理. Check 16: 深度+1 编号 (LLM 自检强化). 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废. paper card h3 (N. Title) 不变.
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

- **Generation mode (default)**: user 提供老师姓名/学校 → 生成新 docx
- **Audit mode**: user 提供 docx URL/doc_id → 审计合规性
- **Rewrite mode (v0.3.4+)**: user 提供 docx + "按模板重写/排版/规范化/升级" 指令 → 全量 regenerate

**Mode 判定**: 触发词含 "审计/audit/检查/合规/review" → Audit; 含 "调研/生成/写一份" → Generation; 显式提供老师姓名 → Generation; 显式 docx URL 且无 Generation 触发词 → Audit.

**Rewrite 触发词**: "按 skill 模板重写" / "按 v0.3.3 重写" / "规范化 doc" / "重排版" / "按模板排版" / "升级到最新格式" / "fix this doc to match the skill" / "regenerate according to skill template".

**Rewrite 不响应场景**: user 只说 "审计一下 [URL]" → Audit mode, 不自动 rewrite. user 说 "fix this" 但没指明 docx URL → 反问 user 哪一篇.

### Step 1 — Data fetching (4-level fallback)

> **🚨 硬规则**:
> - L2 Semantic Scholar 失败时, **只准 1 次 5s 重试**, 任何 5s/15s/30s/60s 指数退避 = 违反本 skill. L4 web_search 聚合是 S2 字段的有效替代, 直接跳.
> - L3 DBLP pid 0 hits 时, 不要无限重试, 直接走 L4.
> - L1 抓到 SPA 锚点不全时, 必须切 playwright, 不要只 webfetch.
> - 任何 L1-L4 抓取中, "导师本人一作顶会论文数" 是必查字段, 0 → 风险灯号 🟡 中 (见 §Failure handling).

**数据源链**: L1 学校/学院官网 (webfetch → playwright 兜底) → L2 S2 API → L3 DBLP → L4 MiniMax web_search → L5 kimi-webbridge → L6 anysearch → **L7 申博论坛 (v0.5.0 新增, mysupervisor.org + 学院 PDF + 知乎 + 小红书 + 博客园)**.

**L7 反幻觉**: L1 字段 (学术身份/职务/email) → 无标签; L7 字段 (招生偏好/团队氛围/培养模式) → 必显式标 `[社区来源]` 或 `[社区-多人共识]` (≥3 条独立); L1+L7 冲突 → 标 `[冲突: L1 vs L7]`.

完整 L1-L7 字段映射表 + ZJU URL 模式 + S2 API 字段详见 `references/data-sources.md`.

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
  - v0.4.0 还需自检: arXiv ID 嵌入 `<h3>` title + arXiv URL 是 1-click 入口 + **16 项 v0.4.0 必跑 (15 项 v0.7.0 通用 + Check 16: 深度+1 编号, 2026-06-11)**, 详见 v0.4.0 章节 + `references/paper-card-v0.4.0.md §6`


---

## Paper Entry Format (v0.3.9 完整版) — 详见 references/

> 完整 15 行/paper paper card 规范 (224 行) 已下沉到 [`references/paper-entry-v0.3.9.md`](references/paper-entry-v0.3.9.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 起默认使用紧凑版 (7 行/paper, 详见 §Paper Card v0.4.0 紧凑 + references/paper-card-v0.4.0.md)**。v0.3.9 完整版仅在论文 ≤ 3 篇 / 套磁信深度引用 / 单篇 deep-dive 时使用。
>
> **选型指南**: 论文 ≤ 3 篇 → v0.3.9 完整版 (信息密度高) / 论文 ≥ 10 篇 → v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)。同一 doc 中可混用, 但**同一论文不能同时用两种格式**。

---
## Paper Card v0.4.0 紧凑 (2026-06-10 新增)

> **完整 9 轮 grill-with-docs 决策记录 + 7-line 模板 + inline 标记规则 + 16 项 v0.8.0 LLM 自检清单**已下沉到 [`references/paper-card-v0.4.0.md`](references/paper-card-v0.4.0.md) (~290 行, 2026-06-10 拆分; v0.8.0 加 Check 16 深度+1 编号).
>
> **TL;DR**: v0.3.9 完整版 15 行/paper 对 ≥10 篇 paper 太长, v0.4.0 紧凑版 7 行/paper 不损失关键信息, 节省 53% 篇幅.
>
> **选型**: 论文 ≤3 篇 → v0.3.9 完整版; 论文 ≥10 篇 → v0.4.0 紧凑版; 同一 doc 可混用但同一论文不混.

## v0.5.0 申博实操增强 (2026-06-10 新增)

> **完整 8 h3 字段映射表 + L7 反幻觉协议 + 升级路径**已下沉到 [`references/v0.5.0-h3-mapping.md`](references/v0.5.0-h3-mapping.md) (67 行, 2026-06-11 拆分).
>
> **TL;DR**: v0.4.0 论文导向满足"找方向"阶段; 但申博可入度阶段需要 8 个操作维度 (招生偏好/培养模式/科研资源/团队氛围/毕业去向/申请时间节点), v0.4.0 完全没覆盖。v0.5.0 保留 5 h2 框架, 在 §1/§2/§3 内部叠加 8 新 h3, 总 h3 2 → 12. 数据源扩 L7 (mysupervisor.org 浙大CS 213 位 + 16 评价/PI + 知乎 + 小红书 + 学院 PDF), L7 字段用 [社区来源] 标签与 L1 区分.

## Output Schema (v0.3.9 strict, 12 项自检) — 详见 references/

> 完整 Output Schema + 12 项 LLM 自检清单 (404 行) 已下沉到 [`references/output-schema-v0.3.9.md`](references/output-schema-v0.3.9.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 增强**: 13 项自检 (新增 Check 13 Wiki Subject Author Verification, 详见 references/paper-card-v0.4.0.md §6)。每篇 paper card 必跑, 全通过才输出。
> **v0.6.0 增强 (2026-06-11)**: 14 项自检 (新增 Check 14: H2 无装饰性 emoji, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 5 H2 = 65 段清理落地). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; allowlist (✅❌⚠⭐🟢🟡🔴⛔🚨) 保留.
> **v0.7.0 增强 (2026-06-11)**: 15 项自检 (新增 Check 15: H3 编号 dot 后缀, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 11-12 H3 = 144 段清理落地). 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废, h3 统一为 `1.1.` 形式.
> **v0.8.0 增强 (2026-06-11)**: 16 项自检 (新增 Check 16: 深度+1 编号, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 5 h2 + 11-12 h3 = 65+144=209 段清理落地). 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废. h2 统一为 `1.X.`, h3 章节统一为 `1.X.Y.`, paper card h3 (N. Title) 不变.

---

## 🚨 Paper-Set Diff 硬规则 (H1, 2026-06-10 写入)

> **完整触发条件 + 强制流程 + 判定矩阵 + 已知 bug**已下沉到 [`references/paper-set-diff-rules.md`](references/paper-set-diff-rules.md) (65 行, 2026-06-11 拆分).
>
> **TL;DR**: push v0.3.x draft 到 wiki 前必跑双向 diff (wiki titles ∩ draft titles); matched < 50% 强制 STOP. 来源 case: 2026-06-10 6 teacher wikis 共有 44 papers, draft 36 papers, **仅 5 papers match (11%)**.

## Anti-Hallucination Rules (v0.2.9+, 2026-06-06+)

> **完整 6 类校验矩阵 + 3 层生成防御 + 1 层使用防御 + 4 类绝对禁止**已下沉到 [`references/anti-hallucination-rules.md`](references/anti-hallucination-rules.md) (53 行, 2026-06-11 拆分).
>
> **核心**: v0.2.8 之前 teacher-report 曾出现系统性幻觉 (5 字段从 AI 推断而非平台校验, 5 篇 ICLR 2026 "已撤稿" 标注全部错误, 行政职务滞后 2 时间点)。v0.2.9+ 强制走 OpenReview/arXiv 校验矩阵。

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
