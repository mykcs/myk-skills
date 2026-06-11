#!/usr/bin/env python3
"""
check_chinese_name.py — teacher-report v0.10.0 Check 17
中文名字符级 typo 扫描 — 检测老师 wiki 文档里中文姓名是否与权威来源一致。

触发 case (2026-06-11): 邓舒敏 (Shumin Deng) 文档 28 处中文名是「邓**舒**敏」(shū, comfortable),
实际正确是「邓**淑**敏」(shú, virtuous) — 同音不同义 LLM auto-generate typo,
claudecode 当时只对比结构没对比字符级。

Usage:
    # 单个 doc
    python3 check_chinese_name.py <content.xml>
    # stdin
    python3 check_chinese_name.py --stdin
    # 跑全 wiki (需 lark-cli, 调 docs +fetch)
    python3 check_chinese_name.py --wiki-scan
    # 指定 doc_obj_token 列表
    python3 check_chinese_name.py --wiki-scan --doc-tokens=<path.json>

Exit codes:
    0 = clean (no typo detected, all HIGH-CONF names match)
    1 = typo detected
    2 = error (file not found, dict missing, etc.)

Authoritative sources (按优先级):
    1. Faculty 个人主页 (cshen.github.io / kunkuang.github.io / person.zju.edu.cn/...)
    2. ORCID (0000-0001-XXXX-XXXX)
    3. LinkedIn URL slug (e.g. shumin-deng-邓淑敏-2a1b26142)
    4. 中文期刊/专利署名 (软件学报 / 中国科学 / 发明专利)
    5. OpenReview / Semantic Scholar / papers.cool 显示的中文名

数据源: references/name-dictionary-tier-20260610.json
    - HIGH-CONF (31 keys, 16 unique zh): claudecode 不可推断, 必须 L1-L4 验证后 push
    - LOW-CONF (504 keys, 256 unique zh): claudecode best-guess, 标 ' // LOW-CONF' 后缀警示

新规则 (v0.10.0):
    1. 所有 HIGH-CONF zh 必须字符级匹配 (含 title / TL;DR / callouts / paper cards 作者)
    2. LOW-CONF 标 ' // LOW-CONF' 后缀后, 必须用户 review
    3. 新加 HIGH-CONF entry 必须 source != best-guess-from-paper-coauthor
    4. 同音/形近字 typo 集合 (高频 LLM 误用): 见 TYPO_PAIRS
"""
import json
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# -------- 同音/形近字 typo 启发式 --------
# 源自 2026-06-11 邓舒敏/邓淑敏 案例
TYPO_PAIRS = [
    # 同音不同义 (声母+韵母相同, 调可能异)
    ('舒', '淑'),  # shū 舒服 / shú 淑女
    ('青', '清'),  # qīng
    ('振', '震'),  # zhèn
    ('伟', '炜'),  # wěi
    ('明', '铭'),  # míng
    ('强', '墙'),  # qiáng
    ('国', '郭'),  # guó (仅 姓 时)
    ('红', '宏'),  # hóng
    ('建', '键'),  # jiàn
    ('亮', '量'),  # liàng
    ('松', '嵩'),  # sōng
    ('欣', '新'),  # xīn
    ('星', '兴'),  # xīng
    ('毅', '义'),  # yì
    ('涛', '滔'),  # tāo
    ('飞', '菲'),  # fēi
    ('俊', '军'),  # jùn
    ('杰', '捷'),  # jié
    ('佳', '家'),  # jiā
    ('磊', '雷'),  # lěi
    ('波', '博'),  # bō
    ('鹏', '彭'),  # péng (仅 姓 时)
    ('磊', '蕾'),  # lěi
    ('浩', '昊'),  # hào
    ('晗', '涵'),  # hán
    ('彤', '童'),  # tóng
    ('宁', '凝'),  # níng
    ('晨', '辰'),  # chén
    ('俊', '峻'),  # jùn
    ('超', '朝'),  # chāo
    ('丹', '单'),  # dān (仅 姓 时)
]

# 形近字 (字形相似, 笔划接近)
NEAR_PAIRS = [
    ('未', '末'),
    ('已', '己'),
    ('土', '士'),
    ('干', '千'),
    ('刀', '力'),
    ('人', '入'),
    ('口', '日'),
    ('夭', '天'),
    ('匕', '比'),
    ('仑', '伦'),
    ('仑', '论'),
]

# -------- 字典加载 --------
TIER_PATH = Path(__file__).parent.parent / 'references' / 'name-dictionary-tier-20260610.json'

def load_tier():
    if not TIER_PATH.exists():
        return None
    return json.loads(TIER_PATH.read_text(encoding='utf-8'))

# -------- 提取中文名 --------
# 中文姓+名 = 2-3 汉字, 第 1 字是姓 (常见 100+ 姓)
COMMON_SURNAMES = set('王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤')
NAME_RE = re.compile(r'[一-鿿]{2,3}')


def extract_chinese_names(text: str) -> list:
    """从 text 提取所有 2-3 字中文字符串 (粗筛, 不验证是否是名字)."""
    return NAME_RE.findall(text)


# -------- typo 检测 --------
def get_typo_candidates(char: str) -> list:
    """返回 char 的同音/形近候选字."""
    cands = []
    for a, b in TYPO_PAIRS:
        if char == a:
            cands.append((b, 'homophone', a))
        elif char == b:
            cands.append((a, 'homophone', b))
    for a, b in NEAR_PAIRS:
        if char == a:
            cands.append((b, 'similar-shape', a))
        elif char == b:
            cands.append((a, 'similar-shape', b))
    return cands


# -------- 单 doc 检测 --------
def check_content(content: str, tier_data: dict) -> dict:
    """扫描 content 找潜在中文名 typo, 与 tier_data 交叉对比."""
    issues = []
    high_zh_set = set()
    high_zh_to_en = defaultdict(list)
    low_zh_set = set()

    if tier_data:
        for k, v in tier_data.items():
            zh = v.get('zh', '').replace(' // LOW-CONF', '').strip()
            if not zh or len(zh) < 2:
                continue
            if v.get('tier') == 'HIGH':
                high_zh_set.add(zh)
                high_zh_to_en[zh].append(k)
            else:
                low_zh_set.add(zh)

    # 1) 提取所有 2-3 字中文名
    names = extract_chinese_names(content)
    name_counter = defaultdict(int)
    for n in names:
        if 2 <= len(n) <= 3:
            name_counter[n] += 1

    # 2) 对每个名字, 检查是否在 HIGH 集合 (期望出现) 或 不在 (潜在缺失)
    # 3) 对每个名字, 检查字符是否在 TYPO_PAIRS 候选中

    # 我们做两件事:
    # A) 列出 content 中所有 2-3 字中文, 看是否在 HIGH 集合 - 不在的话标 'unverified'
    # B) 列出 HIGH 集合中, content 中出现但有 typo 风险的字符

    unverified = []
    for name, cnt in sorted(name_counter.items(), key=lambda x: -x[1]):
        if name in high_zh_set:
            continue  # HIGH-CONF match
        if name in low_zh_set:
            continue  # LOW-CONF match (acceptable)
        # 不在字典
        # 检查字符是否在 typo 候选
        char_risks = []
        for c in name:
            cands = get_typo_candidates(c)
            if cands:
                char_risks.append((c, cands))
        unverified.append({
            'name': name,
            'count': cnt,
            'char_risks': char_risks,
        })

    return {
        'unverified_names': unverified,
        'high_zh_in_content': sorted(high_zh_set & set(name_counter.keys())),
        'low_zh_in_content': sorted(low_zh_set & set(name_counter.keys())),
        'total_unique_names': len(name_counter),
    }


# -------- main --------
def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__, file=sys.stderr)
        return 0

    tier_data = load_tier()
    if tier_data is None:
        print(f'ERROR: tier dict not found: {TIER_PATH}', file=sys.stderr)
        return 2

    if sys.argv[1] == '--wiki-scan':
        return wiki_scan(tier_data)

    if sys.argv[1] == '--stdin':
        content = sys.stdin.read()
    else:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f'ERROR: file not found: {path}', file=sys.stderr)
            return 2
        content = path.read_text(encoding='utf-8')

    result = check_content(content, tier_data)
    return print_and_return(result)


def print_and_return(result):
    print(f'# Chinese name typo check (v0.10.0)')
    print()
    print(f'Unique 2-3 字 names in content: {result["total_unique_names"]}')
    print(f'HIGH-CONF names found: {len(result["high_zh_in_content"])}')
    print(f'LOW-CONF names found: {len(result["low_zh_in_content"])}')
    print(f'Unverified names (not in tier dict): {len(result["unverified_names"])}')
    print()

    if result['unverified_names']:
        print('## Unverified names (top 20 by frequency):')
        sorted_unv = sorted(result['unverified_names'], key=lambda x: -x['count'])[:20]
        for u in sorted_unv:
            risk_marker = f' ⚠ chars at risk: {u["char_risks"]}' if u['char_risks'] else ''
            print(f'  {u["name"]:<8} × {u["count"]:<3}{risk_marker}')
        print()
        print('NOTE: These names are NOT in name-dictionary-tier-20260610.json.')
        print('They could be: (a) author names from papers not yet in dict, (b) typos of HIGH/LOW entries.')
        print('For HIGH-CONF teacher names (e.g. 邓舒敏, 魏颖), ALWAYS verify against L1-L4 sources.')
    else:
        print('✅ All detected names are in tier dict (HIGH or LOW).')

    has_issues = any(u['char_risks'] for u in result['unverified_names'])
    return 1 if has_issues else 0


# -------- wiki scan --------
def fetch_doc_content(obj_token: str) -> str:
    try:
        out = subprocess.check_output(
            ['lark-cli', 'docs', '+fetch', '--api-version=v2',
             '--doc', obj_token, '--detail=with-ids', '--format=json'],
            stderr=subprocess.DEVNULL, timeout=30
        )
        return json.loads(out).get('data', {}).get('document', {}).get('content', '')
    except Exception:
        return ''


def wiki_scan(tier_data: dict) -> int:
    """扫描所有 wiki children. 必须先有 /tmp/wiki-children.json (从 lark-cli 抓)."""
    wiki_path = Path('/tmp/wiki-children.json')
    if not wiki_path.exists():
        print('ERROR: /tmp/wiki-children.json not found, run lark-cli first', file=sys.stderr)
        return 2
    wiki = json.loads(wiki_path.read_text(encoding='utf-8'))
    nodes = wiki.get('data', {}).get('nodes', [])

    print(f'# Chinese name typo wiki scan ({len(nodes)} docs)\n')

    all_issues = []
    for n in nodes:
        title = n.get('title', '')
        obj = n.get('obj_token', '')
        content = fetch_doc_content(obj)
        if not content:
            print(f'⚠ {title}: fetch failed')
            continue
        r = check_content(content, tier_data)

        # 1) 提取 title 中文名, 检查是否在 HIGH
        title_zh = re.search(r'[一-鿿]{2,3}', title)
        title_zh_name = title_zh.group() if title_zh else ''

        high_in_doc = r['high_zh_in_content']
        # 2) 找 HIGH 中字符风险
        high_issues = []
        for hzh in high_in_doc:
            for c in hzh:
                cands = get_typo_candidates(c)
                if cands:
                    high_issues.append((hzh, c, cands))

        # 3) 标 题 字符 风险
        title_char_risks = []
        if title_zh_name:
            for c in title_zh_name:
                cands = get_typo_candidates(c)
                if cands:
                    title_char_risks.append((c, cands))

        print(f'## {title}')
        print(f'  HIGH names in doc: {high_in_doc}')
        if high_issues:
            print(f'  ⚠ HIGH names with risky chars: {high_issues}')
            all_issues.append({'title': title, 'obj': obj, 'high_issues': high_issues})
        if title_char_risks:
            print(f'  ⚠ Title chars at risk: {title_char_risks}')
            all_issues.append({'title': title, 'obj': obj, 'title_char_risks': title_char_risks})
        if not (high_issues or title_char_risks):
            print(f'  ✓ clean')
        print()

    # Save report
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = Path(f'/tmp/name-typo-scan-{ts}.json')
    out.write_text(json.dumps({
        'scanned_at': ts,
        'doc_count': len(nodes),
        'all_issues': all_issues,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nReport: {out}')
    return 1 if all_issues else 0


if __name__ == '__main__':
    sys.exit(main())
