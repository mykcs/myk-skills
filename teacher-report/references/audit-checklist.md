# Audit Checklist — 14 项合规检查 (v0.2.8+ → v0.4.0 加 Check 14)

> **用法**:Audit mode 跑这份 checklist。每项独立 pass/fail,失败时附**原始片段** + **修复建议**。
>
> **设计原则**:
> - 单一职责 — 每项检查只验一个硬规则
> - 幂等 — 跑两次结果相同
> - 廉价 — 不重新抓 L1-L4,只读 docx XML
> - 不破坏 — 不修改 docx,只报告

---

## Check 1 — 5 h2 章节齐全且顺序正确

**期望**:`<h2>1.</h2>` ... `<h2>2.</h2>` ... `<h2>3.</h2>` ... `<h2>4.</h2>` ... `<h2>5.</h2>`(共 5 个,顺序固定)

**Output contract 要求**:TL;DR callout / 导师与课题组画像 / 申博匹配度评估 / 套磁与行动建议 / 论文产出全景(按年)/ 数据来源与说明

**检测方法**:
```bash
# 用 ripgrep 数 h2
rg -o '<h2>[^<]*</h2>' | wc -l  # 期望 5
# 数 § 数据来源
rg -c '数据来源'  # 期望 ≥ 1
```

**失败**:
- ❌ h2 数量 ≠ 5
- ❌ 缺"数据来源"章节

**修复**:
- 缺章节 → 用 `lark-cli docs +update --command append` 补对应章节
- 顺序错 → 整篇 overwrite

---

## Check 2 — h2 标题用 `1.` `2.` `3.` 风格(无中文数字、**无 emoji 前缀**)

**期望**:`<h2>1. 导师与课题组画像</h2>`(纯阿拉伯数字,无 emoji)

**反模式**:
- ❌ `<h2>一、导师与课题组画像</h2>`(中文数字)
- ❌ `<h2>第1章 导师画像</h2>`(无编号或前缀)
- ❌ `<h2>1.1 课题组定位</h2>` (h2 用了 h3 风格,层级错)
- ❌ `<h2>👤 1. 导师与课题组画像</h2>`(**emoji 前缀** — 飞书 outline 仍识别但不属于标准模板)

**检测** (v0.3.0 已修 emoji 前缀 false positive):
```bash
# ✅ 正确:严格匹配纯阿拉伯数字 (无 emoji 前缀也算 OK,因为是降级)
rg -o '<h2>[^<]+</h2>' | rg -v '^[0-9]+\. '

# 检测 emoji 前缀(可选,警告级不强制):
rg -o '<h2>[^<]+</h2>' | rg '^[^\d]+\d+\. '  # 命中 → emoji 前缀警告
```

**修复**:
```
<h2>1. 导师与课题组画像</h2>     ← 期望(无 emoji 前缀)
<h2>👤 1. 导师与课题组画像</h2>   ← 警告级(emoji 前缀,建议改但非阻塞)
<h2>一、导师与课题组画像</h2>   ← 必须改(中文数字)
```

---

## Check 3 — h3 标题用 `1.1` `1.2` 子节风格

**期望**:`<h3>1.1 基本信息</h3>` / `<h3>2.3 论文精读</h3>`

**反模式**:
- ❌ `<h3>基本信息</h3>`(无编号)
- ❌ `<h3>1. 基本信息</h3>`(用了 h2 风格,层级错)

**检测** (v0.3.0 已修 emoji 前缀 false positive):
```bash
# ✅ 正确:允许 emoji 前缀
rg -o '<h3>[^<]+</h3>' | rg -v '^[^\d]*\d+\.\d+ '

# ❌ 老 bug:`^[0-9]+\.[0-9]+ ` 不接受 emoji 前缀
```

**修复**:
```
<h3>1.1 基本信息</h3>            ← 期望
<h3>基本信息</h3>               ← 改成上面
```

---

## Check 4 — h4 无手动 `(1) (2) (3)` 编号

**期望**:`<h4>1. 大模型 + 因果(3 篇)</h4>`

**反模式**:
- ❌ `<h4>(1) 大模型 + 因果(3 篇)</h4>`(飞书 outline 不识别括号编号)
- ❌ `<h4>第一组 大模型</h4>`(中文序号)

**检测**:
```bash
rg -o '<h4>[^<]+</h4>' | rg '\([0-9]+\)|第[一二三四]'
```

**修复**:
```
<h4>1. 大模型 + 因果(3 篇)</h4>          ← 期望
<h4>(1) 大模型 + 因果(3 篇)</h4>        ← 改成上面
```

**反例来源**:v0.2.3 模板(2026-06-05 之前)

---

## Check 5 — 无内联 `① ② ③` 字符

**期望**:论文精读用 `<p><b>完整标题</b></p>`,无内联编号字符

**反模式**:
- ❌ `<p><b>① Causality for LLMs...</b></p>`
- ❌ `<p><b>(1) Causality for LLMs...</b></p>`

**检测**:
```bash
rg -o '①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩'
```

**修复**:
```
<p><b>① Causality for LLMs...</b></p>     ← 失败
<p><b>Causality for LLMs...</b></p>       ← 期望
```

**反例来源**:v0.2.3 模板(2026-06-05 之前,论文精读内联编号)

---

## Check 6 — 无 `████████` 字符画趋势图

**期望**:用 `<table>` + 精确数字

**反模式**:
- ❌ `<p>2023 ████ 5 篇</p>`
- ❌ `<p>2024 ████████ 8 篇</p>`

**检测**:
```bash
rg -c '█'
```

**修复**:
```
<p>2023 ████ 5 篇</p>        ← 失败
<table>
  <tr><td>2023</td><td>5 篇</td></tr>  ← 期望
</table>
```

**反例来源**:v0.2.4 dashboard 摘要行 / 早期 v0.1 模板

---

## Check 7 — TL;DR 用 callout + grid(非纯文字)

**期望**:`<callout emoji="🎯">` 包含 `<grid><column>` 双列布局

**反模式**:
- ❌ `<p><b>TL;DR</b>:{老师}是 {学校} {职称}...</p>`(纯文字)
- ❌ `<callout>` 但无 `<grid>`(单列)
- ❌ `<grid>` 但无 `<callout>`(裸露 grid)

**检测**:
```bash
# 找到 TL;DR 位置,检查是否含 callout + grid
rg -A 5 'TL;DR' | rg -q 'callout|grid'
```

**修复**:套用 `report-template.md §1` 模板。

---

## Check 8 — §5 数据来源含检索时间

**期望**:`<p><b>检索时间</b>:{YYYY-MM-DD}</p>`

**反模式**:
- ❌ 完全无 §5 章节
- ❌ §5 存在但无"检索时间"字段
- ❌ "检索时间"模糊(只写"近期" / "最近")

**检测**:
```bash
rg -c '检索时间.*[0-9]{4}-[0-9]{2}-[0-9]{2}'
```

**修复**:补 `<li><b>检索时间</b>:`{YYYY-MM-DD}`</li>`

---

## Check 9 — ≥ 3 个 callout(防止全文字段)

**期望**:至少 3 个 `<callout>` 块(TL;DR + 课题组定位 + 风险点 等)

**反模式**:
- ❌ 整篇只有 1 个 callout(TL;DR)
- ❌ 整篇 0 个 callout(全文字段)

**检测**:
```bash
rg -c '<callout'  # 期望 ≥ 3
```

**修复**:关键观察(风险点 / 数据稀疏 / 课题组定位)都用 ⚠️/💡/👥 callout 包裹。

---

## Check 10 — table 用 `<table>` + `<colgroup>`(非 markdown)

**期望**:
```xml
<table>
  <colgroup><col/><col/></colgroup>
  <thead>...</thead>
  <tbody>...</tbody>
</table>
```

**反模式**:
- ❌ `<table>|列1|列2|\n|--|--|\n|a|b|</table>`(markdown 表格在飞书 v2 不渲染)
- ❌ `<table>` 无 `<colgroup>`(v2 渲染时列宽错乱)

**检测**:
```bash
rg -A 3 '<table>' | rg -c '<colgroup>'  # 期望 table 数 = colgroup 数
```

**修复**:套用 `report-template.md §2/§6/§11` 模板,所有 table 都加 `<colgroup>`。

---

## Check 11 — 论文精读含 arXiv/DOI inline link(降级检查)

**期望**:`<a href="https://arxiv.org/abs/...">arXiv</a>` 或 `<a href="https://doi.org/...">DOI</a>`

**反模式**:
- ⚠️ 论文精读有 `(venue year)` 但**无** arXiv/DOI 链接(降级,不强制失败)
- ❌ 完全没有 `(venue year)` 标识(失败,见 Check 12)

**检测**:
```bash
rg -c 'arxiv.org/abs'  # 期望 ≥ 1(每篇精读论文 1 个)
rg -c 'doi.org'        # 备选
```

**修复**:从 S2 论文 metadata 拿 `externalIds.ArXiv` / `externalIds.DOI`,在 (venue year) 后加 `<a>` 链接。

> **v0.3.0 (2026-06-08) 注意**: 本 Check 11 在 v0.3.0 升级为 Check 13 (论文 6 行 paper card 必含 arXiv 行 + paperscool 行). 旧 v0.2.5-v0.2.9 docx 仍可保留 inline link 形式 (✅), 但升级时必须改用 paper card 6 行格式.

---

## Check 12 — Footer Persona = `claudecode teacher-report skill`

**期望**:`<p>整理人:claudecode teacher-report skill</p>`

**反模式**:
- ❌ `<p>整理人:Mavis teacher-report skill</p>`(违反 Persona 规则)
- ❌ `<p>整理人:claude teacher-report skill</p>`(用全名,违反 claudecode 简称规则)
- ❌ 完全没有 footer

**检测**:
```bash
rg '整理人' | rg -v 'claudecode'  # 期望 0 行
```

**修复**:`Mavis` → `claudecode`(见 `memory/identity-first-person.md`)

---

## 报告模板

每项检查输出格式:
```markdown
### ✅ Check N: {check name}
通过。

### ❌ Check N: {check name}
**位置**:{section / line context}
**原始片段**:`<原始 XML 或文本>`
**修复建议**:
\`\`\`xml
<期望 XML>
\`\`\`
**修复命令**(可选):
\`\`\`bash
lark-cli docs +update --api-version v2 --doc {doc_id} --command replace \\
  --match "{原始字符串}" \\
  --replace "{修复字符串}"
\`\`\`
```

## 总览格式

```markdown
## 总览
- 14 项检查: ✅ X / ❌ Y / ⚠️ Z (v0.3.0 起 12 → 13 加 Check 13 paper card; v0.4.0 起 13 → 14 加 Check 14 h2 紧邻 h3)
- 合规度:{百分比}%
- 关键问题:{最严重的 1-2 项}
```

## 限制

- **不抓新数据** — 只读现有 docx
- **不验证内容正确性** — 不检查数据真伪(如 h-index 是否过期)
- **不比对历史版本** — 单一快照,不做 diff
- **不直接修复** — 只报问题,user 决定是否 overwrite

## Check 13 — 论文 6 行 Paper Card 格式 (2026-06-08 v0.3.0 新增 → 2026-06-10 v0.3.9 强化)

> **🚨 背景**:v0.3.0 强制所有论文条目用 6 行 paper card 格式 (verbatim 标题 + 全作者列表 + **v0.3.9 强化: 全作者中文括注** + 发表 venue/year/角色 + arXiv URL + paperscool URL). 旧 v0.2.5-v0.2.9 的紧凑 `<p><b>{title} (venue year) ⭐</b></p>` 格式 **DEPRECATED**. **v0.3.9 强化**: 不仅 Fei Wu,所有作者均需 `Name（中文名）` 格式,外籍作者保留英文.

**期望**: 每篇论文均含以下 6 行 (顺序固定, 空行不算):

```
{论文标题 (verbatim, 通常是 h4 bold 段)}
{空行}作者：{空行}
{完整作者列表, 含 v0.3.9 全作者中文括注, 例: Nan Chen（陈楠）, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He（何炳生）, Rizal Fathony, Jun Hu（胡军）, Jia Chen（陈佳）}
{空行}发表：{venue} {year} ({角色})
{空行}arXiv：https://arxiv.org/abs/{id}
{空行}paperscool：https://papers.cool/arxiv/{id}
```

**反模式 (v0.3.0 + v0.3.9 全部 ❌)**:
- ❌ `<p><b>{title} (venue year) ⭐</b></p>` (v0.2.5 紧凑格式, DEPRECATED)
- ❌ `<h4>{title}</h4><p>Authors: ... (et al.)</p>` (作者 et al. 缩写, 缺中文 标注)
- ❌ **v0.3.9 新增**: `Nan Chen, Zemin Liu（刘泽民）, Bryan Hooi, Bingsheng He, Rizal Fathony, Jun Hu（胡军）, Jia Chen` ← 部分作者漏中文括注
- ❌ **v0.3.9 新增**: 仅 Fei Wu（吴飞）单独标,其他作者无 `（中文名）` (违反 v0.3.9 强一致性)
- ❌ 缺 `作者：` / `发表：` / `arXiv：` / `paperscool：` 任一前缀
- ❌ arXiv URL 缺 `https://arxiv.org/abs/{id}` 完整格式
- ❌ 缺 `paperscool：` 行 (user 失去 1-click 阅读入口)
- ❌ Fei Wu 漏 `（吴飞）` 中文标注 (即使 Fei Wu 是第 1 作者)

**检测命令**:
```bash
# 13a: 论文条目 ≥ 6 行结构
rg -c '作者：' | xargs -I{} echo "author count: {}"  # 期望 = 论文数
rg -c '发表：' | xargs -I{} echo "venue count: {}"   # 期望 = 论文数
rg -c 'arXiv：' | xargs -I{} echo "arxiv count: {}"  # 期望 = 论文数
rg -c 'paperscool：' | xargs -I{} echo "paperscool count: {}"  # 期望 = 论文数
# 13c: Fei Wu 中文标注
rg 'Fei Wu' | rg -v '（吴飞）' | wc -l  # 期望 0
# 13d: arXiv URL 完整
rg -c 'arxiv.org/abs'  # 期望 = 论文数 (含 https://)
# 13e: paperscool URL 完整
rg -c 'papers.cool/arxiv'  # 期望 = 论文数
```

**5 子项 (a-e) 全 ✅ 才算 Check 13 PASS; 任一 ❌ = Check 13 FAIL**:
- ✅ Check 13a: 4 前缀齐 (`作者：` `发表：` `arXiv：` `paperscool：`)
- ✅ Check 13b: 6 行结构 (含标题 + 5 字段, 允许空行)
- ✅ Check 13c: Fei Wu 全部有 `（吴飞）` 标注
- ✅ Check 13d: arXiv URL 完整
- ✅ Check 13e: paperscool URL 完整

**修复**: 旧 v0.2.5 docx 升级, 推荐按 paper 块逐个 `block_replace`:

```bash
lark-cli docs +update --api-version v2 --doc {doc_id} --command block_replace \
  --block-id {old_paper_block_id} \
  --content "<new paper card 6-line block>"
```

**报告模板新增 Check 13 段落**:

```markdown
### ❌ Check 13: 论文 6 行 paper card 格式
**位置**: §4 论文产出全景 — rows 3, 7, 12 (举例)
**原始片段**:
\`\`\`xml
<h4>1. OS Agents: A Survey on MLLM-based Agents for General Computing Devices Use (ACL 2025 Oral) ⭐</h4>
\`\`\`
**失败子项**: 13a (缺 4 字段前缀) + 13b (非 6 行结构) + 13c (Fei Wu 漏中文标注) + 13d/e (缺 arXiv / paperscool URL)
**修复建议**:
\`\`\`xml
<h4>1. OS Agents: A Survey on MLLM-based Agents for General Computing Devices Use</h4>
<p>作者：</p>
<p>Xueyu Hu, ..., Fei Wu（吴飞）</p>
<p>发表：ACL 2025 (Oral)</p>
<p>arXiv：<a href="https://arxiv.org/abs/2508.04482">https://arxiv.org/abs/2508.04482</a></p>
<p>paperscool：<a href="https://papers.cool/arxiv/2508.04482">https://papers.cool/arxiv/2508.04482</a></p>
\`\`\`
```

## 已知反例(2026-06-05 之前的 4 docx)

| doc_id | 失败项 | 已修复? |
|--------|--------|---------|
| HpyNdN2s2oiy7xxhXumcEKr3nHO (吴飞) | Check 4, 5, 6, 13 (v0.3.0) | ⏳ v0.3.0 待办 (2026-06-08) |
| J35xdiI04oeQEUxhRajc8QJmnLd (况琨 v0.2.2) | Check 2 (中文数字) | ✅ v0.2.5 overwrite |
| DnlbdntvNoiUTexclCic00ChnYe (况琨 v0.2.3) | Check 1 (缺 §2) | ✅ v0.2.5 overwrite |
| MqEzdtwcso2AGyxUPuCcyQRAnwe (况琨 v0.2.4) | None | ✅ 原本就 OK |
| WBLvdxoFCokxmLxSU27cxIxjnSe (dashboard) | Check 12 (Persona) | ✅ v0.2.5 清理 |

详见 `references/normalization-audit-2026-06-05.md`.

## v0.3.0 (2026-06-08) 升级清单

| 文件 | 变更 |
|------|------|
| `SKILL.md` | +新增 `## Paper Entry Format (v0.3.0) — 硬要求` 章节; Output contract 引用新格式; description 标注 v0.3.0 |
| `references/report-template.md` | §5.0 标 DEPRECATED; 新增 §5.1 6 行 paper card 模板 + 反例 + 迁移命令 |
| `references/llm-prompt.md` | §8 套磁信章节加 paper card 硬要求; 检查清单加 v0.3.0 自检项 |
| `references/audit-checklist.md` | Check 11 升级说明; 新增 Check 13 (5 子项 a-e) + Check 14 (h2 紧邻 h3); 总览从 12 项 → 13 → 14 项 |
| (user 已发布 docx) | v0.2.5-v0.2.9 docx 跑 audit mode (Check 13) 会标 ❌; 修复用 `block_replace` 逐 paper 升级 |

## Check 14 — h2 必须紧邻自家 h3 (2026-06-10 v0.4.0 新增, 来源 邓舒敏 v0.3.5→v0.4.0 case)

> **来源**: 2026-06-10 邓舒敏 wiki doc fix. v0.3.5 generator 把 5 个 h2 集中放在 doc 开头, 然后才接 body — 飞书渲染时 5 个空 § 标题连排 + body 顺序错乱 (§5 body 突然出现), 用户看到"重复一轮又一轮".
>
> **硬规则**: h2 必须在它 h3 子节之前出现, 禁止 5 个 h2 集中 doc 开头. XML 物理顺序: `h2 1 + h3 1.x + §1 body + h2 2 + h3 2.x + §2 body + ... + h2 5 + h3 5.x + §5 body`.

### Check 14 强制审计流程 (任何 v0.4.0+ docx 必跑)

```python
import re
def check_h2_h3_order(content):
    """Returns (passed, info)."""
    h2_positions = [(m.start(), int(m.group(1))) for m in re.finditer(r'<h2[^>]*?>(\d+)\.', content)]
    h3_pattern = re.compile(r'<h3[^>]*?>(.*?)</h3>', re.DOTALL)
    h3_with_section = []
    for m in h3_pattern.finditer(content):
        text = m.group(1).strip()
        m_section = re.match(r'(\d+)\.(\d+)', text)  # N.M pattern (e.g., "1.1 基本信息")
        m_paper = re.match(r'(\d+)\.\s+\w', text)   # N. Title pattern (e.g., "1. SkillX: ...")
        if m_section:
            h3_with_section.append((m.start(), int(m_section.group(1))))
        elif m_paper:
            h3_with_section.append((m.start(), 4))  # v0.4.0 paper cards belong to §4

    if not h2_positions:
        return (False, 'no h2 found')

    # Check 1: 5 h2 集中 doc 前 5% (warning)
    if len(h2_positions) >= 5:
        first_5_h2_range = max(h2[0] for h2 in h2_positions[:5]) - min(h2[0] for h2 in h2_positions[:5])
        doc_len = len(content)
        if first_5_h2_range < doc_len * 0.05:
            return (False, f'❌ 5 h2 集中 doc 前 5% ({first_5_h2_range} bytes in first {doc_len*0.05:.0f} bytes)')

    # Check 2: each h2 must come BEFORE its h3s (positional)
    for h2_pos, h2_num in h2_positions:
        h3_with_same_num = [pos for pos, num in h3_with_section if num == h2_num]
        if h3_with_same_num and min(h3_with_same_num) < h2_pos:
            return (False, f'❌ h2 {h2_num} at {h2_pos} appears AFTER its h3 at {min(h3_with_same_num)}')

    return (True, '✅ h2/h3 顺序正确 (h2 紧邻自家 h3)')
```

### Check 14 失败处理 (强制 block-level 修复)

| 失败场景 | 必做动作 |
|----------|---------|
| 5 h2 集中 doc 前 5% | 跑 `python3 reorder_dengshumin_v040_h2.py` 重排 XML (h2 散开), 然后 `lark-cli docs +update --command overwrite` |
| h2 N 出现在 h3 N.x 之后 | 跑同样 reorder 脚本, h2 提到 h3 紧前 |
| h2 数量 < 5 | 缺 § 章节, 加缺失 h2 + body |
| 同一 § 含 2 个 h2 (e.g., h2 1 + h2 1) | 重复 § 标题, 删除多余 h2 + 紧邻 body |

### Check 14 反例 (v0.3.5 generator bug 实测)

```xml
<!-- ❌ 错误: 5 h2 集中 + body 全部接在后面 -->
<h2>1. 导师画像</h2><h2>2. 匹配度</h2><h2>3. 套磁</h2><h2>4. 论文</h2><h2>5. 数据源</h2>
<h3>5.1 ...</h3> ... <h3>5.3 ...</h3>
<h3>1.1 ...</h3> ... <h3>1.3 ...</h3>
<h3>2.1 ...</h3> ...
<h3>3.1 ...</h3> ...
<h3>1. SkillX...</h3> ... <h3>12. WKM...</h3>

<!-- ✅ 正确: h2 紧邻 h3 -->
<h2>1. 导师画像</h2>
<h3>1.1 基本信息</h3>
<p>...</p>
<h3>1.2 学术谱系</h3>
...
<h2>2. 匹配度</h2>
<h3>2.1 ...</h3>
...
```

### Check 14 总览 (v0.4.0 起 13 → 14 项)

- **Check 1-12**: v0.2.5 / v0.3.0 / v0.3.9 章节 + Persona + 9 项回归
- **Check 13**: 6 行 paper card 格式 (v0.3.0 → v0.3.9 强化)
- **Check 14**: h2 紧邻自家 h3 (2026-06-10 v0.4.0 新增, 防 5 h2 集中 doc 开头导致飞书渲染异常)
