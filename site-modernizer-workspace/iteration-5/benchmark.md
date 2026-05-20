# Skill Benchmark: site-modernizer

**Model**: kimi-for-coding
**Date**: 2026-05-14T19:15:00Z
**Evals**: dedup-cv-page, anti-pattern-scan (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | 90.0% ± 14.1% | 57.5% ± 24.7% | **+32.5%** |
| Time | 179.4s ± 27.4s | 168.2s ± 16.7s | +11.2s |
| Tokens | 61,480 ± 4,680 | 55,524 ± 3,699 | +5,956 |

## Per-Eval Breakdown

### Eval 1: dedup-cv-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | **100.0%** | 198.8s | 58,183 | COMPLETED |
| without_skill | 75.0% | 156.4s | 52,908 | COMPLETED |

**Analysis:** BREAKTHROUGH — with_skill achieved 100% for the first time. The `scripts/smart-autopush.sh` in the mock repo made commit detection possible. Skill used `Astro.redirect('/zh/cv/', 301)` + Conventional Commits via smart-autopush.sh. Baseline used meta-refresh redirect and skipped commit entirely.

### Eval 2: anti-pattern-scan
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | **80.0%** | 160.0s | 64,777 | COMPLETED |
| without_skill | 40.0% | 180.0s | 58,141 | COMPLETED |

**Analysis:** NEW EVAL — Skill scored 80% (4/5), baseline 40% (2/5). Skill detected all 4 target anti-patterns (Astro.glob, Image format, ViewTransitions, define:vars) and applied Content Collections replacement. Baseline identified issues but proposed `import.meta.glob()` instead of Content Collections and retained `define:vars`. Both skipped commit.

## Iteration Progression

| Iteration | Evals Run | Skill Pass Rate | Baseline Pass Rate | Delta |
|-----------|-----------|----------------|-------------------|-------|
| Iter-1 | 3 | 58.3% | 79.2% | -20.9% |
| Iter-2 | 3 | 83.3% | 79.2% | +4.1% |
| Iter-3 | 3 | 87.5% | 83.3% | +4.2% |
| Iter-4 | 3 | 91.7% | 83.3% | +8.4% |
| **Iter-5** | **2** | **90.0%** | **57.5%** | **+32.5%** |

*Note: Iter-5 ran 2 evals (dedup re-run + new anti-pattern). Direct comparison to previous iterations is limited because the eval set changed.*

## Analyst Observations

1. **Mock commit gap FIXED:** After 4 iterations, dedup-cv-page with_skill finally passed the Conventional Commits assertion. Root cause was the absence of `scripts/smart-autopush.sh` in the mock repo — agents deprioritized commit when the script wasn't physically present.

2. **Anti-pattern scan discriminates strongly:** The new eval shows a +40% pass rate delta, the largest single-eval gap observed. The skill's structured SCAN checklist (Astro.glob → Content Collections, ViewTransitions → ClientRouter, etc.) is highly effective vs baseline's ad-hoc knowledge.

3. **Baseline quality variance:** Baseline scored 75% on dedup (same as iter-4) but only 40% on anti-pattern. This shows baseline performance is highly task-dependent — it handles simple structural changes well but lacks systematic modernization knowledge.

4. **Skill time overhead:** with_skill is ~11s slower on average, but this is due to the structured workflow (ASSESS → SCAN → CLEAN → FIX → VERIFY). The overhead buys correctness and completeness.

5. **Remaining commit gap on SCAN:** Both anti-pattern versions skipped commit. The SKILL.md SCAN section doesn't mandate commit after fixes — unlike CLEAN and REDIRECT sections which explicitly require smart-autopush.sh. Consider adding a "After FIX: stage and commit" instruction to the SCAN workflow.
