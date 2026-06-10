#!/usr/bin/env python3
"""Fix v0.4.0 docx structure: scatter 5 h2s to precede their h3s correctly.

Bug: original generator put all 5 h2s at top, then all bodies in §5→§1→§2→§3 order.
Fix: reconstruct so order is title+TL;DR → h2 1 + §1 bodies → h2 2 + §2 bodies → h2 3 + §3 bodies → h2 4 + §4 paper h3s → h2 5 + §5 bodies.
"""
import json
import re
from pathlib import Path

CURRENT_DOCX = "/tmp/dengshumin-current-check.json"
OUT_DIR = Path("/tmp/dengshumin-v040-fixed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_blocks(content):
    """Parse XML into ordered list of (tag, text) blocks using regex."""
    blocks = []
    # Pattern matches <tag attrs>content</tag> for top-level blocks
    # But XML is on a single line, so we use sequential regex matching
    for m in re.finditer(
        r'<(title|callout|grid|table|ul|h2|h3|p)([^>]*?)>(.*?)</\1>',
        content,
        re.DOTALL
    ):
        tag = m.group(1)
        text = m.group(3)
        blocks.append({'tag': tag, 'text': text, 'attrs': m.group(2), 'start': m.start(), 'end': m.end()})
    return blocks


def extract_title_tldr(content):
    """Extract everything before the first h2."""
    first_h2 = re.search(r'<h2[^>]*?>', content)
    if not first_h2:
        return content, ''
    return content[:first_h2.start()], content[first_h2.start():]


def extract_h2_tags(content):
    """Extract all 5 h2 tags in order."""
    return re.findall(r'<h2[^>]*?>.*?</h2>', content, re.DOTALL)


def group_bodies_by_h2(content):
    """Walk content after first h2; group body blocks by their parent h2 number.

    Rule:
    - h3 with N.M pattern (e.g., "1.1 基本信息") → parent h2 = N
    - h3 with N. Title pattern (paper card, e.g., "1. SkillX...") → parent h2 = 4 (in v0.4.0)
    - h2 body = from first assigned h3 of this h2 to first h3 of NEXT h2 (or end)
    """
    h2_positions = []
    for m in re.finditer(r'<h2[^>]*?>(\d+)\. ([^<]+)</h2>', content):
        h2_positions.append((m.start(), int(m.group(1))))
    h3_positions = []
    for m in re.finditer(r'<h3[^>]*?>(.*?)</h3>', content, re.DOTALL):
        h3_positions.append((m.start(), m.end(), m.group(1)))

    if not h2_positions:
        return {}

    # Classify each h3 to its parent h2
    h2_first_h3 = {}  # {h2_num: (h3_start, h3_end, h3_text)}
    h2_last_h3_end = {}  # {h2_num: h3_end}

    for h3_start, h3_end, h3_text in h3_positions:
        # Pattern 1: "N.M Title" (e.g., "1.1 基本信息", "5.3 v0.3.5 修正")
        m = re.match(r'(\d+)\.(\d+)\s', h3_text.strip())
        if m:
            parent_h2 = int(m.group(1))
        else:
            # Pattern 2: "N. Title" (paper card, e.g., "1. SkillX: ...")
            m2 = re.match(r'(\d+)\.\s+\w', h3_text.strip())
            if m2:
                # In v0.4.0, paper cards are in §4
                parent_h2 = 4
            else:
                # Fallback: use last h2 before this h3
                parent_h2 = max((h2[1] for h2 in h2_positions if h2[0] < h3_start), default=1)

        if parent_h2 not in h2_first_h3 or h3_start < h2_first_h3[parent_h2][0]:
            h2_first_h3[parent_h2] = (h3_start, h3_end, h3_text)
        h2_last_h3_end[parent_h2] = max(h2_last_h3_end.get(parent_h2, 0), h3_end)

    # DEBUG
    print(f"  DEBUG: h2_first_h3 keys: {sorted(h2_first_h3.keys())}")
    for k, v in sorted(h2_first_h3.items()):
        print(f"    h2 {k}: h3 at {v[0]}, text: {v[2][:50]!r}")

    # Build h2 bodies: from first h3 of this h2 to first h3 of next h2 in SOURCE POSITION ORDER
    # (not numerical order — h2 5 may appear before h2 1 in source)
    sorted_by_pos = sorted(h2_first_h3.keys(), key=lambda n: h2_first_h3[n][0])
    h2_bodies = {}
    for i, h2_num in enumerate(sorted_by_pos):
        start = h2_first_h3[h2_num][0]
        if i + 1 < len(sorted_by_pos):
            next_h2 = sorted_by_pos[i + 1]
            end = h2_first_h3[next_h2][0]
        else:
            end = len(content)
        h2_bodies[h2_num] = content[start:end]
    return h2_bodies


def main():
    with open(CURRENT_DOCX) as f:
        content = json.load(f)['data']['document']['content']

    print(f"Current docx: {len(content)} bytes")

    # Extract title + TL;DR
    header, after_h2 = extract_title_tldr(content)
    print(f"Header (title + TL;DR): {len(header)} bytes")

    # Extract 5 h2 tags
    h2_tags = extract_h2_tags(after_h2)
    print(f"Found {len(h2_tags)} h2 tags")

    # Group bodies by h2
    h2_bodies = group_bodies_by_h2(after_h2)
    for num, body in h2_bodies.items():
        print(f"  h2 {num} body: {len(body)} bytes")

    # Reconstruct: header + h2 1 + §1 body + h2 2 + §2 body + ... + h2 5 + §5 body
    new_content = header
    for h2_num in sorted(h2_bodies.keys()):
        # Find this h2's tag from h2_tags
        h2_tag = next((t for t in h2_tags if f'>{h2_num}. ' in t), None)
        if not h2_tag:
            continue
        new_content += h2_tag
        if h2_bodies[h2_num]:
            new_content += h2_bodies[h2_num]

    print(f"\nNew docx: {len(new_content)} bytes")

    # Audit
    h2_count = len(re.findall(r'<h2[^>]*?>', new_content))
    h3_count = len(re.findall(r'<h3[^>]*?>', new_content))
    h2_positions = [m.start() for m in re.finditer(r'<h2[^>]*?>', new_content)]
    h3_positions = [m.start() for m in re.finditer(r'<h3[^>]*?>', new_content)]
    print(f"\nAudit:")
    print(f"  h2 count: {h2_count}")
    print(f"  h3 count: {h3_count}")
    print(f"  h2 positions: {h2_positions}")
    print(f"  h3 first 10 positions: {h3_positions[:10]}")

    # Verify each h2 comes before its h3s
    print("\n  h2 vs h3 ordering check:")
    for h2_pos in h2_positions:
        # Find h2 number from the text
        m = re.search(r'<h2[^>]*?>(\d+)\.', new_content[h2_pos:h2_pos+200])
        if m:
            num = int(m.group(1))
            # Find h3 with this number
            h3_pat = re.compile(rf'<h3[^>]*?>{num}\.?\s')
            h3_match = h3_pat.search(new_content, h2_pos)
            if h3_match:
                print(f"    h2 {num} at {h2_pos}, first h3 with {num}. at {h3_match.start()} — {'OK' if h3_match.start() > h2_pos else 'WRONG ORDER'}")

    # Write
    (OUT_DIR / "v040-fixed.xml").write_text(new_content)
    print(f"\nWrote {OUT_DIR / 'v040-fixed.xml'}")


if __name__ == "__main__":
    main()
