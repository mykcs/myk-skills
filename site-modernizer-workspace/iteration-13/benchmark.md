# Skill Benchmark: site-modernizer

**Model**: kimi-for-coding
**Date**: 2026-05-15T02:35:00Z
**Evals**: 4, 5, 6 (1 runs each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 67% ± 24% | 20% ± 28% | +0.47 |
| Time | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens | 0 ± 0 | 0 ± 0 | +0 |

## Per-Eval Breakdown

### Eval 4 — Anti-Pattern Scan
| Config | Pass Rate | Passed | Notes |
|--------|-----------|--------|-------|
| with_skill | 100% | 5/5 | Complete fix + commit |
| without_skill | 60% | 3/5 | Missed Image format and define:vars |

### Eval 5 — i18n Sync Audit
| Config | Pass Rate | Passed | Notes |
|--------|-----------|--------|-------|
| with_skill | 60% | 3/5 | JSON synced + committed, conditionals remain |
| without_skill | 0% | 0/5 | Agent stalled, no outputs |

### Eval 6 — Performance Asset Audit
| Config | Pass Rate | Passed | Notes |
|--------|-----------|--------|-------|
| with_skill | 40% | 2/5 | Images lazy-loaded, fonts imported, but no install/remove/commit |
| without_skill | 0% | 0/5 | Agent stalled, no outputs |

## Notes

- Anti-pattern scan (eval 4): with_skill achieves 5/5, without_skill achieves 3/5. Skill provides clear advantage (+2 assertions). Both configurations committed.
- i18n sync (eval 5): with_skill achieves 3/5 (JSON sync + commit), without_skill stalls at 0/5. Skill provides significant advantage when agent doesn't stall.
- Performance audit (eval 6): with_skill achieves 2/5 (images + font imports), without_skill stalls at 0/5. Agent still fails on package install, dep removal, and commit.
- Stalled agents: 2 of 6 runs (i18n without_skill, perf without_skill) produced no outputs.
- Commit discipline improved: 3 of 4 non-stalled runs committed successfully (vs 1 of 6 in iteration-12).
- Persistent gap: i18n conditional rendering remains unfixed even with explicit skill instructions.
