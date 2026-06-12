---
name: paper-card
description: 紧凑 paper card v0.4.0 — 7 line/paper, h3 heading, 通讯/大老板 inline 标记, arXiv 嵌入 title, 一作/共一 行末标记
metadata:
  type: spec
  project_id: teacher-report
  version: 0.4.0
  status: draft (2026-06-10)
  supersedes: v0.3.9 完整 paper card (强制替代)
---

# Paper Card v0.4.0 紧凑格式 (2026-06-10 新版, 替代 v0.3.9)

> **来源**: User 在 2026-06-10 grill-with-docs session 中提出, 经 9 轮问答定型. 详见 `~/.claude/knowledge/cases/wiki/CASE-PAPER-CARD-V040-COMPACT-20260610.md` (待归档).
>
> **替代关系**: v0.4.0 是 v0.3.9 的**视觉/排版**压缩版, 不是 v0.3.9 的**信息密度**升级版. 两者数据要求一致 (4 维 taxonomy / 完整作者 / 通讯作者 byline / arXiv URL), 只是排版更紧凑.
>
> **适用场景**:
> - 论文清单 ≥ 10 篇 (e.g. v0.3.9 15 行 × 12 = 180 行 → v0.4.0 7 行 × 12 = 84 行, 节省 ~53% 篇幅)
> - Reader 想要 1-click 横向对比 (4 维 taxonomy 4 行对齐, 视觉上 scannable)
> - 飞书 outline 偏好 (12 h3 paper title 直接展开, 不嵌套 h4)
>
> **不适用场景**:
> - 论文 ≤ 3 篇 (e.g. 套磁信 1-2 篇深度引用) → 用 v0.3.9 完整版更清晰
> - 论文需要详细 abstract 摘要 → v0.4.0 不含 abstract 字段, 用 v0.3.9

## 1. 7-line paper card 模板 (v0.4.0 fixed-template)

```xml
<h3>{N}. {TITLE} <a href="https://arxiv.org/abs/{ARXIV_ID}">[arXiv {ARXIV_ID}]</a></h3>
<p>{AUTHOR_LIST_WITH_INLINE_MARKERS}</p>
<p>{VENUE} {YEAR} ({ROLE})</p>
<p>大领域：{D}</p>
<p>中方向：{M}</p>
<p>小任务：{T}</p>
<p>子技术：{S}</p>
```

**严格 7 行 (加 1 空行) per paper card**. 任何 8-th line (e.g. 单独 `一作:` 行 / 单独 `arXiv:` 行 / 单独 `paperscool:` 行) **禁止** 出现在 v0.4.0 格式.

## 2. inline 标记规则 (author 行)

author 列表 = 全部作者用 `, ` (英文逗号 + 空格) 分隔, 按 arXiv byline 顺序. 通讯 / 大老板 / 一作 用 inline 标记嵌入, **不** 单独成行.

### 2.1 学生识别

**放弃学生识别**. 一律 `English Name（中文名）` 格式, 不管作者是老师还是同学. 理由: 学生身份判断需查 12+ paper byline + 课题组主页, 投入产出比低; v0.3.9 全作者标 `（中文）` 在 dashboard 横向对比时已足够 disambiguation.

**例外**: 当作者**外籍** (无对应中文名) 时, 保留 `English Name` 不加中文括注. 跟 v0.3.9 一致.

### 2.2 通讯作者标记

规则: arXiv byline `†` / `‡` footnote 验证的真实通讯作者, 在 author 列表末尾加 `(通讯)` tag.

- 单一通讯 (e.g. KnowPilot 邓舒敏 sole 通讯): `..., **Shumin Deng（邓舒敏）**(大老板)(通讯)`
- 共同通讯 (e.g. KnowAgent 陈华钧+张宁豫): `..., **Huajun Chen（陈华钧）**(大老板)(通讯), **Ningyu Zhang（张宁豫）**(大老板)(通讯)`
- 共同通讯 (e.g. CaKE 陈华钧+Nanyun Peng, 末位是大老板): `..., **Nanyun Peng（彭南云）**(通讯), **Huajun Chen（陈华钧）**(大老板)(通讯)`

### 2.3 大老板标记

规则: 在 author 列表**末位 1-2 位**的 senior PI (e.g. 陈华钧/张宁豫/Bryan Hooi/Nanyun Peng) 是大老板. 用 bold `**...**` 渲染 + `(大老板)` tag.

- 单一末位: bold + `(大老板)` + `(通讯)` 全部
- 共同末位: 两个都 bold + `(大老板)`, 各自可能 (通讯) 或不

### 2.4 一作/共一 标记

规则: author 行末尾追加 `(一作: X)` 或 `(一作: X, Y) (共一)` (当 2 人共一).

- 单一一作: `..., **Huajun Chen（陈华钧）**(大老板)(通讯) (一作: Xiaohan Wang)`
- 共一: `..., **Huajun Chen（陈华钧）**(大老板)(通讯) (一作: Xiaohan Wang, Shengyu Mao)`
- 一作 = 通讯 (e.g. 周晓巍 TPAMI 案例): `..., **Name（中文）**(大老板)(通讯) (一作: Name)` (双重身份)

### 2.5 inline 标记冲突规则 (优先级)

当某作者同时是 通讯 + 大老板 + 一作 时, 三个 tag 全标. 当某作者只是 大老板 不是通讯时, 只标 `(大老板)`. 当某作者只是 通讯 不是大老板 (e.g. Nanyun Peng in CaKE, 末位是陈华钧不是 Peng), 只标 `(通讯)`, 不 bold.

## 3. venue + role 行格式

```
{venue} {year} ({role})
```

示例:
- `ACL 2024 (Main Conference)` — 一作通讯类
- `EMNLP 2024 Findings (Findings)` — 标注是 Findings
- `NeurIPS 2024 (Main Conference)` — 顶会主会
- `AAAI 2026 Demo (Demo)` — Demo track
- `arXiv preprint (Work in progress)` — 预印本, 未发表

**禁止**:
- `EMNLP 2024 Findings Findings` — Findings 重复, 无 parens
- `EMNLP (Findings) 2024` — year 位置错乱
- 单独 year 行 (year 必须嵌入 venue)

## 4. 4 维 taxonomy 顺序 (跟 v0.3.9 一致)

```xml
<p>大领域：{大领域}</p>
<p>中方向：{中方向}</p>
<p>小任务：{小任务}</p>
<p>子技术：{子技术}</p>
```

4 行顺序固定. 不允许压平到 1 行 (v0.3.9 反例) 或 4 列表格.

## 5. 与 v0.3.9 完整版的对比

| 维度 | v0.3.9 完整版 | v0.4.0 紧凑版 |
|------|--------------|--------------|
| 行数 per paper | 15 行 | 7 行 |
| 12 篇 paper 总额外行数 | 180 行 | 84 行 (省 53%) |
| 标题级别 | `<p>` 段落 | `<h3>` heading (Feishu outline 可见) |
| 通讯作者 | 单独 `<p>通讯作者：X</p>` 行 | author 行内 `(通讯)` tag |
| 大老板 | 单独 `<p>作者角色：X</p>` 行 | author 行内 `**(大老板)**` bold + tag |
| 一作/共一 | 单独 `<p>一作/共一：X</p>` 行 | author 行末 `(一作: X, Y)` |
| arXiv URL | 单独 `<p>arXiv：URL</p>` 行 | 嵌入 title `[arXiv ID]` |
| paperscool URL | 单独 `<p>paperscool：URL</p>` 行 | (无, 改为 arXiv 1-click 入口) |
| 12 项 LLM 自检 | 100% 必跑 | **同样 100% 必跑** (v0.4.0 同样禁止 placeholder / 中途截断 / 错配串名) |
| §G audit 通讯 | 必跑 | 必跑 (通讯 inline tag 数据源) |
| §I hallucination 检查 | 必跑 (4-index 0 results 标 ⚠️) | 必跑 |
| 数据完整性要求 | 100% 一致 | 100% 一致 |
| abstract 字段 | 无 | 无 |
| author affiliation | 无 | 无 |

**关键 v0.4.0 不损失项**:
- ✅ 4 维 taxonomy 4 行 (数据完整性)
- ✅ 全作者中文括注 (v0.3.9 强化项)
- ✅ 通讯作者真实 byline (§G audit)
- ✅ 大老板身份 (用 inline bold + tag, 不丢信息)
- ✅ 一作/共一 位置 (§H 信号)
- ✅ arXiv 1-click 入口 (嵌入 title)
- ✅ §G §H §I §J audit 全部必跑

**v0.4.0 主动丢弃项**:
- ❌ `paperscool` URL (改为 arXiv 1-click 入口)
- ❌ 单独 `URL 类型` 行 (合并到 title)
- ❌ 单独 `作者角色` 行 (合并到 author 行)
- ❌ abstract / affiliation 字段 (本来就没有)

## 6. 13 项 LLM 自检清单 (v0.4.0 适用, 2026-06-10 升级, 加 Check 13)

跟 v0.3.9 12 项完全一致 + 新增 **Check 13: Wiki Subject Author Verification** (防止 v0.1.0→v0.3.5 邓舒敏 case 复发). 任一 ❌ 必须修正后才能输出:

| # | 检查项 | 通过条件 | 失败处理 |
|---|--------|---------|----------|
| 1 | 标题 verbatim | 完全从 arXiv abs 页复制 | ❌ 中途截断 / 错字字符 |
| 2 | 标题无 et al. 缩写 | 完整标题 | ❌ 缩写 |
| 3 | 标题 h3 + arXiv ID inline | `<h3>N. Title [arXiv X]</a></h3>` | ❌ 用 `<p>` 而非 h3 |
| 4 | 4 行 taxonomy 顺序 | 大领域→中方向→小任务→子技术 | ❌ 顺序错乱 |
| 5 | 4 行 taxonomy 无 table | 4 个 `<p>` 块 | ❌ 4 列表格 |
| 6 | taxonomy + 作者 无占位符 | 4 字段 + 作者列表 均有具体值 | ❌ `[待补]` / `[未知]` |
| 7 | 作者完整 verbatim | 全部列出, 无 et al. | ❌ 省略 / 缩写 |
| 8 | 禁止 (末位/通讯) 缩写 | author 行无描述性缩写 | ❌ 缩写 |
| 9 | 全作者中文括注 | 100% 作者含 `Name（中文名）` | ❌ 部分漏标 |
| 10 | inline 标记 (通讯/大老板/一作) | 3 个 inline tag + bold 齐全 | ❌ 缺一 |
| 11 | 真实 1-click URL (arXiv inline) | `<a href="...">[arXiv X]</a>` 嵌入 title | ❌ URL 缺失 |
| 12 | arXiv ID 真实 (v0.3.xxxx / v3.xxxx 格式) | arXiv ID 是真 ID | ❌ placeholder / 错格式 |
| **13** | **Wiki Subject Author Verification (2026-06-10 新增)** | **wiki subject (e.g. 邓舒敏/Shumin Deng) 必须在 paper author list 里** | ❌ wiki subject NOT in author list → paper 误归, 必删除 |

### Check 13 强制审计流程 (任何 v0.4.0 paper card 必跑)

```python
import re
def check_wiki_subject_in_authors(paper_card_xml, wiki_subject_names):
    """Returns (passed, info). wiki_subject_names = ['Shumin Deng', '邓舒敏', ...]"""
    m = re.search(r'<p[^>]*?>([^<]*(?:,|，)[^<]*)</p>', paper_card_xml)
    if not m:
        return (False, 'no author line found')
    author_line = m.group(1)
    for name in wiki_subject_names:
        if name in author_line:
            return (True, f'✅ {name} found in authors')
    return (False, f'❌ wiki subject {wiki_subject_names} NOT in author line: {author_line[:100]}')

# 对每个 paper card 跑
for paper in paper_cards:
    check_wiki_subject_in_authors(paper, ['Shumin Deng', '邓舒敏'])
```

### Check 13 失败处理 (v0.4.0 必删)

| 失败场景 | 必做动作 |
|----------|---------|
| paper 在 doc 中, wiki subject NOT in author list | **删除该 paper card** (block_delete) |
| paper 在 doc 中, wiki subject NOT in author list 但被标"通讯" | **删除** (双倍错配) |
| paper 在 doc 中, wiki subject 名字拼写错 (e.g. "Shumin Deng" vs "Shu-Min Deng") | **修正拼写** (block_replace) |
| paper 在 doc 中, wiki subject 在 middle author 位置但被标"独立通讯" | **改标"合作"或删除** (per §J 协议) |

### Check 13 来源: 邓舒敏 v0.1.0→v0.3.5 case (2026-06-10)

v0.1.0 简单版占位 doc 在 §4 论文产出全景中, 把 2 篇 paper **误归**给 邓舒敏:
- **EasyEdit (2308.07269)**: arXiv byline 14 作者 (Peng Wang, Ningyu Zhang, Bozhong Tian, ...), **邓舒敏 NOT in author list**. 实际是导师组 (张宁豫/陈华钧) 主导 paper.
- **WISE (2405.14768)**: arXiv byline 9 作者 (Peng Wang, Zexi Li, Ningyu Zhang, ...), **邓舒敏 NOT in author list**. 同上.

LLM 默认把"陈华钧组/张宁豫组" = "邓舒敏组", 跳过逐篇 verify 实际 author list. 这就是 v0.1.0→v0.3.5 必须修的 hallucination attribution 案例.

v0.3.5 升级: 删除 EasyEdit + WISE 误归, 替换为 12 篇真实 arXiv byline 含 邓舒敏 论文 (e.g. SkillX/KnowPilot/StructMem 等 邓舒敏 是末位作者).

**v0.4.0 必跑 Check 13** 防止未来 session 重蹈覆辙. 任何 paper card 缺 wiki subject → 必删, 不允许"是导师组 paper, 算邓舒敏组的"等借口.

## 7. 完整样例 (邓舒敏 v0.3.5 12 papers 中 Editing Conceptual Knowledge)

```xml
<h3>11. Editing Conceptual Knowledge for Large Language Models <a href="https://arxiv.org/abs/2403.06259">[arXiv 2403.06259]</a></h3>
<p>Xiaohan Wang（王晓晗）, Shengyu Mao（毛圣雨）, Ningyu Zhang（张宁豫）, Shumin Deng（邓舒敏）, Yunzhi Yao（姚蕴之）, Yue Shen（沈悦）, Lei Liang（梁磊）, Jinjie Gu（顾津锦）, **Huajun Chen（陈华钧）**(大老板)(通讯) (一作: Xiaohan Wang, Shengyu Mao)</p>
<p>EMNLP 2024 Findings (Findings)</p>
<p>大领域：自然语言处理</p>
<p>中方向：知识编辑</p>
<p>小任务：概念级知识编辑</p>
<p>子技术：ConceptEdit 数据集; 概念级知识; 知识更新</p>
```

跟 v0.3.9 完整版 (15 行) 对比:
- 节省 8 行 (53%)
- 标题升级为 h3, Feishu outline 可展开
- 通讯/大老板/一作 inline, 不再 3 单独行
- arXiv URL 嵌入 title, 不再单独 2 行 (arXiv + URL 类型 + paperscool)

## 8. 迁移路径 (v0.3.9 → v0.4.0)

### 现有 v0.3.9 doc 升级

适用 block-level 升级 (v0.3.6 §C 协议):

```bash
# 对每个 paper card, block_replace 从 15 行换 7 行
lark-cli docs +update --api-version v2 --doc {DOC_ID} \
  --command block_replace --block-id {PAPER_CARD_BLOCK_ID} \
  --content @paper-card-v040.xml
```

### v0.4.0 LLM 输出 workflow

```
1. 抓 arXiv abs 页 → 复制完整 title + 完整作者列表 + arXiv ID + venue/year/role
2. §G audit → 验证通讯作者 byline
3. §H audit → 检测一作位置 (§H 触发 if 1st = wiki subject)
4. §J audit → 检测 middle author (§J 触发 if middle, 不默认填 wiki subject)
5. §I hallucination check → 4-index 0 results 标 ⚠️
6. 按 v0.4.0 7-line 模板填 7 个 block (h3 title + author + venue + 4 taxonomy)
7. 跑 12 项 LLM 自检清单 → 任一 ❌ 必须修正后重跑
8. 全 ✅ 后才能进 1v1 block 写入
```

## 9. 12 papers 真实样例 (邓舒敏 v0.3.5 wiki doc 12 篇全部)

| # | Paper | h3 heading | venue |
|---|-------|-----------|-------|
| 1 | SkillX | `1. SkillX: Automatically Constructing Skill Knowledge Bases for Agents [arXiv 2604.04804]` | arXiv preprint 2026 (Work in progress) |
| 2 | KnowPilot | `2. KnowPilot: Your Knowledge-Driven Copilot for Domain Tasks [arXiv 2604.19820]` | AAAI 2026 Demo (Demo) |
| 3 | StructMem | `3. StructMem: Structured Memory for Long-Horizon Behavior in LLMs [arXiv 2604.21748]` | ACL 2026 (Short Paper) |
| 4 | InnoGym | `4. InnoGym: Benchmarking the Innovation Potential of AI Agents [arXiv 2512.01822]` | ICLR 2026 (Main Conference) |
| 5 | OceanGym | `5. OceanGym: A Benchmark Environment for Underwater Embodied Agents [arXiv 2509.26536]` | arXiv preprint 2026 (Preprint) |
| 6 | VPI-Bench | `6. VPI-Bench: Visual Prompt Injection Attacks for Computer-Use Agents [arXiv 2506.02456]` | ICLR 2026 (Main Conference) |
| 7 | CaKE | `7. CaKE: Circuit-aware Editing Enables Generalizable Knowledge Learners [arXiv 2503.16356]` | EMNLP 2025 (Main Conference) |
| 8 | ReLearn | `8. ReLearn: Unlearning via Learning for Large Language Models [arXiv 2502.11190]` | ACL 2025 (Main Conference) |
| 9 | KnowAgent | `9. KnowAgent: Knowledge-Augmented Planning for LLM-Based Agents [arXiv 2403.03101]` | NAACL 2025 Findings (Findings) |
| 10 | FlipAttack | `10. FlipAttack: Jailbreak LLMs via Flipping [arXiv 2410.02832]` | ICML 2025 (Main Conference) |
| 11 | Editing Conceptual Knowledge | `11. Editing Conceptual Knowledge for Large Language Models [arXiv 2403.06259]` | EMNLP 2024 Findings (Findings) |
| 12 | WKM | `12. Agent Planning with World Knowledge Model [arXiv 2405.14205]` | NeurIPS 2024 (Main Conference) |

## 10. 跟 v0.3.9 共存策略

v0.3.9 完整版不删除, 跟 v0.4.0 并存:
- **v0.3.9**: 论文 ≤ 3 篇 (套磁信深度引用), 抽象摘要详细, 单独成行
- **v0.4.0**: 论文 ≥ 10 篇 (论文全景), 横向对比 scannable, inline 标记

LLM 自检: 同一 doc 中可以混用 v0.3.9 和 v0.4.0, 但**同一论文不能同时用两种格式** (避免 reader 困惑).

## 11. SKILL.md 更新点

teacher-report/SKILL.md 需加:
1. 新章节 "## Paper Card v0.4.0 (紧凑, 2026-06-10) — 硬要求" (在 v0.3.9 章节后)
2. 12 项 LLM 自检清单 → 扩展到 v0.3.9 + v0.4.0 通用
3. Output Schema (v0.3.9 strict) → 加 v0.4.0 strict 章节
4. 适用位置 章节 → 注明 v0.3.9 vs v0.4.0 选型
5. 迁移指南 → v0.3.9 → v0.4.0 block-level 升级

## 12. 设计决策来源

详见 `~/.claude/knowledge/cases/wiki/CASE-PAPER-CARD-V040-COMPACT-20260610.md` (待归档):
- 9 轮 grill-with-docs 问答
- 关键 trade-off: 视觉紧凑 vs 信息密度 (v0.4.0 选视觉)
- 关键 trade-off: 单独行 vs inline 标记 (v0.4.0 选 inline, 节省 8 行)
- 关键 trade-off: 学生识别 (v0.4.0 放弃, 减少数据成本)
- 关键 trade-off: 一作/共一 单独行 vs 行末 (v0.4.0 选行末)

## 13. 作者

claudecode teacher-report skill, 2026-06-10, grill-with-docs session.
