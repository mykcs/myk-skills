#!/usr/bin/env python3
"""
fix-v012-tao-ci.py — Remove §1.4. 套磁与申请建议 section + renumber (teacher-report v0.12.0)

Trigger: user 2026-06-12 "修改 skill 模板里去掉《套磁与申请建议》然后应用到全部老师"

Strategy:
1. Fetch doc content
2. Find §1.4. 套磁 与申请建议 (or 套磁与行动建议) h2 block_id by text match
3. Find all block_ids between this h2 and next h2 (exclusive)
4. block_delete each block
5. block_replace §1.5 论文产出全景 → §1.4
6. block_replace §1.6 数据来源与说明 → §1.5
7. For docs with §1.6.x h3 → renumber to §1.5.x

Usage:
    python3 fix-v012-tao-ci.py [teacher_name]  # default: 毛玉仁
    python3 fix-v012-tao-ci.py 毛玉仁
    python3 fix-v012-tao-ci.py 高云君
    python3 fix-v012-tao-ci.py --all  # apply to all 13 docs that match pattern
"""
import json, re, subprocess
import sys
from pathlib import Path

DRY_RUN = False
RATE_LIMIT_MS = 200

WIKI_CHILDREN = '/tmp/wiki-children.json'
WIKI_SPACE = 'P49mwGQU0iEh9CkXbCTcC418nPb'  # 申博 space


def call_lark(obj, cmd_name, **kwargs):
    cmd = ['lark-cli', 'docs', '+update', '--api-version=v2', f'--doc={obj}',
           f'--command={cmd_name}']
    for k, v in kwargs.items():
        flag = k.replace('_', '-')
        cmd.append(f'--{flag}={v}')
    if DRY_RUN:
        cmd.append('--dry-run')
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    ok = r.returncode == 0 and '"ok": false' not in r.stdout and '"success": false' not in r.stdout
    return ok, r.stdout[:200] if not ok else 'OK'


def find_block_id_by_text(content, tag, text):
    m = re.search(rf'<{tag}[^>]*?id="([^"]+)"[^>]*?>{re.escape(text)}</{tag}>', content)
    if m: return m.group(1)
    m = re.search(rf'<{tag}[^>]*?id="([^"]+)"[^>]*?>([^<]*{re.escape(text[:6])}[^<]*)</{tag}>', content)
    return m.group(1) if m else None


def find_blocks_between(content, h2_id_start, h2_id_next):
    pos = content.find(f'id="{h2_id_start}"')
    if pos < 0: return []
    end = content.find(f'id="{h2_id_next}"')
    if end < 0: end = len(content)
    sub = content[pos:end]
    id_re = re.compile(r'<(?:h[1-6]|p|callout|grid|column|table|todo|code|quote|list|bullet|ordered)[^>]*?\sid="([^"]+)"')
    return list(dict.fromkeys(m.group(1) for m in id_re.finditer(sub)))


def fetch_doc(obj):
    out = subprocess.check_output(
        ['lark-cli', 'docs', '+fetch', '--api-version=v2', '--doc', obj, '--detail=with-ids', '--format=json'],
        stderr=subprocess.DEVNULL, timeout=30
    )
    return json.loads(out).get('data', {}).get('document', {}).get('content', '')


def fix_taoci_section(obj, teacher_name, h2_taoci_text, h3_renumbers=None):
    """Apply v0.12.0 fix to one doc."""
    h3_renumbers = h3_renumbers or []
    print(f'\n=== {teacher_name} ({obj}) ===')

    try:
        content = fetch_doc(obj)
    except Exception as e:
        print(f'  fetch err: {e}')
        return False

    # Find h2 block_ids by text
    h2_taoci_id = find_block_id_by_text(content, 'h2', h2_taoci_text)
    h2_paper_id = find_block_id_by_text(content, 'h2', '1.5. 论文产出全景')
    h2_data_id = find_block_id_by_text(content, 'h2', '1.6. 数据来源与说明')

    if not all([h2_taoci_id, h2_paper_id, h2_data_id]):
        print(f'  ⚠ missing block ids (taoci={h2_taoci_id}, paper={h2_paper_id}, data={h2_data_id}), skip')
        return False

    print(f'  h2 taoci: {h2_taoci_id}')
    print(f'  h2 paper: {h2_paper_id}')
    print(f'  h2 data:  {h2_data_id}')

    # Find blocks to delete
    blocks = find_blocks_between(content, h2_taoci_id, h2_paper_id)
    blocks = [b for b in blocks if b != h2_taoci_id]
    print(f'  blocks to delete: {len(blocks)}')

    # Delete
    deleted = 0
    for bid in [h2_taoci_id] + blocks:
        ok, msg = call_lark(obj, 'block_delete', block_id=bid)
        if ok: deleted += 1
        else: print(f'    ✗ delete {bid[:25]}: {msg}')
    print(f'  deleted: {deleted}/{len(blocks) + 1}')

    # Renumber h2 §1.5 → §1.4
    ok, msg = call_lark(obj, 'block_replace', block_id=h2_paper_id, content='<h2>1.4. 论文产出全景</h2>')
    print(f'  §1.5→§1.4: {"✓" if ok else "✗ " + msg}')

    # Renumber h2 §1.6 → §1.5
    ok, msg = call_lark(obj, 'block_replace', block_id=h2_data_id, content='<h2>1.5. 数据来源与说明</h2>')
    print(f'  §1.6→§1.5: {"✓" if ok else "✗ " + msg}')

    # Renumber h3 (if any)
    for h3_text, new_prefix in h3_renumbers:
        h3_id = find_block_id_by_text(content, 'h3', h3_text)
        if not h3_id:
            print(f'  ✗ h3 {h3_text[:30]} not found')
            continue
        re_pat = re.compile(rf'<h3[^>]*?id="{h3_id}"[^>]*>([^<]+)</h3>')
        m = re_pat.search(content)
        if not m: continue
        old_text = m.group(1).strip()
        new_text = re.sub(r'^1\.\d+\.\d*\.?', new_prefix, old_text)
        ok, msg = call_lark(obj, 'block_replace', block_id=h3_id, content=f'<h3>{new_text}</h3>')
        print(f'  h3 {h3_id[:20]} → {new_prefix}: {"✓" if ok else "✗ " + msg}')

    return True


# Known taoci patterns (text → list of h3 to renumber)
TAOCI_PATTERNS = {
    '1.4. 套磁与行动建议': {
        'teacher_keys': ['毛玉仁'],
        'h3_renumbers': [],  # 毛玉仁 has no h3 in §1.4
    },
    '1.4. 套磁与申请建议': {
        'teacher_keys': ['高云君'],
        'h3_renumbers': [
            ('1.6.1. L1-L4 论文类数据源', '1.5.1.'),
            ('1.6.2. L7 社区类数据源 (v0.5.0 新增)', '1.5.2.'),
            ('1.6.3. ❓ 待补字段汇总 (建议补充路径)', '1.5.3.'),
        ],
    },
}


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 fix-v012-tao-ci.py [teacher_name | --all]')
        sys.exit(1)

    wiki = json.load(open(WIKI_CHILDREN))

    if sys.argv[1] == '--all':
        targets = []
        for pattern, info in TAOCI_PATTERNS.items():
            for teacher_key in info['teacher_keys']:
                for n in wiki.get('data', {}).get('nodes', []):
                    if teacher_key in n.get('title', ''):
                        targets.append((n.get('title', ''), n.get('obj_token', ''), pattern, info['h3_renumbers']))
                        break
    else:
        teacher = sys.argv[1]
        targets = []
        for pattern, info in TAOCI_PATTERNS.items():
            for n in wiki.get('data', {}).get('nodes', []):
                if teacher in n.get('title', ''):
                    targets.append((n.get('title', ''), n.get('obj_token', ''), pattern, info['h3_renumbers']))
                    break

    if not targets:
        print(f'No matching teacher found in wiki children')
        sys.exit(1)

    for title, obj, pattern, h3_renumbers in targets:
        fix_taoci_section(obj, title, pattern, h3_renumbers)


if __name__ == '__main__':
    main()
