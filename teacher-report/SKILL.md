---
name: teacher-report
description: |
  Generate OR audit a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx).

  **Generate**: user mentions researcher/advisor/老师/导师 and asks "调研/写一份报告/整理材料". Output: **5-section report (v0.13.6, 4 章节必含 + TL;DR)** — (1) 1.1 自评 (user-owned) / (2) 1.2 导师画像 (1.2.1-1.2.5) / (3) 1.3 论文全景 (1.3.A 顶会 10 v0.3.0 增强 h3 + 1.3.B 主题表 + 1.3.C 趋势, 论文 ≥ 10 篇必重组) / (4) 1.4 数据来源 (含 1.4.3 P0/P1/P2 待补汇总) / (5) 1.5 套磁准备清单 (替代 v0.5.0 旧 §1.4 套磁). Triggers: "调研 XXX", "生成 XXX 老师的报告", "PhD advisor report for XXX". 22 项 LLM 自检 (v0.13.0 → v0.13.2, paper card 格式统一 v0.3.0 增强 h3).

  **Audit (v0.2.8+)**: user provides EXISTING docx (URL/doc_id) + asks "审计/检查/合规/review". Runs 12 compliance checks, outputs pass/fail + fixes. Triggers: "审计一下 [URL]", "review teacher report compliance".

  **v0.13.2 (2026-06-17) Paper card 格式统一 v0.3.0 增强 (NEW)**: §1.4.A 顶会 10 paper card 格式从 v0.4.0 紧凑 (callout 4 行 metadata) **改为 v0.3.0 增强 (h3 + 12 行, 1 h3 含 arXiv inline + 4 行独立 taxonomy + 全作者中文括注 + 通讯作者独立行 + 发表 + arXiv 完整 URL + paperscool 完整 URL)**. 触发 case: 魏颖 wiki 1.4.A 顶会 10 篇 (2026-06-17, user 反馈 v0.4.0 紧凑格式不符合预期). 同步修: report-template.md §5.1 例子 (callout 改为 h3 + 12 行) + paper-card-formats.md 选型决策树 (§1.4.A 顶会 10 改为 v0.3.0 增强) + SKILL.md 描述.
  **v0.13.5 (2026-06-17) paper link 字段名 + fallback 硬要求 (NEW, 违反 = skill 协议破坏)**: 字段名 `arXiv：` → `paper link:`. Fallback 顺序: (1) arXiv ID 真 → arXiv URL. (2) arXiv ID 假/无 → OpenReview URL. (3) 都没有 → 暂无. 触发 case: 魏颖 wiki (2026-06-17, user 反馈 "arXiv 改为 paper link"). 同步加 **Check 24 paper link fallback 硬要求** + 1.4.A 10 篇 + 1.4.B 5 主题 63 篇 全按 fallback 重写. 详见 CHANGELOG.md v0.13.5.
  **v0.13.6 (2026-06-17) §1.3 申博匹配度评估整块删除 (NEW)**: 6 章节必含 → 4 章节必含 + TL;DR (1.1/1.2/1.3 论文/1.4 数据/1.5 套磁). §1.3 申博匹配度评估 h2 + 1.3.1 学术方向匹配度 h3 + 1.3.2 团队氛围 h3 + 1.3.3 毕业要求 h3 整块删除 (73 block batch delete in docx). 章节重编号: 原 1.4 论文全景 → 1.3, 原 1.5 数据来源 → 1.4, 原 1.6 套磁准备清单 → 1.5. 触发 case: 魏颖 wiki 1.3 段 (2026-06-17, user 反馈 "skill 去掉《1.3. 申博匹配度评估》这一整块内容"). 同步修 4 文件: report-template.md 5 章节必含 + §4 1.3 整段删除 + 章节重编号 / output-contract.md 6 → 4 章节 + Check 18 重命名 / paper-card-formats.md (无需修改, 1.3.1 仅在用户偏好列表) / SKILL.md description 4 章节 + 加 v0.13.6 描述. 详见 CHANGELOG.md v0.13.6.
  **v0.13.4 (2026-06-17) arXiv 幻觉重大修复 (NEW, 违反 = skill 协议破坏)**: teacher-report skill 之前生成的 73 篇 arXiv ID 中 8/10 1.4.A 顶会 + 63/63 1.4.B 5 主题 = **70+ 假 arXiv ID** (LLM 幻觉, 不存在或 ID 真实但内容 LLM 编造). 5 假 ID (#1 22hBwIf7OC / #2 5U1rlpX68A / #3 gc8QAQfXv6 / #5 TpD2aG1h0D / #7 iTTZFKrlGV) + 1 ID 真内容假 (#9 2206.04335) 全部 标 "待补" + 删 href. 1.4.B 5 主题 63 篇 arXiv 列 全标 "待补". 触发 case: 魏颖 wiki 1.4.A 顶会 10 篇 (2026-06-17, user 反馈 "https://arxiv.org/abs/22hBwIf7OC 这些链接全是假的"). 同步加 **Check 23 arXiv URL verify 硬要求** (每个 arXiv ID 必跑 WebFetch verify HTTP 200 + title 匹配, 失败标 "待补") + `scripts/check_arxiv_url.py` 脚本. 主页 / 邮箱 verify 通过 (person.zju.edu.cn/yingwei 真, ying.wei@zju.edu.cn 真). 详见 CHANGELOG.md v0.13.4.
  **v0.13.0 (2026-06-17) 重大重构 (NEW)**: 5 h2 → 6 h2 (新增 §1.6 套磁准备清单, 替代 v0.5.0 旧 §1.4 套磁 h2) + 6 个新结构 (§1.3.1 学术方向匹配度 4 档 / §1.4 A 顶会 10 + B 主题表 5-7 + C 趋势 / §1.5.3 P0/P1/P2 待补汇总 / §1.2 顶部 2xN 方向矩阵) + 主动 WebFetch 主页 (§1.2.1 主页/邮箱必抓, 失败留 P1) + 3 个新硬要求 (v0.13.0 #1-#3) + 19 → 22 项 LLM 自检 (新增 Check 20 P0/P1/P2 + 21 主动 WebFetch + 22 1.6 套磁清单) + 模板整合 (report-template.md 583 → 470 行 v0.13.0 + output-contract.md 与 report-template.md 100% 一致) + paper-card 入口整合 (新建 paper-card-formats.md, 删 paper-card-v04.md + paper-card-v11.md 索引) + bin 脚本归档 (4 个 v0.4.0 legacy → bin/archive/v04-legacy/) + 无水印 (删 "整理人: claudecode teacher-report skill v0.5.0"). 触发 case: 魏颖 wiki 套磁清理 (2026-06-17, claudecode 帮用户修了 12 项 patch) 暴露模板缺失. 详见 `references/report-template.md` §12 v0.13.0 变更日志.
  **v0.12.0 (2026-06-12) 4 章节模板 (去套磁) (NEW)**: 移除 §1.4. 套磁与申请建议 + 3 h3 (套磁信 / 申请时间节点 / 风险点). 新结构 5 h2: 1.1. 自评 (user-owned v0.9.0) / 1.2. 导师与课题组画像 / 1.3. 申博匹配度评估 / 1.4. 论文产出全景 / 1.5. 数据来源与说明. 套磁信独立写, 不在 docx h2 章节里. 19 项 LLM 自检 (Check 18 新: 不含 §套磁). 触发 case: 用户 2026-06-12 显式说明「修改 skill 模板里去掉《套磁与申请建议》」. 与 v0.5.0+v0.9.0 旧规则 (含 §1.4 套磁) 冲突, 旧规则作废. 现有 13 PIs wiki docx 中, 仅 2 个 (毛玉仁/高云君) 含此 §, 需 fix.
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

> **完整 Output contract (4 章节必含 + H2 emoji 硬要求 + paper card 硬要求 + 5 必含 sections)**已下沉到 [`references/output-contract.md`](references/output-contract.md) (~50 行, 2026-06-11 拆分, v0.12.0 改 4 章节).
>
> **TL;DR (v0.12.0)**: Primary 输出是飞书 docx URL; 4 章节 h2 顺序固定 (TL;DR / 导师画像 / 申博匹配度 / 论文全景 / 数据来源 — 不含套磁); 必含 1 TL;DR callout + 1 grid + ≥1 callout/section + `<table>` 块; H2 标题禁止装饰性 emoji (👤📊✉📚📖🎯ℹ); paper card 必须 v0.11.0 完整版 / v0.4.0 紧凑版 二选一.

## Paper Entry Format (v0.3.9 完整版) — 详见 references/

> 完整 15 行/paper paper card 规范 (224 行) 已下沉到 [`references/paper-entry.md`](references/paper-entry.md) (v0.4.0 progressive disclosure refactor, 2026-06-10)。
>
> **v0.4.0 起默认使用紧凑版 (7 行/paper, 详见 §Paper Card v0.4.0 紧凑 + references/paper-card.md)**。v0.11.0 完整版仅在论文 ≤ 3 篇 / 套磁信深度引用 / 单篇 deep-dive 时使用 (套磁信独立写, 不在 docx h2 章节里, v0.12.0)。
>
> **选型指南 (v0.11.0)**: 论文 ≤ 3 篇 → v0.11.0 完整版 (信息密度高) / 论文 ≥ 10 篇 → v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)。同一 doc 中可混用, 但**同一论文不能同时用两种格式**。

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
> **TL;DR**: L1-L4 全失败 → "信息黑洞 — 建议手动提供主页 URL", **禁止编造**. L1 成功 + L2/L3/L4 半失败 → 🟡 数据稀疏. 一作顶会论文 = 0 → 🟡 通讯/末位 PI 模式, 套磁时追问 1v1 带生. 用户同时调研 ≥3 位老师 → 切换 `phd-scout --mode batch`. (v0.12.0: 套磁信独立写,不在 docx h2 章节里)


📂 **Examples** → see [`references/examples.md`](references/examples.md) (loaded on demand)

## References

- `references/report-template.md` — 飞书 docx v0.13.6 XML 模板 (TL;DR callout / 4 章节必含 + 1.3 A/B/C 论文重组 + 1.4.3 P0/P1/P2 + 1.5 套磁清单; v0.13.5 paper link fallback)
- `references/output-contract.md` — 飞书 docx v0.13.0 6 章节必含硬要求 + 22 项 LLM 自检 (Check 1-22)
- `references/paper-card-formats.md` — v0.13.2 paper card 选型入口 (v0.3.0 增强 12 行 h3 [1.4.A 顶会 10 默认] + v0.4.0 紧凑 7 行 [1.4.B 主题表用] + v0.11.0 完整 10 行 [论文 ≤ 3 篇] + 22 项自检)
- `references/paper-card.md` — v0.4.0 紧凑 paper card 详细规范 (295 行, 含 inline 标记规则 / 13 项自检 / 12 papers 样例)
- `references/paper-entry.md` — v0.11.0 完整 paper card 详细规范 (299 行, 含 8 enum status / 7 paper URL / 22 项自检)
- `references/output-schema.md` — 12 项硬要求 (v0.6.0 → v0.10.0)
- `references/audit-checklist.md` — 12 项 audit mode 合规检查
- `references/data-sources.md` — L1-L4 抓取细节 + ZJU URL 模式 + S2 API 字段
- `references/llm-prompt.md` — 总结 prompt (synthesis rules + 章节填充指引)
- `bin/README.md` — 工具目录说明 (2 active + 4 archive/v04-legacy)
- `CHANGELOG-archive.md` — v0.4.0 → v0.10.0 7 个历史版本详细 changelog (主页 CHANGELOG.md 只保留 v0.11+)