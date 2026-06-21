#!/usr/bin/env python3
"""通用 h2 顺序修复脚本 - 适用任意 teacher-report docx.

用法:
  python3 reorder-h2-fix.py --doc <DOC_OBJ_TOKEN> [--output /path/to/fixed.xml]

流程:
  1. fetch docx 当前内容
  2. 解析 h2/h3 位置
  3. 重新组装: title + TL;DR + h2 1 + §1 bodies + h2 2 + §2 bodies + ... + h2 5 + §5 bodies
  4. 写到 stdout 或文件 (供 lark-cli 后续 upload)
"""
import json
import re
import sys
import subprocess
import argparse
from pathlib import Path


def fetch_docx(doc_token):
    """Fetch docx content via lark-cli."""
    result = subprocess.run(
        ['lark-cli', 'docs', '+fetch', '--api-version', 'v2', '--doc', doc_token, '--format', 'json'],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"lark-cli fetch failed: {result.stderr}")
    return json.loads(result.stdout)['data']['document']['content']


def extract_title_tldr(content):
    """Extract everything before the first h2."""
    first_h2 = re.search(r'<h2[^>]*?>', content)
    if not first_h2:
        return content, ''
    return content[:first_h2.start()], content[first_h2.start():]


def extract_h2_tags(content):
    """Extract all 5 h2 tags in source order."""
    return re.findall(r'<h2[^>]*?>.*?</h2>', content, re.DOTALL)


def group_bodies_by_h2(content):
    """Walk content after first h2; group body blocks by their parent h2 number.

    h3 classification rules:
    - "N.M Title" (e.g., "1.1 基本信息") → parent h2 = N
    - "N. Title" (e.g., "1. SkillX: ...") → parent h2 = 4 (paper cards)
    - Fallback: use last h2 before this h3
    """
    h2_positions = []
    for m in re.finditer(r'<h2[^>]*?>(\d+)\. ([^<]+)</h2>', content):
        h2_positions.append((m.start(), int(m.group(1))))
    h3_positions = []
    for m in re.finditer(r'<h3[^>]*?>(.*?)</h3>', content, re.DOTALL):
        h3_positions.append((m.start(), m.end(), m.group(1)))

    if not h2_positions:
        return {}

    h2_first_h3 = {}
    for h3_start, h3_end, h3_text in h3_positions:
        m = re.match(r'(\d+)\.(\d+)\s', h3_text.strip())
        if m:
            parent_h2 = int(m.group(1))
        else:
            m2 = re.match(r'(\d+)\.\s+\w', h3_text.strip())
            if m2:
                parent_h2 = 4  # paper cards in §4
            else:
                parent_h2 = max((h2[1] for h2 in h2_positions if h2[0] < h3_start), default=1)

        if parent_h2 not in h2_first_h3 or h3_start < h2_first_h3[parent_h2][0]:
            h2_first_h3[parent_h2] = (h3_start, h3_end, h3_text)

    # Build h2 bodies in source position order
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


def check_h2_order(content):
    """Check if 5 h2 are concentrated at top of doc. Returns (passed, info)."""
    h2_positions = [m.start() for m in re.finditer(r'<h2[^>]*?>', content)]
    if len(h2_positions) < 5:
        return True, f"only {len(h2_positions)} h2s (no order issue)"
    first_5_range = max(h2_positions[:5]) - min(h2_positions[:5])
    doc_len = len(content)
    if first_5_range < doc_len * 0.05:
        return False, f"❌ 5 h2 集中 doc 前 5% ({first_5_range}/{doc_len*0.05:.0f} bytes)"
    return True, f"✅ h2 已散开 (first 5 span {first_5_range} bytes)"


def reorder_h2(content):
    """Reorder doc content so h2 are interspersed with their h3s."""
    header, after_h2 = extract_title_tldr(content)
    h2_tags = extract_h2_tags(after_h2)
    h2_bodies = group_bodies_by_h2(after_h2)

    new_content = header
    for h2_num in sorted(h2_bodies.keys()):
        h2_tag = next((t for t in h2_tags if f'>{h2_num}. ' in t), None)
        if not h2_tag:
            continue
        new_content += h2_tag
        if h2_bodies[h2_num]:
            new_content += h2_bodies[h2_num]
    return new_content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doc', required=True, help='docx obj_token')
    ap.add_argument('--output', help='output XML file (default: stdout)')
    ap.add_argument('--dry-run', action='store_true', help='only check, do not output')
    args = ap.parse_args()

    print(f"Fetching docx {args.doc}...")
    content = fetch_docx(args.doc)
    print(f"  bytes: {len(content)}")

    # Pre-check
    pre_passed, pre_info = check_h2_order(content)
    print(f"Pre-check: {pre_info}")

    if pre_passed:
        print("No fix needed.")
        if not args.dry_run:
            print(content)
        return 0

    # Reorder
    new_content = reorder_h2(content)
    print(f"  reordered: {len(new_content)} bytes")

    # Post-check
    post_passed, post_info = check_h2_order(new_content)
    print(f"Post-check: {post_info}")

    if not args.dry_run:
        if args.output:
            Path(args.output).write_text(new_content)
            print(f"  written to {args.output}")
        else:
            sys.stdout.write(new_content)

    return 0 if post_passed else 1


if __name__ == "__main__":
    sys.exit(main())
