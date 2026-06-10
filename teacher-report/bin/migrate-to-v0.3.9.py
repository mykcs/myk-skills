#!/usr/bin/env python3
"""
migrate-to-v0.3.9.py - 批量将现有 wiki 的作者列表从 v0.3.3 (仅 Fei Wu 单独标)
升级到 v0.3.9 (全作者中文括注)。

Usage:
    python3 migrate-to-v0.3.9.py <doc_id> [<doc_id2> ...]
    python3 migrate-to-v0.3.9.py --all          # 处理 dashboard 全部 9 nodes
    python3 migrate-to-v0.3.9.py --audit       # 只 audit,不修改

功能:
1. 从 lark-cli 获取 wiki content
2. 解析所有 作者: 块
3. 对每作者查 name-dictionary-v0.3.9.json 加中文括注
4. block_replace 更新到 wiki
5. 显示 audit 报告

要求:
- ~/.agents/skills/teacher-report/references/name-dictionary-v0.3.9.json 存在
- lark-cli 已 auth login
- 备份 (脚本会提示) 虽非强制,推荐 SKILL.md §D
"""
import json, re, subprocess, sys, os
import argparse
from pathlib import Path

DICT_PATH = Path(__file__).parent.parent / 'references' / 'name-dictionary-v0.3.9-LOW-CONF-MARKED.json'
# Deprecated (2026-06-10): original file renamed to name-dictionary-v0.3.9-DEPRECATED-UNMARKED.json
# Use the LOW-CONF-MARKED version so LOW values carry ' // LOW-CONF' suffix visible in output.
DASHBOARD_TOKEN = 'P49mwGQU0iEh9CkXbCTcC418nPb'


def load_dict():
    with open(DICT_PATH) as f:
        return json.load(f)


def lookup_zh(name_en, name_dict):
    """Look up Chinese name from dictionary.

    LOW-CONF values from the marked dictionary carry a ' // LOW-CONF' suffix.
    Return tuple (zh, is_low_conf) so callers can decide whether to keep the
    suffix in the output (visual warning) or strip it.
    """
    def _lookup(entry):
        v = name_dict.get(entry)
        if v is None:
            return None, False
        if v.endswith(' // LOW-CONF'):
            return v[: -len(' // LOW-CONF')], True
        return v, False

    zh, low = _lookup(name_en)
    if zh:
        return zh, low
    if ', ' in name_en:
        parts = name_en.split(', ', 1)
        if len(parts) == 2:
            rev = f'{parts[1]} {parts[0]}'
            zh, low = _lookup(rev)
            if zh:
                return zh, low
    return None, False


def transform_authors(authors_line, name_dict):
    """Transform author list to v0.3.9 - each author needs Chinese parens.

    Supports BOTH formats:
      1. "Last, First（中文）" (CSV-style, comma between last and first)
      2. "First Last（中文）"  (no comma, wiki-style)

    The previous regex only matched format 1, missing the wiki's format 2.
    Fix: split authors on commas/Chinese-paren boundaries, then look up each.
    """
    # Strategy: split on commas not inside Chinese parens, then process each piece
    # Each piece is either "Last, First" or "First Last" or "Last, First（中文）"
    parts = []
    current = []
    paren_depth = 0
    for ch in authors_line:
        if ch == '（':
            paren_depth += 1
            current.append(ch)
        elif ch == '）':
            paren_depth = max(0, paren_depth - 1)
            current.append(ch)
        elif ch == ',' and paren_depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())

    result = []
    for part in parts:
        if not part:
            continue
        # Check if already has Chinese parens (skip if so, already v0.3.9)
        if '（' in part and '）' in part:
            # Already in v0.3.9 format, leave alone
            result.append(part)
            continue
        # Look up
        zh, low_conf = lookup_zh(part, name_dict)
        if zh:
            marker = ' // LOW-CONF' if low_conf else ''
            result.append(f'{part}（{zh}）{marker}')
        else:
            # No match - try first 2 words as key
            words = part.split()
            if len(words) >= 2:
                # Try "First Last" reversed to "Last First"
                alt = f'{words[-1]} {words[0]}'
                zh2, low2 = lookup_zh(alt, name_dict)
                if zh2:
                    marker = ' // LOW-CONF' if low2 else ''
                    result.append(f'{part}（{zh2}）{marker}')
                    continue
            result.append(part)
    return ', '.join(result)


def has_full_v039(authors_line):
    """Check if all authors have Chinese parens."""
    n_surnames = len(re.findall(r'[A-Z][a-zA-Z\-\']+', authors_line))
    n_authors = n_surnames // 2
    n_ann = authors_line.count('（')
    return n_authors > 0 and n_ann >= n_authors


def fetch_doc(doc_id):
    """Fetch doc with full details."""
    r = subprocess.run(
        ['lark-cli', 'docs', '+fetch', '--api-version=v2', f'--doc={doc_id}', '--detail', 'with-ids'],
        capture_output=True, text=True
    )
    return json.loads(r.stdout)


def update_block(doc_id, block_id, content):
    """Update a single block via lark-cli."""
    r = subprocess.run(
        ['lark-cli', 'docs', '+update', '--api-version=v2', f'--doc={doc_id}',
         '--command', 'block_replace', f'--block-id={block_id}', f'--content={content}'],
        capture_output=True, text=True
    )
    return '"result": "success"' in r.stdout


def process_doc(doc_id, name_dict, audit_only=False):
    """Process one doc: find all author blocks, transform, optionally update."""
    d = fetch_doc(doc_id)
    content = d['data']['document']['content']
    title = d['data']['document'].get('title', doc_id)

    author_markers = [m.start() for m in re.finditer(r'作者[：:]</p>', content)]

    stats = {'full': 0, 'partial': 0, 'placeholder': 0, 'updated': 0, 'unmapped': []}
    seen_bids = set()

    for pos in author_markers:
        rest = content[pos:pos+2000]
        m = re.search(r'<p[^>]*?id="([^"]+)"[^>]*?>([^<]+)</p>', rest)
        if not m or m.group(1) in seen_bids:
            continue
        seen_bids.add(m.group(1))
        author_bid = m.group(1)
        text = m.group(2).strip()

        if '待补' in text or '完整作者列表' in text:
            stats['placeholder'] += 1
            continue
        if not re.search(r'[A-Z][a-z]+', text):
            continue

        if has_full_v039(text):
            stats['full'] += 1
        else:
            stats['partial'] += 1
            new_text = transform_authors(text, name_dict)
            if new_text != text:
                if not audit_only:
                    if update_block(doc_id, author_bid, f'<p>{new_text}</p>'):
                        stats['updated'] += 1
                for m2 in re.finditer(
                    r'([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)*)',
                    text
                ):
                    if '（' not in m2.group(0):
                        zh, _low_conf = lookup_zh(m2.group(0), name_dict)
                        if not zh:
                            key = f'{title[:30]}:{m2.group(0)}'
                            if key not in stats['unmapped']:
                                stats['unmapped'].append(key)

    return stats


def get_all_dashboard_wikis():
    """Get all 9 wiki docs from dashboard."""
    r = subprocess.run(
        ['lark-cli', 'api', 'GET',
         '/open-apis/wiki/v2/spaces/-/nodes',
         '--params', f'{{"parent_node_token": "{DASHBOARD_TOKEN}", "page_size": 50}}'],
        capture_output=True, text=True
    )
    d = json.loads(r.stdout)
    items = d.get('data', {}).get('items', [])
    return [item['obj_token'] for item in items if item.get('obj_type') == 'docx']


def main():
    parser = argparse.ArgumentParser(description='Migrate wikis to v0.3.9 author format')
    parser.add_argument('doc_ids', nargs='*', help='Doc IDs to migrate')
    parser.add_argument('--all', action='store_true', help='Migrate all 9 dashboard wikis')
    parser.add_argument('--audit', action='store_true', help='Audit only, no modification')
    args = parser.parse_args()

    if not DICT_PATH.exists():
        print(f'❌ Dictionary not found: {DICT_PATH}')
        print('Run: git pull in ~/.agents/skills/teacher-report')
        sys.exit(1)

    name_dict = load_dict()
    print(f'Loaded {len(name_dict)} name mappings from {DICT_PATH}')
    print()

    if args.all:
        doc_ids = get_all_dashboard_wikis()
        print(f'Found {len(doc_ids)} docs in dashboard')
    else:
        doc_ids = args.doc_ids

    if not doc_ids:
        print('No docs to process')
        sys.exit(0)

    print(f'Mode: {"audit-only" if args.audit else "migrate"}')
    print()
    print(f'{"Doc":12s} {"v0.3.9":10s} {"partial":10s} {"placeholder":12s} {"updated":10s} {"unmapped"}')
    print('='*100)

    total_updated = 0
    all_unmapped = []
    for doc_id in doc_ids:
        stats = process_doc(doc_id, name_dict, audit_only=args.audit)
        d = fetch_doc(doc_id)
        title = d['data']['document'].get('title', doc_id)[:20]
        print(f'{title:12s} {stats["full"]:10d} {stats["partial"]:10d} {stats["placeholder"]:12d} {stats["updated"]:10d} {len(stats["unmapped"])}')
        total_updated += stats['updated']
        all_unmapped.extend(stats['unmapped'])

    print('='*100)
    print(f'Total updated: {total_updated}')
    print(f'Total unmapped: {len(all_unmapped)}')
    if all_unmapped:
        print('\nUnmapped authors (need dict update):')
        for u in all_unmapped[:20]:
            print(f'  {u}')

if __name__ == '__main__':
    main()
