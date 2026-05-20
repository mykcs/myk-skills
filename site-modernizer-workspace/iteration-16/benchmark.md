# Skill Benchmark: site-modernizer (Iteration-16)

**Model**: sonnet
**Date**: 2026-05-15T03:51:44Z
**Evals**: 4, 5, 6 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 87% ± 12% | 67% ± 12% | +0.20 |
| Time | 407.2s ± 174.9s | 198.1s ± 51.4s | +209.1s |
| Tokens | 65039 ± 6086 | 54323 ± 1578 | +10716 |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill |
|------|-----------|---------------|
| anti-pattern-scan | 4/5 (no commit) | 3/5 |
| i18n-sync-audit | 5/5 (committed) | 3/5 |
| performance-asset-audit | 4/5 (no commit) | 4/5 |

## Notes

- Commit rate with skill: 1/3 (only i18n-sync-audit committed)
- with_skill pass rate 86.7% vs without_skill 66.7% (+20pp)
- Time overhead: +209s average (with_skill takes longer due to thoroughness)
- Token overhead: +10,716 average
- Iteration-17 focus: embed commit as explicit final numbered step in every fix workflow
