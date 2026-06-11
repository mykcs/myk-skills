#!/usr/bin/env python3
"""
check_h2_emoji.py — teacher-report v0.6.0 Check 14 self-check
H2 标题无装饰性 emoji (decorative emoji ban)

Usage:
    python3 check_h2_emoji.py <content.xml>
    python3 check_h2_emoji.py --stdin
    echo "<h2>1. xxx</h2>" | python3 check_h2_emoji.py --stdin

Exit codes:
    0 = clean (no decoration emoji in H2)
    1 = decoration emoji found (with diff to stdout)
    2 = error (file not found, etc.)

Allowlist (status/signal emojis, NOT flagged):
    ✅ ❌ ⚠ ⭐ 🟢 🟡 🔴 ⛔ 🚨

Decoration emoji flagged (sample):
    👤 📊 ✉ 📚 📖 🎯 ℹ 💡 🔥 ✨ etc.
"""
import sys
import re
from pathlib import Path

# Status / signal emojis that are allowed
ALLOWLIST = set("✅❌⚠⭐🟢🟡🔴⛔🚨")

# Variation selectors (U+FE0F, U+FE0E, U+200D) — part of emoji sequences, not flagged
ZWJ_CHARS = {0xFE0F, 0xFE0E, 0x200D}

# Unicode emoji ranges (covers standard emojis incl. 👤📊✉📚📖🎯ℹ etc.)
EMOJI_RANGES = [
    (0x1F300, 0x1F5FF),  # Symbols & Pictographs
    (0x1F600, 0x1F64F),  # Emoticons
    (0x1F680, 0x1F6FF),  # Transport & Map
    (0x1F700, 0x1F77F),  # Alchemical
    (0x1F780, 0x1F7FF),  # Geometric Shapes Extended
    (0x1F800, 0x1F8FF),  # Supplemental Arrows-C
    (0x1F900, 0x1F9FF),  # Supplemental Symbols & Pictographs
    (0x1FA00, 0x1FA6F),  # Chess
    (0x1FA70, 0x1FAFF),  # Symbols & Pictographs Extended-A
    (0x2600, 0x26FF),    # Misc Symbols
    (0x2700, 0x27BF),    # Dingbats
    (0x2100, 0x214F),    # Letterlike Symbols (ℹ etc.)
    (0x2B00, 0x2BFF),    # Misc Symbols and Arrows
    (0x2300, 0x23FF),    # Misc Technical
]


def is_emoji(ch: str) -> bool:
    """Return True if ch is an emoji that should be flagged (decoration)."""
    cp = ord(ch)
    if ch in ALLOWLIST or cp in ZWJ_CHARS:
        return False
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)


def find_decoration_emoji(text: str) -> list:
    """Find decorative emoji in text (excluding allowlist + variation selectors)."""
    return [ch for ch in text if is_emoji(ch)]


def strip_decoration_emoji(h2_text: str) -> str:
    """Remove decorative emoji + variation selectors + collapse whitespace + strip."""
    out = []
    for ch in h2_text:
        if is_emoji(ch) or ord(ch) in ZWJ_CHARS:
            continue
        out.append(ch)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def check_h2(content: str) -> tuple:
    """
    Parse H2 titles, check for decoration emoji.
    Returns (status, results) where:
      - status: 0=clean, 1=has_emoji, 2=error
      - results: list of dicts with h2 text, emoji found, suggested fix
    """
    h2_re = re.compile(r'<h2[^>]*?id="([^"]+)"[^>]*>(.*?)</h2>', re.DOTALL)
    inner_tag = re.compile(r"<[^>]+>")

    results = []
    has_emoji = False
    for m in h2_re.finditer(content):
        block_id = m.group(1)
        raw = inner_tag.sub("", m.group(2)).strip()
        emojis = find_decoration_emoji(raw)
        flagged = bool(emojis)
        if flagged:
            has_emoji = True
        results.append({
            "block_id": block_id,
            "raw": raw,
            "emoji": sorted(set(emojis)),
            "flag": "EMOJI" if flagged else "OK",
            "suggested": strip_decoration_emoji(raw) if flagged else raw,
        })
    return (1 if has_emoji else 0), results


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 0

    if sys.argv[1] == "--stdin":
        content = sys.stdin.read()
    else:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
        content = path.read_text(encoding="utf-8")

    status, results = check_h2(content)
    if not results:
        print("WARN: no <h2> blocks found in content", file=sys.stderr)
        return 2

    print(f"# H2 emoji check: {len(results)} H2 blocks")
    for r in results:
        if r["flag"] == "EMOJI":
            print(f"❌ {r['raw']!r} → {r['suggested']!r}  (emoji: {r['emoji']})")
        else:
            print(f"✓  {r['raw']!r}")

    n_emoji = sum(1 for r in results if r["flag"] == "EMOJI")
    print(f"\nTotal: {n_emoji} decoration emoji H2 / {len(results)} H2 total")
    return status


if __name__ == "__main__":
    sys.exit(main())
