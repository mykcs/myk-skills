---

**v0.11.1 changelog (2026-06-12)**: Output Discipline 范围扩展到 docx 内部. v0.11.0 仅禁止 chat 输出 4 行元信息 preamble, 但实际 13 PIs 飞书 wiki docx 内部 12/13 都含同款 preamble callout (LLM 在生成 docx 时把元信息也写进 callout 了). v0.11.1 硬要求 LLM **不得**在 docx 内部生成 4 行元信息 callout: 「本报告: vX.X.X (升级自 vY.Y.Y, L? 数据已实际抓取) / 调研对象: ... / 招生匹配度: 🟡 ... / 论文产出: N 篇...」. 元信息正确存放点: docx §1 导师画像 + §2 申博匹配度 + §4 论文全景 + §5 数据来源, **不**用紧凑 4 行 callout 形式. 现有 13 PIs docx 12/13 已 F2 块级修删除 (本报告/调研对象/招生匹配度/论文产出 4 行 preamble callout), 详见 `## 🚨 Output Discipline 硬要求 (v0.11.0, 2026-06-11, 违反 = skill 协议破坏)` v0.11.1 扩展 subsection.
**v0.11.0 paper card changelog (2026-06-11)**: Paper card v0.11.0 完整版 (替代 v0.3.9 完整版, v0.4.0 紧凑版保留). 12 决策: (1) 版本定位 v0.11.0 完整版, (2) 标题 `<p>` 段落, (3) status 字段独立新行, (4) arXiv 可空 (`arXiv：暂无` 合法状态值), (5) 编号 `1.` 纯文本前缀, (6) inline 中文括号 `（大老板）（通讯）`, (7) Skill 顶层 v0.11.0 单一版本号 (去 11 文件版本号后缀), (8) status 严格 enum 8 值 (被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿), (9) paper URL 7 种优先级 (OpenReview 优先 → arXiv/DOI/papers.cool/proceedings/journal/主页 PDF), (10) LLM 自检 17 → 22 (Check 18 status enum + 19 paper URL + 20 arXiv/paper 一致性 + 21 status/paper URL 联动 + 22 paper card 编号样式), (11) 强制迁移 14 wiki docx, (12) 写完整 case file. v0.11.0 paper card 与 v0.11.0 Output Discipline 独立维度, 叠加生效. 触发 case: 12 决策 grill-with-docs session 2026-06-11. 详见 `references/paper-entry.md` (v0.3.9 完整版升级) + `references/paper-card.md` (v0.4.0 紧凑版保留) + 22 项 LLM 自检 (Check 1-22). 案例文件: `~/.claude/knowledge/cases/wiki/CASE-PAPER-CARD-V110-FULL-STATUS-ARXIV-20260611.md` (待写).
**v0.11.0 changelog (2026-06-11)**: Output Discipline 硬要求. 禁止 LLM 在 chat 输出 4 行元信息 preamble: 「本报告: vX.X.X (升级自 vY.Y.Y, L? 数据已实际抓取) / 调研对象: ... — ... / 招生匹配度: 🟡/🟢/🔴 ... / 论文产出: N 篇代表论文 (year1-year2)」. 这是 LLM 在调用 lark-cli 前的「自由复述」习惯, 没有任何 prompt 模板要求, 纯属噪音. claudecode 收到 teacher-report 触发后应**直接**调 `lark-cli docs +create` (含 `--content @<xml>`) → 输出 docx URL 单行收尾, 中间不输出元信息. 详见 `## 🚨 Output Discipline 硬要求 (v0.11.0, 2026-06-11, 违反 = skill 协议破坏)`.
**v0.10.0 changelog (2026-06-11)**: 中文名字符级 typo 硬要求. Check 17: 老师姓名必须与 L1-L4 权威来源字符级匹配. 触发 case: 邓舒敏 (Shumin Deng) 文档 28 处中文名 typo 「邓**舒**敏 (shū)」→ 实际正确「邓**淑**敏 (shú)」. 同音不同义 LLM auto-generate typo, 之前 v0.2.9 反幻觉规则只校验 OpenReview/arXiv 字段正确性, 不校验中文姓名字符级. 17 项 LLM 自检 (16 v0.9.0 + Check 17 中文名字符). 同音/形近字 typo 启发式列表 (28 pairs, 含 舒/淑/青/清/振/震 等) 已写入 `scripts/check_chinese_name.py`. push wiki 前必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规.
**v0.9.0 changelog (2026-06-11)**: Progressive disclosure 进一步拆分 (rich-audit 触发). 595 → 168 lines (-72%). 7 新 reference files: anti-hallucination-rules.md (53) + paper-set-diff-rules.md (65) + h3-mapping.md (67) + inputs-and-mode.md (40) + output-contract.md (45) + audit-mode-output.md (35) + failure-handling.md (25). main SKILL.md 仅保留概述 + 索引 + v0.7.0/v0.8.0 硬要求引用. 触发 case: rich-audit v2.6.2+ skill_authoring_checker 检测 teacher-report/SKILL.md 超 500 行限制 (Anthropic SKILL.md 最佳实践),违反 documented guideline.
**v0.8.0 changelog (2026-06-11)**: 深度+1 编号重构. h2 = `1.X.` (5 章 → 1.1./1.2./1.3./1.4./1.5.), h3 章节 = `1.X.Y.` (原 1.1./2.1./3.2./5.3. → 1.1.1./1.2.1./1.3.2./1.5.3.). paper card h3 (N. Title) 不变. 13 docs × 5 h2 + 11-12 h3 = 65 + 144 = 209 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **16 项 LLM 自检 (15 v0.7.0 + Check 16 深度+1 编号)**. 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废.
**v0.7.0 changelog (2026-06-11)**: H1-H4 编号标题 dot 后缀硬要求 (`1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`). 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **15 项 LLM 自检 (14 v0.6.0 + Check 15 编号 dot 后缀)**. 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废.
**v0.6.0 changelog (2026-06-11)**: H2 标题去装饰性 emoji 硬要求 (来源 13 docs × 5 H2 = 65 段统一清理, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). 14 项 LLM 自检 (新增 Check 14: H2 标题无装饰性 emoji). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; 保留 ✅❌⚠⭐🟢🟡🔴⛔🚨 等状态/信号类 (allowlist).
**v0.4.0 changelog (2026-06-10)**: Progressive disclosure refactor (Anthropic SKILL.md 500-line best practice). 1300 → 435 lines (-67%). 3 reference files: url-validation-rules.md (277) + paper-entry.md (233) + output-schema.md (413). v0.3.9 paper card demoted to reference (legacy), v0.4.0 紧凑 promoted to default. 13 项 LLM 自检强化 (新增 Check 13 Wiki Subject Author Verification).
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).

  **Generate**: user mentions researcher/advisor/老师/导师 and asks "调研/写一份报告/整理材料". Output: 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景). Triggers: "调研 XXX", "生成 XXX 老师的报告", "PhD advisor report for XXX".

  **Audit (v0.2.8+)**: user provides EXISTING docx (URL/doc_id) + asks "审计/检查/合规/review". Runs 12 compliance checks, outputs pass/fail + fixes. Triggers: "审计一下 [URL]", "review teacher report compliance".

  **v0.11.1 (2026-06-12) Output Discipline 范围扩展到 docx 内部 (NEW)**: v0.11.0 仅禁止 chat 输出 4 行 preamble, 但 LLM 在生成 docx 时**也会**把同款 4 行元信息 callout 写进 docx (本报告/调研对象/招生匹配度/论文产出 4 行). v0.11.1 硬要求 LLM 在生成 docx 时**不得**创建此 4 行 callout. 元信息正确存放点: §1 导师画像 (基本信息) + §2 申博匹配度 (招生匹配度) + §4 论文全景 (论文产出) + §5 数据来源 (L? 抓取状态). 13 PIs docx 12/13 已用 F2 块级修 (lark-cli docs +update --command block_delete) 清理.
  **v0.11.0 (2026-06-11) Paper Card v0.11.0 完整版 (NEW)**: 替代 v0.3.9 完整版 (v0.4.0 紧凑版保留). 论文 ≤ 3 篇用 v0.11.0, ≥ 10 篇用 v0.4.0. 关键字段: (a) status 独立新行 (8 enum: 被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿), (b) arXiv 可空 (`arXiv：暂无` 合法), (c) `paper：` 统一 URL 行 (OpenReview 优先 → arXiv abs → DOI → papers.cool → proceedings → journal → 主页 PDF), (d) 编号 `1.` 纯文本前缀, (e) inline 中文括号 `（大老板）（通讯）`. **22 项 LLM 自检 (Check 1-22)**: Check 18 status enum + 19 paper URL 合法类型 + 20 arXiv/paper 一致性 + 21 status/paper URL 联动 (被拒/在投/R&R 状态 → paper URL 必为 OpenReview) + 22 paper card 编号样式. 强制迁移 14 wiki docx (`bin/migrate.py --all`).
  **v0.11.0 (2026-06-11) Output Discipline 硬要求 (NEW)**: 禁止 LLM 在 chat 输出 4 行元信息 preamble (本报告: vX.X.X ... / 调研对象: ... / 招生匹配度: 🟡 ... / 论文产出: N 篇...). LLM 应直接调 `lark-cli docs +create` → 输出 docx URL. 元信息 (招生匹配度 / 论文产出数 / L? 数据源状态) 是 docx TL;DR callout 内容, **不应在 chat 复述**.
  **v0.10.0 (2026-06-11) 17 项 LLM 自检 + 中文名字符级 typo 检查**: v0.8.0 编号 + v0.9.0 自评 + Check 17 中文名权威来源字符级匹配 (与 L1-L4 来源对照: faculty 主页 / ORCID / LinkedIn slug / 中文期刊署名). 触发 case: 邓舒敏 doc 28 处「邓**舒**敏 (shū)」→ 实际「邓**淑**敏 (shú)」. Check 17 落地脚本 `scripts/check_chinese_name.py` (同音/形近字启发式 + tier 字典交叉).
  **v0.8.0 (2026-06-11) 16 项 LLM 自检 + H1-H4 编号 dot 后缀 + H2 无装饰性 emoji**: v0.4.0 默认紧凑 paper card (4-dim taxonomy, full author list, arXiv inline title) + v0.5.0 申博实操 8 h3 字段 (招生偏好/培养模式/科研资源/团队氛围/毕业去向/申请时间节点) + v0.7.0/v0.8.0 编号硬要求. v0.2.9 anti-hallucination (OpenReview/arXiv 校验). See references/paper-entry.md + output-schema.md + §Anti-Hallucination Rules + §Output contract.

  Do NOT use for: batch processing many teachers (→ `phd-scout` Bitable), single paper deep-dive, lab summary.
---

# Teacher Report

Generate a single-advisor PhD dossier in Feishu wiki doc format. Input: a researcher name (optionally with university / school). Output: a Feishu `docx` URL that the user can move to a wiki node.


📂 **Inputs to collect** → see [`references/inputs.md`](references/inputs.md) (loaded on demand)


📂 **🚨 自评 user-owned 硬要求 (v0.9.0, 2026-06-11, 违反 = skill 协议破坏)** → see [`references/user-owned.md`](references/user-owned.md) (loaded on demand)

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

> 完整 15 行/paper paper card 规范 (224 行) 已下沉到 [`references/paper-entry.md`](references/paper-entry.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 起默认使用紧凑版 (7 行/paper, 详见 §Paper Card v0.4.0 紧凑 + references/paper-card.md)**。v0.3.9 完整版仅在论文 ≤ 3 篇 / 套磁信深度引用 / 单篇 deep-dive 时使用。
>
> **选型指南**: 论文 ≤ 3 篇 → v0.3.9 完整版 (信息密度高) / 论文 ≥ 10 篇 → v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)。同一 doc 中可混用, 但**同一论文不能同时用两种格式**。

---

📂 **Paper Card v0.4.0 紧凑 (2026-06-10 新增)** → see [`references/paper-card-v04.md`](references/paper-card-v04.md) (loaded on demand)

## v0.5.0 申博实操增强 (2026-06-10 新增)

> **完整 8 h3 字段映射表 + L7 反幻觉协议 + 升级路径**已下沉到 [`references/h3-mapping.md`](references/h3-mapping.md) (67 行, 2026-06-11 拆分).
>
> **TL;DR**: v0.4.0 论文导向满足"找方向"阶段; 但申博可入度阶段需要 8 个操作维度 (招生偏好/培养模式/科研资源/团队氛围/毕业去向/申请时间节点), v0.4.0 完全没覆盖。v0.5.0 保留 5 h2 框架, 在 §1/§2/§3 内部叠加 8 新 h3, 总 h3 2 → 12. 数据源扩 L7 (mysupervisor.org 浙大CS 213 位 + 16 评价/PI + 知乎 + 小红书 + 学院 PDF), L7 字段用 [社区来源] 标签与 L1 区分.

## Output Schema (v0.3.9 strict, 12 项自检) — 详见 references/

> 完整 Output Schema + 12 项 LLM 自检清单 (404 行) 已下沉到 [`references/output-schema.md`](references/output-schema.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 增强**: 13 项自检 (新增 Check 13 Wiki Subject Author Verification, 详见 references/paper-card.md §6)。每篇 paper card 必跑, 全通过才输出。
> **v0.6.0 增强 (2026-06-11)**: 14 项自检 (新增 Check 14: H2 无装饰性 emoji, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 5 H2 = 65 段清理落地). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; allowlist (✅❌⚠⭐🟢🟡🔴⛔🚨) 保留.
> **v0.7.0 增强 (2026-06-11)**: 15 项自检 (新增 Check 15: H3 编号 dot 后缀, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 11-12 H3 = 144 段清理落地). 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废, h3 统一为 `1.1.` 形式.
> **v0.8.0 增强 (2026-06-11)**: 16 项自检 (新增 Check 16: 深度+1 编号, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb 13 docs × 5 h2 + 11-12 h3 = 65+144=209 段清理落地). 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废. h2 统一为 `1.X.`, h3 章节统一为 `1.X.Y.`, paper card h3 (N. Title) 不变.
> **v0.10.0 增强 (2026-06-11)**: 17 项自检 (新增 Check 17: 中文名字符级 typo 检查, 触发 case 邓舒敏 doc 28 处「邓**舒**敏」→ 「邓**淑**敏」). 与 v0.2.9 反幻觉规则互补: v0.2.9 校验 OpenReview/arXiv 字段, v0.10.0 校验中文字符级. 必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规.

---

## 🚨 Paper-Set Diff 硬规则 (H1, 2026-06-10 写入)

> **完整触发条件 + 强制流程 + 判定矩阵 + 已知 bug**已下沉到 [`references/paper-set-diff-rules.md`](references/paper-set-diff-rules.md) (65 行, 2026-06-11 拆分).
>
> **TL;DR**: push v0.3.x draft 到 wiki 前必跑双向 diff (wiki titles ∩ draft titles); matched < 50% 强制 STOP. 来源 case: 2026-06-10 6 teacher wikis 共有 44 papers, draft 36 papers, **仅 5 papers match (11%)**.


📂 **Anti-Hallucination Rules (v0.2.9+, 2026-06-06+)** → see [`references/anti-hallucination.md`](references/anti-hallucination.md) (loaded on demand)

## Failure handling

> **完整 9 类 failure 模式 + 处理动作**已下沉到 [`references/failure-handling.md`](references/failure-handling.md) (~25 行, 2026-06-11 拆分).
>
> **TL;DR**: L1-L4 全失败 → "信息黑洞 — 建议手动提供主页 URL", **禁止编造**. L1 成功 + L2/L3/L4 半失败 → 🟡 数据稀疏. 一作顶会论文 = 0 → 🟡 通讯/末位 PI 模式, 套磁信追问 1v1 带生. 用户同时调研 ≥3 位老师 → 切换 `phd-scout --mode batch`.


📂 **Examples** → see [`references/examples.md`](references/examples.md) (loaded on demand)

## References

- `references/report-template.md` — 飞书 docx XML 模板 (TL;DR callout / 5 章节结构)
- `references/data-sources.md` — L1-L4 抓取细节 + ZJU URL 模式 + S2 API 字段
- `references/llm-prompt.md` — 总结 prompt (synthesis rules + 章节填充指引)
- `references/audit-checklist.md` — 12 项合规检查 (Audit mode 跑这份 checklist)
- `references/normalization-audit-2026-06-05.md` — 4 docx 飞书标题号规范化审计追踪(v0.2.5 → v0.2.7 重跑记录)
