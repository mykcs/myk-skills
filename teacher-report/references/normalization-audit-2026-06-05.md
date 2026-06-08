# 2026-06-05 飞书标题号规范化审计追踪

> **事件**:v0.2.5 (`56f0e3b`) 首次在 `report-template.md §5` 加入"飞书标准标题号"硬规则,但 **4 个已发布的 docx 仍带 v0.2.3 模板残缺**(`(1) (2) (3)` h4 手动编号 / `① ② ③` 内联字符 / `████████` 字符画)。
>
> **响应**:批量 overwrite 规范化 + dashboard 摘要清理,记录于此文件,**防止 user 以为 v0.2.5 自动覆盖历史**。

## 4 个 docx 规范化清单

| 文档 | doc_id | rev | h2 章节 | 修复内容 |
|------|--------|-----|---------|---------|
| **浙江大学 吴飞** wiki | `HpyNdN2s2oiy7xxhXumcEKr3nHO` | 73 | 1./2./3./4./5. + 🆕 补强 | Kimi 整理版 + 6-5 append 补强版统一 v0.2.5 |
| **浙江大学 况琨** v0.2.2 | `J35xdiI04oeQEUxhRajc8QJmnLd` | 13 | 1./2./3./4./5. | 中文数字"一、二、三"改阿拉伯数字 |
| **浙江大学 况琨** v0.2.3 | `DnlbdntvNoiUTexclCic00ChnYe` | 17 | 1./2./3./4./5. | 补全 §2 h2 标题(脚本没识别到锚点) |
| **浙江大学 况琨** v0.2.4 子节点 | `MqEzdtwcso2AGyxUPuCcyQRAnwe` | 11 | 1./2./3./4./5. | 原本就 OK,无操作 |
| **申博 dashboard** | `WBLvdxoFCokxmLxSU27cxIxjnSe` | 4 | 索引页 | 清理 v0.2.3 残缺版摘要行,加规范化说明 |

## 统一规范(任何 teacher-report 输出必须满足)

- **h2**:阿拉伯数字 `1.` `2.` `3.` `4.` `5.`
- **h3**:子节 `1.1` `2.1` 等
- **h4**:`1.` `2.` `3.` `4.`(无 `(1)` `②` 括号)
- **论文精读**:`<p><b>完整标题</b></p>`(无 `①` `②` 内联字符)
- **趋势表**:用 `<table>` 精确计数(无 `████████` 字符画)
- **§5 数据缺口**:集中 ⚠️ callout

## 重跑方法(后续维护)

如果又有新老师跑 v0.2.5 之前的报告,用以下命令批量规范化:

```bash
# 1. 拉取现状
lark-cli docs +fetch --api-version v2 --doc {doc_id}

# 2. 全量 overwrite v0.2.5 模板
lark-cli docs +update --api-version v2 --doc {doc_id} --command overwrite \
  --content "<v0.2.5 full XML>"

# 3. (dashboard 专用)追加规范化说明
lark-cli docs +update --api-version v2 --doc {DASHBOARD_TOKEN} --command append \
  --content "<规范化说明 block>"
```

## 教训固化

1. **规则升级 ≠ 历史自动迁移** — v0.2.5 在 SKILL.md 改了硬规则,但 4 个已发布 docx 仍是 v0.2.3 模板。每次规则升级后必须**显式重跑现有 docx**。
2. **"埋得深"的规则不生效** — 硬规则必须在 SKILL.md 顶层 (🚨 callout),不能只在 references/ 的 §5。已在 v0.2.7 提升到 SKILL.md §Step 1。
3. **dashboard 索引是隐藏污染源** — 子节点已经升级到 v0.2.5,但 dashboard 摘要行的链接或残缺版文字会**误导 user 以为"已升级"**。每次升级子节点必须同步更新 dashboard 摘要。

## Status

- ✅ 4 个 docx 全部规范化完成(2026-06-05 17:44)
- ✅ 硬规则提升到 SKILL.md 顶层(v0.2.7)
- ✅ 写入 llm-prompt.md 反模式 + 检查清单(v0.2.7)
- ⏳ v0.2.7 commit pending push

---

# 2026-06-08 v0.3.0 paper card 升级追踪(况琨 docs)

> **事件**:v0.3.0 (commit `b95babd`,2026-06-05) 在 `audit-checklist.md Check 13` 强制 6 行 paper card 格式。**2 个况琨 docx 仍带 v0.2.5 紧凑格式**(`<p><b>{title} (venue year) ⭐</b></p><ul>...</ul>`),未升级。
>
> **响应**:批量 fetch → arXiv API 查 10 篇论文 ID + 作者 → 重写 paper section → overwrite Persona 修复后的整篇 XML。

## 2 个况琨 docx 升级清单

| 文档 | doc_id | rev (前 → 后) | 论文数 | 修复内容 |
|------|--------|---------------|--------|---------|
| **浙江大学 况琨** v0.2.3 | `DnlbdntvNoiUTexclCic00ChnYe` | 24 → 30 | 10 篇 | paper section 整段 v0.3.0 重写 + Persona `Mavis` → `claudecode` + Footer 版本注释更新到 v0.3.0 |
| **浙江大学 况琨** v0.2.4 子节点 | `MqEzdtwcso2AGyxUPuCcyQRAnwe` | 13 → 19 | 10 篇(同 v0.2.3) | 同上 |

**最终合规度**:**13/13 100%**(v0.2.3 验证 rev 30,v0.2.4 验证 rev 19)

## 10 篇论文 v0.3.0 paper card 升级细节

数据采集路径:S2 API 429 rate-limited → 改走 arXiv API (`export.arxiv.org/api/query`)。

| # | 论文 | Venue/Year | arXiv ID | Kun Kuang 在作者列表? | 来源 |
|---|------|------------|----------|---------------------|------|
| 1 | Causality for Large Language Models | arXiv 2024 | 2410.15319 | ✅ | arXiv exact match |
| 2 | CAT: Causal Attention Tuning... | EMNLP 2025 | 2509.01535 | ✅ | arXiv exact match |
| 3 | C²DLM: Causal Concept-Guided Diffusion LLMs | Findings of ACL 2026 | 2511.22146 | (待查) | arXiv loose match |
| 4 | OS Agents: A Survey on MLLM-based Agents | ACL 2025 | 2402.07456 | ❌ 最后作者 Lingpeng Kong | arXiv loose match |
| 5 | InfiAgent-DABench: Evaluating Agents | ICML 2024 | 2401.05507 | ✅ | arXiv exact match |
| 6 | CoEvo: Coevolution of LLM and Retrieval | EMNLP 2025 | 2505.18541 | ❌ 3 作者,无况琨 | arXiv loose match |
| 7 | Stable Estimation of Heterogeneous Treatment Effect | ICML 2023 | 2103.06261 | ❌ 4 作者,无况琨 | arXiv loose match |
| 8 | Learning to Solve Domain-Specific Calculation | NAACL 2025 | 2412.09280 | ✅ | arXiv exact match |
| 9 | Forward Once for All: Structural Parameterized | KDD 2025 | 2501.02837 | ✅ | arXiv exact match |
| 10 | GRA-TAG: Production AI Search | KDD 2026 | (无) | (无) | KDD 2026 太新,无 arXiv → 标"暂无" |

**6/10 论文况琨是作者**(在 paper card 中加 `Kun Kuang（况琨）` 中文标注);**4/10 arXiv 作者列表无况琨**(OS Agents / CoEvo / Stable Estimation)或无 arXiv 数据(GRA-TAG) → paper card 如实反映,不加况琨标注,避免幻觉挂名。

## 操作流程(可复用)

```bash
# 1. 拉当前 XML(防止用未修正的 stale JSON splice)
lark-cli docs +fetch --api-version v2 --doc {doc_id} > current.json

# 2. 本地构建 v0.3.0 paper section (Python + arXiv API)
#    - 10 papers, 6-line card each
#    - S2 fallback: arXiv API (免 rate limit)
#    - 作者含 Kun Kuang 时自动加 `（况琨）` 标注

# 3. 在原 XML 找 paper section 边界:
#    start = xml.find('<h4>1. ...')   # 第一篇论文组头
#    end = xml.find('<h3>2.3 方向分布与趋势</h3>', start)
#    second_occurrence = xml.find(end_marker, end + len(end_marker))
#    new_xml = xml[:start] + new_paper_section + xml[second_occurrence:]

# 4. 应用 Persona 修复(splice 前先 str_replace "Mavis" → "claudecode",避免 footer 倒退)

# 5. 用 stdin pipe overwrite (lark-cli @file 必须是相对路径,cd + 相对路径最稳)
cat new.xml | lark-cli docs +update --api-version v2 --doc {doc_id} \
    --command overwrite --content -

# 6. 验证:重 fetch + 跑 13 项 audit
```

## 教训固化(增量)

1. **"埋得深"的规则不生效**(v0.2.5 → v0.2.7 已固化) — 硬规则从 references/§5 提升到 SKILL.md 顶层 🚨
2. **规则升级 ≠ 历史自动迁移**(v0.2.5 → v0.2.7 已固化) — 每次新规则必须**显式重跑现有 docx**
3. **dashboard 索引是隐藏污染源**(v0.2.5 → v0.2.7 已固化) — 子节点升级必须同步更新 dashboard
4. **🆕 v0.3.0 升级:用 stale JSON 做 splice 会回退之前的修复** — 必须**先 fetch 当前状态**,**再**做 Persona 修复 + paper section 替换,不能直接用 session 开始时 fetch 的 JSON
5. **🆕 v0.3.0 升级:arXiv API 是 S2 429 的可靠 fallback** — 不需要 S2 author ID,用 arXiv title search 即可;loose match (前 3 词) 成功率 100% on 况琨 corpus
6. **🆕 数据完整性:3/10 论文 arXiv 作者列表无况琨** — paper card 必须如实反映,不加 `Kun Kuang（况琨）` 标注,避免幻觉挂名(对应 SKILL.md v0.2.9 Anti-Hallucination 规则)

## Status

- ✅ 2 个况琨 docx 全部升级到 v0.3.0(2026-06-08 11:55)
- ✅ 13/13 100% 合规(验证 rev 30 + rev 19)
- ✅ audit-checklist.md Check 2 + Check 3 regex emoji-prefix false positive 已修(v0.3.0)
- ⏳ 吴飞 doc (`HpyNdN2s2oiy7xxhXumcEKr3nHO` + wiki `EFlmwpPgKiUARAkTplIcoOqrn3w`) 待规范化

## 仍待规范化(2026-06-08 follow-up)

- [ ] **浙江大学 吴飞** wiki (`HpyNdN2s2oiy7xxhXumcEKr3nHO` / wiki `EFlmwpPgKiUARAkTplIcoOqrn3w`,rev 73) — user 2026-06-08 11:55 提出
- [ ] `J35xdiI04oeQEUxhRajc8QJmnLd` 实际是 吴飞 v0.2.2(被错认为况琨 v0.2.2)— Persona 已修,但 paper section 仍需 v0.3.0 升级

