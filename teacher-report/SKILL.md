---

**v0.11.0 changelog (2026-06-11)**: Output Discipline 硬要求. 禁止 LLM 在 chat 输出 4 行元信息 preamble: 「本报告: vX.X.X (升级自 vY.Y.Y, L? 数据已实际抓取) / 调研对象: ... — ... / 招生匹配度: 🟡/🟢/🔴 ... / 论文产出: N 篇代表论文 (year1-year2)」. 这是 LLM 在调用 lark-cli 前的「自由复述」习惯, 没有任何 prompt 模板要求, 纯属噪音. claudecode 收到 teacher-report 触发后应**直接**调 `lark-cli docs +create` (含 `--content @<xml>`) → 输出 docx URL 单行收尾, 中间不输出元信息. 详见 `## 🚨 Output Discipline 硬要求 (v0.11.0, 2026-06-11, 违反 = skill 协议破坏)`.
**v0.10.0 changelog (2026-06-11)**: 中文名字符级 typo 硬要求. Check 17: 老师姓名必须与 L1-L4 权威来源字符级匹配. 触发 case: 邓舒敏 (Shumin Deng) 文档 28 处中文名 typo 「邓**舒**敏 (shū)」→ 实际正确「邓**淑**敏 (shú)」. 同音不同义 LLM auto-generate typo, 之前 v0.2.9 反幻觉规则只校验 OpenReview/arXiv 字段正确性, 不校验中文姓名字符级. 17 项 LLM 自检 (16 v0.9.0 + Check 17 中文名字符). 同音/形近字 typo 启发式列表 (28 pairs, 含 舒/淑/青/清/振/震 等) 已写入 `scripts/check_chinese_name.py`. push wiki 前必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规.
**v0.9.0 changelog (2026-06-11)**: Progressive disclosure 进一步拆分 (rich-audit 触发). 595 → 168 lines (-72%). 7 新 reference files: anti-hallucination-rules.md (53) + paper-set-diff-rules.md (65) + v0.5.0-h3-mapping.md (67) + inputs-and-mode.md (40) + output-contract.md (45) + audit-mode-output.md (35) + failure-handling.md (25). main SKILL.md 仅保留概述 + 索引 + v0.7.0/v0.8.0 硬要求引用. 触发 case: rich-audit v2.6.2+ skill_authoring_checker 检测 teacher-report/SKILL.md 超 500 行限制 (Anthropic SKILL.md 最佳实践),违反 documented guideline.
**v0.8.0 changelog (2026-06-11)**: 深度+1 编号重构. h2 = `1.X.` (5 章 → 1.1./1.2./1.3./1.4./1.5.), h3 章节 = `1.X.Y.` (原 1.1./2.1./3.2./5.3. → 1.1.1./1.2.1./1.3.2./1.5.3.). paper card h3 (N. Title) 不变. 13 docs × 5 h2 + 11-12 h3 = 65 + 144 = 209 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **16 项 LLM 自检 (15 v0.7.0 + Check 16 深度+1 编号)**. 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废.
**v0.7.0 changelog (2026-06-11)**: H1-H4 编号标题 dot 后缀硬要求 (`1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`). 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **15 项 LLM 自检 (14 v0.6.0 + Check 15 编号 dot 后缀)**. 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废.
**v0.6.0 changelog (2026-06-11)**: H2 标题去装饰性 emoji 硬要求 (来源 13 docs × 5 H2 = 65 段统一清理, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). 14 项 LLM 自检 (新增 Check 14: H2 标题无装饰性 emoji). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; 保留 ✅❌⚠⭐🟢🟡🔴⛔🚨 等状态/信号类 (allowlist).
**v0.4.0 changelog (2026-06-10)**: Progressive disclosure refactor (Anthropic SKILL.md 500-line best practice). 1300 → 435 lines (-67%). 3 reference files: url-validation-rules.md (277) + paper-entry-v0.3.9.md (233) + output-schema-v0.3.9.md (413). v0.3.9 paper card demoted to reference (legacy), v0.4.0 紧凑 promoted to default. 13 项 LLM 自检强化 (新增 Check 13 Wiki Subject Author Verification).
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).

  **Generate**: user mentions researcher/advisor/老师/导师 and asks "调研/写一份报告/整理材料". Output: 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景). Triggers: "调研 XXX", "生成 XXX 老师的报告", "PhD advisor report for XXX".

  **Audit (v0.2.8+)**: user provides EXISTING docx (URL/doc_id) + asks "审计/检查/合规/review". Runs 12 compliance checks, outputs pass/fail + fixes. Triggers: "审计一下 [URL]", "review teacher report compliance".

  **v0.11.0 (2026-06-11) Output Discipline 硬要求 (NEW)**: 禁止 LLM 在 chat 输出 4 行元信息 preamble (本报告: vX.X.X ... / 调研对象: ... / 招生匹配度: 🟡 ... / 论文产出: N 篇...). LLM 应直接调 `lark-cli docs +create` → 输出 docx URL. 元信息 (招生匹配度 / 论文产出数 / L? 数据源状态) 是 docx TL;DR callout 内容, **不应在 chat 复述**.
  **v0.10.0 (2026-06-11) 17 项 LLM 自检 + 中文名字符级 typo 检查**: v0.8.0 编号 + v0.9.0 自评 + Check 17 中文名权威来源字符级匹配 (与 L1-L4 来源对照: faculty 主页 / ORCID / LinkedIn slug / 中文期刊署名). 触发 case: 邓舒敏 doc 28 处「邓**舒**敏 (shū)」→ 实际「邓**淑**敏 (shú)」. Check 17 落地脚本 `scripts/check_chinese_name.py` (同音/形近字启发式 + tier 字典交叉).
  **v0.8.0 (2026-06-11) 16 项 LLM 自检 + H1-H4 编号 dot 后缀 + H2 无装饰性 emoji**: v0.4.0 默认紧凑 paper card (4-dim taxonomy, full author list, arXiv inline title) + v0.5.0 申博实操 8 h3 字段 (招生偏好/培养模式/科研资源/团队氛围/毕业去向/申请时间节点) + v0.7.0/v0.8.0 编号硬要求. v0.2.9 anti-hallucination (OpenReview/arXiv 校验). See references/paper-entry-v0.3.9.md + output-schema-v0.3.9.md + §Anti-Hallucination Rules + §Output contract.

  Do NOT use for: batch processing many teachers (→ `phd-scout` Bitable), single paper deep-dive, lab summary.
---

# Teacher Report

Generate a single-advisor PhD dossier in Feishu wiki doc format. Input: a researcher name (optionally with university / school). Output: a Feishu `docx` URL that the user can move to a wiki node.

## Inputs to collect

> **完整 6 字段收集 + Disambiguation edge cases + Step 0.5 token 询问**已下沉到 [`references/inputs-and-mode.md`](references/inputs-and-mode.md) (~55 行, 2026-06-11 拆分).
>
> **TL;DR**: 必收 1 老师姓名 + 2 学校 (强推) + 5 申博 wiki dashboard token (推荐). Step 0.5 必跑 AskUserQuestion (模式 A/B/C) 确认 dashboard/parent token 提供意愿. 1+2 缺失 → 不要开始抓取, 反问 user.

## Procedure

### Step 0 — Mode selection (v0.3.4+)

- **Generation mode (default)**: user 提供老师姓名/学校 → 生成新 docx
- **Audit mode**: user 提供 docx URL/doc_id → 审计合规性
- **Rewrite mode (v0.3.4+)**: user 提供 docx + "按模板重写/排版/规范化/升级" 指令 → 全量 regenerate

**Mode 判定**: 触发词含 "审计/audit/检查/合规/review" → Audit; 含 "调研/生成/写一份" → Generation; 显式提供老师姓名 → Generation; 显式 docx URL 且无 Generation 触发词 → Audit.

**Rewrite 触发词**: "按 skill 模板重写" / "按 v0.3.3 重写" / "规范化 doc" / "重排版" / "按模板排版" / "升级到最新格式" / "fix this doc to match the skill" / "regenerate according to skill template".

**Rewrite 不响应场景**: user 只说 "审计一下 [URL]" → Audit mode, 不自动 rewrite. user 说 "fix this" 但没指明 docx URL → 反问 user 哪一篇.

## 🚨 自评 user-owned 硬要求 (v0.9.0, 2026-06-11, 违反 = skill 协议破坏)

- **「1.1. 自评」章节**: 所有 teacher-report docx 必须以 `<h2>1.1. 自评</h2>` 作为**第一个** h2 章节 (在 1.2. 导师与课题组画像 之前)
- **现有 5 章 h2 后移**: `1.1. 导师` → `1.2. 导师` / `1.2. 申博` → `1.3. 申博` / `1.3. 套磁` → `1.4. 套磁` / `1.4. 论文` → `1.5. 论文` / `1.5. 数据` → `1.6. 数据`
- **144 h3 同步后移**: `1.X.Y.` → `1.(X+1).Y.` (如 `1.1.1.` → `1.2.1.`)
- **🚨 user-owned 禁区**: 「1.1. 自评」章节内容**由用户自己写**, claudecode **不得修改** (除非用户**明说**). 适用:
  - LLM 生成新 docx 时: 创建空壳 `<h2>1.1. 自评</h2><p>[自评内容由用户填写]</p>`, 内容留空
  - LLM 审计 docx 时: 不检查自评章节的内容合规性, 只确认章节存在
  - LLM 重排版/规范化 docx 时: 自评章节**保留原样**, 不重写
  - LLM 后续 agent 复用 docx 时: 跳过自评章节, 不当作 AI 输出处理
- **触发 case**: 用户 2026-06-11 显式说明「这是我自己写的, 一般你不要自己改, 除非我明说」
- **执行状态**: 14 docs × 1 insert + 13 docs × (5 h2 + 11-12 h3) renumber = 222 段操作 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb)

## 🚨 中文名字符级 typo 硬要求 (v0.10.0, 2026-06-11, 违反 = skill 协议破坏)

- **所有老师中文名必须与 L1-L4 权威来源字符级匹配** — 不接受音近/形近字变体. 权威来源 (按优先级):
  1. **Faculty 个人主页** (cshen.github.io / kunkuang.github.io / person.zju.edu.cn/...)
  2. **ORCID** (0000-0001-XXXX-XXXX)
  3. **LinkedIn URL slug** (e.g. `shumin-deng-邓淑敏-2a1b26142`)
  4. **中文期刊/专利署名** (软件学报 / 中国科学 / 发明专利)
  5. OpenReview / Semantic Scholar / papers.cool 显示的中文名
- **必查字段**: docx 文档里**每一处**老师中文名 (含 title / TL;DR / 招生偏好 / 培养模式 / 套磁信 / paper card 作者署名 等), 字符必须与权威来源 1:1 匹配
- **违规模式 (反例)**:
  - ❌ 「邓**舒**敏 (shū, comfortable)」 — 实际「邓**淑**敏 (shú, virtuous)」, 同音不同义 LLM auto-generate
  - ❌ 字段一致但字符错位 (如「**长**江」vs「**常**江」)
  - ❌ 形近字混淆 (未/末, 已/己, 仑/伦 等)
- **执行协议**:
  - **LLM 生成新 docx 前**: 必须先 L1-L4 抓取老师中文名, 写到 `references/name-dictionary-tier-*.json` 的 HIGH-CONF 段 (source 必填非 'best-guess-from-paper-coauthor')
  - **LLM 审计 docx 时**: 必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规
  - **LLM 重排版/规范化 docx 时**: 必跑同脚本, 发现的 typo 列在 report 头部待用户决定 (避免自动改用户未确认的字段)
- **🚨 不要在 1.1. 自评 user-owned 章节上跑** — 那是用户自写, claudecode 不修改 (见 v0.9.0 硬要求)
- **同音/形近字 typo 启发式 (28 pairs)**: 已写入 `scripts/check_chinese_name.py` 的 `TYPO_PAIRS` + `NEAR_PAIRS`. LLM 推断中文名时若落在这些 pair, 必须显式标 `[unverified: 同音 X/Y 候选]` 等待用户确认
- **触发 case (2026-06-11)**: 邓舒敏 doc 28 处字符 typo, claudecode 当时 v0.2.9 反幻觉只校验了 OpenReview/arXiv 字段 (Shumin Deng 这个英文名是正确的, 但没校验中文字符级), 28 处错字穿透了所有 check
- **执行状态**: scripts/check_chinese_name.py v0.10.0 已写; 待跑全 15 wiki docs 出报告 + 等用户决定是否 batch fix

## 🚨 Output Discipline 硬要求 (v0.11.0, 2026-06-11, 违反 = skill 协议破坏)

**核心禁令**: LLM 在调 `lark-cli docs +create` 之前 / 之后, **禁止在 chat 输出 4 行元信息 preamble**:

| ❌ 禁止 (chat preamble 反例) | 应放在 docx 哪里 (正确) |
|----------------------------|------------------------|
| 「本报告: v0.5.0 申博实操增强 (2026-06-10 升级自 v0.4.0, L7 数据已实际抓取)」 | 写 changelog 时已经在 SKILL.md 顶部, docx 不需复述 |
| 「调研对象: 邓淑敏 (Shumin Deng) — ZJU100 Young Professor, 博士生导师」 | docx §1.1 基本信息与学术身份 + TL;DR callout |
| 「招生匹配度: 🟡 中 (L7 字段部分已抓, 部分仍 ❓ 待补, 建议套磁时 1v1 追问)」 | docx §2 申博匹配度评估灯号 + TL;DR callout (🟢/🟡/🔴 + 文字) |
| 「论文产出: 12 篇代表论文 (2024-2026)」 | docx §4 论文产出全景 + TL;DR callout (精确数字, 不写 "12 篇代表论文") |

**正确 chat 行为 (Step 0 协议)**:
1. 收到 teacher-report 触发词 → 跳过任何 "我将..." / "本次报告..." / "调研对象..." 复述
2. 直接进入 Step 0/1 抓取 (lark-cli / webfetch / playwright) → 调 `lark-cli docs +create --api-version v2 --title "..." --content @<xml>`
3. chat 最终输出 = **单行** docx URL (e.g. `https://feishu.cn/docx/MqEzdtwcso2AGyxUPuCcyQRAnwe`) + 必要的错误诊断

**理由**:
- 元信息 (招生匹配度 / 论文产出数 / L? 数据源状态 / 调研对象) **本就是 docx TL;DR callout 内容** (`references/output-contract.md` §TL;DR). 在 chat 复述 = 重复劳动
- 暴露内部 L? 抓取阶段 (L1-L7 是 skill 内部协议, user 不需要知道) = 协议泄漏
- 暴露 ❓ 待补 placeholder = 暗示 docx 内容稀疏, 但实际 docx TL;DR callout 已标 [L7 社区来源] + [社区-个别观点] 标签, 信息密度更高
- 让 user 误以为 "报告" 是 chat 输出而非 docx = 误导产物位置

**反例 (2026-06-11 触发 case)**:
邓淑敏 (Shumin Deng) doc 28 处 typo 修复后, LLM 跑 teacher-report 触发时在 chat 输出 4 行元信息 preamble, user 显式要求"去掉这种"。preamble 文本无任何 prompt 模板源头 (SKILL.md / llm-prompt.md / report-template.md 全部 grep 验证 0 命中「本报告/调研对象/代表论文」+ 「招生匹配度」仅命中 docx 内部规则), 纯属 LLM "自由生长" 习惯, 必须用硬规则阻断。

**执行协议**:
- LLM 跑 teacher-report 触发 → 跳过 preamble → 抓取 → `lark-cli docs +create` → 输出 URL
- 中间任何 step 失败 → 输出 `🚨 [step X] 错误信息` (单行), 不复述元信息
- 写多行 chat 输出的**唯一合法场景** = audit mode (12 项 check 结果) 或 rewrite mode (diff summary), 详见 `references/audit-mode-output.md` + `references/output-contract.md`

**审计/重写模式豁免**: audit mode 输出的 12 项 check pass/fail + rewrite mode 的 diff summary 不受本规则约束 (那是合规性报告, 不是 docx 元信息)。

**执行状态**: v0.11.0 已写入 SKILL.md + llm-prompt.md; 待后续 teacher-report session 验证 LLM 是否遵守 (case: 邓淑敏 / 吴飞 / 况琨 3 个 PIs re-run teacher-report 时检查 chat 输出)。

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
## Audit mode 输出格式

> **完整 audit 输出模板 (总览 + 失败项详情 + 修复命令 + Step A4 回复模板 + Audit 模式限制)**已下沉到 [`references/audit-mode-output.md`](references/audit-mode-output.md) (~35 行, 2026-06-11 拆分).
>
> **TL;DR**: 1 行总结 + 失败项列表 (每项 1 行) + 可选修复命令. Audit 模式**不直接 overwrite** (避免误覆盖已定制内容), 不抓新数据, 不验证内容正确性.

## Output contract

> **完整 Output contract (5 章节必含 + H2 emoji 硬要求 + paper card 硬要求 + 5 必含 sections)**已下沉到 [`references/output-contract.md`](references/output-contract.md) (~50 行, 2026-06-11 拆分).
>
> **TL;DR**: Primary 输出是飞书 docx URL; 5 章节 h2 顺序固定 (TL;DR / 导师画像 / 申博匹配度 / 套磁建议 / 论文全景 / 数据来源); 必含 1 TL;DR callout + 1 grid + ≥1 callout/section + `<table>` 块; H2 标题禁止装饰性 emoji (👤📊✉📚📖🎯ℹ); paper card 必须 v0.3.9 完整版 / v0.4.0 紧凑版 二选一.

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
> **v0.10.0 增强 (2026-06-11)**: 17 项自检 (新增 Check 17: 中文名字符级 typo 检查, 触发 case 邓舒敏 doc 28 处「邓**舒**敏」→ 「邓**淑**敏」). 与 v0.2.9 反幻觉规则互补: v0.2.9 校验 OpenReview/arXiv 字段, v0.10.0 校验中文字符级. 必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规.

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

> **完整 9 类 failure 模式 + 处理动作**已下沉到 [`references/failure-handling.md`](references/failure-handling.md) (~25 行, 2026-06-11 拆分).
>
> **TL;DR**: L1-L4 全失败 → "信息黑洞 — 建议手动提供主页 URL", **禁止编造**. L1 成功 + L2/L3/L4 半失败 → 🟡 数据稀疏. 一作顶会论文 = 0 → 🟡 通讯/末位 PI 模式, 套磁信追问 1v1 带生. 用户同时调研 ≥3 位老师 → 切换 `phd-scout --mode batch`.

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
