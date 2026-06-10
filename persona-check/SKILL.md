---
name: persona-check
description: Self-audit claudecode's prose drafts for first/second-person pronoun violations before posting. Wraps `~/.claude/scripts/pronoun-audit.sh` and surfaces the result. Triggers: "check persona", "audit draft", "self-check", "pronoun audit", "persona check", "审一下 / 自检 / 看看有没有违反".
---

# persona-check

Self-audit a prose draft for persona rule violations before posting. The persona rule (see `~/.claude/memory/identity-first-person.md`) requires:
- First-person 「我」→ "claudecode"
- Second-person 「你/您」→ "用户"
- Exceptions: code blocks, blockquotes, list items, headings, table rows

## When to use

- After writing a long prose response (>10 lines of prose, not in code blocks)
- Before calling `AskUserQuestion` with reverse-question phrasing
- When in doubt whether the current draft complies

## Usage

```bash
# Save draft to a file (e.g. /tmp/draft.md), then:
bash ~/.claude/scripts/pronoun-audit.sh /tmp/draft.md
```

Or pipe via stdin:

```bash
cat /tmp/draft.md | bash ~/.claude/scripts/pronoun-audit.sh
```

## Exit codes

| Exit | Meaning | Action |
|---|---|---|
| 0 | Clean — no pronoun matches | Proceed with posting |
| 1 | Matches in exception context (code / quote / list / heading / table) | Review; usually OK to proceed |
| 2 | Matches in prose — likely violation | **MUST revise draft** before posting |

## Workflow for claudecode

1. **Draft** the response (in a temporary file or in your head).
2. **Run** `bash ~/.claude/scripts/pronoun-audit.sh <draft>`.
3. **Check** exit code:
   - `0` or `1` → proceed
   - `2` → revise the draft, replacing 我/你/您 with claudecode/用户 (or move matches into code blocks / quotes / lists)
4. **Re-run** the audit; confirm exit 0 or 1.
5. **Post** the revised draft.

## Reference

- Persona rule: `~/.claude/memory/identity-first-person.md`
- Question Template (for reverse-question phrasing): `~/.claude/memory/identity-first-person.md` (section "Question Template")
- Audit script: `~/.claude/scripts/pronoun-audit.sh`
- Stop hook (post-hoc audit): `~/.claude/scripts/stop-persona-audit.py`
- Case file: `~/.claude/knowledge/cases/wiki/CASE-IDENTITY-FIRST-PERSON-RULE-20260605.md`

## Created

2026-06-10 (CASE Deja Vu 2026-06-10 hardening).
