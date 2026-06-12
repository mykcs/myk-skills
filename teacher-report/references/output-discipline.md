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

**v0.11.1 扩展 (2026-06-12) — docx 内部 preamble callout 禁止**:

**问题背景**: v0.11.0 仅禁止 LLM 在 chat 输出 4 行元信息 preamble, 但实际 13 PIs 飞书 wiki docx 内部 12/13 都含同款 4 行 preamble callout (本报告/调研对象/招生匹配度/论文产出 4 行 inline 紧凑版). LLM 在生成 docx 时**不仅**在 chat 复述, 还**直接写入** docx 内部 callout. v0.11.0 硬要求漏了 docx 内部维度.

**硬要求 (扩展 v0.11.0)**:
- LLM 在生成新 docx 时, **不得**在 docx 内部创建 4 行元信息 preamble callout:
  - ❌ `<callout emoji="🎯">\n  <p><b>本报告</b>: v0.5.0 ...</p>\n  <p><b>调研对象</b>: ...</p>\n  <p><b>招生匹配度</b>: 🟡 ...</p>\n  <p><b>论文产出</b>: N 篇...</p>\n</callout>`
- 元信息正确存放点 (与 v0.11.0 表格对齐):
  - **本报告 / v0.5.0 升级声明** → 写 changelog 时已经在 SKILL.md 顶部, docx 不需复述
  - **调研对象** → docx `<title>` 标签 + §1.1 基本信息与学术身份 h3 (不是独立 callout)
  - **招生匹配度** → docx §2 申博匹配度评估 (含 🟢/🟡/🔴 灯号 + 文字说明) + TL;DR grid 4 列之一
  - **论文产出** → docx §4 论文产出全景 (按年表 + paper card 列表, 精确数字) + TL;DR grid 4 列之一
  - **L? 抓取状态** → docx §5 数据来源与说明 (L1-L7 数据源分别列, 标 [社区来源]/[L4 推断] 等标签)
- **合法 callout 形式 (允许)**:
  - TL;DR callout (含 TL;DR 字符串, 4 列 grid) — 允许, 这是 v0.4.0 设计
  - §5 待补字段 callout (含 `<b>本报告未确认的字段 (影响决策)</b>`) — 允许, 这是 v0.5.0 字段汇总
  - ❓ / 🎓 / 💡 / 💌 / 📅 等带 emoji 装饰的状态/信息 callout — 允许 (与 v0.6.0 装饰性 emoji ban 不冲突, 因为这些是状态/信息 emoji, 不是装饰)
- **违规检测** (审计/重写时):
  - 跑 `grep -c '<b>本报告</b>:' <docx_xml>` (注意: 排除 `<b>本报告未确认` 合法形式) > 0 → 违规
  - 跑 `grep -c 'L7 数据已实际抓取' <docx_xml>` > 0 → 违规 (这是 preamble 专用 marker)
  - 跑 `grep -c '<b>招生匹配度</b>: 🟡 中' <docx_xml>` > 0 → 违规 (紧凑 4 行形式)
- **违规清理** (F2 块级修):
  - 找含 `<b>本报告</b>` (且 not `<b>本报告未确认`) 的 callout 的 block_id
  - `lark-cli docs +update --api-version v2 --doc <obj> --command block_delete --block-id <callout_block_id>`
  - verify: re-fetch + grep count = 0
- **执行状态 (2026-06-12)**: 13 PIs docx 12/13 已 F2 块级修清理 (邓淑敏 P3-pre test + 张圣宇/魏颖/吴飞/刘泽民/况琨/赵洲/沈春华/肖俊/周晓巍/郑小林/刘忠鑫 batch 11 docs), 1 PI (汤斯亮 obj=A8lN) 漏删 (per obj_token 错位 1 位 bug, 后已补删), 1 shortcut (高云君 obj=YaXo) 误删 + append 重建说明 callout. 13 PIs 全部 v0.11.1 CLEAN (0 违规 marker).

### Step 1 — Data fetching (4-level fallback)

> **🚨 硬规则**:
> - L2 Semantic Scholar 失败时, **只准 1 次 5s 重试**, 任何 5s/15s/30s/60s 指数退避 = 违反本 skill. L4 web_search 聚合是 S2 字段的有效替代, 直接跳.
> - L3 DBLP pid 0 hits 时, 不要无限重试, 直接走 L4.
> - L1 抓到 SPA 锚点不全时, 必须切 playwright, 不要只 webfetch.
> - 任何 L1-L4 抓取中, "导师本人一作顶会论文数" 是必查字段, 0 → 风险灯号 🟡 中 (见 §Failure handling).

**数据源链**: L1 学校/学院官网 (webfetch → playwright 兜底) → L2 S2 API → L3 DBLP → L4 MiniMax web_search → L5 kimi-webbridge → L6 anysearch → **L7 申博论坛 (v0.5.0 新增, mysupervisor.org + 学院 PDF + 知乎 + 小红书 + 博客园)**.

**L7 反幻觉**: L1 字段 (学术身份/职务/email) → 无标签; L7 字段 (招生偏好/团队氛围/培养模式) → 必显式标 `[社区来源]` 或 `[社区-多人共识]` (≥3 条独立); L1+L7 冲突 → 标 `[冲突: L1 vs L7]`.

完整 L1-L7 字段映射表 + ZJU URL 模式 + S2 API 字段详见 `references/data-sources.md`.
