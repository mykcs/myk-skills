# Skill Benchmark: site-modernizer

**Model**: kimi-for-coding
**Date**: 2026-05-14T17:30:00Z
**Evals**: dedup-cv-page, strip-redirect-only, create-project-page (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | 83.3% ± 11.8% | 79.2% ± 15.6% | +4.1% |
| Time | 214.4s ± 85.4s | 185.7s ± 52.7s | +28.7s |
| Tokens | 73,582 ± 15,067 | 62,029 ± 10,050 | +11,553 |

## Per-Eval Breakdown

### Eval 1: dedup-cv-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 75.0% | 133.8s | 54,162 | COMPLETED |
| without_skill | 75.0% | 111.4s | 51,233 | COMPLETED |

**Analysis:** Both versions scored identically (3/4). Skill used `astro.config.mjs` redirects with Astro docs caveat; baseline used `Astro.redirect()` in frontmatter. Both missing explicit commit step. The key improvement from iteration-1: skill no longer refuses when files exist (mock repo fix + hypothetical plan fallback).

### Eval 2: strip-redirect-only
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 100.0% | 176.8s | 75,708 | COMPLETED |
| without_skill | 100.0% | 217.8s | 59,218 | COMPLETED |

**Analysis:** Both perfect scores. Skill version faster (-41s) and more structured with explicit ASSESS→CLEAN→REDIRECT→VERIFY workflow, [BATCH MODE] marker, and risk matrix. Baseline included useful GitHub Pages source switch instructions.

### Eval 3: create-project-page
| Configuration | Pass Rate | Time | Tokens | Status |
|--------------|-----------|------|--------|--------|
| with_skill | 75.0% | 332.5s | 90,877 | COMPLETED |
| without_skill | 62.5% | 227.8s | 75,635 | COMPLETED |

**Analysis:** Skill version outperformed on complex eval (+12.5%). Used Content Collection pattern (`osa-page` collection) with detailed asset inventory. Baseline used hardcoded page approach with less asset sourcing detail. Both missed oklch colors and gdkvm mirroring assertions.

## Analyst Observations

1. **Iteration-1 regression fixed:** Eval1 with-skill went from 0% to 75% thanks to mock repo + hypothetical plan fallback.

2. **Non-discriminating assertions:** "Uses Astro 6 + Tailwind v4" and "Includes build verification" passed for all completed runs — baseline expectations, not skill differentiators.

3. **Skill strength:** Structured workflow adherence (ASSESS→CLEAN→REDIRECT→VERIFY), operational details (smart-autopush.sh, [BATCH MODE]), and Content Collection patterns for project pages.

4. **Skill weakness:** Both versions consistently miss "Conventional Commits commit message" (eval1) and "oklch colors" / "gdkvm mirroring" (eval3). These may be overfit assertions or need stronger prompting in the skill.

5. **Token/time tradeoff:** Skill uses ~19% more tokens and ~15% more time on average, but achieves higher quality on complex tasks.

6. **Recommendation:** Consider whether oklch/gdkvm assertions are truly skill differentiators or just preferences. The skill already covers the core workflow well.
