# Skill Benchmark: site-modernizer

**Model**: kimi-for-coding
**Date**: 2026-05-14T20:30:00Z
**Evals**: dedup-cv-page, strip-redirect-only, create-project-page (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | 91.7% ± 11.8% | 83.3% ± 11.8% | **+8.4%** |
| Time | 107.3s ± 38.5s | 92.5s ± 17.3s | +14.8s |
| Tokens | 68,179 ± 10,307 | 63,578 ± 8,290 | +4,601 |

## Per-Eval Breakdown

### Eval 1: dedup-cv-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 75.0% | 83.4s | 57,445 | COMPLETED |
| without_skill | 75.0% | 72.9s | 55,014 | COMPLETED |

**Analysis:** Both versions identical (3/4). Skill used `Astro.redirect()` frontmatter; baseline used `astro.config.mjs` redirects. Both still missing commit step — even with git-initialized mock repo and SKILL.md instruction.

### Eval 2: strip-redirect-only
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 100.0% | 76.9s | 65,006 | COMPLETED |
| without_skill | 100.0% | 115.0s | 60,926 | COMPLETED |

**Analysis:** Both perfect. Skill version faster (-38s) with structured file-verdict table. Baseline included backup branch and 404.html for deep links.

### Eval 3: create-project-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | **100.0%** | 161.7s | 82,087 | COMPLETED |
| without_skill | 75.0% | 89.5s | 74,794 | COMPLETED |

**Analysis:** **Breakthrough** — first 100% run. Plan included:
- **oklch colors**: Full `@theme` block with `oklch(55% 0.15 255)`, `oklch(65% 0.18 30)`, etc.
- **gdkvm mirroring**: Reused Layout.astro, i18n helper, highlight-title animation, service worker, structuredData.ts
- **Playwright E2E tests**: Smoke tests for both languages, hero visibility, BibTeX copy button
- **Risk & user actions**: 4 risks, 5 user action items

Baseline missed oklch and gdkvm (same as iter-2/3).

## Iteration Progression

| Iteration | Skill Pass Rate | Baseline Pass Rate | Delta |
|-----------|----------------|-------------------|-------|
| Iter-1 | 58.3% | 79.2% | -20.9% |
| Iter-2 | 83.3% | 79.2% | +4.1% |
| Iter-3 | 87.5% | 83.3% | +4.2% |
| **Iter-4** | **91.7%** | **83.3%** | **+8.4%** |

## Analyst Observations

1. **Iteration-4 breakthrough on complex eval:** create-project-page with-skill achieved the first-ever 100% pass rate. The oklch MANDATORY instruction in SKILL.md worked — after 3 iterations of complete misses, the agent finally incorporated oklch color tokens into the plan.

2. **Delta doubled:** The pass rate gap between skill and baseline expanded from +4.2% (iter-3) to +8.4% (iter-4). This is entirely driven by the create-project-page skill improvement.

3. **Skill efficiency on simple tasks:** For strip-redirect-only, skill was 33% faster than baseline while producing equally comprehensive output. The structured ASSESS→CLEAN→REDIRECT→VERIFY workflow prevents aimless exploration.

4. **Persistent mock repo commit gap:** Despite git-initializing the mock repo and adding "Even in hypothetical plans or mock repos, include the commit command" to SKILL.md, both dedup-cv-page versions still skip commit. Agents may detect the absence of `scripts/smart-autopush.sh` and deprioritize commit. **Recommendation:** Either (a) add a minimal `scripts/smart-autopush.sh` to the mock repo, or (b) accept that commit assertions are non-discriminating for mock-repo evals and remove them.

5. **Non-discriminating assertions:** "Uses Astro 6 + Tailwind v4" and "Includes build verification" continue to pass universally. They are baseline expectations, not skill differentiators.

6. **Recommendation:** The skill is now performing well (91.7% mean pass rate, 100% on the most complex eval). The remaining 8.3% gap is entirely from the mock-repo commit assertion. Consider whether to fix this edge case or declare the skill sufficiently optimized.
