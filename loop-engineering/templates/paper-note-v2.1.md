# Paper Note v2.1 模板 (Stage 3)

> **来源**: weiying20260624 week2 NOTE-AGENT 用模板 (commit f2e9721, 39 份 note, 4242 行)
> **8 段强制**: §1 + §1.5 + §2 + §3 + §4 + §6 + §7 + 元信息
> **3 关注点**: 解决什么问题 / 实验怎么设计 / 可信度

## 命名规则

`<NN>-<short-kebab-case-slug>.md` (NN = 2 位序号)

## 复制下面整段, 改占位符

```yaml
---
name: <Paper Title>
description: <一句话, 写明 paper 解决什么 + 跟 weekly 关联>
metadata:
  type: paper_note
  project_id: <PROJECT_ID>
  paper_id: <short-slug>
  status: v0 骨架 / round 1 摘要 / round 2 全文 / round N≥3 / user 真读校准
  venue: <ICML 2026 / ICLR 2025 oral / arXiv 2509.25123 / 微信公众号>
  team: <团队 / 实验室>
  arxiv: <arXiv ID / DOI / URL>
  code: <github URL 或 null>
  关联 weekly: <weekly-03 / 不引>
  写于: YYYY-MM-DD HH:MM
---

# <Paper Title>

> **写的人**: user | claudecode (round 0/1/2)
> **状态**: <跟 frontmatter status 一致>
> **风险**: 真读 pending / user 已校准

---

## §1 它主要解决什么问题 (MUST, ≤ 100 字)

- **痛点**: <1-2 句>
- **本文思路**: <1 句话>
- **跟我关系**: <1 句话, 跟 weekly / 课题 / CV 关联>

---

## §1.5 子方向归位 (week 2 加, pipeline 任务必填)

| 维度 | 填什么 |
|------|--------|
| 子方向名 (1-2 个) | <填> |
| 跟哪个 weekly 关联 | <weekly-0X / 不引> |
| 我倾向的 1-2 idea | <填> |
| 跟组里连接 | <compositionality / 等> |
| 待补 / 风险 | <填> |

---

## §2 实验设计 (MUST, 5 列强制)

| 实验 | 数据集 | baseline | 关键数字 | 设计意图 (MUST) |
|------|--------|----------|----------|---------------|
| 主实验 | <benchmark> | <方法 1, 2> | <数字 + %> | **为什么选这个数据 + 验证什么?** |
| 消融 1 | <变体> | <去掉的组件> | <数字> | **验证哪部分真有用?** |
| 消融 2 | ... | ... | ... | ... |
| 跨数据集 | <数据集 B> | <同主实验> | <数字> | **跨域泛化证据?** |
| case study | <真实例子 1-3> | — | <成功/失败> | **展示什么现象?** |

---

## §3 可信度评估 (MUST, 7 维度评分)

| 维度 | 评分 (1-5) | 证据 (MUST) |
|------|-----------|-------------|
| 论文 venue | <1-5> | <evidence> |
| 通讯 + 一作背景 | <1-5> | <team h-index> |
| 代码可复现 | <1-5> | <github / paper> |
| 数据集公开 | <1-5> | <公开/私有> |
| 数字可验证 | <1-5> | <图表 / CI> |
| 引用数 | <1-5> | <数字, 未发表=1> |
| 跟我方向匹配 | <1-5> | <weekly 关联> |
| **综合** | **<平均, 1 位>** | — |

> **用法**: ≤ 3 分 weekly 慎引, ≤ 2 不引

---

## §4 方法概述

- **关键 idea**: <1 句>
- **核心机制**: <2-3 段实现>
- **训练/推理 cost**: <改 base model / retrain / FLOPs>

---

## §6 我没读懂的点 (诚实, MUST 填)

> **不写 = 假完成**

- **round 1 待补**: <列 3-7 个>
- **claudecode 推测**: <[推测] 或 round 0>

---

## §7 真读 risk + 引用源

- **user 必须真读吗?**: 是 (key paper) / 否 (background)
- **引用源** (3+ 个, 写明访问日期):
  1. <URL 1> — YYYY-MM-DD
  2. <URL 2>
  3. <URL 3>

---

## 元信息

- 关联: <其他 note 文件>
- round history:
  - round 1 (YYYY-MM-DD HH:MM): <做了什么, file size>
```

## 关键不变量

| # | 不变量 | 违反后果 |
|---|---|---|
| 1 | 8 段必填 (§1 + §1.5 + §2-§4 + §6 + §7 + 元信息) | 缺段 = 假完成 |
| 2 | §2 5 列必填 + "设计意图" 列 must | 写不出 = 没读懂 |
| 3 | §3 7 维度评分, ≤3 慎引 | 不评 = 风险 |
| 4 | §6 round 1 待补必列 3-7 个 | 不写 = 假完成 |
| 5 | §7 引用源 3+ 个 + 日期 | 缺源 = 不可 verify |

## 🔗 相关

- `~/.agents/skills/loop-engineering/SKILL.md` §Stage 3 精读
- weiying20260624/03-research/01-reading-notes/01-sakana-ai-scientist-v1.md (实跑版参考)
- `process.md §A.1.5` URL verify 协议 (引用源必读一手)
