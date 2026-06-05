# Audit Checklist — 12 项合规检查 (v0.2.8+)

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

## Check 2 — h2 标题用 `1.` `2.` `3.` 风格(无中文数字)

**期望**:`<h2>1. 导师与课题组画像</h2>`

**反模式**:
- ❌ `<h2>一、导师与课题组画像</h2>`(中文数字)
- ❌ `<h2>第1章 导师画像</h2>`(无编号或前缀)
- ❌ `<h2>1.1 课题组定位</h2>` (h2 用了 h3 风格,层级错)

**检测**:
```bash
rg -o '<h2>[^<]+</h2>' | rg -v '^[0-9]+\. '
```

**修复**:
```
<h2>1. 导师与课题组画像</h2>     ← 期望
<h2>一、导师与课题组画像</h2>   ← 改成上面
```

---

## Check 3 — h3 标题用 `1.1` `1.2` 子节风格

**期望**:`<h3>1.1 基本信息</h3>` / `<h3>2.3 论文精读</h3>`

**反模式**:
- ❌ `<h3>基本信息</h3>`(无编号)
- ❌ `<h3>1. 基本信息</h3>`(用了 h2 风格,层级错)

**检测**:
```bash
rg -o '<h3>[^<]+</h3>' | rg -v '^[0-9]+\.[0-9]+ '
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
- 12 项检查: ✅ X / ❌ Y / ⚠️ Z
- 合规度:{百分比}%
- 关键问题:{最严重的 1-2 项}
```

## 限制

- **不抓新数据** — 只读现有 docx
- **不验证内容正确性** — 不检查数据真伪(如 h-index 是否过期)
- **不比对历史版本** — 单一快照,不做 diff
- **不直接修复** — 只报问题,user 决定是否 overwrite

## 已知反例(2026-06-05 之前的 4 docx)

| doc_id | 失败项 | 已修复? |
|--------|--------|---------|
| HpyNdN2s2oiy7xxhXumcEKr3nHO (吴飞) | Check 4, 5, 6 | ✅ v0.2.5 overwrite |
| J35xdiI04oeQEUxhRajc8QJmnLd (况琨 v0.2.2) | Check 2 (中文数字) | ✅ v0.2.5 overwrite |
| DnlbdntvNoiUTexclCic00ChnYe (况琨 v0.2.3) | Check 1 (缺 §2) | ✅ v0.2.5 overwrite |
| MqEzdtwcso2AGyxUPuCcyQRAnwe (况琨 v0.2.4) | None | ✅ 原本就 OK |
| WBLvdxoFCokxmLxSU27cxIxjnSe (dashboard) | Check 12 (Persona) | ✅ v0.2.5 清理 |

详见 `references/normalization-audit-2026-06-05.md`。
