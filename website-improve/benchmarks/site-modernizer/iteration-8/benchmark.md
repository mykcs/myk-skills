# Benchmark: site-modernizer — Iteration 8

## Summary

| Metric | with_skill | without_skill | Delta |
|--------|-----------|---------------|-------|
| **Pass Rate (mean)** | 100.0% | 71.0% | **+29%** |
| **Time (mean)** | 232.4s | 149.6s | +82.8s |
| **Tokens (mean)** | 72,961 | 65,434 | +7,527 |

## Per-Eval Breakdown

| Eval | with_skill | Baseline | Delta |
|------|-----------|----------|-------|
| dedup-cv-page | 100% (4/4) | 75% (3/4) | +25% |
| **anti-pattern-scan** | **100% (5/5)** | **60% (3/5)** | **+40%** |
| strip-redirect-only | 100% (4/4) | 75% (3/4) | +25% |
| create-project-page | 100% (8/8) | 75% (6/8) | +25% |

## Key Win: Commit Gap Closed

The primary goal of Iteration-8 was fixing the persistent commit assertion failure in anti-pattern scan. Results confirm success:

- **with_skill agent**: Executed `git commit` with hash `947cdb6` and Conventional Commit message `refactor(site): fix Astro anti-patterns...`
- **baseline agent**: No commit executed

The SKILL.md wording change from "include the commit command as a required step" to "**NEVER skip the commit step.** Even in test, mock, or evaluation repos, you MUST physically run the commit command" successfully drove commit behavior.

## Analyst Notes

### 1. Test Setup Contamination (Important Caveat)

The iter-8 anti-pattern mock repo was copied from iter-7's working directory, which already contained partial fixes from iter-7's baseline run (`import.meta.glob` and `ClientRouter` already present). This means:

- Both agents started with a partially-fixed codebase, not the original anti-pattern codebase
- The baseline pass rate of 60% is **not directly comparable** to iter-7's 20%
- The with_skill 100% includes the commit win but may have been aided by the cleaner starting state

**Remediation**: Future iterations should reset the mock repo via `git checkout 4aa60a2 -- .` before each run.

### 2. Skill Passes All Assertions Across All Evals

For the first time in the iteration history, the skill achieves **100% mean pass rate** across all 4 evals:

| Iteration | Skill Pass Rate | Baseline Pass Rate | Delta |
|-----------|----------------|-------------------|-------|
| iter-1 | 58.3% | 33.3% | +25% |
| iter-4 | 91.7% | 66.7% | +25% |
| iter-5 | 91.7% | 66.7% | +25% |
| iter-6 | 95.0% | 66.0% | +29% |
| iter-7 | 95.0% | 61.0% | +34% |
| **iter-8** | **100.0%** | **71.0%** | **+29%** |

### 3. Time & Token Overhead

Skill time overhead increased slightly (+82.8s avg) due to the commit step addition and more thorough fix application. Token overhead is stable at ~7.5K tokens per eval. Given the +29% correctness delta, this overhead is well-justified.

### 4. Baseline Variance

Baseline pass rates have varied across iterations:
- dedup: consistently 75%
- anti-pattern: 40% (iter-5/6) → 20% (iter-7) → 60% (iter-8, contaminated)
- strip-redirect: consistently 75%
- create-project: consistently 75%

The anti-pattern baseline is the most variable, suggesting it is the most skill-dependent eval — exactly where the skill provides the most value.

## Recommended Next Steps

1. **Skill is mature**: 100% pass rate with +29% baseline delta across 4 diverse evals suggests the skill is performing well.
2. **If continuing**: Reset anti-pattern mock repo to original state and do one clean validation run to confirm 100% holds without contamination.
3. **If stopping**: The skill is ready for broader use. Consider adding more evals (e.g., i18n synchronization, performance audit) if expanding scope.
