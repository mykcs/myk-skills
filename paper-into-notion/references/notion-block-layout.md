# Notion Block Layout Protocol — 元素位置 + 分隔线 + 层级规范

> **SSOT 引用**: paper-into-notion 写 Notion block 布局时, 走本表. 跟 `notion-content-verify.md` 协同 (本表管"怎么写", verify 管"写完怎么查")
> **起源**: weekly-report-phd v1.1 §X 元素位置协议 (line 131-183) — 周报项目实证 49 块, 提炼通用协议位
> **适用范围**: 任何 Notion 文档布局 (paper 摘要 / 周报 / 调研报告 / skill 输出), 跨项目稳定
> **不适用**: 表格数据库 (database property) — 走 `notion-schema-migration.md`

---

## §1 7 个必选元素 (位置固定, 顺序不可乱)

| 顺序 | 元素 | 位置 | 格式约束 |
|------|------|------|---------|
| 1 | **callout block** (frontmatter metadata) | **顶部** (在 divider 之前 / 第一个 h1 之上) | callout icon + 3-4 行内容, ⚠️ Notion API append 末尾, 必 user 手动拖 |
| 2 | **divider** (`---`) | callout 之后 | 分隔 frontmatter 与正文 |
| 3 | **heading_1** (TL;DR 或主标题) | divider 之后 | h1 必用真 `#` 触发 TOC block 识别, 不用 `**N.**` 粗体文本 |
| 4 | **正文内容** (paragraph + list + table) | h1 之下 | 视情况 |
| 5 | **divider** | 正文末尾 | 分隔内容与 TOC |
| 6 | **table_of_contents block** | divider 之后 (正文末尾, 总收尾之前) | Notion API 直插, `table_of_contents: {}` (空 `{}`, 不传 color/is_toggleable 否则 400) |
| 7 | **divider** + 末尾收尾段 | TOC 之后 | 1 段简短收尾 (1-3 行), 不加 |

---

## §2 分隔线 (divider) 用法矩阵

| 分隔位置 | 必加 | 原因 |
|---|---|---|
| callout 与正文之间 | ✅ 必加 | frontmatter 跟正文分离 |
| 正文与 TOC 之间 | ✅ 必加 | 内容 vs 目录分离 |
| TOC 与末尾收尾之间 | ✅ 必加 | 目录跟收尾分离 |
| 各大段之间 (h1 之间) | ❌ 不加 | heading_1 本身是分隔, 多加视觉割裂 |
| 段内子段之间 (h2 之间) | ❌ 不加 | h2 是分隔 |
| 文档末尾收尾之后 | ❌ 不加 | 收尾即结束 |

---

## §3 元素用法决策表

| 元素 | 何时用 | 何时不用 |
|---|---|---|
| 表格 | 多列数据对比 (≥ 3 列 × ≥ 3 行) | ≤ 3 行用列表 |
| 无序列表 `- [ ]` | 待办 / todo / 状态项 | 不是 todo 用有序或 paragraph |
| 有序列表 `1. 2. 3.` | 摘要 3 项 / paper 编号列表 / 阶段列表 | 编号 ≤ 3 用 paragraph |
| 数字 + 段标题 `1.` `2.` | 不用 markdown list, 用 paragraph + bold `**1.**` | ⚠️ 在 heading 不用 list 语法 |
| callout | 顶部 metadata / 警示 (❗) / 关键提示 | 不用做普通 paragraph |
| quote | (reserved) | 不用做 metadata |
| divider | 大段切换 (per §2) | 子段 / 段内不加 |

---

## §4 h1/h2/h3 层级规范

| Level | 何时用 | 命名样式 |
|---|---|---|
| **h1** `# 段标题` | 主结构段 (TL;DR / §1/§2/§3 ...) | 人话主题 (不写元结构词: "共识/冲突/关键判断") |
| **h2** `## 子主题` | 子段 / 子方向 / 子分类 | `## 1.1 / 1.2 / 1.3` (数字 + 主题) |
| **h3** `###` | (保留, 视需求) | 待下次需求 |

**关键约束**:
- h1 必须用真 `# N. 段标题`, 触发 Notion TOC block 自动识别
- `**N.**` 粗体文本**≠** heading_1, 二选一不能混 (TOC 识别不到粗体)
- 不写元结构 outline 词 (共识/冲突/关键判断/反向 anchor/5 分奠基) — 给真人看的不是 claudecode 给自己看的 metadata

---

## §5 page title + 文档标题命名

| 文档类型 | Notion page title 样式 | 备注 |
|---|---|---|
| 单文档 (paper 摘要 / 周报) | `类型_MMDD-MMDD` 或 `类型_主题` | 无空格, 用 `_`, 无 emoji 装饰, 无"索引/汇总"自描述 |
| 总 page (容器) | 简短主题 | 同上 |
| h1 标题内 | **不重复** page title | 不要"每周汇报 — XX" |

---

## §6 IF...THEN 规则 (写 Notion 布局必跑)

1. **IF** 文档需要目录 **THEN** TOC block 必基于真 h1 (用 `#` 不是 `**N.**`)
2. **IF** 文档顶部要 metadata **THEN** 用 callout (不是 paragraph / quote), icon + color 必传, 改段时整段 PATCH
3. **IF** 段落间需要分隔 **THEN** 走 §2 决策表, h1 之间不加 divider
4. **IF** 用 `**N.**` 想当编号 **THEN** 走 markdown list 自动编号 OR `**N.**` 粗体文本 (二选一不混)
5. **IF** Notion API 插 block 位置 ambiguity (顶部/末尾/某块前后) **THEN** 必先 ask 1 字母选项, Notion v1 API 无原生 prepend 必用 UI 拖动
6. **IF** h1 ≥ 3 段想加 TOC **THEN** 走 §1 顺序: 内容 → divider → TOC → divider → 末尾收尾

---

## §7 永久失效反模式 (5 条)

1. ❌ 用 `**N.**` 粗体文本当 h1 (触发不了 Notion TOC block 识别)
2. ❌ h1 之间多加 divider (视觉割裂, heading 本身是分隔)
3. ❌ callout 改段时只传新段 (rich_text 数组被覆盖, 其他段丢失)
4. ❌ Notion TOC block 传 color 或 is_toggleable 字段 (返回 400, 必传空 `{}`)
5. ❌ h1 标题用元结构词 (共识/冲突/关键判断/反向 anchor) — 给真人看的不是 claudecode metadata

---

## §8 联动

- `references/notion-content-verify.md` (写完怎么查, 5 类逐项 verify)
- `~/.agents/skills/paper-into-notion/SKILL.md` (主 SKILL)
- 起源: `~/.agents/skills/_archive/weekly-report-phd/SKILL.md` §X (line 131-183, v1.1 2026-07-14)

---

## §9 历史

- 2026-07-16 v1.0 立 — 从 weekly-report-phd v1.1 §X 抽离, 通用化 (跨项目 stable)
- 起源 case: weekly-report-phd v1.1 §X.1-§X.5, 49 块 W2 周报实证