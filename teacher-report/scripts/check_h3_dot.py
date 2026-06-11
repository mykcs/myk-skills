#!/usr/bin/env python3
"""
check_h3_dot.py — teacher-report v0.7.0 Check 15 self-check
H1-H4 编号标题 dot 后缀硬要求

Usage:
    python3 check_h3_dot.py <content.xml>
    python3 check_h3_dot.py --stdin

Exit codes:
    0 = clean (all numbered headings end with dot)
    1 = missing dot detected
    2 = error (file not found, etc.)

Rule:
    Numbered heading must end with `.<space>` (or `.<EOL>`):
    - h1: `1. ` (already has dot, h2 in our format)
    - h2: `1. ` (already has dot)
    - h3 (sections): `1.1. ` (was `1.1` in v0.2.5, v0.7.0 REQUIRES dot)
    - h4: `1. ` (same as h2)
    - h3 (paper card): `1. Title` (already has dot, exempt)

Note: only section h3 (X.Y format) is checked for missing dot. Paper card h3
(N. format) and h1/h2/h4 already have dots.
"""
import sys
import re
from pathlib import Path

# Numbered heading at start: X.Y... (where X.Y are digits, optionally more dots)
NUM_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s*(\.?)")

# h3 paper card format: "N. Title" (single digit, dot, space, text)
# Section h3 format: "X.Y" or "X.Y." followed by space and title
# We use the NUMBERED format only; paper card "1. Title" already has dot, so it passes.


def is_numbered_section_h3(raw: str) -> bool:
    """Section h3 has X.Y format. Paper card h3 has 'N. Title' format (single N)."""
    m = NUM_RE.match(raw)
    if not m:
        return False
    num = m.group(1)
    # X.Y format has at least one dot in number
    return '.' in num


def needs_dot_fix(raw: str) -> tuple:
    """Return (needs_fix, current_num, has_dot, suggested_after)."""
    m = NUM_RE.match(raw)
    if not m:
        return (False, '', True, raw)
    num = m.group(1)
    existing_dot = m.group(2) or ''
    has_dot = bool(existing_dot)
    needs_fix = not has_dot
    # Build the suggested after text: "1.1. 标题"
    matched = m.group(0)
    rest = raw[len(matched):]
    after = f'{num}. {rest.strip()}' if needs_fix else raw
    return (needs_fix, num, has_dot, after)


def check_doc(content: str) -> tuple:
    """Check all h1-h4 headings for dot suffix. Returns (status, results)."""
    results = []
    any_issue = False
    for level in (1, 2, 3, 4):
        pattern = re.compile(rf'<h{level}[^>]*?id="([^"]+)"[^>]*>(.*?)</h{level}>', re.DOTALL)
        for m in pattern.finditer(content):
            block_id = m.group(1)
            raw = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            # For h3, only check section h3 (X.Y format), not paper card (N. Title)
            if level == 3 and not is_numbered_section_h3(raw):
                continue
            needs_fix, num, has_dot, after = needs_dot_fix(raw)
            if needs_fix:
                any_issue = True
            results.append({
                'level': level, 'block_id': block_id, 'raw': raw,
                'num': num, 'has_dot': has_dot,
                'flag': 'NEEDS_DOT' if needs_fix else 'OK',
                'suggested': after,
            })
    return (1 if any_issue else 0), results


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__, file=sys.stderr)
        return 0

    if sys.argv[1] == '--stdin':
        content = sys.stdin.read()
    else:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f'ERROR: file not found: {path}', file=sys.stderr)
            return 2
        content = path.read_text(encoding='utf-8')

    status, results = check_doc(content)
    if not results:
        print('WARN: no numbered h1-h4 headings found', file=sys.stderr)
        return 2

    n_issues = sum(1 for r in results if r['flag'] == 'NEEDS_DOT')
    print(f'# H1-H4 dot check: {len(results)} numbered headings')
    for r in results:
        if r['flag'] == 'NEEDS_DOT':
            print(f"❌ h{r['level']}: {r['raw']!r} → {r['suggested']!r}")
        else:
            print(f"✓  h{r['level']}: {r['raw']!r}")

    print(f'\nTotal: {n_issues} missing dot / {len(results)} numbered headings')
    return status


if __name__ == '__main__':
    sys.exit(main())
