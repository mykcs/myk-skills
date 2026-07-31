# teacher-report Paper Entry Format v0.11.0 (完整版, 替代 v0.3.9, 2026-06-11 升级)

> **来源**: v0.11.0 paper card 升级 (2026-06-11 grill-with-docs session, 12 decisions). 案例: `~/.claude/knowledge/cases/wiki/CASE-PAPER-CARD-V110-FULL-STATUS-ARXIV-20260611.md` (待写).
> **目的**: ~10 行/paper 完整版 paper card 规范, 适用于论文 ≤ 3 篇场景. v0.11.0 替代 v0.3.9 完整版 (历史 reference, 见 §v0.3.9 历史模板). v0.4.0 紧凑版保留, 不被 v0.11.0 替代 (见 references/paper-card.md).
> **加载时机**: SKILL.md 顶层 pointer 引用本文件时 / 套磁信 1-2 篇深度引用 / 单篇 deep-dive 写作.
> **v0.4.0 共存**: 论文 ≥ 10 篇仍用 v0.4.0 紧凑版 (7 行/paper, 53% 篇幅节省, 详见 references/paper-card.md).
> **v0.3.9 替代**: v0.11.0 完整版替代 v0.3.9 完整版, 加 3 新字段 (status / arXiv 可空 / paper URL), 加 5 新 LLM 自检 (Check 18-22). 详细迁移见 §v0.11.0 迁移指南 v0.3.9 → v0.11.0 段.

---

## Paper Entry Format (v0.11.0, 2026-06-11) — 硬要求

> **v0.3.x → v0.4.0 → v0.11.0 升级**:
> - **v0.3.x 痛点** (2026-06-10 之前): ① 没法快速核对 author 完整性和通讯作者标注 ② 没法给 Fei Wu 显式高亮 ③ 没法直接跳到 arXiv 全文 ④ 论文在 4 级研究 hierarchy 中的位置不可见
> - **v0.3.1**: 4 维 taxonomy 表格
> - **v0.3.2 hotfix**: 4 维 taxonomy 改为 4 行独立 `<p>` 块
> - **v0.3.3 hotfix**: ① 作者列表 verbatim ② 标注行单独成行 ③ Fei Wu 显式标 `（吴飞）`
> - **v0.3.9 hotfix**: ① 全作者中文括注 ② 标注行 inline + 中文括注
> - **v0.4.0 升级** (2026-06-10): 7 行紧凑版, arXiv 嵌入 title, 通讯/大老板 inline 标记
> - **v0.11.0 升级** (2026-06-11): 4 字段 (status / arXiv 状态 / paper URL / 编号样式) + 8 enum status + 7 paper URL 优先级 + 5 新自检 (Check 18-22)

### Paper Card v0.11.0 模板 (~10 行/paper, 完整版, 论文 ≤ 3 篇)

```
1. {论文完整标题 (verbatim, 不可改字/改序/省字)}
{AUTHOR_LIST_WITH_INLINE_MARKERS_CHINESE_PARENS}    ← e.g. **Ying Wei（魏颖）**（大老板）（通讯）
{venue} {year} ({role})    ← e.g. ICML 2026 (Oral) / EMNLP 2024 Findings (Findings) / arXiv preprint (Preprint)
{venue} {year} {status_enum_8values}    ← v0.11.0 新 (独立新行, 8 值 enum: 被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿)
arXiv：{url_or_暂无}    ← v0.11.0 新 (独立行, arXiv 可空, "暂无" 是合法状态值)
paper：{url_openreview_or_arxiv_or_doi_or_proceedings}    ← v0.11.0 新 (统一 1-click 入口, 7 种 URL 优先级)
大领域：{大领域}
中方向：{中方向}
小任务：{小任务}
子技术：{子技术}
```

### 8 enum status 严格定义 (v0.11.0 新)

| 值 | 含义 | 触发场景 | 必配 paper URL 类型 |
|----|------|---------|------------------|
| **被拒** | rejected by venue | 投稿被 reject, 没接收 | OpenReview (decision = reject) |
| **在投** | under review | 投稿在审稿中, 没决策 | OpenReview (decision pending) |
| **R&R** | revise & resubmit | 审稿人要求修后再投, 不是接受 | OpenReview (decision = R&R) |
| **已收** | accepted, not yet presented | 已 accept, 但未 camera-ready, 未 index | OpenReview 或 proceedings |
| **Camera Ready** | accepted + camera-ready submitted | camera-ready 已提交, 等会议 | proceedings 或 journal |
| **已发表** | published / presented / indexed | 会议已开 / 期刊已 index | proceedings / journal / DOI |
| **Preprint** | arXiv-only, not submitted anywhere | 仅 arXiv, 没投任何 venue | arXiv abs |
| **撤稿** | withdrawn / retracted | 主动撤稿或被撤稿 | OpenReview (decision = withdraw) |

> **严禁** free text (e.g. `unknown` / `pending` / `submitted` / `[待补]` / `未发表`) — Check 18 auto-reject.

### 7 paper URL 优先级 (v0.11.0 新)

1. **OpenReview forum** `https://openreview.net/forum?id={forum_id}` — 被拒/在投/R&R 状态**强制**此 URL
2. **arXiv abs** `https://arxiv.org/abs/{id}` — Preprint 状态必此 URL
3. **DOI** `https://doi.org/{doi}` — 期刊论文 (无 OpenReview 时)
4. **papers.cool** `https://papers.cool/arxiv/{id}` — 备用
5. **会议 proceedings** (e.g. `proceedings.neurips.cc/paper/.../hash/...`) — Camera Ready / 已发表
6. **期刊页** — 期刊论文
7. **主页 PDF** `https://{faculty}.github.io/papers/{slug}.pdf` — 最后 fallback

### 22 项 LLM 自检 (v0.10.0 + v0.11.0 增量)

v0.10.0 已 17 项 (Check 1-17). v0.11.0 加 5 项 (Check 18-22):

- **Check 18 (status enum)**: paper card 的 status 行必 ∈ 8 enum, free text auto-reject
- **Check 19 (paper URL 合法类型)**: `paper：` 行必 ∈ 7 URL 模板之一
- **Check 20 (arXiv/paper 一致性)**: `arXiv：暂无` ↔ `paper：非空` 必同时成立
- **Check 21 (status/paper URL 联动)**: 被拒/在投/R&R 状态 → paper URL 必为 OpenReview
- **Check 22 (paper card 编号样式)**: 编号 `1.` `2.` `3.` 纯文本前缀, 非 hyperlink

详细 Check 1-17 见 references/output-schema.md + references/paper-card.md. 任何 ❌ 必修正后才能写入 docx.

---

## Paper Entry Format (v0.3.9, 2026-06-10) — 硬要求

> **背景**:v0.3.0 之前 docx 论文展示痛点:① 没法快速核对 author 完整性和通讯作者标注 ② 没法给 Fei Wu 显式高亮(通讯作者被埋没) ③ 没法直接跳到 arXiv 全文(用户必须自己搜) ④ 论文在 4 级研究 hierarchy(大领域→中方向→小任务→子技术)中的位置不可见,套磁信无法精准定位方向。
>
> **v0.3.0 → v0.3.1 → v0.3.2 → v0.3.3 → v0.3.9 升级**: 
> - **v0.3.1**: 在原 6 行 paper card 基础上,**追加 4 维 taxonomy** (大领域/中方向/小任务/子技术) — 但用 4 列表格
> - **v0.3.2 hotfix**: 4 维 taxonomy 改为 4 行独立 <p> 块(每字段一行,不是表格)
> - **v0.3.3 hotfix (2026-06-08)**:
>   1. **作者列表: 写完整 verbatim**。禁止 "(末位/通讯)" 或 "(通讯 PI 模式)" 描述性缩写 — 必须 verbatim 列出全部作者
>   2. **标注行: 单独成行**。作者身份/位置/学生身份等元信息(谁通讯、谁一作、谁是 Fei Wu)写独立 `<p>标注：</p>` 段,不混在作者列表里
>   3. **Fei Wu 显式标 `Fei Wu（吴飞）`**(中文括号),即使排在第 1 位
> - **v0.3.9 hotfix (2026-06-10)**:
>   1. **🚨 全作者中文括注(必须)** — 所有作者名字必须带中文括注,如 `Nan Chen, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He（何炳生）, Rizal Fathony, Jun Hu（胡军）, Jia Chen（陈佳）`。**禁止**仅对 Fei Wu/重点作者加括注。**禁止**只列英文名无括注。
>   2. **原因**:
>      - 用户在 dashboard 横向对比时,需快速识别每个作者的中文身份(尤其在申博候选池中,中文名是关键的 person 身份锚点)
>      - 防止 LLM 在 6 节点 30+ papers 批量生成时,只对 Fei Wu (高知名度) 显式标中文,忽略其他作者 (跨 paper card 一致性差)
>      - 申博场景下,**每个作者都可能成为潜在合作者或评审**,中文括注是必备 disambiguation
>   3. **v0.3.8 §G 升级**: 之前只对 Fei Wu 显式标(v0.3.3)→ 现在所有作者都必须标(v0.3.9)。**强一致性,无例外**。

### Paper Card 模板(v0.3.9,每篇论文一份,无例外)

```
{论文完整标题 (verbatim, 不可改字/改序/省字)}
大领域：{大领域}    ← 1 行 1 字段,不是表格
中方向：{中方向}
小任务：{小任务}
子技术：{子技术}
作者：
{作者1（中文名）, 作者2（中文名）, 作者3（中文名）, ..., 作者N（中文名）}    ← 全部 verbatim 列出(无 et al. 无缩写),每个作者都加中文括注
标注：
通讯作者：{通讯 1（中文名）, 通讯 2（中文名）}    ← 单独成行;不混在作者列表里;通讯作者也要带中文括注
一作/共一：{一作 1（中文名）, 一作 2（中文名）}    ← 第一作者(可多个,共一用括号)
学生：{学生 1, 学生 2}    ← 博士生/硕士生身份,标 (学生) 后缀
发表：{venue year (角色)}    ← 例: ACL 2025 (Oral) / ICLR 2026 (Spotlight) / KDD 2024 (Long Paper) / TPAMI 2024 (期刊) / arXiv preprint
arXiv：https://arxiv.org/abs/{arxiv-id}    ← 必须 arXiv ID;无 arXiv 用 DOI
paperscool：https://papers.cool/arxiv/{arxiv-id}    ← 必须,这是 user 1-click 阅读入口
```

#### v0.3.1 → v0.3.2 关键变化

- **4 维 taxonomy 从 4-列表格改为 4 行独立 <p> 块**(`大领域：` / `中方向：` / `小任务：` / `子技术：` 每行 1 字段)
- 表格形式在飞书 UI 里读起来割裂;4 行更清晰可读,可直接 grep/复制
- LLM 输出格式示例:
  ```html
  <p>大领域：人工智能</p>
  <p>中方向：强化学习</p>
  <p>小任务：探索策略</p>
  <p>子技术：状态启发式; 空间链接; 新颖性鼓励</p>
  ```

#### 4 维 taxonomy 填写规范

| 字段 | 说明 | 示例 |
|------|------|------|
| **大领域** | 最上层研究领域(2-5 个候选:CV / NLP / 图形学 / 多媒体 / 机器学习 / 具身智能) | 计算机视觉 / 自然语言处理 / 多模态 / 推荐系统 |
| **中方向** | 大领域下的细分方向(导师的主线方向,通常 5-15 个候选) | 多模态大模型 / GUI Agent / 视觉问答 / 端云协同 / 通用分割 |
| **小任务** | 中方向下的具体任务(论文直接解决的子问题) | 图像编辑 / 点云理解 / 视频问答 / 智能体规划 |
| **子技术** | 实现小任务的关键技术 / 方法(论文核心贡献) | 扩散模型 / 注意力机制 / RLHF / 思维链 / 世界模型 |

> 4 维 taxonomy 关系:**大领域 ⊃ 中方向 ⊃ 小任务 ⊃ 子技术**。每篇论文对应唯一的 4 元组。LLM 必须从论文 abstract + 引言 + 方法 章节判定,**禁止**用 placeholder(如"未知 / N/A")。
>
> **v0.3.2 强制输出格式**: 每字段 1 个独立 `<p>` 块,不是 1 个 4-列 `<table>`。例:见上方 Paper Card 模板。

### 字段规范(v0.3.1,共 9 字段)

| 字段 | 必填 | 规则 |
|------|------|------|
| **大领域** | ✅ | 4-列 taxonomy 第 1 列;最上层研究领域,5-10 候选 (CV / NLP / 多媒体 / 机器学习 / 具身智能 / 推荐系统) |
| **中方向** | ✅ | 4-列 taxonomy 第 2 列;大领域下细分方向,5-15 候选 (多模态大模型 / GUI Agent / 视觉问答 / 端云协同 / 通用分割) |
| **小任务** | ✅ | 4-列 taxonomy 第 3 列;中方向下具体任务,论文直接解决的子问题 (图像编辑 / 点云理解 / 视频问答 / 智能体规划) |
| **子技术** | ✅ | 4-列 taxonomy 第 4 列;实现小任务的关键技术,论文核心贡献 (扩散模型 / 注意力机制 / RLHF / 思维链 / 世界模型) |
| **标题** | ✅ | verbatim, 不可改字/改序/省字;**禁止**用缩写或 et al. 替代 |
| **作者** | ✅ | 全部列出(无 et al.), 用 `, ` 逗号+空格分隔; **v0.3.9 强化: 全作者中文括注(必须)**, 例 `Nan Chen, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He（何炳生）, Rizal Fathony, Jun Hu（胡军）, Jia Chen（陈佳）`;**禁止**仅 Fei Wu 单独标 |
| **发表** | ✅ | `{venue} {year} ({角色})`, 角色可省: Oral / Spotlight / Poster / Long Paper / Short Paper / Findings / Track 1 / Invited Talk / Preprint |
| **arXiv** | ✅ | URL 必含 `https://arxiv.org/abs/{id}`;无 arXiv 用 `https://doi.org/{DOI}` 兜底 |
| **paperscool** | ✅ | URL 必含 `https://papers.cool/arxiv/{id}`;与 arXiv ID 一致;**禁止**漏 |

### 正确示例 (v0.3.9,完整作者列表 + 单独标注行 + 全作者中文括注)

```
OS Agents: A Survey on MLLM-based Agents for General Computing Devices Use
大领域：多模态
中方向：智能体 Agent
小任务：OS 操作
子技术：综述 + Benchmark
作者：
Xueyu Hu（胡学宇）, Tao Xiong（熊涛）, Biao Yi（易彪）, Zishu Wei（魏子顺）, Ruixuan Xiao（肖若轩）, Yurun Chen（陈雨润）, Jiasheng Ye（叶家声）, Meiling Tao（陶美玲）, Xiangxin Zhou（周翔鑫）, Ziyu Zhao（赵子宇）, Yuhuai Li（李宇怀）, Shengze Xu（徐胜泽）, Shenzhi Wang（王慎之）, Xinchen Xu（许鑫辰）, Shuofei Qiao（乔硕飞）, Zhaokai Wang（王兆凯）, Kun Kuang（况琨）, Tieyong Zeng（曾铁勇）, Liang Wang（王亮）, Jiwei Li（李纪伟）, Yuchen Eleanor Jiang（蒋雨晨）, Wangchunshu Zhou（周汪春树）, Guoyin Wang（王国印）, Keting Yin（殷科廷）, Zhou Zhao（赵洲）, Hongxia Yang（杨红霞）, Fan Wu（吴帆）, Shengyu Zhang（张圣宇）, Fei Wu（吴飞）
发表：ACL 2025 (Oral)
arXiv：https://arxiv.org/abs/2508.04482 
paperscool：https://papers.cool/arxiv/2508.04482
```

> **v0.3.9 中文括注示范 (刘泽民 wiki 真实论文 Consistency Training with Limited Supervision)**:
>
> ```
> 作者：
> Nan Chen（陈楠）, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He（何炳生）, Rizal Fathony, Jun Hu（胡军）, Jia Chen（陈佳）
> ```
> 注意: 即使 Bryan Hooi 是外籍作者(无对应中文名),也保留英文名;**禁止**省略或填 "N/A"。Rizal Fathony 同理。

#### 4 维 taxonomy 反推流程 (从论文 abstract → 4 字段)

| 步骤 | 操作 | 工具/来源 |
|------|------|----------|
| 1. 读 abstract 末 2 句 | 提取"解决什么任务 / 用什么方法" 关键词 | paper abstract |
| 2. 查 venue 标签 | 标 ACL/NeurIPS/CVPR → 大领域候选 | arXiv abs 页 venue 字段 |
| 3. 标"小任务" | abstract 中"我们提出 X 用于 Y" 的 Y | abstract + 引言 |
| 4. 标"子技术" | abstract 中"基于 Z 改进 / 采用 Z" 的 Z | abstract + 方法章节 |
| 5. 标"中方向" | 综述论文 → 大领域 + 小任务聚合;否则 = 大领域下导师主线方向 | 课题组主页 + L1 |
| 6. 标"大领域" | 5 选 1:CV / NLP / 多模态 / 机器学习 / 具身智能 | 综述标题 + L1 |
| 7. 校验 hierarchy | 4 字段必须满足大领域 ⊃ 中方向 ⊃ 小任务 ⊃ 子技术 | LLM 自检 |

> **常见 taxonomy 错误**:
> - 大领域="Computer Vision" 错 → 应写"计算机视觉"(中文一致)
> - 子技术="提出新方法" 错 → 必须具体(扩散模型 / 注意力 / RLHF)
> - 中方向="深度学习" 错 → 太宽,应写"多模态大模型" 或 "端云协同"
> - 4 字段字数差异大(1 字 vs 20 字)→ 标准化为 4-8 字关键词

### 反例 (v0.3.0 全部禁止)

```
❌ OS Agents  ACL 2025, Hu et al.                          ← 1 行简化
❌ OS Agents (ACL 2025 Oral) ⭐                             ← 标题 + venue 1 行,无作者
❌ <p><b>OS Agents (ACL 2025 Oral) ⭐</b></p>               ← HTML 紧凑格式
❌ Xinyu: ... (Yiquan Wu, Bo Tang, ... 16 名作者)          ← 作者被压在标题括号里
❌ Wu et al. (2025) OS Agents ACL                          ← 缩写 + 顺序错乱
❌ arXiv: 2508.04482                                       ← arXiv 没给 URL
❌ paperscool (省略)                                       ← 缺 user 1-click 入口
❌ 大领域:CV | 中方向:Agent | 小任务:GUI | 子技术:RL      ← 单行 taxonomy 压平 (应 4 行)
❌ <table>大领域 中方向 小任务 子技术</table>                ← 4 列表格 (应 4 个 <p> 块)
❌ 作者：... (末位/通讯), Fei Wu                           ← (末位/通讯) 缩写 (应写完整 + 单独标注)
❌ 作者：... (通讯 PI 模式)                                 ← 模式描述 (应写完整作者 + 标注)
❌ 作者：Nan Chen, Zemin Liu, Bryan Hooi, Bingsheng He, Rizal Fathony, Jun Hu, Jia Chen    ← v0.3.9 反例: 无中文括注 (必须全作者标中文)
❌ 作者：Nan Chen（陈楠）, Zemin Liu（刘泽民）, Bryan Hooi   ← v0.3.9 反例: 中间作者漏标 (Bryan Hooi 无中文名时也保留英文, 不可省略)
❌ 作者：Fei Wu（吴飞）, Xueyu Hu, ...                      ← v0.3.9 反例: 仅 Fei Wu 单标 (必须所有作者全标)
```

### 适用位置 (全 docx 强制,5 章均生效)

1. **§4 论文产出全景** — 每个分年表**上方或下方**列出该年所有论文的 paper cards (year ≥ 3 篇 → 列在表下; year 1-2 篇 → 可用 callout 装)
2. **§2.2 方向匹配度** — 引用具体论文举例时, 用 paper card 格式 (5 字段+作者)
3. **§3 套磁与行动建议** — 套磁信草稿引用具体论文时, paper card 块嵌入
4. **§1 TL;DR** — 提到"代表论文"时, paper card 列在 callout 下方
5. **§1.2 / §1.3 学生代表作** — 列每位博士代表作时, paper card

### 与 v0.2.5 旧"论文精读子段模板"的关系

| 维度 | v0.2.5 (旧) | v0.3.0 (新) |
|------|-------------|-------------|
| 论文展示形式 | 表内 1 行 / `<p><b>...</b></p>` 紧凑 | 6 行 paper card |
| 作者列表 | 禁止 (et al.) | 必须 (全名 + Fei Wu 中文标注) |
| arXiv 链接 | inline `<a href>` 在标题后 | 独立 `arXiv：` 行 |
| papers.cool | 无 | 必须 `paperscool：` 行 |
| 信息密度 | 低 (5 字段 UL 跟在标题后) | 高 (一篇一段,可独立打印) |

> **迁移指南**: 现有 v0.2.5-v0.2.9 的 docx 跑 audit mode (Check 13) 时,会标 ❌ "缺少 paperscool" / "缺少作者列表",给出修复建议。修复时用 `lark-cli docs +update --command block_replace` 把每个 `<p><b>{title} (venue year) ⭐</b></p>` 替换为对应 6 行 paper card block。
>
> **v0.3.0 → v0.3.1 迁移**: 现有 v0.3.0 docx 跑 audit mode (Check 14) 时,会标 ❌ "缺 4-列 taxonomy 分类表"。修复时:对每篇 paper card 跑 `block_insert_after` 在 `<p>{title}</p>` 后插入 4-列 table,然后 `block_replace` 改 taxonomy cell 值。LLM 需从 paper abstract 反推 4 维 taxonomy (参考 report-template §6.2 taxonomy 反推 prompt)。

### Audit Check 13 (2026-06-08 v0.3.0 6-行 paper card)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 13a | 论文条目 ≥ 6 行 (标题 + 5 字段) | 100% paper cards 符合 6 行结构 | ❌ 简化为 1 行 → 必须扩为 6 行 |
| 13b | 含 `作者：` `发表：` `arXiv：` `paperscool：` 4 个字段前缀 | 100% 4/4 | ❌ 缺任一字段 → 必须补 |
| 13c | `Fei Wu（吴飞）` 显式标注 | 100% Fei Wu 署名的论文 | ❌ 漏 `（吴飞）` → 必须补中文括号 |
| 13d | arXiv URL = `https://arxiv.org/abs/{id}` | 100% 链接规范 | ❌ 缺 URL / 用缩写 ID → 必须规范化 |
| 13e | paperscool URL = `https://papers.cool/arxiv/{id}` | 100% 链接规范 | ❌ 缺 papers.cool 入口 → 必须补 |

> Check 13 的 5 子项 (a-e) 全 ✅ 才算 Check 13 PASS;任一 ❌ = Check 13 FAIL (3 ❌ = 整体审计 fail, 降级为 🟡)。

### Audit Check 14 (2026-06-08 v0.3.1 新增 — 4 维 taxonomy)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 14a | 每篇 paper card 含 4 维 taxonomy 4 行独立 <p> 块(大领域/中方向/小任务/子技术) | 100% 论文含 4 行 | ❌ 缺 4 行 / 用了 4 列表格 → 必须改为 4 个 <p> 块 |
| 14b | taxonomy 4 字段均有具体值(无 `未知` / `N/A` / `待补` placeholder) | 100% 4/4 | ❌ placeholder → 必须从 abstract 抽取或 L1-L4 反查 |
| 14c | 4 维 hierarchy 一致性:大领域 ⊃ 中方向 ⊃ 小任务 ⊃ 子技术 | 100% 无逻辑冲突 | ❌ 跨级冲突(如"小任务=图像编辑"配"子技术=RLHF")→ 必须重判 |
| 14d | taxonomy 描述 ≤ 12 字(简洁,可对比) | ≥ 95% 论文满足 | ❌ 过长 → 截断为关键词 |

> Check 14 的 4 子项 (a-d) 全 ✅ 才算 Check 14 PASS;任一 ❌ = Check 14 FAIL (≥ 3 ❌ = 整体审计 fail, 降级为 🟡)。

### Audit Check 15 (2026-06-08 v0.3.3 新增 — 完整作者列表 + 单独标注行)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 15a | 作者列表 verbatim 全列 | 100% 论文完整列出全部作者,无 `et al.` / 无 `... N 名作者` 省略 / 无缩写 | ❌ 缩写 → 必须补全作者列表(查 arXiv abs 页) |
| 15b | 禁止 `(末位/通讯)` / `(通讯 PI 模式)` 等描述性缩写 | 100% 作者行无描述性缩写 | ❌ 缩写 → 必须 verbatim 复制 + 标注行单列 |
| 15c | 标注行: 通讯作者/一作/学生 独立成行 | 100% 论文含 `<p>标注：</p>` 段 | ❌ 缺标注行 → 必须从 arXiv byline 抽取并单列 |
| 15d | Fei Wu 显式标 `Fei Wu（吴飞）` 即使排第 1 | 100% Fei Wu 署名论文 | ❌ 漏 `（吴飞）` → 必须补中文括号 |

> Check 15 的 4 子项 (a-d) 全 ✅ 才算 Check 15 PASS;任一 ❌ = Check 15 FAIL (≥ 3 ❌ = 整体审计 fail, 降级为 🟡)。

### Audit Check 16 (2026-06-10 v0.3.9 新增 — 全作者中文括注)

| # | Check | 期望 | 失败处理 |
|---|-------|------|---------|
| 16a | **全作者中文括注(必须)** | 100% 论文的作者列表中,**每个**作者均含 `Name（中文名）` 格式,即使外籍作者无中文名也保留英文名(不可省略) | ❌ 任何作者漏 `（中文名）` → 必须补,外籍作者可保留英文名(不可填 N/A) |
| 16b | **禁止仅 Fei Wu 单独标** | 100% 论文: 若 Fei Wu 标了 `（吴飞）`,则同一行的**所有其他作者**也必须标中文 | ❌ 出现 "Xueyu Hu, ..., Fei Wu（吴飞）" 部分标注 → 必须补齐 |
| 16c | 标注行: 通讯作者/一作/学生 也带中文括注 | 100% 论文的 `<p>通讯作者：{X}</p>` 中,通讯作者必须 `Name（中文名）` 格式 | ❌ 通讯作者漏标 → 立即补 |
| 16d | 中文名与作者姓名正确对应 | 100% 作者的 `（中文名）` 须与 arXiv 真实中文名一致 (e.g., 沈春华 = Chunhua Shen, 刘泽民 = Zemin Liu) | ❌ 中文名错配 → 查 arXiv 作者主页或 Google Scholar 校准 |

> Check 16 的 4 子项 (a-d) 全 ✅ 才算 Check 16 PASS;任一 ❌ = Check 16 FAIL (≥ 3 ❌ = 整体审计 fail, 降级为 🟡)。
>
> **示例 (v0.3.9)**:
> ```
> 作者：
> Nan Chen（陈楠）, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He（何炳生）, Rizal Fathony, Jun Hu（胡军）, Jia Chen（陈佳）
> ```
> - Nan Chen → 陈楠 ✓ (中文括注)
> - Zemin Liu → 刘泽民 ✓ (中文括注)
> - Bryan Hooi → 保留英文 ✓ (外籍作者无对应中文名,保留英文)
> - Bingsheng He → 何炳生 ✓
> - Rizal Fathony → 保留英文 ✓
> - Jun Hu → 胡军 ✓
> - Jia Chen → 陈佳 ✓
>
> **反例 (v0.3.9 禁止)**:
> ```
> ❌ 作者：Nan Chen, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He  ← 部分标注
> ❌ 作者：Nan Chen（陈楠）, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He, Rizal Fathony  ← 后面漏标
> ❌ 作者：Fei Wu（吴飞）, Xueyu Hu, ...                          ← 仅 Fei Wu 标
> ```

