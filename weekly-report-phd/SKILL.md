---
name: weekly-report-phd
description: PhD 申请周报 (浙大魏颖 CompLife Lab) 写 + Notion 同步 SOP. 触发词: 周报 / 每周汇报 / 给老师看 / PhD 申请汇报 / weekly update / reading report / 浙大魏颖周报. 7 件 checklist (3 写前 + 3 写中 + 1 写后 4 字段自检). 引用 CASE-WEEKLY-HUMANIZE (humanize 7 条) + ADR-0043 (Notion ntn 渲染) + project-rules.md (真实记录 / 公开 / 暴露焦虑).
metadata:
  type: skill
  project_scope: weiying20260624
  skill_id: weekly-report-phd
  version: v1.0 (2026-07-08)
  起源: user 原话"把这个写成一个 skill, 有必要吗" + 7 件 checklist 散在 4 文件 (CASE-WEEKLY-HUMANIZE-20260627 + CASE-NOTION-NTN-MD-RENDER-FIX-20260708 + ADR-0043 + project-rules.md)
  关联 ADR: ADR-0044
---

# weekly-report-phd v1.0

> **项目专用** — 只适用 `weiying20260624` (PhD 申请周报) 项目, 不适用其他项目
> **触发**: user 说"周报/每周汇报/给老师看/PhD 申请汇报/weekly update/reading report/浙大魏颖周报"时必跑

---

## 何时用

| 触发场景 | 跑这个 skill |
|---|---|
| user 说"写周报" / "汇报" | ✅ |
| user 说"给老师看" / "魏老师" | ✅ |
| week N 收尾写 week N+1 周报 | ✅ |
| 给其他导师/公司写 status report | ❌ (用 `internal-comms`) |
| 给老师写 paper 调研报告 (单篇) | ❌ (用 `teacher-report`) |
| 写 paper slide (用 `content2html`) | ❌ |

---

## 7 件 checklist (per ADR-0044)

### A. 写之前 3 件 (必跑)

1. **选模板** — `05-drafts/templates/reading-report-v1.md` (week 1 主题) 或 `reading-report-week2-v1.md` (week 2+ 阶段化含阶段 1→2 切换)
2. **本地源落档** — `.html` 1:1 写到 `05-drafts/YYYY-MM-DD-reading-report.html` (不靠 claudecode 推的 .md, 推的常跟 HTML 有差异)
3. **Notion 路线预热** — `ntn pages get {page_id}` warm up (避免首次连接超时) + 确认 OAuth workspace=`zju_wy`

### B. 写内容 3 件 (per project-rules.md + CASE-WEEKLY-HUMANIZE 8 条)

4. **真实记录** (project-rules 规则 2) — 读 paper 时的批注/吐槽/读不懂/跟作者观点不同的判断**全部**写进 markdown, 允许 `❓ 没看懂` / `⚠️ 怀疑 claim` / `🔴 实验设计 flaw`, **不要洗一遍再写**
5. **公开 + 暴露焦虑** (project-rules 规则 1+3) — 已有科研成果/个人背景/批注/评价/判断**全部**写进文档, 允许 "我今天在 X 概念上卡了 4 小时" (比包装 "今天顺利读完 3 篇" 更可信, 魏颖老师看过太多"完美但假"的学生)
6. **humanize 13 条** (per CASE-WEEKLY-HUMANIZE-20260627 + 7/8 user 5 次反馈) — 写完必 grep + 改这 13 类 AI 味:
   - "摸清 / 探索 / 形成判断" (真人邮件不写)
   - "(不急, 老师有空回即可)" (套话, AI 味)
   - "我带 XX 经验进组" (面试说过, 老师已知, 重复)
   - **"导师: X / OpenReview"** (老师认识你, 不用列 — **frontmatter 永久不写导师信息**, per 7/8 user 反馈)
   - 长句 + 抽象词 (改成短句 + 具体数字)
   - "学术黑话 反复出现" (1 次够了, 第 2 次变扣分)
   - "我想跟老师探索一个可能的方向" (改成 "I'm interested in")
   - 周报项数 / 询问老师问数 跟 W1 模板对位 (3 写中密度协议, 7/8 feedback)
   - **元信息段 / 报告 ID / 配套路径 / 模板版本 / 自检 grep / AI 痕迹** (周报末尾, claudecode 自我标注, 老师不需要看 — **7/8 user 反馈第 2 次**)
   - **claudecode 内部命名 / 周编号 (week N) / 阶段编号 (C1/C2) / 子方向 tag / 模板版本 (v1/v2/v2.1) / 自评分数 (可信度 7 维度) / baseline / paper note 数量 / 子方向全景图** (正文**人话** vs claudecode 自己跟自己对话 — **7/8 user 反馈第 3 次 "完全不像人话"**)
   - **claudecode 元结构 outline**（"共识 / 冲突 / 关键判断" / "高 confidence" / "反向 anchor 必要" / "5 分奠基" / "80% 关键证据" / "可信度 7 维度" / "AI 痕迹自检" 等 case file 模板抽象概念 — 周报是给真人看的沟通不是 claudecode 给自己看的 metadata / 案例报告 — **7/8 user 反馈第 4 次**)
   - **claudecode planner 动词** ("凑" / "填" / "cover" / "过一遍" 等自顾自动作, 应改为 "写"/"汇报"/"告诉您" 真人沟通动词, per 7/8 user 第 5 次)
   - **report-style 编号用粗体文本不写 markdown list** (想用 `N.` 编号但不进入 Notion 重新编号序列, 用 `**N.**` 文本方式 — per 7/8 `§8 改 8. 编号`; h1 仍用真 `# N. 段标题` 触发 TOC block 识别)

### C. 写之后 1 件 (5 字段自检, per ADR-0043 + 7/8 增量)

7. **5 字段自检** — 必跑 5 件:
   - **path**: `.html` + `.md` + ntn page_id 3 个绝对路径
   - **ntn edit**: `ntn pages edit --content .md 源` exit code 0
   - **raw blocks 验真**: `ntn api v1/blocks/{page_id}/children?page_size=100` 验 `rich_text[].annotations.bold` ≥ 5
   - **TOC block 在**: 验证 `table_of_contents` block 存在 (ntn edit `--allow-deleting-content` 会删 TOC, 必 rebuild)
   - **user 硬刷新 confirm**: user Cmd+R / F5 硬刷新 Notion 后, bold 正常显示 (字面 `**` = 0) + TOC 渲染完整

---

## 完整 SOP (6 步 = 写 5 + 1 rebuild)

```bash
# 1. 选模板 + 写 .html 源
ls /Users/myk/Claude/Projects/weiying20260624/05-drafts/templates/  # 选 v1 or week2-v1
# 写 05-drafts/YYYY-MM-DD-reading-report.html (per project-rules 规则 2+3)

# 2. 写 .md 中间产物 (claudecode 用来 ntn edit, 必须 1:1 跟 HTML 源)
# 解析 HTML → 文字 + Markdown 语法 (** 加粗, - [ ] todo, | 表格 |)
# 不在 .md 加 claudecode 推测内容, 跟 HTML 1:1
# 摘要部分必先写"人话版", 不是 claudecode 内部命名

# 3. humanize 13 条 grep (per CASE-WEEKLY-HUMANIZE + 7/8 5 次反馈)
grep -E "摸清|探索|形成判断|不急.*即可|我带.*经验|导师.*OpenReview|阶段 [12]|week [12345]|v[12]\.[01]|可信度.*维度|共识|冲突|关键判断|高 confidence|反向 anchor|5 分奠基|锚定 70%|AI 痕迹自检|凑" /tmp/w_md.md
# 命中 → 改; 不命中 → pass

# 4. ntn edit (per ADR-0043) — ⚠️ 会删 TOC block
ntn pages get {page_id}  # warm up
ntn pages edit {page_id} --allow-deleting-content --content "$(cat /tmp/w_md.md)" -v
# 期望: exit 0 + 返 page_id

# 4.5 rebuild TOC block (因为 --allow-deleting-content 副作用 = 删 TOC)
# 找 "下一步" paragraph 当 anchor (TOC 插在它之后, divider 之前)
ANCHOR=$(ntn api v1/blocks/{page_id}/children?page_size=15 | python3 -c "import json,sys; d=json.load(sys.stdin); print(next(r['id'] for r in d['results'] if r.get('type')=='paragraph' and '下一步' in ''.join(c.get('plain_text','') for c in r.get('paragraph',{}).get('rich_text',[])) ))")
ntn api v1/blocks/{page_id}/children -X PATCH -d "{\"children\":[{\"object\":\"block\",\"type\":\"table_of_contents\",\"table_of_contents\":{}}],\"after\":\"$ANCHOR\"}" \
  -H "Authorization: Bearer $(echo $TOKEN)" -H "Notion-Version: 2022-06-28" -H "Content-Type: application/json"
# 期望: 200 + table_of_contents block id (空 `{}` 即可, 不传 color/is_toggleable 否则 400)

# 5. 5 字段自检 (含 TOC)
ntn api v1/blocks/{page_id}/children?page_size=100 | python3 -c "
import json, sys
d = json.load(sys.stdin)
# field 3: bold chunks
bold = sum(1 for r in d['results'] for c in r.get(r['type'],{}).get('rich_text',[]) if c.get('annotations',{}).get('bold'))
# field 4: TOC block 在
toc = sum(1 for r in d['results'] if r.get('type')=='table_of_contents')
h1 = sum(1 for r in d['results'] if r.get('type')=='heading_1')
print(f'bold={bold} (≥ 5) | toc={toc} (= 1) | h1={h1} (≥ 5)')
assert bold >= 5, f'bold 不足: {bold}'
assert toc == 1, f'TOC 缺: {toc}'
assert h1 >= 5, f'h1 不足 (TOC 识别不到): {h1}'
"
# 让 user Cmd+R 硬刷新 confirm
```

---

## 5 维 Lifecycle (per 7/8 user 多次反馈)

| Phase | User 反馈 (时序) | Humanize 升级 | Permanent lesson |
|-------|------|------|------|
| **Phase 1 启动** | (1) 写新 HTML (1) (2) Notion 总 page + 子 page (3) 集成 token (4) | 必跑 §A 7 件 checklist | Notion 结构: 总 page = 容器 + 子 page = 内容 |
| **Phase 2 探索** | (5) "内容不对" → "装饰" → (7) "完全不像人话" | humanize 第 4/10/11 条 (frontmatter / 内部命名 / 元结构 outline) | user feedback 必先 ask 区分 (文字/装饰/格式), 不反复 grep 猜 |
| **Phase 3 内容改** | (8-17) 9 次反馈: 删导师 / 删元信息段 / 删 (week 2+3) / 删 §5 / 改 §8 / 删标题 / 改标题为人话 / 加 TOC / §7 凑改 | humanize 第 1-11 条 | 1 session 多次反馈 → humanize 11 条, 每条加 grep 自检 |
| **Phase 4 跨周对位** | (18-20) W2 像 W1 一样 / 真 h1 / 参考 W1 风格 | h1 必用真 `# N. 段标题` (触发 TOC 识别), 不混 `**N.**` 文本 | Notion TOC block 必须基于真 heading, 不基于文本粗体 |
| **Phase 5 标题微调** | (21) 去掉 § / (22) frontmatter 改内容 | humanize 第 13 条 (report-style 编号用粗体文本) | `**N.**` 粗体文本 ≠ heading_1, 二选一不能混 |
| **Phase 6 Notion API** | (23) "我目录呢" → TOC rebuild (25) callout block (26) ntn CLI (27) page title 规范化 | 4 字段自检 → 5 字段 (加 TOC 在不在) | ntn edit `--allow-deleting-content` 副作用 = 删 TOC, 必 4.5 step rebuild |
| **Phase 7 工艺化** | (28-32) 7 件 checklist / skill / case / ADR | skill + case + ADR + mem0 多件 SSOT | 1 session 多次反馈 → 沉淀 humanize N+1 条 + case file + ADR + skill |

## §X 元素位置协议 (per 7/8 user 反馈 — 固化版)

> **目标**: 周报元素位置 + 分隔线用法 100% 可复用, 7/20 week 4 必照这个写

### X.1 7 个必选元素 (位置固定)

| 顺序 | 元素 | 位置 | 格式 |
|------|------|------|------|
| **1** | **callout block** (frontmatter metadata) | **W2 最顶部** (在 divider 之前 / TL;DR heading 之上) — **⚠️ Notion API append 末尾, 必 user 手动拖** | callout icon=📋 + 3 行内容 (汇报人 + 日期 + 周期), 不写导师/经验/套话 |
| **2** | **divider** (`---`) | callout 之后 | 分隔 frontmatter 与正文 |
| **3** | **TL;DR heading_1** | divider 之后 (实际 W2 第一个 block) | h1 = `# TL;DR` (不要"摘要") |
| **4** | **TL;DR 摘要内容** (3 numbered_list_item + 下一步 paragraph) | TL;DR heading 之下 | 3 项编号 (week 2/3/核心判断), 每项 ≤ 4 行, 最后 1 段下一步 (1v1 用 §7/§8 同样 1 句格式) |
| **5** | **divider** | TL;DR 内容之后 | 分隔摘要与 TOC |
| **6** | **table_of_contents block** | divider 之后 (TL;DR 与 §1 之间) | Notion API 直插, `table_of_contents: {}` (空 {} 不传 color/is_toggleable) |
| **7** | **divider** + §1 heading_1 + 内容... | TOC 之后 | 8 个 h1 (`# 1.` → `# 8.` 数字无 §), 跟 W1 风格对位 |

### X.2 分隔线用法

| 分隔位置 | 必加 / 不加 | 原因 |
|---|---|---|
| callout 与 TL;DR 之间 | **必加 divider** | frontmatter 跟正文分离 |
| TL;DR 与 TOC 之间 | **必加 divider** | 摘要 vs 全报告目录分离 |
| TOC 与 §1 之间 | **必加 divider** | 目录跟正文分离 |
| 各大段之间 (§1/§2/§3/...) | **不加 divider** | heading_1 本身是分隔, 多加视觉割裂 |
| 段内子段之间 | **不加** | h2 是分隔 |
| 末尾 | **不加** | toc 之后 §8 结束即收尾 |

### X.3 表格 / 列表 / 调用 block 用法

| 元素 | 何时用 | 何时不用 |
|---|---|---|
| 表格 | 多列数据对比 (paper 子方向 / cluster) | ≤ 3 行用列表 |
| 无序列表 `- [ ]` | 待办 / todo | 不是 todo 用有序或 paragraph |
| 有序列表 `1. 2. 3.` | 摘要 3 项 / paper 编号列表 | 编号 ≤ 3 用 paragraph |
| 数字 + 段标题 `1.` `2.` | 不用 markdown list, 用 paragraph + bold `**1.**` | ⚠️ 在 heading 不用 list 语法 |
| callout | 顶部 metadata / 警示 (❗) | 不用做普通 paragraph |
| quote | (reserved) | 不用做 metadata |

### X.4 h1/h2/h3 层级

| Level | 何时用 | 命名样式 |
|---|---|---|
| **h1** `# N. 段标题` | 6 段 (TL;DR + §1/§2/§3/§4 + §6/§7/§8) — 不要 § 符号 | 人话主题 (不写 "共识 / 冲突 / 关键判断" 元结构) |
| **h2** `## N.M 子主题` | 子段 (paper 子方向 / 时间轴 / 核心引用 等) | paper 类子段 N.M = `1.1 / 1.2 / 1.3`; 表格 section `2.1 / 2.2 / 2.3` |
| **h3** | (保留, week 4 暂未用) | 待下次需求 |

### X.5 title (page title + Notion title) 命名

- **Notion page title**: `周报_MMDD-MMDD` (无空格, 用 `_`, per 7/8 user)
- **Notion sub-page title**: 同 `周报_MMDD-MMDD`
- **总 page title**: 同 `周报_MMDD-MMDD` (无 emoji 装饰, 无"周报总索引" 自描述)
- **h1 标题内**: 不要重复 page title (不要"每周汇报 — XX")

## 6 IF...THEN 规则 (per 7/8 user feedback)

1. **IF** user 说"周报/每周汇报/给老师看" **THEN** 必跑 weekly-report-phd skill, 7 件 checklist + humanize 13 条 grep
2. **IF** user 反馈"内容不对" **THEN** 第 1 轮必 ask 区分 (文字 vs 装饰 vs 格式 vs 排版), 不反复猜根因 3 轮
3. **IF** ntn edit 后 user 反馈字面 `**` 或"我目录呢" **THEN** 必先验 raw blocks (bold 没设 / TOC 在不在), 不改后端代码
4. **IF** 周报有 humanize 13 条关键词 (共识/冲突/反向 anchor/5 分奠基/v2/v2.1 paper note/凑 week 等) **THEN** 必 grep 自检 + 改
5. **IF** Notion API 插 block position ambiguity (顶部/末尾/某块前后) **THEN** 必先 ask 1 字母选项, Notion API 无原生 prepend 必用 UI 拖动
6. **IF** 写周报 `**N.**` 想当编号用 **THEN** 走 markdown list 自动编号 OR `**N.**` 粗体文本 (二选一, 不混), h1 必须用真 `# N. 段标题` 触发 TOC block

## 6 永久失效反模式

1. ❌ 周报 frontmatter 写导师信息 / 我带经验 / 套话 (humanize 第 4/8/9 条)
2. ❌ 周报末尾元信息段 / 报告 ID / 配套路径 (humanize 第 9 条)
3. ❌ 周报正文写 claudecode 内部命名 (v2.1 template / week N / 阶段 C1/C2 / 子方向全景图, humanize 第 10 条)
4. ❌ 周报写 claudecode 元结构 outline (共识/冲突/关键判断/高 confidence/反向 anchor/5 分奠基, humanize 第 11 条)
5. ❌ 周报用 claudecode planner 动词 (凑/填/cover/过一遍, humanize 第 12 条)
6. ❌ 周报标题用 `**N.**` 粗体文本当 h1 (触发不了 TOC block 识别, humanize 第 13 条)

## 7. 完整 Layout 模板 (W2 实证, 1:1 复用)

**详见** `00-meta/weekly-report-design-v1.md` (跟 W2 49 块 1:1, 含 frontmatter / TL;DR / 7 段 / 分割线 / 表格 / 列表 / callout / TOC 全位置). 写新周报时必先读 design, 1:1 复制结构.

**核心 layout 顺序** (49 块 W2 实测, 简版):
1. **callout** (frontmatter 3 行)  → ⚠️ user 手动拖顶部
2. divider
3. **TL;DR** (heading_1) + paragraph (主线) + 3 个 numbered_list_item + paragraph (下一步)
4. divider + **table_of_contents** + divider
5. **# 1. 第一阶段** (heading_1) + 1.1/1.2/1.3 (h2 + table)
6. divider + **# 2. 第二阶段** + 2.1/2.2/2.3 (h2 + table/paragraph)
7. divider + **# 3. 跟您方法论对位** + 4 个 h2 (1 段 method 描述 + 4 table)
8. divider + **# 4. 阶段 2 子方向推荐** + 1 段 + 1 table
9. divider + **# 6. 本周成果总结** + 1 段 + 1 table (7 维度)
10. divider + **# 7. 下周计划** + 4 个 to_do
11. divider + **# 8. 询问老师** + 1 段 (1 项 `**8.**` 短问)

**关键规则**:
- 7 段 (TL;DR + 1/2/3/4/6/7/8) 必有, **跳过 §5** (humanize 第 11 条永久失效)
- divider 必 8-9 个 (frontmatter 后 / 摘要后 / TOC 前后 / §1/2/3/4/6/7 后)
- 标题层级 ≤ 2 (不用 h3, 周报不嵌套太深)
- 表格 8 个 (固定 8 位置, 跟 W1 模板对位)
- callout 必 1 个 (frontmatter), 必 user 手动拖 (Notion v1 API 不支持 prepend)

---

## 8. 周报模板 (kimi v4 1:1 复刻, 给魏老师看)

**用法**: 复制下面 markdown 块 → 粘贴到 Notion 目标 page → Notion 自动渲染 (block 类型: heading_1/2/3 + callout + table + bullets).

> **更新时间**: 2026-07-08 (kimi v4 完整版, 跟 W2_0629-0713_真 Notion page 1:1 对位)
> **关键 frontmatter 4 件** (callout): 汇报人 / 日期 / 周期 / 目的 — 老师已知事项不写 (e.g. 申请浙大普博 / 学校 / 年级, 老师面试已知, 不重复)
> **标点规则**: 中文全角 "。" (非半角 "."), 数字保留半角
> **人话语气**: 学生向导师主动对齐方向 + 汇报进展 + 寻求指导, 不写自降姿态 (转方向 / 跨领域 / 展示能力 / 我得证明)

```markdown
[汇报人 callout 蓝色背景]
📋 汇报人: 王锐
日期: 2026.7.13
周期: 2026.6.29 — 2026.7.13
目的: 给魏老师汇报组内方向理解 + 2-3 个月计划 + 论文自动收集系统, 请老师指导方向。

以上理解如有偏差, 还请老师指正。

[大标题 h1]
# 周报_0629-0713_真 (王锐 → 魏颖老师)

[目录 Notion 自动生成]
[Notion API: PATCH /blocks/{page_id}/children with table_of_contents block, anchor = "下一步" paragraph 或 h1 之后]

# TL;DR
[3 段 numbered list, 按 user 原话风格]

# 一、对组内方向与考核要求的理解
## 关于研究方向
[paragraph + 3 bullet, 最后: 以上理解如有偏差, 还请老师指正。]

## 关于考核周期与评估标准
[paragraph + 3 numbered bullet, 顺序: 做东西速度/commitment/契合度]

## 我的初步思考
[paragraph 预期产出 + paragraph 3 种安排 + 请老师判断哪种]

# 二、工作计划 (week N — week N+1+1)
[table 反向设计 4 维度 + 4 阶段 + 风险备案 table]

# 三、文献追踪系统汇报
[project 定位 + ASCII 架构 + table 数据源 + 4 循环 + table 迭代路线]

# 本周行动
[3-5 个 bullet]

# 📩 附: 跟进消息模板 (微信/邮件)
[code block 含消息正文]
```

**Notion API 写这块的 5 步**:
1. `ntn pages edit {page_id} --allow-deleting-content --content <md>` (用真 markdown 源, 不是 blocks JSON)
2. 删原 callout: PATCH /blocks/{callout_id} (rebuild with 4 件 frontmatter + 全角点)
3. 删原 4 个 code: PATCH DELETE (避免视觉灰色块)
4. 插新 4 段 prepend: chain PATCH 拿新 id, after=上一段新 id (h1 报告 → callout → h1 TL;DR → TOC)
5. PATCH 13 处 `**word**` 改 rich_text annotations bold (Notion bold 用 annotation 不是 markdown 语法)

**关键避坑**:
- Notion v1 API **不支持 prepend** (PATCH after= 是 append after), 必 链式 PATCH after=新 block id
- **1 session 改同文档 ≤ 3 次**, 超过必 reset 重写 (否则残留 h1/h2 累积混乱)
- **table 替换 code** 才视觉协调 (code 嵌入像没渲染的灰色块)
- **真 h1/h2/h3 必 # ## ###** 触发 TOC block 自动识别, 不用 `**N.**` 粗体文本当 heading
- **1 段 PATCH ≤ 60 blocks** (避免 2 min 超时), 大文档拆 2-3 段



## 9. 改前 1:1 verify 协议 (per 7/8 user 第 30+34 次反馈, 解决 meta 问题)

**问题**: 1 session 同文档改 30+ 次, claudecode 每次 verify 只查数量, 漏查内容 (数字格式 / 标点 / 标题用字 / 内容字面). 1 句 user 反馈可能含多类 bug (e.g. "0。1 错" 实际含 vv0.1 + 1v0.1 + 0。1 + 12 处 : 半角 = 4 类).

**5 类逐项 + 字符级 verify 协议 (必跑, 不可走流程不真 verify)**:

### 9.1 verify 5 类 (5 步, 字符级)

| # | 类 | grep 模式 | 期望 | 例 (错误) |
|---|---|---|---|---|
| 1 | 数字格式 | `0[。.][0-9]` (中文数字+全角点) | 0 命中 | "0。1" 应 "0.1" |
| 2 | 数字格式 | `\dv0[。.][0-9]` (smart_fix_period 双 v) | 0 命中 | "vv0.1" 应 "v0.1" |
| 3 | 半角标点 | `(?<!\d)[,;:'"](?!\d)` (半角在中文环境) | 0 命中 | ": " 中文环境应 "：" |
| 4 | 标题用字 | `(一|二|三|四|五|六|七|八|九|十)[、.]` (h1/h2 中文数字) | 0 命中 | "一、对" 应 "1. " |
| 5 | 内容字面 | 1:1 跟 user 最新原话 diff | 0 字符差 | e.g. "v0.1" 跟 "0.1" 混 |

### 9.2 5 步 verify 流程 (必跑)

```bash
# Step 1: 拿当前 Notion 全文
ntn api v1/blocks/{page_id}/children?page_size=100 > /tmp/w2_now.json
cat /tmp/w2_now.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(''.join(c.get('plain_text','') for c in r.get(r.get('type'),{}).get('rich_text',[])) for r in d['results'] if r.get('type') in ('paragraph','bulleted_list_item','numbered_list_item','heading_1','heading_2','heading_3','callout')))" > /tmp/w2_now.txt

# Step 2: 5 类 grep
echo "=== verify 5 类 ==="
echo "[1] 0[。.][0-9]:"; grep -oE '0[。.][0-9]' /tmp/w2_now.txt | head -5
echo "[2] vv0[。.][0-9]:"; grep -oE 'vv0[。.][0-9]' /tmp/w2_now.txt | head -5
echo "[3] 半角标点:"; grep -oE '(?<<!\d)[,;:"'](?!\d)' /tmp/w2_now.txt | head -5
echo "[4] 标题中文数字:"; grep -oE '^#+\s*(一|二|三|四|五|六|七|八|九|十)[、.]' /tmp/w2_now.txt | head -5

# Step 3: 1:1 字符级跟原话对比 (user 最新原话 → /tmp/w2_expected.txt)
diff /tmp/w2_now.txt /tmp/w2_expected.txt

# Step 4: 列出 4 类荒谬 (智能 + 全角 + 数字 + 模板)
python3 -c "
text = open('/tmp/w2_now.txt').read()
issues = []
for m in __import__('re').finditer('0[。.][0-9]', text):
    issues.append(('0[。.]X', m.group(), m.start()))
for m in __import__('re').finditer('vv0[。.][0-9]', text):
    issues.append(('vv0[。.]X', m.group(), m.start()))
if issues:
    print('荒谬 found:')
    for cat, txt, pos in issues:
        print(f'  [{cat}] {txt} at {pos}')
else:
    print('0 荒谬 found')
"
# Step 5: 改完必 verify 0 issues 才 declare done
```

### 9.3 5 永久失效反模式 (claudecode 必避)

- ❌ verify 只查数量 (5 h1 / 5 h2 / 3 callout) 不查内容 (5 h1 是 "1. 对组内方向" 还是 "TL;DR" 错位?)
- ❌ 改 1 段 漏跑 5 类逐项 (regex grep 5 类) 
- ❌ 1 句话 user 反馈当 1 个 bug 处理 (可能含多类)
- ❌ 1 session 改 > 3 次 (累积残留)
- ❌ 改完不 1:1 字符级对比 user 最新原话

### 9.4 1 句话 user 反馈 = 1:1 diff 多类 bug (规则)

当 user 说"X 错" / "X 荒谬" 时, 必**1:1 grep 5 类** (不是只改 1 处). 例:
- user 反馈 "0。1 错" → 实际含 4 类: 0。1 + vv0.1 + 0。10/24/25/15/16/30 + 1v0.1-1v0.20
- 1 个 grep "0[。.][0-9]" → 4 类全部暴露

### 9.5 例子 (7/8 user 第 34 次反馈 "0。1 错" → 1:1 diff → 4 类全找到)

```bash
# 输入
echo "0。1 已跑通, v0。1 推进中" > /tmp/w2_now.txt
# verify
grep -oE '0[。.][0-9]' /tmp/w2_now.txt
# → ["0。1", "0。1"]
# 实际含 0。1 (全角点 + 阿拉伯数字) → 改 "0。1" → "0.1" (保留 0 数字位置)
# 但 "v0。1" 同样问题 → 改 "v0。1" → "v0.1" (保留 v 字母, 不硬塞 v0.1 → 变 vv0.1)
# 1 句话 → 2 处改
```

## 联动 (引用既有沉淀)## 联动 (引用既有沉淀)

- `00-meta/project-rules.md` 规则 1+2+3 (公开 / 真实 / 暴露焦虑)
- `00-meta/weekly-report-design-v1.md` (W2 49 块 1:1 layout 模板, 写新周报时必先读)
- `05-drafts/templates/reading-report-v1.md` (week 1 模板)
- `05-drafts/templates/reading-report-week2-v1.md` (week 2+ 阶段化模板)
- `~/.claude/knowledge/cases/wiki/CASE-WEEKLY-HUMANIZE-20260627.md` (humanize 7 条根因 + 修复)
- `~/.claude/knowledge/cases/wiki/CASE-NOTION-NTN-MD-RENDER-FIX-20260708.md` (Notion 渲染踩坑 5 维 evidence)
- `~/.claude/docs/adr/0043-notion-ntn-md-render-protocol.md` (Notion ntn CLI markdown 协议位)
- `~/.claude/docs/adr/0044-weekly-report-phd-skill-scope.md` (本 skill scope 决策)
- `~/.claude/docs/adr/0045-weekly-report-humanize-8-rules.md` (8→9→10→11→12→13 条升级沿革)
- `~/.claude/memory/MEMORY.md` §Cases Active (2026-07-08 Notion ntn + weekly-report-phd skill 索引)
- mem0 add_memory × 5+ (per post-task-recommend §3 + memory-strategy v2 本体优先)

---

## 反模式 (永久失效, 5 条)

1. ❌ user 说"内容不对"立刻猜"文字错" → 必先 ask 区分 (文字 vs 装饰 vs 排版), 1 问 1 个字母选项
2. ❌ ntn edit 后立即让 user 看渲染 → Notion 客户端有 cache, 不硬刷新看不到
3. ❌ claudecode 推的 .md 替代本地 .html 源 → 推的常跟 HTML 有差异, user 真读时发现文字不对位
4. ❌ 周报 (给老师看) 跟 06-journal (真实焦虑) 原文照抄混用 → 周报可引用 journal, 但**不**原文抄, 保持两个文件
5. ❌ 写周报走集成 token + blocks JSON 路线 → 双重转义 `**` 变 `\*\*`, Notion 渲染失败. **永远走** ntn CLI + .md 源

---

## 何时**不**用这个 skill

- 给其他导师/公司写 status report → 用 `internal-comms`
- 给老师写单篇 paper 调研 → 用 `teacher-report`
- 写 paper slide (HTML 翻页) → 用 `content2html`
- 写周报 (项目) 但**不**给浙大魏颖 → 临时改写, 或在 CLAUDE.md 加项目级 anchor pointer

---

## 历史 record

- 2026-07-08 v1.0: 立 (user 原话"把这个写成一个 skill, 有必要吗" + 7 件 checklist 散在 4 文件 → 项目级 skill 收敛)
