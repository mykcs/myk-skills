---
name: teacher-report-output-contract
description: |
  teacher-report Output contract v0.13.6 完整规范 (2026-06-17). **4 章节必含** (1.1 自评 / 1.2 导师画像 / 1.3 论文全景 / 1.4 数据来源 / 1.5 套磁准备) + H2 emoji 硬要求 + paper card 选型 + 与 report-template.md 100% 一致. main SKILL.md 仅保留概述.
---

# teacher-report Output contract (v0.13.6)

> **核心变更 (2026-06-17 v0.13.6)**: 4 章节必含 (TL;DR + 1.1 自评 / 1.2 导师画像 / 1.3 论文全景 / 1.4 数据来源 / 1.5 套磁准备清单) + 19 → 22 项 LLM 自检 (新增 Check 20 P0/P1/P2 标签 + 21 主动 WebFetch 主页 + 22 1.5 套磁清单).

- **Primary**: a Feishu `docx` URL (looks like `https://{tenant}.feishu.cn/docx/doxcn...`)
- **Document title**: `{学校} {老师}` (e.g. "浙江大学 魏颖")
- **4 required sections in order** (v0.13.6): 1.1 自评 / 1.2 导师画像 / 1.3 论文全景 / 1.4 数据来源 / 1.5 套磁准备清单
- **Visual elements required**: 1 TL;DR callout + 1 grid, ≥ 1 callout per section for non-text observations, all data tables formatted as `<table>` blocks (not markdown)
- **套磁信** (v0.12.0 → v0.13.6): 套磁信草稿在 chat 输出, **不**写到飞书 docx h2 章节里. 飞书 docx 内**只**放 §1.5 套磁准备清单 (24h 5 件事 + 1v1 5 题 + 发信时窗 + 备份计划), 不放具体套磁信正文.

## 🚨 4 章节必含硬要求 (2026-06-17 v0.13.6, 违反 = skill 协议破坏)

- 必须有 5 个 `<h2>` 章节 (含 1 TL;DR), **顺序固定** (4 章节必含):
  0. `<h1>` 标题 (e.g. "浙江大学 魏颖") + TL;DR callout + grid (header 块, 1 h2 之外)
  1. `<h2>1.1. 自评</h2>` (user-owned v0.9.0, 禁止写入)
  2. `<h2>1.2. 导师与课题组画像</h2>` (1.2.1-1.2.5)
  3. `<h2>1.3. 论文产出全景</h2>` (1.3.A 顶会 10 + 1.3.B 主题表 + 1.3.C 趋势)
  4. `<h2>1.4. 数据来源与说明</h2>` (1.4.1-1.4.3)
  5. `<h2>1.5. 套磁准备清单</h2>` (1.5.1-1.5.4)
- **§1.1 / §1.2 / §1.3 / §1.4 / §1.5 同理**必须有 `<h2>` 标题, 不能缺
- 模板生成后, LLM 必须自检: `grep -c '<h2>' content` = 5 (4 章节必含 + TL;DR 计数 0 h2)
- **v0.12.0 → v0.13.0 移除**: v0.5.0 旧的 `<h2>1.4. 套磁与申请建议</h2>` 章节 — 替换为 `<h2>1.5. 套磁准备清单</h2>`. Check 18 自检: 禁止 §1.4 套磁 h2 出现, 必须有 §1.5 套磁清单 h2

## 🚨 H2 标题无装饰性 emoji 硬要求 (2026-06-11 v0.6.0, 违反 = skill 协议破坏)

- 6 大章节 H2 标题 (1.1-1.6) **禁止**装饰性图标 emoji: 👤📊✉📚📖🎯ℹ 等
- **保留** (allowlist, 状态/信号类, 不算装饰): ✅❌⚠⭐🟢🟡🔴🟥🟨🟩⛔🚨
- **Why**: 飞书 outline 节点树视觉一致, 避免乱图标
- **Template 实施**: LLM 生成 H2 标题时, 一律用纯中文 "1.2. 导师与课题组画像" (无前缀图标); 现有 13 docs × 5 H2 = 65 段已统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb, 2026-06-11)
- **新 docx 模板生成前必跑**: `python3 ~/.agents/skills/teacher-report/scripts/check_h2_emoji.py {content}` → 0 decoration emoji 才输出

## 🚨 论文条目 paper card 硬要求 (2026-06-08 v0.3.3 → 2026-06-17 v0.13.0)

- **§1.3 论文重组 (v0.13.0 NEW)**: §1.3 必含 3 个 h3:
  - 1.3.A 顶会代表作 (10 篇, oral/spotlight/BP Finalist 选, 各 1 callout 4 行 metadata)
  - 1.3.B 其他论文 (按 5-7 主题汇总, 每主题 1 callout 内部 table)
  - 1.3.C 趋势分析 (1 callout, 5 观察点)
- **paper card 选型 (v0.13.6)**: 与 1.3.A 一致
  - **v0.11.0 完整版** (15 行/paper): 详见 `references/paper-card-v11.md`
  - **v0.4.0 紧凑版** (7 行/paper): 详见 `references/paper-card-v04.md`
- **v0.11.0 vs v0.4.0 选型指南**:
  - 论文 ≤ 3 篇 → 优先 v0.11.0 完整版 (信息密度高)
  - 论文 ≥ 10 篇 → 优先 v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)
  - 1.3.A 顶会 10 篇 → v0.4.0 紧凑 (callout 内 4 行 metadata)
  - 1.3.B 主题表 → 仅 title + venue + arXiv (无完整 paper card)
- 同一 doc 中可混用 v0.11.0 和 v0.4.0, 但**同一论文不能同时用两种格式** (避免 reader 困惑)
- **必须包含 4 维 taxonomy 4 行独立 `<p>` 块**(`大领域：` / `中方向：` / `小任务：` / `子技术：` 每行 1 字段)— **禁止** 4 列表格 (无论 v0.11.0 还是 v0.4.0)
- **作者列表**: 写完整 verbatim + 中文括注(全作者), 禁止 `(末位/通讯)` 缩写 / `(通讯 PI 模式)` 描述 / `... 16 名作者` 省略 / 仅 `Fei Wu` 单独括注

## 🚨 H1-H4 编号标题 dot 后缀硬要求 (2026-06-11 v0.7.0)

- h1 / h2 / h3 / h4 编号标题必须以 `.<space>` 结尾: `1.` `2.` / **`1.1.` `2.1.` `3.2.` (h3 必须带 dot)** / `1.` `2.`
- **核心变更**: h3 编号从 v0.2.5 `1.1` (无 dot) 升级到 v0.7.0 `1.1.` (有 dot 后缀), 与 h2/h4 一致
- **禁止**手动 `(1) (2) (3)` 编号 / `① ② ③` 字符 / `████████` 字符画 / 混用 4 种编号风格

## 🚨 主动 WebFetch 主页硬要求 (2026-06-17 v0.13.6, 违反 = skill 协议破坏)

- **§1.2.1 基本信息与学术身份** 表格 9 行, 主页 + 邮箱 **必含**主动 WebFetch 抓取:
  - **主页 URL**: LLM 必跑 `WebFetch <person.{学校缩写}.edu.cn/{pinyin}>` + `WebSearch "{老师} {学校} 主页"`, 2 路 1 抓即填
  - **邮箱**: 主页抓取后从页面 metadata 解析, 必含 `<a href="mailto:...">` 链接
  - **抓取失败**: 留 🟨 P1 待补 + 抓取命令提示 (e.g. "建议重试 WebFetch https://person.zju.edu.cn/yingwei"), **不**留 ❓
- **3 路反幻觉**: WebFetch 主页 + WebSearch 同名 + boshihoujob 招聘网, 至少 2 路一致才填

## 🚨 P0/P1/P2 标签硬要求 (2026-06-17 v0.13.6, 违反 = skill 协议破坏)

- **❌ 禁止单独使用 ❓ / ❌ / ❎ 占位符** (v0.5.0 旧模板行为)
- **必含** P0/P1/P2 标签 + 优先级语义:
  - 🟥 **P0** = critical for decision (套磁必问 / 招生名额 / 实际带生者 / 团队氛围 / 矛盾说法)
  - 🟨 **P1** = important for ongoing eval (1v1 频率 / 实习政策 / 留校情况 / 行政职务 / 学术兼职)
  - 🟩 **P2** = nice-to-have (其他非关键字段)
- **统一路径**: 所有待补字段汇总到 §1.4.3 (单一 callout). 其他章节末尾不再重复 "建议补充路径" (4 行 → 1 行 "见 §1.4.3")
- **§1.4.3 必含**: 至少 5 条 P0 + 3 条 P1 + 1 条 P2 待补项, 每条标 [数据源] + [建议补充路径]

## 🚨 1.5 套磁准备清单硬要求 (2026-06-17 v0.13.6, 违反 = skill 协议破坏)

- **5 h2 章节**含 §1.5 套磁准备清单, **替代** v0.5.0 旧 §1.4 套磁与申请建议
- **4 个 h3 必含**:
  - 1.5.1 24h 内必做的 5 件事 (精读 2 篇 / 写开场白 / CV / OpenReview 评论 / 找 1v1)
  - 1.5.2 1v1 必问 5 题 (Onboarding / 推免 vs 申请-考核 / 方向 bridge / 延毕与转博 / 实习与会议) — 每题**必含** "覆盖 §X.Y" 标注
  - 1.5.3 发信时窗 + 邮件模板要点 (callout 列出最佳/次佳/避免时窗 + 邮件 6 段结构)
  - 1.5.4 备份计划 (Plan A 正博 / B senior PhD 联培 / C 同方向其他 PI / D 跨校备份 / E 时间线) — callout 红色
- **套磁信正文禁止写到 docx** (v0.12.0 Output Discipline). 套磁信草稿在 chat 输出, docx 内**只**放 1.5 准备清单
- **与 v0.5.0 旧 §1.4 套磁 h2 互斥**: 禁止同时存在 `<h2>1.4. 套磁与申请建议</h2>` (Check 18 自检)

## 🚨 无水印硬要求 (2026-06-17 v0.13.6, 违反 = skill 协议破坏)

- **禁止** "整理人: claudecode teacher-report skill vX.X.X" 水印 (v0.5.0 旧模板残留)
- **替换为**: 文档生成时间 + v0.13.6 套磁就绪版 + 关键变更标签 (1.3 论文 A/B/C + 1.5 套磁清单 + 主动 WebFetch 主页 + P0/P1/P2 + paper link fallback v0.13.5) + 模板源 link
- **必含** 模板源 `<a href="https://github.com/mykcs/myk-skills/tree/main/teacher-report/references/report-template.md">teacher-report v0.13.6</a>` link

## 🚨 22 项 LLM 自检清单 (v0.13.6)

| # | 自检 | 规则 | 工具/脚本 |
|---|------|------|-----------|
| 1 | H2 数量 | `grep -c '<h2>' content` = 5 | manual |
| 2 | H2 顺序 | h2 编号 1.1→1.2→1.3→1.4→1.5 按出现顺序 | manual |
| 3 | H2 紧邻 h3 | h2 后面紧跟 h3 + body, 不孤立 | manual |
| 4 | H2 无装饰 emoji | 装饰 emoji 0 hits (allowlist 状态类保留) | `scripts/check_h2_emoji.py` |
| 5 | H3 编号 dot 后缀 | h3 = `1.X.Y.` (有 dot) | manual |
| 6 | H2 长编号 | h2 = `1.X.` (有 dot) | manual |
| 7 | paper card 选型 | 论文 ≤3 → v0.11.0 / ≥10 → v0.4.0 | manual |
| 8 | 4 维 taxonomy | `大领域：` / `中方向：` / `小任务：` / `子技术：` 4 行独立 `<p>` 块 | manual |
| 9 | 作者列表完整 | 禁止 `et al.` / `...` / 缩写 | manual |
| 10 | arXiv 完整 URL | `https://arxiv.org/abs/{id}` | manual |
| 11 | paper URL 7 优先级 | OpenReview → arXiv → DOI → papers.cool → proceedings → journal → 主页 PDF | manual |
| 12 | status enum 8 值 | 被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿 | manual |
| 13 | Wiki Subject Author Verification | byline 必须与 L1-L4 来源匹配 | `scripts/check_wiki_subject.py` |
| 14 | H2 装饰 emoji (v0.6.0) | 👤📊✉📚📖🎯ℹ 等装饰 emoji 0 hits | `scripts/check_h2_emoji.py` |
| 15 | H3 编号 dot 后缀 (v0.7.0) | h3 全部带 dot 后缀 | manual |
| 16 | 深度+1 编号 (v0.8.0) | h2=1.X. / h3=1.X.Y. / h4=1.X.Y.Z. | manual |
| 17 | 中文名字符级 typo (v0.10.0) | 老师姓名与 L1-L4 来源字符级匹配 | `scripts/check_chinese_name.py` |
| 18 | 4 章节齐全 + 不含套磁 v0.12.0 → v0.13.6 | 5 h2 = 1.1/1.2/1.3/1.4/1.5, 禁止旧 §1.4 套磁 h2 | manual |
| 19 | paper card 编号样式 (v0.11.0) | 编号 `1.` `2.` 纯文本前缀 | manual |
| 20 | **P0/P1/P2 标签 (v0.13.0 NEW)** | 0 ❓ 占位符, 待补字段全部标 P0/P1/P2 + 数据源 + 建议补充路径 | `scripts/check_p0_p1_p2.py` |
| 21 | **主动 WebFetch 主页 (v0.13.0 NEW)** | §1.2.1 主页 + 邮箱必含 WebFetch 验证, 失败留 P1 + 抓取命令 | `scripts/check_webfetch_homepage.py` |
| 22 | **1.5 套磁清单齐全 (v0.13.0 NEW)** | 1.5.1 / 1.5.2 / 1.5.3 / 1.5.4 4 h3 必含, 1.5.2 每题必含 "覆盖 §X.Y" 标注 | `scripts/check_taoci_checklist.py` |
| 23 | **arXiv URL 真伪 verify (v0.13.4 NEW, 违反 = skill 协议破坏)** | 每个 arXiv ID 必跑 `WebFetch https://arxiv.org/abs/{id}` verify HTTP 200 + title 匹配 L1 byline. **禁止** LLM 编造 YYMM.NNNNN 格式外 arXiv ID. 8 假 arXiv ID (e.g. 22hBwIf7OC / TpD2aG1h0D) 必标 "待补" + 删 href. 1 ID 真但内容 LLM 编造 (e.g. 2206.04335) 也必标 "待补" 重 verify. | `scripts/check_arxiv_url.py --id {id}` |
| 24 | **paper link fallback 硬要求 (v0.13.5 NEW, 违反 = skill 协议破坏)** | 字段名 `arXiv：` → `paper link:`. Fallback 顺序: (1) arXiv ID 真 (YYMM.NNNNN 格式 + Check 23 verify) → `https://arxiv.org/abs/{id}`. (2) arXiv ID 假/无 → `https://openreview.net/forum?id={id}` (用 arXiv ID 拼). (3) OpenReview 也无 → `暂无`. 5 假 ID (22hBwIf7OC/5U1rlpX68A/gc8QAQfXv6/TpD2aG1h0D/iTTZFKrlGV) + 36 假 ID 1.3.B 5 主题 → OpenReview fallback. 1 无 arXiv (#10 Scalable Heterogeneous Translated Hashing) → 暂无. | `scripts/check_arxiv_url.py --id {id}` |

**Check 20-22 v0.13.0 新增**: 22 → 22 项 (旧 19 项保留 + 新 3 项)

## 完整章节必含 + 子节必含 (v0.13.6 final)

- **§1.1 自评**: `<h2>` + 占位 `<p>` + `<hr/>` (3 blocks, user-owned)
- **§1.2 导师画像**: `<h2>` + `<h3>1.2.1</h3>` 9 行 table + `<h3>1.2.2</h3>` 列表 + `<h3>1.2.3</h3>` 2 callout + `<h3>1.2.4</h3>` 2 callout + `<h3>1.2.5</h3>` 6 行 table + 2 callout
- **§1.3 论文产出全景**: `<h2>` + 数据快照 callout + `<h3>1.3.A</h3>` 10 callout (⭐ 顶会代表作, v0.3.0 增强 11 行) + `<h3>1.3.B</h3>` 5 callout (5 主题 paper link) + `<h3>1.3.C</h3>` 1 callout (趋势分析)
- **§1.4 数据来源**: `<h2>` + `<h3>1.4.1</h3>` 4 li + `<h3>1.4.2</h3>` 4 li + `<h3>1.4.3</h3>` 1 大 callout (统一路径 P0/P1/P2 待补汇总)
- **§1.5 套磁准备清单**: `<h2>` + `<h3>1.5.1</h3>` 5 li (24h 5 件事) + `<h3>1.5.2</h3>` 5 li (1v1 5 题, 必含 "覆盖 §X.Y" 标注) + `<h3>1.5.3</h3>` 1 callout (时窗 + 邮件 6 段结构) + `<h3>1.5.4</h3>` 1 callout (Plan A-E 备份计划)

- **footer**: `<hr/>` + 2 `<p>` (无水印, v0.13.6 模板源 link)
