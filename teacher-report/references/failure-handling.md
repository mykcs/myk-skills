---
name: teacher-report-failure-handling
description: |
  teacher-report Failure handling 完整规范. 9 类 failure 模式 + 处理动作. main SKILL.md 仅保留概述.
---

# teacher-report Failure Handling

| Failure | What to do |
|---------|------------|
| L1-L4 all return nothing | Stop, tell the user "信息黑洞 — 五级抓取都失败, 建议手动提供主页 URL 或姓名 + 单位"。**Do not fabricate.** |
| L1 成功 + L2/L3/L4 部分失败 (半失败): L2 抓到的近 3 年论文 < 5 篇, 或 venue 验证不全 | 🟡 中。报告顶部 ⚠️ callout 必须显式标 "**数据稀疏 — 套磁信引文可能不准确**", **禁止** 在套磁信里引用 L2 没验证过的论文。 |
| L1 成功 + 近 3 年署名论文 ≥ 30 篇, 但**本人一作 / 共一论文 = 0** | 🟡 中。典型 "通讯/末位 PI 模式", 实际带生者高度疑为青年教师。报告中必须显式标红 + 套磁信必须追问 1v1 带生安排。 |
| 课题组定位 "双核心 / 三核心" 硬塞给学生代笔模式 | ⛔ **禁止** (见 `report-template.md §3` 反模式段)。如果导师是末位/通讯 PI、实际带生者疑为青年教师, **必须** 用 ⚠️ callout 显式标 "实际带生者高度疑似 X, 导师时间投入 < 50%, 需邮件确认 1v1 带生安排" — 不可包装成 "X-Y 双核心" 或 "X-Y-Z 三核心" callout (那是把 "学生代笔" 美化成 "团队结构")。 |
| User asks for many teachers at once (≥ 3 位) | **Out of scope, redirect to `phd-scout --mode batch`**。回复模板: "`teacher-report` 一次只处理一位老师 (深度报告)。如需批量调研多位老师, 请告诉我 — 我会切换到 `phd-scout --mode batch` 写 Bitable 表, 之后再对感兴趣的字段再做深度 `teacher-report`。" |
| Personal page exists but is JS-rendered SPA | Use `playwright` MCP `browser_navigate` → `browser_snapshot` to get rendered text. Avoid `webfetch` on SPAs. |
| L2 Semantic Scholar rate-limited (429) | 1 次重试 (5s), 仍 429 跳 L3。**不要指数退避** — 5s/15s/30s/60s 在已知失败的端点上浪费 ≥2 分钟。L4 web_search 聚合是 S2 字段的有效替代。 |
| User has not enabled lark-cli auth | The `docs +create` call will return `LARK_USER_AUTH_REQUIRED`. Tell the user to run `lark-cli auth login` and retry. |
| LLM output exceeds `--content` size limit | Split into skeleton + appends per Step 3. |
| Same teacher fetched twice with different results | Trust L2 (Semantic Scholar) h-index + paperCount over L1 self-claimed numbers. Note both in `5. 数据来源`. |
