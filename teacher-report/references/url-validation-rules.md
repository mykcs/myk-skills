# teacher-report URL 验证硬规则 (v0.4.0+ 下沉)

> **来源**: 从 SKILL.md v0.3.9 (2026-06-10) 拆分（v0.4.0 progressive disclosure refactor, 2026-06-10）。
> **目的**: 强约束 URL 验证规则集 (arXiv / papers.cool / Wiki / 通讯作者交叉验证等)。
> **加载时机**: 准备生成 paper card 前必查 / 套磁信引用具体论文时 / 审计合规检查时。

---

## 🚨 URL 验证硬规则 (2026-06-09 写入, 违反 = skill 协议破坏)

> **反模式案例**: 张圣宇 (Shengyu Zhang) doc 写了 `https://person.zju.edu.cn/shengyu` (404, LLM 瞎编), exa 实查发现真 URL 是 `https://person.zju.edu.cn/shengyuzhang` (200) — `pinyin` 不是简单的名字拼接, 浙大用 `shengyuzhang` (全名连续), 不是 `shengyu` 或 `syzhang` 或 `zhangshengyu` 或 `zhangsy`.
>
> **Why**: ZJU `person.zju.edu.cn/{pinyin}` 模板的 `{pinyin}` 是学校分配的**用户自定义 slug**, 不是系统从中文名生成的. 不同老师 slug 命名习惯差异巨大:
> - 沈春华 → `chunhua` (名 only)
> - 赵洲 → `zhaozhou` (姓+名连拼)
> - 张圣宇 → `shengyuzhang` (全名连续)
> - 英文版可能是 ID 数字: `en/NB23073`
>
> **LLM 瞎编的 URL 模式** (实测全部 404): `{pinyin}` / `{surname}{given}` / `{given}{surname}` / `{initial}{surname}` / `{name_en}` 等. **没有任何 LLM 推断能保证正确**, 必须 HTTP HEAD 验证.

### 强制流程 (改/写任何 L1 官网 URL 前必跑)

1. **HTTP HEAD 验证**: `curl -I --max-time 10 "{candidate_url}"` 或 python `urllib.request.Request(method="HEAD")`
2. **200 OK** → URL 可用
3. **404 / 403 / 0** → URL 错, **禁止写入 docx**, 立即走 L4 (MiniMax web_search) 或 exa web_search 搜 "{老师姓名} {学校} personal homepage" 找真 URL
4. **找到真 URL 后** → 再跑一次 HTTP HEAD 验证, 200 OK 才写入

### 反例 (2026-06-09 真实案例, 已被用户发现)

| 老师 | LLM 编的 URL | HTTP HEAD | 真实 URL (exa 搜出) | HTTP HEAD |
|------|-------------|-----------|---------------------|-----------|
| 张圣宇 | `https://person.zju.edu.cn/shengyu` | 404 ❌ | `https://person.zju.edu.cn/shengyuzhang` | 200 ✅ |
| (其他误例) | `https://person.zju.edu.cn/en/shengyu` | 404 ❌ | `https://person.zju.edu.cn/en/NB23073` (ID 数字) | 200 ✅ |
| 沈春华 | `https://person.zju.edu.cn/en/chunhua` | 200 ✅ | (同上, 已是真实 URL) | 200 ✅ |
| 赵洲 | `https://person.zju.edu.cn/zhaozhou` | 200 ✅ | (同上, 已是真实 URL) | 200 ✅ |

### 找真实 URL 的 LLM 友好顺序

1. **L4 MiniMax web_search**: `"{中文名}" {学校} 个人主页` 或 `"{英文名}" {学校} personal homepage`
2. **exa web_search_exa**: 同上
3. **OpenReview / Google Scholar 个人主页** 字段: 经常含真 URL
4. **学院教师列表页** (e.g. `cs.zju.edu.cn` / `ai.zju.edu.cn` faculty) — 链接通常是真 slug

### 自检 (写入 docx 前)

每个 L1 官网 URL 必跑:

```python
import urllib.request
def head_check(url, timeout=10):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "teacher-report-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except: return 0
assert head_check(URL) == 200, f"URL {URL} 验证失败 ({head_check(URL)}), 禁止写入 docx"
```

### 已知反模式

- **❌ LLM 拼 pinyin**: `shengyu` / `zhangshengyu` / `syzhang` / `zhangsy` / `zs` / `zsy` 等 6+ 种组合, 实测**全 404** (除真实 slug)
- **❌ 抄 OpenReview / Scholar `Homepage` 字段** 不验证: 这些字段可能过期或指向旧 institution
- **❌ 拿学院列表页** (e.g. `cs.zju.edu.cn/2024/0315/c64945a123.html`) 当个人主页: 列表页 ≠ 个人主页

### 扩展应用 (除 ZJU 外)

此规则适用于**所有**学校官网, 不限于 ZJU:
- 清华: `scholar.tsinghua.edu.cn/{slug}`
- 上交: `faculty.sjtu.edu.cn/{slug}`
- 北大: `scholar.pku.edu.cn/{slug}`
- 所有 slug 都必须 HTTP HEAD 验证, 不可 LLM 推断

**Data the model should NOT make up**: student names, h-index, paper counts, CCF tier. If a fact is unverifiable from fetched sources, write `[待验证]` in the report and note it in `5. 数据来源`.

### Step 2 — LLM synthesis (in-conversation, not external API)

You are the LLM. Use the fetched data to produce a structured dossier. Read `references/llm-prompt.md` for the synthesis prompt and `references/report-template.md` for the target XML schema.

**Output of this step**: a single XML string (lark-doc v2 format) ready to pass to `lark-cli docs +create`.

**Synthesis rules**:
- **TL;DR callout** must be ≤ 6 lines per column. Numbers must come from L2/L3 data, not vibes.
- **方向匹配度** must reference the user's stated direction (or "通用 CV/ML/Agent" default). Score per direction with a one-line rationale.
- **套磁邮件草稿** must cite 1-2 specific papers from the fetched list (with venue + year). Generic flattery is forbidden.
- **风险点** must be fact-based: 方向变化、招生名额信息缺失、实际带生者不确定等可证伪的判断。
- If data is sparse, mark sections as `🟡 数据待补` rather than fabricating.

### Step 3 — Write to Feishu

**🚨 硬要求(2026-06-05 v0.2.4)**:每位老师报告**必须**出现在用户的"申博 wiki"里。三种模式,按用户输入(Inputs §5 §6)分支:

#### 模式 A — 提供 wiki parent + dashboard(完整 wiki 集成)
```bash
# 1. 创建子 docx(作为 wiki parent 的子页)
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "<skeleton>" \
  --parent-token {WIKI_PARENT_TOKEN}

# 2. append 章节到子 docx
lark-cli docs +update --command append --content "<section-X>" --doc {child_doc_id}

# 3. append 摘要到 dashboard wiki 节点(让 user 在一个地方看到所有候选老师)
lark-cli docs +update --command append --content "<dashboard-摘要>" --doc {WIKI_DASHBOARD_TOKEN}
```

#### 模式 B — 只提供 dashboard
```bash
# 1. 报告仍 create 到 my_library(独立 docx,user 可手动归档)
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "<skeleton>" \
  --parent-position my_library

# 2. append 章节
lark-cli docs +update --command append --content "<section-X>" --doc {child_doc_id}

# 3. append 摘要到 dashboard(让 user 在 dashboard 看到链接)
lark-cli docs +update --command append --content "<dashboard-摘要>" --doc {WIKI_DASHBOARD_TOKEN}
```

#### 模式 C — 都没提供(legacy 兼容)
```bash
# 直接 create 到 my_library,不 append 到 dashboard
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "<skeleton>" \
  --parent-position my_library

# append 章节(同上)
```

> 摘要模板见 `report-template.md` § 11 申博 wiki dashboard 摘要。

If the doc body is > 30 blocks, split: create with skeleton (title + headings + TL;DR callout only), then `lark-cli docs +update --api-version v2 --doc {doc_id} --command append` per section. This avoids the v2 single-call content-size limit and makes failures recoverable.

Capture the returned `data.document.url` — this is what the user gets.

### Step 4 — Return + handoff

Reply to the user with:
1. The docx URL
2. A 1-line "建议下一步": 套磁信草稿可直接 copy / 添加到知识库得 wiki 链接 / 等等
3. If any section was `🟡 数据待补`, list the specific gaps so the user can补

### Rewrite mode (v0.3.4+ 新增) — 详细流程

> **入参必填**:docx URL / token + user 显式指令(触发词匹配)
> **输出**:overwrite 后的新 docx URL + diff summary

**Step R1 — Fetch 现状**
```bash
lark-cli docs +fetch --api-version v2 --doc {doc_id} --detail with-ids
```
提取:
- docx content(完整 XML)
- revision_id(基线版本,后续用 --revision-id -1)
- 已知 paper cards 位置(用于 dedup)

**Step R2 — 解析当前内容**
按 section 拆解(基于 5 章结构):
- §1 TL;DR callout: 保留(若合规)
- §2 申博匹配度: 重写为 5 维度,每维度引用 paper card
- §3 套磁与行动建议: 重写套磁信,引用 1-2 篇 paper card
- §4 论文产出全景: **整段重写**——按 v0.3.3 paper card 格式重组,删除 v0.3.0 compact 残留
- §5 数据来源: 更新为 4-level 数据源(L1/L2/L3 + 新 L4 MiniMax / L5 Kimi / L6 AnySearch)

**Step R3 — 抓取真实论文数据**
对 §4 每篇论文:
1. L4 MiniMax: `mcp__MiniMax__web_search` 搜 `"{title}" arxiv`
2. L5 Kimi WebBridge(若 L4 失败):浏览器打开 arxiv.org/abs/{id} 拿完整 byline
3. L6 AnySearch(若 L4/L5 失败):搜 `"{title}" filetype:pdf` 拿 PDF 链接 + 摘要
4. fallback: **见 §F v0.3.7 强化协议** (二选一: a) 触发 L4/L5/L6 重抓; b) L4/L5/L6 全失败 → 拒绝输出 paper card,标 `🟡 跳过: {arxiv-id} 数据不全`)**禁止**用 `[待 L4/L5/L6 重抓]` placeholder 提交 final doc

**Step R4 — 生成 v0.3.3 全量 XML**
按 `Output Schema (v0.3.3 strict)` 章节的 fixed-template,11-12 个 block/论文,顺序固定。

**Step R5 — 跑 12 项 LLM 自检**
(详见 `Output Schema (v0.3.3 strict)` 章节)
- 任一 ❌ 必修正后重跑
- 全 ✅ 后才能 overwrite

**Step R6 — Overwrite**
```bash
lark-cli docs +update --api-version v2 --doc {doc_id} --command overwrite \
  --content @/tmp/rewrite-{doc_id_short}.xml
```

**Step R7 — Verify + Diff Summary**
```bash
lark-cli docs +fetch --api-version v2 --doc {doc_id} --scope outline
```
输出 diff summary:
- 5 章节是否齐全(各 1 个 <h2> 标题)
- paper card 数量(旧 vs 新)
- 4 行 taxonomy 覆盖率
- 完整作者列表覆盖率
- arXiv URL 真实率(目标:100%)

**Step R8 — Reply**
```
[X] 报告按 v0.3.3 fixed-template 重写完成:
- 删除了 N 条 v0.3.0 compact 残留
- 重写了 M 条 paper card(完整作者 + 单独标注行)
- L4 MiniMax 抓取 K 论文(arXiv 真实 URL 100%)
- L5 Kimi 补全 J 论文(完整 byline)
- L6 AnySearch 补全 L 论文(PDF 链接)

⚠️ [仍有 G 条占位,需手动补]: {title list}
🔗 新 docx URL: {url}
```

**Rewrite mode 风险控制**:
- **必先 user-confirm** 列出:"会删原 §4 重写,论文数据全部走 L4/L5/L6 重抓,4-5 分钟。OK 吗?" → user 回复"是"才执行
- 不 rewrite 不相关的 docx(只 rewrite user 提供的 URL)
- backup: rewrite 前先 `cp` 旧 docx 到 `/tmp/wiki-audit/backup-rewrite-{date}/`


### Audit mode (v0.2.8+) — 审计已有 docx

> **用途**:对**已发布**的 Feishu docx 跑 v0.2.5+ 合规检查,识别"(1) ② ████"等反模式 + TL;DR 缺失 + Persona 违规,输出修复建议。
>
> **不写飞书,只读飞书**。审计完成后,user 决定是否 overwrite 修复。

#### Audit 触发模式

| 用户输入 | 模式 |
|---------|------|
| `审计一下 https://xxx.feishu.cn/docx/MqEz...` | Audit mode |
| `看看 况琨 报告合不合规` + 已知 doc_id | Audit mode |
| `teacher-report audit MqEzdtwcso2AGyxUPuCcyQRAnwe` | Audit mode |
| `review teacher report compliance for MqEz...` | Audit mode |
| `调研一下 XXX 老师` | Generation mode(忽略 audit) |

#### Audit 流程(4 步)

**Step A1 — Fetch 现状**

```bash
lark-cli docs +fetch --api-version v2 --doc {doc_id}
```

提取 `data.document.content` (XML 字符串)。如果 fetch 失败:
- `LARK_USER_AUTH_REQUIRED` → 提示 user 跑 `lark-cli auth login`
- `404` / doc not found → 提示 user 检查 doc_id
- 其他错误 → 报原始错误,不要重试

**Step A2 — 跑 12 项合规检查**

详见 `references/audit-checklist.md`。每项输出 ✅ / ❌ + 失败时附原始片段。

| # | Check | Hard rule 引用 |
|---|-------|---------------|
| 1 | h2 章节为 5 个(顺序:TL;DR / 画像 / 匹配 / 套磁 / 论文 / 来源) | Output contract |
| 2 | h2 标题用 `1.` `2.` `3.` `4.` `5.` 风格 | SKILL.md 飞书标题号硬规则 |
| 3 | h3 标题用 `1.1` `1.2` 等子节风格 | 同上 |
| 4 | 无 h4 手动 `(1) (2) (3)` 编号 | 同上 |
| 5 | 无内联 `① ② ③` 字符 | 同上 |
| 6 | 无 `████████` 字符画趋势图 | 同上 |
| 7 | TL;DR 用 callout + grid | report-template.md §1 |
| 8 | §5 数据来源含检索时间 | report-template.md §9 |
| 9 | ≥ 3 个 callout(全文字段不算) | report-template.md 视觉丰富度 |
| 10 | table 用 `<table>` + `<colgroup>`(无 markdown table) | llm-prompt.md 反模式 |
| 11 | 论文精读含 arXiv/DOI link(无则降级) | llm-prompt.md §8 |
| 12 | Footer Persona = `claudecode teacher-report skill` | report-template.md §9 |

**Step A3 — 生成审计报告**

写到 `/tmp/teacher-report-audit-{name}-{doc_id_short}.md`,格式:

```markdown
# 审计报告 — {老师}({doc_id_short})
审计时间: {YYYY-MM-DD HH:MM}
docx URL: {url}

