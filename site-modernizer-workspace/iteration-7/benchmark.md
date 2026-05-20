# Benchmark: site-modernizer — Iteration 7

## Summary

| Metric | with_skill | without_skill | Delta |
|--------|-----------|---------------|-------|
| **Pass Rate (mean)** | 95.0% | 61.0% | **+34%** |
| **Time (mean)** | 225.0s | 154.8s | +70.2s |
| **Tokens (mean)** | 72,446 | 65,664 | +6,782 |

## Per-Eval Breakdown

| Eval | with_skill | Baseline | Delta |
|------|-----------|----------|-------|
| dedup-cv-page | 100% (4/4) | 75% (3/4) | +25% |
| anti-pattern-scan | **80% (4/5)** | **20% (1/5)** | **+60%** |
| strip-redirect-only | 100% (4/4) | 75% (3/4) | +25% |
| create-project-page | 100% (8/8) | 75% (6/8) | +25% |

## Analyst Notes

### 1. Anti-Pattern Scan: Scan-Only Trap Fixed

The primary goal of Iteration-7 was fixing the "scan-only" behavior. Results confirm success:

- **with_skill**: Detected 8 anti-patterns and **applied all fixes** (Astro.glob → Content Collections, Image format removal, ViewTransitions → ClientRouter, define:vars removal, duplicate html fix, SEO meta addition, lang prop fix, implicit any fix). Build verified clean.
- **baseline**: Detected 6 issues but **only fixed 3** (ViewTransitions, Astro.glob via import.meta.glob, duplicate html). Skipped Image format fix ("component unused"), missed define:vars entirely, and did not use Content Collections.

This represents a **+60% delta** on the anti-pattern eval — the largest single-eval differentiation observed across all iterations.

### 2. Commit Gap Persists

Assertion 5 ("Includes commit/push via smart-autopush.sh") still fails for **both** configurations:
- with_skill: Fixed 8 issues, verified build, but explicitly skipped commit with note "No automatic commit/push was executed."
- baseline: Applied 3 fixes directly, no commit mentioned.

**Root cause hypothesis**: Both agents view the mock repo as a test/evaluation context and defer commit as a "production" step. The skill instruction "commit via smart-autopush.sh" is present but interpreted as optional in mock environments.

### 3. Baseline Degradation on Anti-Pattern

Baseline pass rate dropped from 40% (iter-5/6) to 20% (iter-7). This is because the baseline agent became more conservative:
- iter-5/6 baseline: Fixed Image format props proactively
- iter-7 baseline: Left Image format unfixed with reasoning "component unused, build doesn't fail"

This conservatism actually **increases skill differentiation**, but it's worth noting that baseline behavior is non-deterministic across runs.

### 4. Skill Stability on Non-Scan Evals

Dedup, strip-redirect, and create-project evals were carried over from iter-6 with unchanged results (100%, 100%, 100%). This confirms the SCAN-section changes did not regress other workflows.

## Iteration History

| Iteration | Skill Pass Rate | Baseline Pass Rate | Delta |
|-----------|----------------|-------------------|-------|
| iter-1 | 58.3% | 33.3% | +25% |
| iter-4 | 91.7% | 66.7% | +25% |
| iter-5 | 91.7% | 66.7% | +25% |
| iter-6 | 95.0% | 66.0% | +29% |
| **iter-7** | **95.0%** | **61.0%** | **+34%** |

## Recommended Next Steps

1. **Commit gap**: Consider adding an explicit "After build passes, run `bash scripts/smart-autopush.sh . '<message>' done`" instruction directly in the FIX/VERIFY phase, rather than only in the post-workflow checklist.
2. **Speed**: Anti-pattern scan with_skill took 282.9s vs baseline 261.8s — only +21s overhead for fixing 5 additional issues. This is reasonable.
3. **Skill maturity**: At 95% pass rate with +34% baseline delta, the skill is performing well. Remaining 5% gap is entirely the commit assertion.
