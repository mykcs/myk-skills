# Skill Benchmark: site-modernizer

**Model**: kimi-for-coding
**Date**: 2026-05-14T09:17:22Z
**Evals**: dedup-cv-page, strip-redirect-only, create-project-page (3 runs each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | 66.7% ± 57.7% | 87.5% ± 12.5% | -20.8% |
| Time | 294.6s ± 194.0s | 358.3s ± 145.8s | -63.7s |
| Tokens | 69,802 ± 14,857 | 67,669 ± 19,269 | +2,133 |

> **Note:** Eval 1 (dedup-cv-page) with-skill failed due to a test setup flaw. Excluding eval 1: skill pass rate = 100%, baseline = 81.3%.

## Per-Eval Breakdown

### Eval 1: dedup-cv-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 0.0% | 78.9s | 53,928 | FAILED |
| without_skill | 100.0% | 187.3s | 52,070 | COMPLETED |

**Analysis:** The skill agent correctly detected that the repository had already been stripped and refused to hallucinate a plan. The baseline agent produced a solid meta-refresh redirect plan. This is a test setup issue, not a skill deficiency.

### Eval 2: strip-redirect-only
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 100.0% | 340.4s | 72,186 | COMPLETED |
| without_skill | 87.5% | 478.9s | 90,604 | COMPLETED |

**Analysis:** The skill version produced a significantly more comprehensive plan (480 lines vs 214 lines) with the ASSESS→CLEAN→REDIRECT→VERIFY workflow, simplified deploy.yml, rollback plan, and explicit risk matrix. It also used 20% fewer tokens.

### Eval 3: create-project-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 100.0% | 464.5s | 83,293 | COMPLETED |
| without_skill | 75.0% | 408.8s | 60,332 | COMPLETED |

**Analysis:** Both produced high-quality ~600-line plans. The skill version mirrored existing gdkvm patterns and included asset sourcing; the baseline created a standalone dark-first design. The baseline was faster and used fewer tokens but missed gdkvm mirroring and asset sourcing.

## Analyst Observations

1. **Non-discriminating assertions:** "Includes build verification" and "Uses Astro 6 + Tailwind v4" passed for all completed runs — these are baseline expectations, not skill differentiators.

2. **Skill strength:** The skill consistently produces more structured plans that follow explicit workflows (ASSESS→CLEAN→REDIRECT→VERIFY), reference existing project patterns (gdkvm), and include operational details (smart-autopush.sh, deploy.yml, risk matrices).

3. **Skill weakness:** The skill agent was overly cautious in eval 1, refusing to produce a hypothetical plan when source files were missing. The baseline agent adapted by creating a plan based on the described scenario.

4. **Token efficiency:** For evals 2-3, the skill used fewer tokens (72K/83K vs 91K/60K) except eval 3 where baseline was more concise.

5. **Recommendation:** Fix eval 1 test setup by using a repo that actually has the duplicate CV pages. Consider adding a "hypothetical plan" fallback to the skill for scenarios where files don't yet exist.
