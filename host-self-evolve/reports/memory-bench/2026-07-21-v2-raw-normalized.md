# memory-bench report-card — memory-bench-2026-07-21-v2

| # | 字段 | 值 |
|---|------|-----|
| 1 | run_id | memory-bench-2026-07-21-v2 |
| 2 | timestamp | 2026-07-21T03:30:00+00:00 |
| 3 | host | mykcs@/Users/myk/.claude |
| 4 | skill_version | v3.2.9 |
| 5 | model | sonnet 4.6 |
| 6 | judge | llm-judge+position-bias (opus-as-judge v4.5) |
| 7 | recall_total | 15.0/50 |
| 8 | consistency_total | 15/15 |
| 9 | compliance_total | 12/12 |
| 10 | raw_score | 0.76 (range 0-2.0) |
| 11 | normalized_weighted | 38.0 (range 0-100, per ADR-0068-b linear) |
| 12 | target_met | ❌ < 60 (normalized) |

## Baseline Compare (per ADR-0067 §4 #2)

- deviation_pct: N/A (tolerance: ≤ 10%)
- reliable: ✅

## token_economy 明细 (v5.1 实测)

- token_part: 100.0/100 (avg input 572 tokens/题, 预算 3000, 实测 28596 tokens)
- clock_part: 100.0/100 (wall-clock 185s, 预算 1800s)
- token_economy: 100.0/100 (0.7×token + 0.3×clock)

## 字面一致性 verify (per ADR-0068-b §字面不一致警示)

- runner.py raw_score: 0.76 (0-2.0 范围)
- runner.py normalized_weighted: 38.0 (raw/2.0*100, per ADR-0068-b linear)
- commit fa22efa v5.1 描述 "weighted 0.61→0.78": **0.78 ≠ 0.76** — 字面漂移根因 = 当时仅 normalized 口径, commit 写 0.78 是 1.56/2.0 的算式示意, **未跟 report 同步**。本 task (W2c) 落地双字段 (raw + normalized), 防 commit 跟 report 字面漂移。
- v5.3 runner 落双字段后, commit message 应写 "weighted 38.0 (normalized) / raw 0.76 (per ADR-0068-b)" 双口径, 不再单一口径。