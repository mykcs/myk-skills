# Skill Benchmark: site-modernizer

**Model**: kimi-for-coding
**Date**: 2026-05-14T19:30:00Z
**Evals**: dedup-cv-page, strip-redirect-only, create-project-page (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | 87.5% ± 10.2% | 83.3% ± 11.8% | +4.2% |
| Time | 150.5s ± 63.8s | 792.9s ± 1002.3s | +642.4s* |
| Tokens | 70,159 ± 18,220 | 57,130 ± 6,377 | +13,029 |

\* Time delta heavily skewed by baseline create-project-page outlier (2210s due to loop). Excluding outlier: baseline mean = 84.3s.

## Per-Eval Breakdown

### Eval 1: dedup-cv-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 75.0% | 108.2s | 53,357 | COMPLETED |
| without_skill | 75.0% | 60.0s | 49,349 | COMPLETED |

**Analysis:** Both versions identical (3/4). Skill used `astro.config.mjs` redirects; baseline used `Astro.redirect()` frontmatter in a replacement page. Both still missing commit step — SKILL.md iter-3 strengthening did not fix this on the mock repo eval.

### Eval 2: strip-redirect-only
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 100.0% | 102.5s | 61,642 | COMPLETED |
| without_skill | 100.0% | 108.5s | 64,969 | COMPLETED |

**Analysis:** Both perfect. Skill version slightly faster and more structured with ASSESS→CLEAN→REDIRECT→VERIFY workflow. Baseline equally thorough with rollback plan and file summary table.

### Eval 3: create-project-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 87.5% | 240.7s | 95,478 | COMPLETED |
| without_skill | 75.0% | 2210.1s | 57,072 | COMPLETED |

**Analysis:** Skill outperformed on complex eval (+12.5%). Most striking: skill was **9x faster** (240s vs 2210s) because baseline got trapped in a loop repeatedly `ls`ing OSA image directories. Skill version included gdkvm quality reference (improved from iter-2); baseline had no gdkvm mention. Both missed oklch colors.

## Analyst Observations

1. **Iteration-3 improvement on complex eval:** create-project-page with-skill improved from 75% (iter-2) to 87.5% (iter-3). The gdkvm pattern reference strengthening in SKILL.md is working — skill version now explicitly references "对标 GDKVM 质量" and inspects existing project pages.

2. **Baseline efficiency collapse on complex eval:** Without skill guidance, the baseline agent spent 37 minutes (2210s) and 331 tool calls on create-project-page, mostly looping through the same image directory listings. This demonstrates the skill's value in preventing aimless exploration.

3. **Non-discriminating assertions:** "Uses Astro 6 + Tailwind v4" and "Includes build verification" continue to pass universally — they are baseline expectations, not skill differentiators.

4. **Persistent skill gaps:**
   - **oklch colors:** Neither version mentions oklch in any eval. The skill has an oklch example in SKILL.md, but agents aren't incorporating it into plans. The instruction may need to be more actionable (e.g., "Replace all hex color values with oklch()" instead of just showing an example).
   - **Conventional Commits on mock repo:** Both versions skip commit steps for dedup-cv-page. This may be because the mock repo lacks git initialization, causing agents to deprioritize commit. Consider initializing git in the mock repo for fairer evaluation.

5. **Token/time tradeoff:** Skill uses ~23% more tokens on average but produces significantly more comprehensive plans (542 lines vs 228 lines for create-project-page). On complex tasks, skill is also dramatically faster due to structured workflow preventing loops.

6. **Recommendation for iteration-4:**
   - Make oklch requirement explicit and actionable: "All color values must use oklch() color space, not hex or rgb"
   - Initialize git in mock repo or add commit assertion only for real-repo evals
   - Consider expanding test set to verify skill generalizes beyond these 3 scenarios
