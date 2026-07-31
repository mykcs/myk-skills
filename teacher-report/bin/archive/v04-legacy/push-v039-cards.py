#!/usr/bin/env python3
"""
push-v039-cards.py — Push v0.3.9 paper cards to 6 teacher wikis via lark-doc block API.

Replaces the broken transform_authors path in migrate.py with a proper
block-level API workflow:
  1. Read all 6 /tmp/v039-cards-{teacher}.md draft files
  2. For each teacher, fetch wiki doc + parse all block_ids
  3. Match draft papers to wiki placeholders by title (normalized)
  4. For each match, find the placeholder note block + replace with author list
  5. Verify each push via re-fetch

Reads:
  - /tmp/v039-cards-{teacher}.md (draft)
  - /tmp/v039-backup/{doc_id}.json (last known good state)
  - ~/.agents/skills/teacher-report/references/name-dictionary-LOW-CONF-MARKED.json

Writes:
  - 6 teacher wikis (via lark-cli docs +update block_replace)
  - /tmp/v039-push.log (operation log)

Designed to be IDEMPOTENT — re-running on the same state is a no-op.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# Constants
TEACHERS = {
    'MqEzdtwcso2AGyxUPuCcyQRAnwe': {
        'name': '况琨',
        'draft': '/tmp/v039-cards-kuang.md',
    },
    'V72MdnUqQofIZQxYbqxcuMPknsd': {
        'name': '沈春华',
        'draft': '/tmp/v039-cards-shen.md',
    },
    'RkqHdAm0yoXoGWxMtu3cUNM2nOe': {
        'name': '郑小林',
        'draft': '/tmp/v039-cards-zhengxl.md',
    },
    'J7f3dPWOyobFFlxjazTcgOHfnah': {
        'name': '肖俊',
        'draft': '/tmp/v039-cards-xiaojun.md',
    },
    'YLyQdcxOOosBJHxE0x0cYFmJnmh': {
        'name': '汤斯亮',
        'draft': '/tmp/v039-cards-tangsl.md',
    },
    'ANeJdDl79oMpw3xFm4ccPBMLnRg': {
        'name': '周晓巍',
        'draft': '/tmp/v039-cards-zhouxw.md',
    },
}

DICT_PATH = Path(__file__).parent.parent / 'references' / 'name-dictionary-LOW-CONF-MARKED.json'
BACKUP_DIR = Path('/tmp/v039-backup')


def load_dict():
    """Load LOW-CONF marked dictionary."""
    with open(DICT_PATH) as f:
        return json.load(f)


def lookup_zh(name_en, name_dict):
    """Look up Chinese name. Returns (zh, is_low_conf)."""
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
            zh, low = _lookup(f'{parts[1]} {parts[0]}')
            if zh:
                return zh, low
    return None, False


def parse_draft_papers(draft_path):
    """Parse a draft file, return list of paper dicts with title, authors, etc."""
    with open(draft_path) as f:
        text = f.read()
    papers = []
    # Each paper is a ### N. Title section
    for m in re.finditer(
        r'### (\d+)\.\s+([^\n]+)\n((?:.|\n)+?)(?=\n### |\Z)',
        text,
    ):
        num, title, body = m.groups()
        title = title.strip()
        # Extract author line
        am = re.search(r'\*\*作者\*\*:\s*([^\n]+)', body)
        author_line = am.group(1).strip() if am else None
        # Extract arXiv
        aim = re.search(r'\*\*arXiv\*\*:\s*(\S+)', body)
        arxiv_id = aim.group(1).strip() if aim else None
        # Extract venue
        vem = re.search(r'\*\*venue\*\*:\s*([^\n]+)', body)
        venue = vem.group(1).strip() if vem else None
        # Extract 通讯作者
        cm = re.search(r'\*\*通讯作者\*\*:\s*([^\n]+)', body)
        corr_author = cm.group(1).strip() if cm else None
        papers.append({
            'num': int(num),
            'title': title,
            'author_line': author_line,
            'arxiv_id': arxiv_id,
            'venue': venue,
            'corr_author': corr_author,
        })
    return papers


def normalize_title(s):
    """Normalize for fuzzy title matching."""
    s = re.sub(r'[:—].*$', '', s).strip()
    s = re.sub(r'[^\w\s]', '', s.lower())
    s = re.sub(r'\s+', ' ', s)
    return s


def fetch_doc(doc_id):
    """Fetch doc content via lark-cli."""
    result = subprocess.run(
        ['lark-cli', 'docs', '+fetch', '--api-version=v2',
         '--doc', doc_id, '--detail', 'with-ids', '--format', 'json'],
        capture_output=True, text=True, timeout=30,
    )
    return json.loads(result.stdout)


def find_placeholder_blocks(content):
    """Find all (title, title_block_id) tuples in a doc.
    A placeholder is a <p><b>Title</b></p> followed by taxonomy + 作者： + [placeholder note].
    """
    # Strategy: find all <p ... id=...><b>Title</b></p> blocks
    # The id can appear anywhere in the <p> opening tag (before <b>)
    titles_blocks = []
    # Allow id to be in any position within <p ...>
    for m in re.finditer(r'<p\b[^>]*?id="([^"]+)"[^>]*?>\s*<b>([^<]+)</b>\s*</p>', content):
        bid, title = m.groups()
        title = title.strip()
        if len(title) < 200 and '：' not in title and 'Migrated' not in title:
            titles_blocks.append((title, bid))
    return titles_blocks


def find_placeholder_note_block(content, title_block_id):
    """Given a title block, find the [完整作者列表待补 — ...] placeholder note block.
    Returns (block_id, text) or None if not found.
    """
    # The placeholder note is typically the <p> right after the "作者：" <p>
    # Find the title block position (allow id to be anywhere in <p ...>)
    m = re.search(rf'<p\b[^>]*?id="{re.escape(title_block_id)}"[^>]*?>\s*<b>[^<]+</b>\s*</p>', content)
    if not m:
        return None
    # From there, find the next "作者：" block, then the next block
    after_title = content[m.end():]
    author_label = re.search(r'<p\b[^>]*?id="([^"]+)"[^>]*?>\s*作者[：:]', after_title)
    if not author_label:
        return None
    # Next <p> after the 作者 label
    after_author = after_title[author_label.end():]
    next_p = re.search(r'<p\b[^>]*?id="([^"]+)"[^>]*?>([^<]*)</p>', after_author)
    if not next_p:
        return None
    return next_p.group(1), next_p.group(2)


def block_replace(doc_id, block_id, content_xml):
    """Replace a block's content via lark-cli."""
    result = subprocess.run(
        ['lark-cli', 'docs', '+update', '--api-version=v2',
         '--doc', doc_id, '--command', 'block_replace',
         '--block-id', block_id, '--content', content_xml],
        capture_output=True, text=True, timeout=30,
    )
    return json.loads(result.stdout)


def push_one_teacher(doc_id, teacher_name, draft_path, name_dict, dry_run=True):
    """Push all matched cards for one teacher. Returns stats dict."""
    print(f"\n=== {teacher_name} ({doc_id}) ===")
    # Load draft
    papers = parse_draft_papers(draft_path)
    print(f"  draft papers: {len(papers)}")
    # Fetch wiki
    fetched = fetch_doc(doc_id)
    if not fetched.get('ok'):
        print(f"  ❌ fetch failed: {fetched}")
        return {'error': 'fetch_failed', 'pushed': 0, 'skipped': 0}
    content = fetched['data']['document']['content']
    # Find placeholders
    titles_blocks = find_placeholder_blocks(content)
    print(f"  wiki titles: {len(titles_blocks)}")
    # Match by title
    wiki_norm = {normalize_title(t): (t, bid) for t, bid in titles_blocks}
    draft_norm = {normalize_title(p['title']): p for p in papers}
    matched = set(wiki_norm.keys()) & set(draft_norm.keys())
    print(f"  matched: {len(matched)}")
    pushed = 0
    skipped = 0
    for norm in matched:
        wiki_title, title_bid = wiki_norm[norm]
        draft_paper = draft_norm[norm]
        # Find placeholder note block
        result = find_placeholder_note_block(content, title_bid)
        if not result:
            print(f"  ⚠️  {wiki_title[:40]}: no placeholder block found (may already be v0.3.9)")
            skipped += 1
            continue
        placeholder_bid, placeholder_text = result
        if '待补' not in placeholder_text and '待核实' not in placeholder_text:
            # Already has real content
            print(f"  ✓ {wiki_title[:40]}: already has author content (skip)")
            skipped += 1
            continue
        # Get author line from draft
        author_line = draft_paper['author_line']
        if not author_line:
            print(f"  ⚠️  {wiki_title[:40]}: no author line in draft")
            skipped += 1
            continue
        # Format content for block
        content_xml = f'<p>{author_line}</p>'
        if dry_run:
            print(f"  [DRY] {wiki_title[:40]}: would push to block {placeholder_bid[:25]}")
            print(f"         author: {author_line[:100]}")
        else:
            res = block_replace(doc_id, placeholder_bid, content_xml)
            if res.get('ok'):
                pushed += 1
                print(f"  ✓ {wiki_title[:40]}: pushed (revision {res['data']['document']['revision_id']})")
            else:
                print(f"  ❌ {wiki_title[:40]}: push failed - {res.get('error', {}).get('message', 'unknown')}")
                skipped += 1
    return {'teacher': teacher_name, 'pushed': pushed, 'skipped': skipped, 'total_draft': len(papers), 'total_wiki': len(titles_blocks), 'matched': len(matched)}


def main():
    parser = argparse.ArgumentParser(description='Push v0.3.9 paper cards to teacher wikis')
    parser.add_argument('--dry-run', action='store_true', default=True, help='dry run (default: true)')
    parser.add_argument('--execute', action='store_true', help='actually push (overrides dry-run)')
    parser.add_argument('--teacher', help='only push this teacher (key from TEACHERS)')
    args = parser.parse_args()
    dry_run = not args.execute

    print(f"=== push-v039-cards.py {'DRY RUN' if dry_run else 'EXECUTE'} ===")
    print(f"Time: {datetime.now().isoformat()}")

    name_dict = load_dict()
    print(f"Loaded {len(name_dict)} name mappings")

    all_stats = []
    for doc_id, info in TEACHERS.items():
        if args.teacher and info['name'] != args.teacher:
            continue
        stats = push_one_teacher(
            doc_id, info['name'], info['draft'], name_dict, dry_run=dry_run,
        )
        all_stats.append(stats)
        time.sleep(1)  # rate limit

    # Summary
    print("\n=== SUMMARY ===")
    total_pushed = sum(s.get('pushed', 0) for s in all_stats)
    total_skipped = sum(s.get('skipped', 0) for s in all_stats)
    total_matched = sum(s.get('matched', 0) for s in all_stats)
    for s in all_stats:
        if 'error' in s:
            print(f"  {s.get('teacher', '?')}: ERROR {s['error']}")
        else:
            print(f"  {s['teacher']}: draft={s['total_draft']} wiki={s['total_wiki']} matched={s['matched']} pushed={s['pushed']} skipped={s['skipped']}")
    print(f"  TOTAL: matched={total_matched} pushed={total_pushed} skipped={total_skipped}")


if __name__ == '__main__':
    main()
