---
name: teacher-report
description: |
  Generate a PhD advisor / professor intelligence dossier as a Feishu wiki doc (Docx). Use when the user mentions a specific researcher / advisor / 老师 / 导师 and asks to "调研 / 写一份报告 / 整理材料 / 看看这位老师" — output is a structured 5-section report (TL;DR / 导师画像 / 方向匹配度 / 套磁建议 / 论文全景) ready to share. Triggers on phrases like "调研一下 XXX", "生成 XXX 老师的报告", "看看张三是不是值得报", "写一份老师材料", "PhD advisor report for XXX". Do NOT use for: batch-processing many teachers (that's `phd-scout` which writes to Bitable), single paper deep-dive, lab research summary, or collecting a teacher into a structured Bitable row.
---

# Teacher Report

Generate a single-advisor PhD dossier in Feishu wiki doc format. Input: a researcher name (optionally with university / school). Output: a Feishu `docx` URL that the user can move to a wiki node.

## Inputs to collect

Before fetching, confirm or infer the following from the user's message:

1. **老师姓名** (required) — full Chinese name or Pinyin. If ambiguous (common name + no university), ask the user.
2. **学校** (strongly recommended) — disambiguates homonyms and lets L1 (university site) work. If missing, infer from context or ask.
3. **学院 / 系** (optional) — narrows L1 search.
4. **用户的研究方向 / 匹配诉求** (optional) — used in the 方向匹配度 section to score fit. If user didn't say, write a generic "通用 CV/ML/Agent" profile and note "无特定方向假设" in the report.

If 1 + 2 are both missing, do NOT start fetching — ask the user.

## Procedure

### Step 1 — Data fetching (4-level fallback)

Try sources in this order. Stop when a source yields enough signal; you do not need all four.

| Level | Source | How to query | What to extract |
|-------|--------|-------------|----------------|
| L1 | 学校/学院官网 | `webfetch` or `playwright` on `{university}.edu.cn/{school}/{name}` patterns. ZJU common patterns: `person.zju.edu.cn/{pinyin}`, `mypage.zju.edu.cn/{pinyin}`, `cs.zju.edu.cn` faculty page | 基本信息、职称、行政职务、联系方式、研究方向、代表性工作 |
| L2 | Semantic Scholar API | `https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,affiliations,paperCount,hIndex,homepage` then `/author/{id}/papers?fields=title,year,venue,citationCount,authors&limit=100` | 论文清单（近 3 年）、h-index、合作者 |
| L3 | DBLP | `https://dblp.org/search/author/api?q={name}&format=json` then `/pid/{pid}.xml` for full paper list | 论文 venue 验证、CCF-A/B 标注 |
| L4 | 个人主页 / 知乎 / Google Scholar | `web_search` for `"{name}" {university} site:{personal_domain}` or `"{name}" scholar profile` | 个人 CV、学生名单、研究亮点 |

L2 (Google Scholar) is intentionally **skipped** in mainland-China network environments — go L2 Semantic Scholar → L3 DBLP → L4 directly.

If L1 fails (e.g., personal page 404 or 动态加载), continue to L2 — the data is still salvageable.

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

```bash
# Write the synthesized XML to a temp file (avoids shell quoting hell)
cat > /tmp/teacher-report-{name}.xml <<'XML_EOF'
<title>...</title>... (full XML)
XML_EOF

# Create the doc
lark-cli docs +create --api-version v2 \
  --title "{学校} {老师}" \
  --content "$(cat /tmp/teacher-report-{name}.xml)" \
  --parent-position my_library
```

If the doc body is > 30 blocks, split: create with skeleton (title + headings + TL;DR callout only), then `lark-cli docs +update --api-version v2 --doc {doc_id} --command append` per section. This avoids the v2 single-call content-size limit and makes failures recoverable.

Capture the returned `data.document.url` — this is what the user gets.

### Step 4 — Return + handoff

Reply to the user with:
1. The docx URL
2. A 1-line "建议下一步": 套磁信草稿可直接 copy / 添加到知识库得 wiki 链接 / 等等
3. If any section was `🟡 数据待补`, list the specific gaps so the user can补

## Output contract

- **Primary**: a Feishu `docx` URL (looks like `https://{tenant}.feishu.cn/docx/doxcn...`)
- **Document title**: `{学校} {老师姓名}` (e.g. "浙江大学 吴飞")
- **5 required sections in order**: TL;DR callout, 导师与课题组画像, 申博匹配度评估, 套磁与行动建议, 论文产出全景（按年）, 数据来源与说明
- **Visual elements required**: 1 TL;DR callout + 1 grid, ≥ 1 callout per section for non-text observations, all data tables formatted as `<table>` blocks (not markdown)

## Failure handling

| Failure | What to do |
|---------|------------|
| L1-L4 all return nothing | Stop, tell the user "信息黑洞 — 五级抓取都失败,建议手动提供主页 URL 或姓名 + 单位"。Do not fabricate. |
| Personal page exists but is JS-rendered SPA | Use `playwright` MCP `browser_navigate` → `browser_snapshot` to get rendered text. Avoid `webfetch` on SPAs. |
| L2 Semantic Scholar rate-limited (429) | Wait 5s, retry once. If still 429, skip to L3 DBLP. |
| User has not enabled lark-cli auth | The `docs +create` call will return `LARK_USER_AUTH_REQUIRED`. Tell the user to run `lark-cli auth login` and retry. |
| LLM output exceeds `--content` size limit | Split into skeleton + appends per Step 3. |
| Same teacher fetched twice with different results | Trust L2 (Semantic Scholar) h-index + paperCount over L1 self-claimed numbers. Note both in `5. 数据来源`. |
| User asks for many teachers at once | Out of scope — defer to `phd-scout --mode batch`. Only one teacher per `teacher-report` run. |

## Examples

### Example 1 — single, full data
- Input: "调研一下浙江大学计算机学院的吴飞老师,看适不适合申博"
- Fetch: L1 (ZJU 主页) → L2 (S2 API 50+ papers) → L3 (DBLP) → L4 (kunkuang.github.io for 况琨 context)
- Output: docx URL with 5 sections, TL;DR shows 🟢 高匹配, 论文按 2023-2026 分年展示

### Example 2 — sparse data
- Input: "看看清华的 XXX 副教授"
- Fetch: L1 404, L2 returns 12 papers, L3 returns 8 (overlap with L2), L4 returns a stale personal page from 2019
- Output: docx URL with TL;DR showing 🟡 数据待补, `5. 数据来源` explicitly says "L1 抓取失败,依赖 L2+L3 共 8 篇去重论文"

## References

- `references/report-template.md` — 飞书 docx XML 模板 (TL;DR callout / 5 章节结构)
- `references/data-sources.md` — L1-L4 抓取细节 + ZJU URL 模式 + S2 API 字段
- `references/llm-prompt.md` — 总结 prompt (synthesis rules + 章节填充指引)
