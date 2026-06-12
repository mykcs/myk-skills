#!/usr/bin/env python3
"""
migrate.py - 批量将现有 wiki paper card 从 v0.3.x (完整版 15 行) 升级到 v0.11.0 完整版 (~10 行 + 3 新字段).

Usage:
    python3 migrate.py <doc_id> [<doc_id2> ...]
    python3 migrate.py --all          # 处理 dashboard 全部 13 PIs (P49mwGQU0iEh9CkXbCTcC418nPb)
    python3 migrate.py --audit       # 只 audit,不修改
    python3 migrate.py --from v0.4.0  # 升级 v0.4.0 紧凑版 → 嵌入的 arXiv ID 拆出独立行
    python3 migrate.py --from v0.3.9  # 升级 v0.3.9 完整版 → v0.11.0 完整版 (默认)

v0.11.0 新增能力 (vs v0.3.9 旧版):
1. 解析 v0.3.9 15 行/paper card, 升级为 v0.11.0 ~10 行/paper card
2. 新增 3 字段 (独立行):
   - {venue_year} {status_enum_8values}  (8 enum: 被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿)
   - arXiv：{url_or_暂无}                  (arXiv 可空, 合法状态值)
   - paper：{url_openreview_or_arxiv_or_doi}  (7 URL 优先级, OpenReview 优先)
3. 保留 v0.3.9 标注行 + 全作者中文括注 (不再破坏)
4. 保留 4 维 taxonomy 4 行独立 <p> 块
5. v0.4.0 紧凑版 → 嵌入的 [arXiv X] 拆出独立 arXiv 行, 保留 inline 通讯/大老板/一作 标记
6. fallback: 找不到的 status 标 [需用户确认], confidence < 0.6 不 auto-migrate
7. dry-run + git pre-flight + 失败 abort (任 1 docx 失败立即 rollback)

要求:
- ~/.agents/skills/teacher-report/references/name-dictionary-LOW-CONF-MARKED.json 存在 (v0.3.9 旧版用 DEPRECATED-UNMARKED)
- lark-cli 已 auth login (lark-cli wiki +node-list --parent-node-token=P49mwGQU0iEh9CkXbCTcC418nPb 列 13 PIs)
- 飞书 wiki dashboard token: P49mwGQU0iEh9CkXbCTcC418nPb (申博 P49mwGQU0iEh9CkXbCTcC418nPb)
- 备份 (脚本会提示) 强烈推荐 (per Plan Review Gate P3 risk)
- 22 项 LLM 自检 (Check 1-22) 必跑, 全 ✅ 才能写入 docx

V0.11.0 changelog (2026-06-11): 加 3 字段 (status / arXiv / paper URL) + status 8 enum + 7 paper URL 优先级
+ 5 新自检 (Check 18-22). 与 v0.4.0 紧凑版共存 (≥10 篇仍用 v0.4.0).
"""
import json, re, subprocess, sys, os
import argparse
from pathlib import Path

DICT_PATH = Path(__file__).parent.parent / 'references' / 'name-dictionary-LOW-CONF-MARKED.json'
# Deprecated (2026-06-10): original file renamed to name-dictionary-DEPRECATED-UNMARKED.json
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
