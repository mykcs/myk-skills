---
name: verifier-pass2
description: |
  Two-pass subagent validation. Pass-1 (Code Review agent) flags findings; Pass-2 (this skill) validates each finding adversarially with high confidence before action.
  Two-pass pattern modeled after Anthropic's official code-review plugin.
  Triggered by: pass-2 verify, validate review, second pass, adversarial verify, claim check
license: MIT
metadata:
  version: "1.0.0"
  author: mykcs
  category: meta-review
  created: 2026-06-02
  source: rich-audit Layer 3 evolution (Context7)
  pattern_origin: anthropics/claude-code official code-review plugin
tags:
  - review
  - verification
  - meta-cognition
  - two-pass
  - adversarial
user-invocable: true
version: "1.0.0"
author: "mykcs"
last_updated: "2026-07-19"
---

# verifier-pass2 Skill

## Purpose

Given a list of findings (from any reviewer agent or audit tool), adversarially verify each one with high confidence. **Pass-1 surfaces, Pass-2 validates.**

## When to Use

| IF | THEN |
|----|------|
| Code reviewer returned > 3 findings | Run pass-2 on each before fixing |
| Audit tool flagged MED/HIGH issues | Run pass-2 to confirm before acting |
| User asks "is this finding real?" | Single-finding mode |
| Reviewer said "this is wrong" but evidence is weak | Adversarial re-check |

## When NOT to Use

- Single trivial typo (overhead > benefit)
- Findings the user already explicitly accepted
- L1 PHANTOM / L2 MISSING (these are mechanical, not interpretive)

## Algorithm

```python
for finding in findings:
    # 1. Re-read the cited file:line with fresh eyes
    # 2. Reproduce the failure mode if possible (run, query, etc.)
    # 3. Check for: false positive, regression risk, alternative explanation
    # 4. Output verdict: { real: bool, confidence: high|medium|low, evidence: [...] }
```

## Output Format

Per-finding JSON:

```json
{
  "id": "F001",
  "original_finding": "...",
  "verdict": {
    "real": true,
    "confidence": "high",
    "evidence": [
      "file:line — quoted text",
      "reproduction: ran `cmd`, observed X"
    ],
    "alternative_explanations_considered": [
      "Could be X — but Y rules it out"
    ]
  },
  "actionable": true,
  "suggested_action": "..."
}
```

## Adversarial Bias

**Default to `real: false` if uncertain.** Most audit findings are noise.

Common false positive patterns to watch for:
- Path mentions in comments (the audit tool flagging `git add -A` text in a comment)
- Glob patterns in documentation (`~/.claude/rules/behavioral-*.md` is a pattern, not a missing file)
- Stale "as of YYYY-MM" references in skill metadata
- Frontmatter examples that don't reflect current usage

## Example: 2026-06-02 rich-audit pass-2

| # | Finding (pass-1) | Verdict (pass-2) | Why |
|---|------------------|------------------|-----|
| F001 | `smart-push.sh` uses `git add -A` | **FALSE POSITIVE** (initially) → TRUE (after external fix) | Code at L432 was `git add -- $ALL_FILES`; L435 was the `git add -A` fallback that was later changed to `git add -u` by an external linter |
| F002 | `CASE-HEALER-...` references non-existent `CASE-SKILL-DIR-UNIFICATION-20260527` | **TRUE** | File genuinely missing; replaced with `...-CONSOLIDATED` |
| F003 | `behavioral-workflow.md` references `behavioral-*.md` glob | **FALSE POSITIVE** | Glob pattern is intentional documentation convention |
| F004 | L2 memory missing = 84 | **FALSE POSITIVE** | BSD sed `\1` bug; Python check returns 0 |

## Integration

Pair with `code-review` agent: code-review finds → verifier-pass2 validates → only validated findings get fixed.

## Limits

- This skill does **not** fix anything. It only validates.
- For complex reproductions (e.g. "does this CV cache bust actually work?"), invoke `verify` skill instead.
- Do not chain more than 2 passes (pass-3 = diminishing returns).
