#!/usr/bin/env python3
"""
fix-v012-tao-ci.py — Remove §1.4. 套磁与申请建议 section + renumber (teacher-report v0.12.0)

Trigger: user 2026-06-12 "修改 skill 模板里去掉《套磁与申请建议》然后应用到全部老师"

Strategy:
1. If obj_token not provided, fetch via drive +search to get fresh token
2. Fetch doc content
3. Find §1.4. 套磁 与申请建议 (or 套磁与行动建议) h2 block_id by text match
4. Find all block_ids between this h2 and next h2 (exclusive)
5. block_delete each block
6. block_replace §1.5 论文产出全景 → §1.4
7. block_replace §1.6 数据来源与说明 → §1.5
8. For docs with §1.6.x h3 → renumber to §1.5.x

Usage:
    python3 fix-v012-tao-ci.py [teacher_name]  # single teacher
    python3 fix-v012-tao-ci.py --all  # all 15 docs in 申博 space
    python3 fix-v012-tao-ci.py --from-tokens <tokens.json>  # use pre-fetched tokens
"""
import json, re, subprocess
import sys
import time
from pathlib import Path

DRY_RUN = False
RATE_LIMIT_MS = 1500  # 13 docs serial, 1.5s between ops

# Known taoci patterns (text → list of h3 to renumber)
TAOCI_PATTERNS = {
    '1.4. 套磁与行动建议': {
        # 毛玉仁 variant (simpler, no h3)
        'h3_renumbers': [],
    },
    '1.4. 套磁与申请建议': {
        # 高云君 + 13 旧 docs variant
        'h3_renumbers': [
            ('1.6.1. L1-L4 论文类数据源', '1.5.1.'),
            ('1.6.2. L7 社区类数据源 (v0.5.0 新增)', '1.5.2.'),
            ('1.6.3. ❓ 待补字段汇总 (建议补充路径)', '1.5.3.'),
        ],
    },
}


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
        if RATE_LIMIT_MS > 0: time.sleep(RATE_LIMIT_MS / 1000.0)
    print(f'  deleted: {deleted}/{len(blocks) + 1}')

    # Renumber h2 §1.5 → §1.4
    ok, msg = call_lark(obj, 'block_replace', block_id=h2_paper_id, content='<h2>1.4. 论文产出全景</h2>')
    print(f'  §1.5→§1.4: {"✓" if ok else "✗ " + msg}')
    if RATE_LIMIT_MS > 0: time.sleep(RATE_LIMIT_MS / 1000.0)

    # Renumber h2 §1.6 → §1.5
    ok, msg = call_lark(obj, 'block_replace', block_id=h2_data_id, content='<h2>1.5. 数据来源与说明</h2>')
    print(f'  §1.6→§1.5: {"✓" if ok else "✗ " + msg}')
    if RATE_LIMIT_MS > 0: time.sleep(RATE_LIMIT_MS / 1000.0)

    # Renumber h3 (if any)
    for h3_text, new_prefix in h3_renumbers:
        h3_id = find_block_id_by_text(content, 'h3', h3_text)
        if not h3_id:
            print(f'  ✗ h3 {h3_text[:30]} not found (likely absent in this doc)')
            continue
        re_pat = re.compile(rf'<h3[^>]*?id="{h3_id}"[^>]*>([^<]+)</h3>')
        m = re_pat.search(content)
        if not m: continue
        old_text = m.group(1).strip()
        new_text = re.sub(r'^1\.\d+\.\d*\.?', new_prefix, old_text)
        ok, msg = call_lark(obj, 'block_replace', block_id=h3_id, content=f'<h3>{new_text}</h3>')
        print(f'  h3 {h3_id[:20]} → {new_prefix}: {"✓" if ok else "✗ " + msg}')
        if RATE_LIMIT_MS > 0: time.sleep(RATE_LIMIT_MS / 1000.0)

    return True


def get_obj_token_via_search(teacher_name):
    """Fetch fresh obj_token via drive +search (stale tokens in wiki-children.json)."""
    r = subprocess.run(['lark-cli', 'drive', '+search', f'--query={teacher_name}'],
                       capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        return None
    data = json.loads(r.stdout)
    for item in data.get('data', {}).get('results', []):
        if item.get('entity_type') == 'WIKI':
            title_hl = item.get('summary_highlighted', '') + item.get('result_meta', {}).get('title_highlighted', '')
            if teacher_name in title_hl:
                return item.get('result_meta', {}).get('token')
    return None


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 fix-v012-tao-ci.py [teacher_name | --all | --from-tokens <tokens.json>]')
        sys.exit(1)

    targets = []

    if sys.argv[1] == '--from-tokens':
        # Use pre-fetched tokens JSON
        if len(sys.argv) < 3:
            print('Usage: --from-tokens <tokens.json>')
            sys.exit(1)
        tokens = json.load(open(sys.argv[2]))
        for teacher, obj in tokens.items():
            # Default pattern: most docs use 套磁与申请建议
            # Detect by trying to fetch content
            try:
                content = fetch_doc(obj)
                if '1.4. 套磁与行动建议' in content:
                    pattern = '1.4. 套磁与行动建议'
                else:
                    pattern = '1.4. 套磁与申请建议'
                targets.append((teacher, obj, pattern, TAOCI_PATTERNS[pattern]['h3_renumbers']))
            except Exception as e:
                print(f'  ⚠ {teacher}: fetch err: {e}')

    elif sys.argv[1] == '--all':
        # All 15 teachers (or those in the wiki space)
        # Get fresh tokens via drive search
        teachers = ['吴飞', '张圣宇', '刘泽民', '魏颖', '邓淑敏', '况琨', '沈春华', '肖俊',
                    '汤斯亮', '周晓巍', '赵洲', '毛玉仁', '高云君', '郑小林']
        for t in teachers:
            tok = get_obj_token_via_search(t)
            if tok:
                targets.append((t, tok, None, None))  # pattern will be auto-detected

    else:
        teacher = sys.argv[1]
        # Single teacher
        # Try wiki-children.json first, then drive search
        wiki = json.load(open('/tmp/wiki-children.json'))
        obj = None
        for n in wiki.get('data', {}).get('nodes', []):
            if teacher in n.get('title', ''):
                obj = n.get('obj_token', '')
                break
        if not obj:
            obj = get_obj_token_via_search(teacher)
        if obj:
            # Try fetch + detect pattern
            try:
                content = fetch_doc(obj)
                if '1.4. 套磁与行动建议' in content:
                    pattern = '1.4. 套磁与行动建议'
                else:
                    pattern = '1.4. 套磁与申请建议'
                targets.append((teacher, obj, pattern, TAOCI_PATTERNS[pattern]['h3_renumbers']))
            except Exception as e:
                print(f'  fetch err: {e}')

    if not targets:
        print('No targets found')
        sys.exit(1)

    # Apply
    results = []
    for teacher, obj, pattern, h3_renumbers in targets:
        if pattern is None:
            # Auto-detect
            try:
                content = fetch_doc(obj)
                if '1.4. 套磁与行动建议' in content:
                    pattern = '1.4. 套磁与行动建议'
                elif '1.4. 套磁与申请建议' in content:
                    pattern = '1.4. 套磁与申请建议'
                else:
                    print(f'  ⚠ {teacher}: no 套磁 section, skip')
                    continue
                h3_renumbers = TAOCI_PATTERNS[pattern]['h3_renumbers']
            except Exception as e:
                print(f'  ⚠ {teacher}: fetch err: {e}')
                continue
        ok = fix_taoci_section(obj, teacher, pattern, h3_renumbers)
        results.append({'teacher': teacher, 'ok': ok, 'pattern': pattern})

    print(f'\n=== Summary: {sum(1 for r in results if r["ok"])}/{len(results)} succeeded ===')
    for r in results:
        print(f'  {"✓" if r["ok"] else "✗"} {r["teacher"]} ({r["pattern"]})')


if __name__ == '__main__':
    main()
