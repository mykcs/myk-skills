---
name: teacher-report-inputs-and-mode
description: |
  teacher-report 6 字段 input 收集 + Disambiguation edge cases + Step 0.5 token 询问. main SKILL.md 仅保留概述, 详细下沉本文件.
---

# teacher-report Inputs + Mode

## 6 字段 input 收集

Before fetching, confirm or infer the following from the user's message:

1. **老师姓名** (required) — full Chinese name or Pinyin. If ambiguous (common name + university), ask the user.
2. **学校** (strongly recommended) — disambiguates homonyms and lets L1 (university site) work. If missing, infer from context or ask.
3. **学院 / 系** (optional) — narrows L1 search.
4. **用户的研究方向 / 匹配诉求** (optional) — used in the 方向匹配度 section to score fit. If user didn't say, write a generic "通用 CV/ML/Agent" profile and note "无特定方向假设" in the report.
5. **申博 wiki dashboard token** (recommended) — 飞书 wiki/docx token, 代表用户的"申博候选池 dashboard"。提供时, 生成的报告**自动 append 摘要**到这个 wiki(让用户在一个 wiki 节点看到所有候选老师)。不提供时, fallback 到 my_library(每个老师独立 docx)。
6. **申博 wiki parent token** (optional) — 飞书 folder/wiki 节点 token, 生成的 docx **作为子页**放到这个 parent 下。和 (5) 配合: parent 是 wiki 树, dashboard 是顶层汇总。

If 1 + 2 are both missing, **do NOT start fetching — ask the user**.

## Disambiguation edge cases (must read)

- **同名老师跨校任职**: S2 affiliations 可能跨校混合(如老师从清华转浙大)。**先 L1 查现职学校官网**, 若学校已变动, 以**现职**为准; 在报告 §5 数据来源标 "L2 论文列表含 2 单位混合数据(2024 前 X 校 / 2024 后 Y 校)"。
- **同名 + 同校 + 跨学院**: CS 学院有 "李明", 医学院也有 "李明"。**用学院+研究方向的 L1 静态页或学院教师列表 grep** 二次定位。
- **拼音歧义**: "李伟" / "Li Wei" 在 S2 上可能匹配英文姓名写法 "Wei Li" (last-first)。**优先用中文名 + 学校搜 L1**, 再 S2 验证。

## Step 0.5 — Confirm dashboard/parent token

> **⏰ 时机**: 在 Step 1 抓取之前, 先问 user 5/6 token 提供意愿, 决定 Step 3 走模式 A / B / C。

如果 user 没有主动提供 §5/§6 token, 使用 `AskUserQuestion` 给 3 个选项:

1. **两个 token 都有** → 模式 A (子页 + dashboard 摘要)
2. **只 dashboard** → 模式 B (my_library + dashboard 摘要)
3. **都没有 / 不在乎** → 模式 C (独立 docx, user 手动归档)

如果 user 在原始消息里**显式说过** token (从上下文提取), 跳过询问直接用。

**为什么需要这个 step**: LLM-prompt.md 和 report-template.md §11 dashboard 摘要都假设 dashboard token 已提供, 但实际 user 经常忘了。提前问一次, 避免生成完 docx 后再问 "要不要加 dashboard"。
