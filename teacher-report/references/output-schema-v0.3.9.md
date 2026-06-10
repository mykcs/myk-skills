# teacher-report Output Schema v0.3.9 (strict, v0.4.0+ 沉到 reference)

> **来源**: 从 SKILL.md v0.3.9 (2026-06-10) 拆分（v0.4.0 progressive disclosure refactor, 2026-06-10）。
> **目的**: 严格输出 schema 定义 — LLM 写每篇 paper card 必跑 12 项自检, 全通过才输出。
> **加载时机**: 论文输出前最后一步自检 / 套磁信引用论文时 / 审计 docx 时对照。
> **v0.4.0 增强**: 13 项自检 (新增 Check 13 Wiki Subject Author Verification), 详见 references/paper-card-v0.4.0.md §6。

---

## Output Schema (v0.3.9 strict, 2026-06-10)

> **背景**:v0.3.3 之前 skill 输出混乱(混 4 列表 + 4 行 + 缩写 + 占位符)。v0.3.9 在 v0.3.3 基础上**强制全作者中文括注**。本节定义**严格的输出 schema**,LLM 写每篇 paper card 严格按 schema 走,自检 12 项通过才允许输出。

### 强制 Output Schema — v0.3.9 paper card block 结构

每篇论文 paper card **必须**由以下 11 个 block 顺序构成(顺序固定,不可调换):

```
1. <p>                          ← 标题 (verbatim,不可改字/改序/省字)
2. <p>大领域：{X}</p>             ← 4 行 taxonomy(每行 1 <p> 块,不是 table)
3. <p>中方向：{X}</p>
4. <p>小任务：{X}</p>
5. <p>子技术：{X}</p>
6. <p>作者：</p>                 ← 作者段头(空 <p>,下个 block 是作者列表)
7. <p>{完整作者列表,所有作者带中文括注}</p>           ← verbatim 完整作者,无 et al.,无缩写,所有作者 `Name（中文名）`, 外籍作者保留英文
8. <p>标注：</p>                 ← 标注段头(空 <p>,下个 block 是标注)
9. <p>通讯作者：{X（中文名）, Y（中文名）}</p>           ← 独立标注行(可选,无则整段省略), 通讯作者也带中文括注
10. <p>发表：{venue year (角色)}</p>  ← 发表信息
11. <p>arXiv：<a href="https://arxiv.org/abs/{id}">https://arxiv.org/abs/{id}</a></p>  ← **优先 arXiv URL**;若论文无 arXiv 预印本,改用原会议/期刊网址 (例: SIGMOD `https://dl.acm.org/doi/10.1145/{doi}`、 ASPLOS `https://dl.acm.org/doi/10.1145/{doi}`、 CVPR `https://openaccess.thecvf.com/content/CVPR{YEAR}/html/{paper}.html`、 NeurIPS `https://proceedings.neurips.cc/paper/{YEAR}/hash/{hash}-Abstract.html`、 期刊 `https://ieeexplore.ieee.org/document/{id}`)。禁止 `[待验证]` 占位符 — 必须有 1-click 入口
12. <p>URL 类型：arXiv 预印本</p>  ← 或 `<p>URL 类型：会议正式版 (SIGMOD/ASPLOS/CVPR/...)</p>` 标注 URL 来源类型,让用户一眼区分
```

### 12 项 LLM 自检清单(写完 paper card 必跑,任一 ❌ 必须修正后才能输出)

| # | 检查项 | 通过条件 | 常见错误 |
|---|--------|---------|---------|
| 1 | 标题 verbatim | 完全从 arXiv abs 页复制,无改字/改序/省字/中途截断/错字字符 | ❌ "OS Agents: Survey" (缺 "A Survey on MLLM-based Agents for General Computing Devices Use") / ❌ "...A Unified Model for 2D/3D/V" (中途截断 + 幻觉字符) |
| 2 | 标题无 et al. 缩写 | 完整标题,无 "et al." 替代 | ❌ "Xinyu: ... (Yiquan Wu et al., 16 authors)" |
| 3 | 4 行 taxonomy 顺序 | 顺序固定:大领域→中方向→小任务→子技术,每行独立 `<p>` 块 | ❌ 单行 "大领域:CV\|中方向:Agent\|小任务:GUI" 压平 |
| 4 | 4 行 taxonomy 无 table | **禁止** 4 列表格 `<table>`,**必须** 4 个 `<p>` 块 | ❌ `<table>大领域 中方向 小任务 子技术</table>` |
| 5 | taxonomy + 作者列表 无占位符 | 4 字段 + 作者列表 均有具体值,无 "未知" / "N/A" / "待补" / "[待 L4/L5/L6 重抓]" / "[待验证]" / "[未知]" placeholder | ❌ `<p>大领域：待补</p>` / ❌ `<p>作者：[待 L4/L5/L6 重抓]</p>` |
| 6 | 作者完整 verbatim | 全部列出,无 "... N 名作者" 省略,无 et al.,**无 [待 L4/L5/L6 重抓] / [待补] / [未知] / [待验证] placeholder** | ❌ "Xueyu Hu, Tao Xiong, ... 27 名作者, Fei Wu" / ❌ `<p>作者：[待 L4/L5/L6 重抓]</p>` / ❌ `<p>作者：[待补]</p>` |
| 7 | 禁止 (末位/通讯) 缩写 | 作者行无 "(末位/通讯)" / "(通讯 PI 模式)" 描述 | ❌ "作者：..., (末位/通讯), Fei Wu" |
| 8 | 禁止 (通讯 PI 模式) 描述 | 作者行无 "通讯 PI 模式" 等描述性短语 | ❌ "作者：... (通讯 PI 模式)" |
| 9 | **全作者中文括注(v0.3.9 强化)** | 100% 论文的作者列表中,**所有**作者含 `Name（中文名）` 格式,外籍作者保留英文(不可填 N/A) | ❌ "Nan Chen, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He" (部分漏标) / ❌ 仅 Fei Wu 单独标 |
| 10 | 标注行单独成行 + **跨 paper 串名检查** + **通讯作者中文括注** | 通讯作者/一作/学生 独立 `<p>标注：</p>` 段,不混作者列表;**通讯作者名字必须 verbatim 出现在作者列表中**(防跨 paper 串名/凑数);**通讯作者字段本身也带 `（中文名）`** | ❌ "作者：..., (通讯), ..., 一作 Xueyu" / ❌ 通讯作者="Zhaozhou Zhao" 但作者列表无此名(错配别 paper) / ❌ `<p>通讯作者：Kun Kuang</p>` 漏中文括注 |
| 11 | 真实 1-click URL (arXiv 优先 / 会议期刊兜底) | 100% 论文有 1-click 入口 URL;有 arXiv 用 arxiv.org,无 arXiv 用 dl.acm.org/openaccess.thecvf.com/proceedings.neurips.cc/ieeexplore.ieee.org,**禁止** `[待验证]` 占位符 | ❌ `<p>arXiv：待 arXiv 验证</p>` (应填会议 doi) / ❌ 缺 URL |
| 12 | paperscool 真实 URL | `<a href="https://papers.cool/arxiv/{id}">...</a>` 完整 URL,非占位 | ❌ `<p>paperscool：待 arXiv 验证</p>` |

> 12 项全 ✅ 才能输出 paper card;任一 ❌ 必须修正后重跑自检
> 触发 §G audit rule 的条件: 同一 wiki doc 中, 11+ paper cards 标 通讯作者 = wiki subject 本人 (LLM 默认填 wiki subject 模式)
>
> **v0.3.9 强化项**:
> - 检查 9 从 "Fei Wu 单独标" → "全作者中文括注" (覆盖整个作者列表)
> - 检查 10 新增 "通讯作者字段本身也带中文括注" (标注行也要 `Name（中文名）`)

### v0.3.3 fixed-template (LLM 输出时直接 fill)

```xml
<p>{TITLE}</p>
<p>大领域：{D}</p>
<p>中方向：{M}</p>
<p>小任务：{T}</p>
<p>子技术：{S}</p>
<p>作者：</p>
<p>{A1}, {A2}, {A3}, ..., Fei Wu（吴飞）, ..., {An}</p>
<p>标注：</p>
<p>通讯作者：{CORR1}, {CORR2}</p>
<p>一作/共一：{FIRST1}, {FIRST2}</p>
<p>学生：{STU1} (学生), {STU2} (学生)</p>
<p>发表：{VENUE} {YEAR} ({ROLE})</p>
<p>arXiv：<a href="https://arxiv.org/abs/{ARXIV_ID}">https://arxiv.org/abs/{ARXIV_ID}</a></p>  ← 优先 arXiv
<p>URL 类型：arXiv 预印本</p>  ← 或 "URL 类型：{VENUE_ABBR} 正式版"
<p>paperscool：<a href="https://papers.cool/arxiv/{ARXIV_ID}">https://papers.cool/arxiv/{ARXIV_ID}</a></p>  ← arXiv 才有 paperscool;无 arXiv 跳过此行

--- v0.3.5 无 arXiv 兜底模板 (e.g. SIGMOD/ASPLOS/CVPR 正式版) ---

<XML><![CDATA[
<p>arXiv：无预印本</p>
<p>URL 类型：{VENUE_ABBR} 正式版</p>
<p>论文网址：<a href="{VENUE_URL}">{VENUE_URL}</a></p>  ← dl.acm.org/doi/... 或 openaccess.thecvf.com 或 proceedings.neurips.cc
]]></XML>
```

### 完整文档规则(v0.3.5+ 必须遵守)

每篇生成的 doc **必须**是一份完整、自包含、可独立阅读的文档。**禁止**以下"画蛇添足"meta-描述:

```
❌ "本次重写以 §4 论文产出 v0.3.3 规范化为重点"
❌ "详细画像见原报告 §1"
❌ "v0.3.3 重写版 (2026-06-08)"
❌ "本次调研以 [某] 方向为重点"
❌ "本节仅作为 v0.3.3 重写标记"
❌ "更多论文见原 doc 表格"
❌ 任何"以...为标记/重点/版本"元描述
```

**正确做法**:5 章节全部填实,§1 画像完整,§2 匹配度具体,§3 套磁信有 call-to-action,§4 论文全列,§5 数据源标检索时间。**不要告诉用户"省略了 X"或"见原报告"**。

### §C 块级升级协议(v0.3.6+ 必须遵守)

**禁止**用 `docs +update --command overwrite` 重写整个 doc(v0.3.5 我犯过这错,删了原 200+ KB 内容)。

正确做法:**保留所有原内容**,只对不规范的元素用块级操作升级:

| 操作 | 适用场景 | 命令 |
|------|---------|------|
| `block_insert_after` | 在某 block 后插入新 block(如 4 行 taxonomy) | `lark-cli docs +update --api-version v2 --doc X --command block_insert_after --block-id <h4_id> --content @4tax.xml` |
| `block_replace` | 替换某 block(如 4 列表格换 4 行) | `lark-cli docs +update --api-version v2 --doc X --command block_replace --block-id <table_id> --content @4lines.xml` |
| `block_delete` | 删除冗余 block(如重复 paper card) | `lark-cli docs +update --api-version v2 --doc X --command block_delete --block-id <id>` |
| `str_replace` | 局部文字替换(如 删 "(末位/通讯)" 缩写) | `lark-cli docs +update --api-version v2 --doc X --command str_replace --pattern "..." --content "..."` |

**overwrite 的使用边界**(极严格):
- **仅**当用户**显式**说"按 v0.3.5 模板完整重写"+提供完整新数据(新论文清单 + 完整作者列表 + 真实 arXiv ID)
- **绝不**在"重写 / 规范化 / 升级"等模糊指令下用 overwrite
- overwrite 前必先 `cp` 备份原 docx 到 `/tmp/wiki-audit/backup-overwrite-{date}/`
- 备份内容保留 ≥ 7 天

**块级升级的优先级清单**(按 v0.3.5/3.6/3.7 升级):
1. 4 列表格 → 4 行 p blocks (Check 14a)
2. paper card 缺 4 行 taxonomy → block_insert_after
3. paper card 缺完整作者 / **含 `[待 L4/L5/L6 重抓]` placeholder** → 强制 L4/L5/L6 重抓,**不允许保留 placeholder 在 final doc** (v0.3.7+)
4. paper card 缺标注行 → block_insert_after
5. 全文 "(末位/通讯)" 缩写 → str_replace
6. 全文 "v0.3.3 重写版" framing → str_replace
7. **NEW (v0.3.7)**: 通讯作者名字与作者列表不一致(跨 paper 串名/凑数) → block_replace 改回(从 arXiv abs 页 verbatim 抽取 corresponding author)
8. **NEW (v0.3.7)**: 标题中途截断 / 错字字符(hallucination) → block_replace 改回(必须一字不差复制 arXiv abs 页 `<title>` 标签内容)
9. **NEW (v0.3.7)**: 通讯作者标 wiki subject 但 **未验证实际 paper 的 †/‡ footnote** → 必须 L4/L5/L6 逐篇验证(见 §G 通讯作者 systemic audit rule)

### §G 通讯作者 Systemic Audit Rule (v0.3.7+ 强制)

**🚨 触发条件**: 同一 wiki doc 中, **11+ paper cards 标 通讯作者 = wiki subject 本人**(如 汤斯亮 wiki 全部 11 篇都标 "Siliang Tang（汤斯亮）")。

**🚨 根因模式 (2026-06-08 实测, 7 错配)**: LLM 在生成时倾向于把通讯作者字段填成 wiki subject, 跳过逐篇验证实际 paper 的 corresponding author footnote。具体错配例子:

| Wiki 节点 | Paper | Wiki 标 | 真实 † Corresponding | 来源 |
|---------|-------|---------|----------------------|------|
| 况琨 | 2401.05507 (InfiAgent-DABench) | Kun Kuang（况琨）| **Fei Wu（吴飞）** (last author) | arXiv html footnote |
| 沈春华 | 2304.03284 (SegGPT) | Chunhua Shen（沈春华）| **Xinlong Wang（王新龙）** (Correspondence to xinlong.wang96@gmail.com) | arXiv html |
| 周晓巍 | 2503.21751 (Reconstructing) | Xiaowei Zhou（周晓巍）| **Georgios Pavlakos** (last author, UT Austin) | arXiv PDF, OpenReview |
| 汤斯亮 | WorldGPT (2404.18202) | Siliang Tang（汤斯亮）| **Juncheng Li（李俊成）** (per GitHub "† Corresponding Authors") | GitHub README |
| 汤斯亮 | On Path to MM Generalist (ICML 2025) | Siliang Tang（汤斯亮）| **Shuicheng Yan（颜水成）, Hanwang Zhang（张寒旺）** (per PMLR 267) | PMLR, ICML 2025 |
| 汤斯亮 | LOUPE (NeurIPS 2022) | Siliang Tang（汤斯亮）| Yueting Zhuang, Qi Tian, **Siliang Tang** (3 corresponding) | NeurIPS 2022 paper |
| 肖俊 | AutoManual (NeurIPS 2024) | Jun Xiao（肖俊）| **Binbin Lin（林斌斌）, Xiaofei He（何晓飞）** (Jun Xiao **不在作者列表中**!) | NeurIPS 2024 paper |

**🚨 强制审计流程 (任何 v0.3.7+ 审计必须跑)**:

```bash
# Step 1: 列出 wiki doc 所有 paper card 的 (title, 通讯作者, arxiv_id)
python3 -c "
import json, re
xml = json.load(open('/path/wiki.json'))['data']['document']['content']
for t in re.finditer(r'<p[^>]*?id=\"([^\"]+)\"[^>]*?><b>([^<]+)</b></p>', xml):
    # find 通讯作者 in next 4000 chars
    ...
"

# Step 2: 对每篇跑 4 源验证通讯作者
#   L4: arXiv API 拿 author list (id_list query)
#   L5: arXiv html 找 †/‡ footnote
#   L6: OpenReview 找 "Corresponding author" 字段
#   L7: CVPR/ICCV openaccess.thecvf.com 找 paper 页

# Step 3: 错配 → block_replace 改回 + backup
mkdir -p /tmp/wiki-audit/backup-$(date +%Y%m%d)-{teacher}/
cp wiki.json /tmp/wiki-audit/backup-.../original.json
lark-cli docs +update --api-version v2 --doc {obj_token} \
  --command block_replace --block-id {comm_bid} \
  --content '<p>通讯作者：{real_name}</p>' --doc-format xml
```

**🚨 输出标准**: 任何 paper card 的通讯作者字段必须严格匹配 arXiv abs 页 † / ‡ footnote / OpenReview "Corresponding Author" 字段。**禁止**默认填 wiki subject,除非该 paper 真实通讯作者就是 wiki subject。

**反例 (LLM 自动错配模式)**:
```html
<!-- ❌ LLM 默认填 wiki subject (没验证 paper) -->
<p>通讯作者：Kun Kuang（况琨）</p>

<!-- ✅ 必须从 arXiv html 的 † footnote 抽取 -->
<p>通讯作者：Fei Wu（吴飞）</p>
```

**Migrating 现有 doc 步骤** (v0.3.7 hotfix):
1. 对 9 节点全部 paper card 跑 §G audit
2. 错配 → backup + block_replace
3. 报告错配数 + 修复证据

### §H 一作 ≠ 通讯 Override (v0.3.8 新增, 2026-06-09)

**🚨 触发条件**: Wiki subject 是论文的 **第一作者 (一作)** 而非末位作者时，"last author = corresponding PI" 规则不适用。

**反例 (周晓巍 TPAMI 2024 一作 案例, 2026-06-09 实测)**:

| Wiki Paper | Wiki Subject 位置 | Wiki 通讯 | 实际 通讯 | 修复 |
|------------|------------------|-----------|----------|------|
| Neural 3D Scene Reconstruction with Indoor Planar Priors (TPAMI 2024) | Zhou (1st/一作) | Xiaowei Zhou | Hujun Bao (last) + Zhou (1st, co-通讯) | ✅ 已修复 |
| Animatable INRs for Creating Realistic Avatars from Videos (TPAMI 2024) | Zhou (1st/一作) | Xiaowei Zhou | Hujun Bao (last) + Zhou (1st, co-通讯) | ✅ 已修复 |

**根因**: LLM 应用 "last author = corresponding" 通用规则时，**忽略一作 signals**。在 TPAMI/期刊论文中，**一作** 同样可以标记为 通讯 (尤其当一作是 PI 本人时)。

**强制审计流程 (任何 v0.3.8+ audit 必须跑)**:

```bash
# Step 1: 检测 wiki subject 是否是 一作
# 检查论文 author list 中 wiki subject 的位置 (1st/2nd/middle/last)
python3 << EOF
import re
with open(f'backup-{teacher}/original.json') as f:
    content = json.load(f)['data']['document']['content']

# For each paper card, check wiki subject position
for block in paper_blocks(content):
    title = block['title']
    authors = block['authors']
    wiki_subj = '{wiki_subj_pinyin}'
    if wiki_subj in authors:
        position = authors.index(wiki_subj) + 1
        if position == 1:
            print(f'WARN: {title} - wiki subject is 一作, must check last author for 通讯')
EOF
```

**修复规则**:
- **一作 case** → 通讯 must include **last author (senior PI)** + **wiki subject (一作)** as co-corresponding
- **末位 case** → 通讯 = wiki subject (per §G convention)
- **中间 case** → must verify arXiv byline † footnote (don't default)

### §I Hallucinated Paper Card Detection (v0.3.8 新增, 2026-06-09)

**🚨 触发条件**: 论文标题在 DBLP / arXiv / OpenAlex / Semantic Scholar 4 个主要 index 中 **0 results**。

**反例 (2026-06-09 实测)**:

| Wiki Node | Hallucinated Paper | 实际 | 来源 |
|----------|-------------------|------|------|
| 况琨 (Kun Kuang) | "GRA-TAG: Production AI Search via Graph-Based Query Decomposition and Triplet Aligned Generation" | 不存在 — DBLP/arXiv/OpenAlex 全 0 results | 4-index 验证 |
| 肖俊 (Jun Xiao) | "AutoML Teaching Platform Series" | 不存在 — Jun Xiao ZJU profile 无 AutoML 方向, Google Scholar top-10 全是 CV/cross-media | 课题组主页 + Google Scholar |

**强制审计流程**:

```bash
# Step 1: 对每个 paper title 跑 4-index 验证
python3 << EOF
def check_hallucinated(title):
    # DBLP XML search
    dblp_url = f'https://dblp.org/search/publ/api?q={title}&format=json'
    # arXiv title search
    arxiv_url = f'https://export.arxiv.org/api/query?search_query=ti:{title}&max_results=1'
    # OpenAlex API
    oa_url = f'https://api.openalex.org/works?search={title}'
    # Semantic Scholar
    s2_url = f'https://api.semanticscholar.org/graph/v1/paper/search?query={title}&limit=1'
    # Count results from all 4
    return total_results
EOF
```

**修复规则**:
- **4-index 全 0 results** → paper card is **HALLUCINATED** → 标 `<p>通讯作者：[待核实 — 论文 DBLP/arXiv/OpenAlex 均查不到,疑似 hallucinated]</p>` + 在 paper card 顶部加 ⚠️ callout 标 "⚠️ 论文疑似不存在"
- **1-3 indexes 有 hit** → 标 "需用户 disambiguate" 列出所有候选
- **All 4 indexes agree** → paper is real, proceed to §G 通讯作者 verification

### §J Co-PI Override Rule (v0.3.8 新增, 2026-06-09)

**🚨 触发条件**: Wiki subject 是论文的**中间作者 (middle author)**，**不是一作也不是末位**。

**反例 (汤斯亮组 6+ papers, 2026-06-09 实测)**:

| Wiki Paper | Wiki Subject 位置 | Wiki 通讯 | 实际 通讯 | 修复 |
|------------|------------------|-----------|----------|------|
| WorldGPT (arXiv 2024) | Siliang Tang (2nd) | Siliang Tang | Juncheng Li (3rd) per GitHub README † | ✅ 已修复 |
| Auto-Encoding Morph-Tokens (ICML 2024) | Siliang Tang (2nd) | Siliang Tang | Juncheng Li (3rd) per GitHub README † | ✅ 已修复 |
| STEP (CVPR 2025) | Siliang Tang (8th) | Siliang Tang | Juncheng Li† (6th, explicit footnote) | ✅ 已修复 |
| LanDiff (ICCV 2025) | Siliang Tang (7th) | Siliang Tang | Xu Tan† + Juncheng Li† (4th, 6th) | ✅ 已修复 |
| DDT-LLaMA (CVPR 2025) | Siliang Tang (co-author) | Siliang Tang | Juncheng Li (explicit footer) | ✅ 已修复 |
| Iris (ICCV 2025) | Siliang Tang (9th) | Siliang Tang | Juncheng Li* + Yueting Zhuang* | ✅ 已修复 |

**根因**: LLM 默认 wiki subject = 通讯，**忽略 middle author 信号**。在 汤斯亮组中，**Juncheng Li (postdoc)** 是大量论文的实际通讯，PI 汤斯亮 仅是 senior 挂名 (middle/middle-last)。

**强制审计流程**:

```bash
# Step 1: 检测 wiki subject 在 author list 中的位置
# 1st = 一作, last = 末位, middle = 中间
# Step 2: 若是 middle → 必查 arXiv byline † footnote, 不能默认填 wiki subject
# Step 3: 若没有 explicit † → 查 GitHub README / OpenReview / 项目页
# Step 4: 若仍无 → 标 "待用户 verify"
```

**修复规则**:
- **Middle author + 显式 † on someone else** → 用 † 的作者作 通讯
- **Middle author + no explicit †** → 用 last author 作 通讯 (per ML convention)
- **Co-first / co-corresponding** → 标"通讯作者：X†, Y†共同通讯"

### §G+ §H+ §I+ §J 综合审计 Checklist (v0.3.8 强制)

对每个 paper card 跑 4 问：

1. **位置问题** (§H §J): Wiki subject 在 author list 的位置？
   - 1st → §H 触发 (一作 ≠ 通讯)
   - last → §G 默认 OK (末位 = 通讯)
   - middle → §J 触发 (Co-PI ≠ 通讯)
2. **存在性** (§I): 论文是否真实存在？
   - 4-index 0 results → HALLUCINATED
3. **† 验证** (§G): 实际 corresponding author 的 † 在哪？
   - arXiv byline † → 用 † 作者
   - OpenReview "Corresponding Author" → 用该作者
   - GitHub README † → 用 † 作者
4. **末位 fallback** (兜底): 没有 † 怎么办？
   - 1st author → §H (co-通讯 with last)
   - last author → §G (default 通讯 = last)
   - middle author → §J (NOT default wiki subject)


### §D 备份要求(v0.3.6+ 强制)

**任何块级操作前必先 backup 当前 doc 全文**到 `/tmp/wiki-audit/backup-{date}-{teacher}/`:

```bash
TOKEN="EFlmwpPgKiUARAkTplIcoOqrn3w"
DATE=$(date +%Y%m%d)
TEACHER="wufei"
mkdir -p /tmp/wiki-audit/backup-$DATE-$TEACHER
lark-cli docs +fetch --api-version v2 --doc $TOKEN --detail with-ids --format json \
  > /tmp/wiki-audit/backup-$DATE-$TEACHER/original.xml
```

如果发现"删太多",从 backup 恢复:
```bash
cd /tmp/wiki-audit/backup-$DATE-$TEACHER
lark-cli docs +update --api-version v2 --doc $TOKEN --command overwrite --content @original.xml
```

### §E 失败案例(v0.3.7+ 必读)— wiki WxDrwA5HCiK0RLk5pFCczmTbnPc paper card 反面教材(2026-06-08)

> **arXiv 2409.19132 真实数据** (Kun Su, Xiulong Liu, Eli Shlizerman; ICML 2024 PMLR v235) vs **飞书 wiki 实际跑出来的 paper card**:

```
❌ 标题(wiki):  "From Vision to Audio and Beyond: A Unified Model for 2D/3D/V"
   ↑ 真实(arXiv abs):  "From Vision to Audio and Beyond: A Unified Model for Audio-Visual Representation and Generation"
   ↑ 错: 中途截断 + "2D/3D/V" 是 LLM 幻觉字符
❌ 作者列表(wiki):  [待 L4/L5/L6 重抓]  ← placeholder 提交,违反 12 项 Check 6
   ↑ 真实(arXiv abs):  Kun Su, Xiulong Liu, Eli Shlizerman (3 人,U. Washington)
❌ 通讯作者(wiki):  Zhaozhou Zhao（赵洲）  ← 错配别 paper
   ↑ 真实(论文 byline):  Eli Shlizerman (shlizee@uw.edu, U. Washington)
❌ 发表(wiki):  (空)
   ↑ 真实:  ICML 2024 (PMLR v235, pp. 46804-46822)
❌ 一作/共一(wiki):  (空)
   ↑ 真实:  Kun Su, Xiulong Liu (共一, U. Washington)
```

**3 类错的根因**:
1. **标题截断 + 错字字符**: LLM 没有强制 read arXiv abs 页 verbatim, 而是 LLM 自由发挥 hallucinate 中途字符(`2D/3D/V` 在原文根本不存在)
2. **作者列表 placeholder**: Step R3 fallback 协议(原 L219)明文允许 `[待 L4/L5/L6 重抓]` placeholder 提交, 12 项自检无 reject 机制 → 漏洞
3. **通讯作者错配**: LLM 从 **别 paper** 抄了作者名(可能是 "Zhaozhou Zhao" 在 arXiv 别处出现过), 没有任何 cross-paper 一致性 check

**v0.3.7 修复** (本节):
- 12 项 Check 1 强化: 标题必须一字不差复制, 反例加 "中途截断 + 错字字符" (2409.19132 案例)
- 12 项 Check 5 强化: 反例加 `[待 L4/L5/L6 重抓]` / `[未知]` placeholder
- 12 项 Check 6 强化: 反例加 `[待 L4/L5/L6 重抓]` / `[待补]` placeholder 提交
- 12 项 Check 10 强化: 通讯作者名字必须 verbatim 在作者列表中, 反例加 "跨 paper 串名" (Zhaozhou Zhao 案例)
- §C 优先级清单 +2 项: 通讯作者串名 → block_replace 改回; 标题截断 → block_replace 改回
- **Step R3 fallback 协议修改**(下方 §F): 禁止 placeholder 提交, 必须 L4/L5/L6 重抓 或 拒绝输出 paper card

### §F Step R3 fallback 协议(v0.3.7 强化)— **禁止 placeholder 提交**

**原 v0.3.4 协议(Rewrite mode Step R3 第 4 步)**:
> 4. fallback: 用现有数据 + 标注 `[待 L4/L5/L6 重抓]` (不直接用 placeholder,留 hook 供后续补)

**v0.3.7 新协议**:
> 4. fallback (二选一, **禁止** 用 `[待 L4/L5/L6 重抓]` 提交 final paper card):
>    - **a) 触发 L4/L5/L6 重抓**: L4 MiniMax Web Search 搜 `arxiv 2409.19132` → L5 Kimi WebBridge 打开 `arxiv.org/abs/2409.19132` → L6 AnySearch 搜 `{title}` 拿到完整作者 + 通讯作者
>    - **b) L4/L5/L6 全失败 → 拒绝输出 paper card**: 在 wiki 标 `🟡 跳过: {arxiv-id} 数据不全, 待 L7+ 兜底`, 留下 retry hook, **不** 在 final doc 中保留 placeholder

**为什么禁止 placeholder 提交**: 12 项自检的"❌ 必须修正后才能输出"对 placeholder 无效(因为 LLM 把 placeholder 当成"已处理"), 导致脏 paper card 永久 ship 到 wiki, 与 v0.3.3 strict schema 目标完全相反。

### "脏"输出反例 (v0.3.3 全部禁止,v0.3.7 加 3 条 wiki 实测)

```
❌ <table>大领域 中方向 小任务 子技术</table>          ← 4 列表格
❌ <p>大领域:CV|中方向:Agent|小任务:GUI|子技术:RL</p>  ← 单行压平
❌ 作者: ..., (末位/通讯), Fei Wu                     ← 缩写
❌ 作者: ..., (通讯 PI 模式)                            ← 模式描述
❌ Xinyu: ... (Yiquan Wu, Bo Tang, ... 16 authors)      ← 省略
❌ arXiv: 2508.04482                                    ← 不是 URL
❌ arXiv: 待 arXiv 验证                                  ← 占位符
❌ paperscool (省略)                                     ← 缺 user 1-click 入口
❌ Wu et al. (2025) OS Agents ACL                       ← 缩写 + 顺序错乱
❌ <p>作者：[待 L4/L5/L6 重抓]</p>                      ← v0.3.7: placeholder 提交
❌ 标题: "...A Unified Model for 2D/3D/V"              ← v0.3.7: 中途截断 + 幻觉字符
❌ 通讯作者=Zhaozhou Zhao (作者列表无此名)               ← v0.3.7: 跨 paper 串名
```

### Output Schema 强制流程(LLM 必须按此顺序执行)

```
1. 写完论文 abstract 后 → 反推 4 维 taxonomy (从 abstract + 引言 + 方法)
2. 抓 arXiv abs 页 → 复制完整标题 + 完整作者列表 + arXiv ID + venue/year/role
3. 标注 (通讯作者/一作/学生) → 从论文 byline + 课题组主页查
4. 按 v0.3.3 fixed-template 顺序填 11-12 个 block
5. 跑 12 项 LLM 自检清单 → 任一 ❌ 必须修正后重跑
6. 全 ✅ 后才能进 1v1 block 写入
```

### v0.3.3 + 后续清理路径

- **新生成的 doc**(teacher-report --mode generate):严格按 v0.3.3 schema + 12 项自检
- **已有 v0.3.0/3.1/3.2 的 doc**:跑 audit mode Check 13+14+15,会标 ❌ "未用 v0.3.3 schema"
- **修复方法**:`overwrite` 整篇 doc,重写时用 v0.3.3 fixed-template

---

