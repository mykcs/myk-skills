# Skill Benchmark: site-modernizer

**Model**: sonnet
**Date**: 2026-05-15T03:06:55Z
**Evals**: 4, 5, 6 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 67% ± 12% | +0.33 |
| Time | 488.1s ± 105.6s | 281.2s ± 53.3s | +206.9s |
| Tokens | 70977 ± 1840 | 63986 ± 1142 | +6991 |

## Notes

- anti-pattern-scan: with_skill achieved 5/5, without_skill 3/5 (missed ViewTransitions + build broke)
- i18n-sync-audit: with_skill 5/5, without_skill 4/5 (left lang ternaries)
- performance-asset-audit: with_skill 5/5, without_skill 3/5 (missed corrupt asset + no commit)
- Commit discipline is the strongest differentiator driven by skill mandate
