# Skill Evolution Log

Records every v-bump from `/skill-evolution` (auto) or manual change.

Format: `<ts> | <skill> | v<old>→v<new> | reason | M=<before> M'=<after>`

## 2026-06-03 — Initial setup

This file was created as part of the `/skill-evolution` v1.0.0 bootstrap.
The skill itself + cron stub at `~/.claude/scripts/run-skill-evolution.sh`
were added in the same change set.

Pending: actual evolution runs require the user to invoke
`/skill-evolution` interactively in a Claude session (the cron stub
only logs a reminder).

## 2026-06-04 — Manual run, REJECTED (no-op)

| ts | skill | verdict | reason |
|----|-------|---------|--------|
| 2026-06-04T11:35:00+08:00 | website-improve | REJECTED | Top cluster `cross-repo-owner-drift` (27 events) already covered by v3.3.0 §31 (commit 5662d4a 2026-06-03). All other clusters target skills bumped <7d ago. Churn rule "每月最多 1 次/skill" applies. |

- Case: `~/.claude/knowledge/cases/CASE-SKILL-EVOLUTION-20260604.md`
- Friction data: `/tmp/skill-evolution-20260604/friction-clusters.json`
- Sessions analyzed: 11
- Friction events: 118 (4 audit-log + 114 jsonl)
- Clusters: 12
- Action: NONE (no v-bump this week)

### Re-run trigger

Next eligible run: **2026-07-04** (30 days after v3.3.0).
If v3.3.0 §31 does NOT prevent new `cross-repo-owner-drift` events in next 30 days,
consider §33 specifically targeting the failure mode.

## 2026-06-06 — Manual update, teacher-report v0.2.9 + lark-doc gotchas

| ts | skill | verdict | reason |
|----|-------|---------|--------|
| 2026-06-06T17:02:00+08:00 | teacher-report | v0.2.8→v0.2.9 | Add Anti-Hallucination Rules section (6-field verification matrix + 3+1 layer defense + 4 absolute prohibitions). Trigger: 吴飞 report had 5 papers mislabeled as "ICLR 2026 Withdrawn" (GAIR / EnCounteR etc actually exist on arXiv); 行政职务 outdated by 2 years; Chinese author name typo (叶鑫海→叶昕海). |
| 2026-06-06T17:02:00+08:00 | lark-doc | update | Append 7 lark-cli gotchas to `references/lark-doc-update.md`: --content @file relative path only, block_replace silent-fail on 2nd call, str_replace escapes XML in markdown mode, 前缀...后缀 syntax, # H1→title mapping, 1. auto-numbering, empty cell matching. |

- Case: 6-字段幻觉分析 (5 papers mislabeled + outdated title + name typo)
- Source: this session, teacher report audit + repair flow on Wu Fei dossier

## 2026-06-08 — Manual update, teacher-report v0.3.0 — Paper Entry Format 6 行 paper card

| ts | skill | verdict | reason |
|----|-------|---------|--------|
| 2026-06-08T10:45:00+08:00 | teacher-report | v0.2.9→v0.3.0 | **Invert** paper entry format: from compact `<p><b>{title} (venue year) ⭐</b></p>` + 5-field UL (which **prohibited** author list per v0.2.5 rule) → mandatory 6-line paper card (verbatim title + full author list + `Fei Wu（吴飞）` explicit label + venue/year/role + arXiv URL + papers.cool URL). Trigger: this session's audit of 23 legal AI / Chinese core papers in 吴飞 dossier found 4 papers (UniLR/CoEvo/Test-Time Scaling/Legal JP) with 5+ missing co-authors including Fei Wu and Kun Kuang as corresponding authors — compact format buried the missing-author bug; also user wants `papers.cool` 1-click reading entry for every paper. |

### Files changed (4)

| file | change |
|------|--------|
| `teacher-report/SKILL.md` | +新增 `## Paper Entry Format (v0.3.0) — 硬要求` 章节 (96 行: 6 行模板 + 字段规范表 + 正确示例 + 6 类反例 + 5 适用位置 + v0.2.5→v0.3.0 对照 + Audit Check 13 5 子项) ; Output contract 加 6 行 paper card 硬要求 ; description frontmatter 标 v0.3.0 |
| `teacher-report/references/report-template.md` | §5.0 旧紧凑格式标 DEPRECATED ; 新增 §5.1 v0.3.0 Paper Card 6 行模板 (XML 模板 + 正确示例 + 6 硬规则 + 6 适用位置 + 5 反例 + 旧→新对照 + 升级命令) |
| `teacher-report/references/llm-prompt.md` | §8 套磁信章节加 paper card 硬要求 ; 检查清单加 v0.3.0 自检项 ; Check 11 旧 inline arXiv 链接要求保留为 v0.3.0 兼容项 |
| `teacher-report/references/audit-checklist.md` | Check 11 升级说明 (旧 inline link 仍 OK 但 v0.3.0 升级为 Check 13) ; 新增 Check 13 (5 子项 a-e: 4 前缀齐 / 6 行结构 / Fei Wu 中文标注 / arXiv URL 完整 / paperscool URL 完整) ; 已知反例表加 v0.3.0 待办 ; 总览从 12 项 → 13 项 |

### Migration plan (existing v0.2.5-v0.2.9 docx)

- ❌ v0.2.5-v0.2.9 docx 跑 audit mode (Check 13) 会标 ❌ "缺 paperscool" + "缺作者列表"
- ✅ 修复用 `lark-cli docs +update --command block_replace` 逐 paper 升级, paper card 6 行 block 模板见 `report-template.md §5.1`
- ⏳ 当前 `HpyNdN2s2oiy7xxhXumcEKr3nHO` (吴飞 docx) 仍 v0.2.5 格式, Check 13 标 ❌, 需 user 确认后批量升级
- 4 docx in `normalization-audit-2026-06-05.md` 已知反例表中, 况琨 v0.2.4 (`MqEzdtwcso2AGyxUPuCcyQRAnwe`) 标 None, 但 v0.3.0 起 Check 13 会标 ❌, 需 reprocess

