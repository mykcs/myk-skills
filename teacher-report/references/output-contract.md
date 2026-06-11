---
name: teacher-report-output-contract
description: |
  teacher-report Output contract 完整规范. 5 章节必含硬要求 + H2 emoji 硬要求 + paper card 选型. main SKILL.md 仅保留概述.
---

# teacher-report Output contract

- **Primary**: a Feishu `docx` URL (looks like `https://{tenant}.feishu.cn/docx/doxcn...`)
- **Document title**: `{学校} {老师姓名}` (e.g. "浙江大学 吴飞")
- **5 required sections in order**: TL;DR callout, 导师与课题组画像, 申博匹配度评估, 套磁与行动建议, 论文产出全景（按年）, 数据来源与说明
- **Visual elements required**: 1 TL;DR callout + 1 grid, ≥ 1 callout per section for non-text observations, all data tables formatted as `<table>` blocks (not markdown)

## 🚨 5 章节必含硬要求 (2026-06-05 v0.2.6, 违反 = skill 协议破坏)

- 必须有 `<h2>1. ...</h2>` / `<h2>2. ...</h2>` / `<h2>3. ...</h2>` / `<h2>4. ...</h2>` / `<h2>5. ...</h2>` 5 个 h2 章节, **顺序固定**
- **§2 申博匹配度评估 必须有 `<h2>2. ...</h2>` 标题**, **禁止**直接跳到 `<h3>2.1` 或 `<h4>(1)` (v0.2.3 残缺版踩过这个坑)
- **§1 / §3 / §4 / §5 同理**必须有 `<h2>` 标题, 不能缺
- 模板生成后, LLM 必须自检: `grep -c '<h2>' content` ≥ 5

## 🚨 H2 标题无装饰性 emoji 硬要求 (2026-06-11 v0.6.0, 违反 = skill 协议破坏)

- 5 大章节 H2 标题 (1. 导师与课题组画像 / 2. 申博匹配度评估 / 3. 套磁与申请建议 / 4. 论文产出全景 / 5. 数据来源与说明) **禁止**装饰性图标 emoji: 👤📊✉📚📖🎯ℹ 等
- **保留** (allowlist, 状态/信号类, 不算装饰): ✅❌⚠⭐🟢🟡🔴⛔🚨
- **Why**: 飞书 outline 节点树视觉一致, 避免乱图标
- **Template 实施**: LLM 生成 H2 标题时, 一律用纯中文 "1. 导师与课题组画像" (无前缀图标); 现有 13 docs × 5 H2 = 65 段已统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb, 2026-06-11)
- **新 docx 模板生成前必跑**: `python3 ~/.agents/skills/teacher-report/scripts/check_h2_emoji.py {content}` → 0 decoration emoji 才输出

## 🚨 论文条目 paper card 硬要求 (2026-06-08 v0.3.3 → 2026-06-10 v0.4.0 紧凑可选)

- 所有论文 (§4 论文产出全景 / §2.2 论文举例 / §3 套磁信引用 任何位置) **必须**用以下 2 种 paper card 格式之一:
  - **v0.3.9 完整版** (15 行/paper, 单独标注行): 详见 `references/paper-entry-v0.3.9.md`
  - **v0.4.0 紧凑版** (7 行/paper, inline 标记): 详见 `references/paper-card-v0.4.0.md`
- **选型指南**:
  - 论文 ≤ 3 篇 → 优先 v0.3.9 完整版 (信息密度高)
  - 论文 ≥ 10 篇 → 优先 v0.4.0 紧凑版 (节省 53% 篇幅, Feishu outline 展开)
  - 同一 doc 中可混用 v0.3.9 和 v0.4.0, 但**同一论文不能同时用两种格式** (避免 reader 困惑)
- **必须包含 4 维 taxonomy 4 行独立 `<p>` 块**(`大领域：` / `中方向：` / `小任务：` / `子技术：` 每行 1 字段)— **禁止** 4 列表格 (无论 v0.3.9 还是 v0.4.0)
- **作者列表**: 写完整 verbatim + 中文括注(全作者), 禁止 `(末位/通讯)` 缩写 / `(通讯 PI 模式)` 描述 / `... 16 名作者` 省略 / 仅 `Fei Wu` 单独括注

## 🚨 H1-H4 编号标题 dot 后缀硬要求 (2026-06-11 v0.7.0)

- h1 / h2 / h3 / h4 编号标题必须以 `.<space>` 结尾: `1.` `2.` / `1.` `2.` / **`1.1.` `2.1.` `3.2.` (h3 必须带 dot)** / `1.` `2.`
- **核心变更**: h3 编号从 v0.2.5 `1.1` (无 dot) 升级到 v0.7.0 `1.1.` (有 dot 后缀), 与 h2/h4 一致
- **禁止**手动 `(1) (2) (3)` 编号 / `① ② ③` 字符 / `████████` 字符画 / 混用 4 种编号风格
