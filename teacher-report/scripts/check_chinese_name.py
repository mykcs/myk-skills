#!/usr/bin/env python3
"""
check_chinese_name.py — teacher-report v0.10.0 Check 17
中文名字符级 typo 扫描 — 检测老师 wiki 文档里中文姓名是否与权威来源一致。

触发 case (2026-06-11): 邓舒敏 (Shumin Deng) 文档 28 处中文名是「邓**舒**敏」(shū, comfortable),
实际正确是「邓**淑**敏」(shú, virtuous) — 同音不同义 LLM auto-generate typo,
claudecode 当时只对比结构没对比字符级。

v0.10.1 (2026-06-11): 1-字符 reverse lookup — HIGH 集合为 ground truth, 找 doc 中所有
1-字符替换命中 = 真 typo. 解决 v0.10.0 启发式 chars at risk 误报.

v0.10.2 (2026-06-11): 扩展到 LOW-CONF 集合 (256 unique zh). 同样 1-字符 typo 检测,
但告警级别 = 'LOW_TYPO' (vs HIGH_TYPO). 1) LOW 字典本身可能错 (LLM auto-generate 时
同音/形近字) 2) LOW entry 在 wiki content 中是 user-visible 字段.
LOW_TYPO 等待用户 review (HIGH 升级后可能改, 或确认是 LLM error 需 batch fix).

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
# 源自 2026-06-11 邓舒敏/邓淑敏 案例 (HIGH-CONF typo)
# v0.10.2 扩充: 李俊程→李俊成 (成 chéng vs 程 chéng 同音)
# v0.10.2 扩充: 张颖 vs 张瀛, 张楹 等 (高频 LOW)
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
    # v0.10.2 新增 (LOW 字典错字案例)
    ('程', '成'),  # chéng 旅程/程程 vs 成就/成全 (2026-06-11 李俊程→李俊成)
    ('程', '诚'),  # chéng
    ('成', '诚'),  # chéng
    ('颖', '瀛'),  # yíng 聪颖/颖悟 vs 瀛海/瀛洲
    ('颖', '楹'),  # yíng 楹联
    ('奕', '弈'),  # yì 奕奕/神采奕奕 vs 博弈/弈棋
    ('奕', '益'),  # yì
    ('帆', '凡'),  # fān 帆船 vs 平凡 (吴帆常见 LOW)
    ('帆', '樊'),  # fán
    ('哲', '喆'),  # zhé 哲学 vs 喆 (吕哲奇常见 LOW)
    ('哲', '者'),  # zhě
    ('慕', '幕'),  # mù 爱慕/羡慕 vs 屏幕/帷幕
    ('慕', '暮'),  # mù
    ('靖', '静'),  # jìng 安靖/靖远 vs 安静/静谧 (卢靖宇常见 LOW)
    ('靖', '菁'),  # jīng 菁华
    ('培', '裴'),  # péi 培养 vs 裴姓 (仅 姓时)
    ('培', '赔'),  # péi
    ('梦', '孟'),  # mèng 梦想 vs 孟姓 (张梦飞常见 LOW)
    ('侠', '霞'),  # xiá 侠客 vs 霞光 (杨红霞常见 LOW)
    ('侠', '峡'),  # xiá
    ('璐', '露'),  # lù 美玉 vs 甘露 (潘璐佳常见 LOW)
    ('璐', '鹭'),  # lù
    ('皓', '浩'),  # hào
    ('昊', '浩'),  # hào
    ('昊', '皓'),  # hào
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
    """扫描 content 找潜在中文名 typo, 与 tier_data 交叉对比.

    核心算法 (v0.10.1 enhanced):
    1. 提取所有 2-3 字中文名
    2. 对 HIGH 集合中每个名字, 计算 1-字符替换的所有"接近字符串" (同音/形近)
    3. 扫描 content 找这些"接近字符串"出现 → 真 typo (because HIGH name is expected)
    4. 对所有提取的中文名, 标 unverified + char_risks for reference
    """
    high_zh_set = set()
    high_zh_to_en = defaultdict(list)
    low_zh_set = set()
    high_zh_to_src = {}

    if tier_data:
        for k, v in tier_data.items():
            zh = v.get('zh', '').replace(' // LOW-CONF', '').strip()
            if not zh or len(zh) < 2:
                continue
            if v.get('tier') == 'HIGH':
                high_zh_set.add(zh)
                high_zh_to_en[zh].append(k)
                high_zh_to_src[zh] = v.get('source', '')
            else:
                low_zh_set.add(zh)

    # 1) 提取所有 2-3 字中文名
    names = extract_chinese_names(content)
    name_counter = defaultdict(int)
    for n in names:
        if 2 <= len(n) <= 3:
            name_counter[n] += 1

    # 2) 对每个 HIGH name, 生成所有 1-char typo 候选 (同音/形近)
    high_typo_candidates = defaultdict(list)  # typo_string -> [(correct_name, char_idx, wrong_char, correct_char, kind)]
    for correct_name in high_zh_set:
        for i, c in enumerate(correct_name):
            for cand, kind, orig in get_typo_candidates(c):
                if not cand:
                    continue
                typo_str = correct_name[:i] + cand + correct_name[i+1:]
                high_typo_candidates[typo_str].append({
                    'correct': correct_name,
                    'wrong_char': cand,
                    'correct_char': c,
                    'char_idx': i,
                    'kind': kind,
                })

    # v0.10.2: 对 LOW 集合也生成 typo candidates (用于 LOW 字典自身错字检测)
    low_typo_candidates = defaultdict(list)  # typo_string -> [(correct_name, ...)]
    for correct_name in low_zh_set:
        for i, c in enumerate(correct_name):
            for cand, kind, orig in get_typo_candidates(c):
                if not cand:
                    continue
                typo_str = correct_name[:i] + cand + correct_name[i+1:]
                # Skip if typo_str 也是一个合法 LOW name (会冲突, 取 freq 高的)
                low_typo_candidates[typo_str].append({
                    'correct': correct_name,
                    'wrong_char': cand,
                    'correct_char': c,
                    'char_idx': i,
                    'kind': kind,
                })

    # 3) 找 content 中真 typo (1-字符替换命中 high_typo_candidates)
    real_typos = []  # HIGH_TYPO: HIGH 名字的 typo
    low_typos = []   # LOW_TYPO: LOW 字典自身可能错 (字符级)
    for name, cnt in name_counter.items():
        if name in high_zh_set or name in low_zh_set:
            continue  # exact match
        if name in high_typo_candidates:
            for hit in high_typo_candidates[name]:
                real_typos.append({
                    'typo': name,
                    'correct': hit['correct'],
                    'wrong_char': hit['wrong_char'],
                    'correct_char': hit['correct_char'],
                    'char_idx': hit['char_idx'],
                    'kind': hit['kind'],
                    'count': cnt,
                    'source': high_zh_to_src.get(hit['correct'], ''),
                    'tier': 'HIGH',
                })
        elif name in low_typo_candidates:
            # 同一 typo 可能对应多个 LOW correct (collision)
            for hit in low_typo_candidates[name]:
                low_typos.append({
                    'typo': name,
                    'correct_candidate': hit['correct'],
                    'wrong_char': hit['wrong_char'],
                    'correct_char': hit['correct_char'],
                    'char_idx': hit['char_idx'],
                    'kind': hit['kind'],
                    'count': cnt,
                    'tier': 'LOW',
                })

    # 4) unverified names (不属 HIGH/LOW 字典, 仅参考)
    unverified = []
    for name, cnt in sorted(name_counter.items(), key=lambda x: -x[1]):
        if name in high_zh_set or name in low_zh_set:
            continue
        if name in high_typo_candidates or name in low_typo_candidates:
            continue  # 已在 real_typos / low_typos
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
        'real_typos': real_typos,
        'low_typos': low_typos,
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
    print(f'# Chinese name typo check (v0.10.2)')
    print()
    print(f'Unique 2-3 字 names in content: {result["total_unique_names"]}')
    print(f'HIGH-CONF names found: {len(result["high_zh_in_content"])}')
    print(f'LOW-CONF names found: {len(result["low_zh_in_content"])}')
    print(f'HIGH-CONF typos: {len(result["real_typos"])}')
    print(f'LOW-CONF typos: {len(result["low_typos"])}')
    print(f'Unverified names: {len(result["unverified_names"])}')
    print()

    if result['real_typos']:
        print('## ❌ HIGH-CONF TYPOS (1-char edit from HIGH-CONF, must fix):')
        for t in result['real_typos']:
            print(f'  ❌ {t["typo"]} (×{t["count"]}) → {t["correct"]} '
                  f'[{t["kind"]}, char[{t["char_idx"]}] {t["wrong_char"]}→{t["correct_char"]}]')
            print(f'      source: {t["source"]}')
        print()

    if result['low_typos']:
        print('## ⚠ LOW-CONF TYPOS (1-char edit from LOW-CONF, 字典自身可能错, 需 review):')
        # Group by typo to show collisions
        from collections import defaultdict
        typo_to_cands = defaultdict(list)
        for t in result['low_typos']:
            typo_to_cands[t['typo']].append(t)
        for typo, hits in sorted(typo_to_cands.items(), key=lambda x: -x[1][0]['count']):
            total = hits[0]['count']
            cands_str = ' / '.join(f"{h['correct_candidate']} ({h['kind']}, char[{h['char_idx']}] {h['wrong_char']}→{h['correct_char']})" for h in hits)
            print(f'  ⚠ {typo} (×{total}) → {cands_str}')
        print()
        print('NOTE: LOW 字典本身可能是 LLM auto-generate 时的同音/形近错字.')
        print('      需要逐一 verify L1-L4 来源 (lab page / ORCID / LinkedIn slug).')
        print('      若 LOW 字典错, 应 batch fix 字典 + 修 wiki content.')

    if result['unverified_names']:
        print('## Unverified names (top 10 by frequency, info only):')
        sorted_unv = sorted(result['unverified_names'], key=lambda x: -x['count'])[:10]
        for u in sorted_unv:
            risk_marker = f' ⚠ chars at risk: {u["char_risks"]}' if u['char_risks'] else ''
            print(f'  {u["name"]:<8} × {u["count"]:<3}{risk_marker}')
        print()
        print('NOTE: These names are NOT in name-dictionary-tier-20260610.json.')
        print('They could be: (a) paper coauthors not yet in dict, (b) LOW-CONF guess.')
        print('For HIGH-CONF teacher names (e.g. 邓淑敏, 魏颖), ALWAYS verify against L1-L4 sources.')

    if not result['real_typos'] and not result['low_typos'] and not result['unverified_names']:
        print('✅ All detected names are in tier dict (HIGH or LOW).')

    return 1 if (result['real_typos'] or result['low_typos']) else 0


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

    print(f'# Chinese name typo wiki scan ({len(nodes)} docs, v0.10.1)\n')

    all_real_typos = []
    for n in nodes:
        title = n.get('title', '')
        obj = n.get('obj_token', '')
        content = fetch_doc_content(obj)
        if not content:
            print(f'⚠ {title}: fetch failed')
            continue
        r = check_content(content, tier_data)

        print(f'## {title}')
        print(f'  HIGH names in doc: {r["high_zh_in_content"]}')
        print(f'  LOW names in doc: {len(r["low_zh_in_content"])}')
        if r['real_typos']:
            print(f'  ❌ HIGH-CONF TYPOS:')
            for t in r['real_typos']:
                print(f'      ❌ {t["typo"]} (×{t["count"]}) → {t["correct"]} '
                      f'[{t["kind"]}, char[{t["char_idx"]}] {t["wrong_char"]}→{t["correct_char"]}]')
                print(f'         source: {t["source"]}')
            all_real_typos.append({'title': title, 'obj': obj, 'typos': r['real_typos'], 'kind': 'HIGH'})
        if r['low_typos']:
            # Group by typo
            from collections import defaultdict
            typo_to_cands = defaultdict(list)
            for t in r['low_typos']:
                typo_to_cands[t['typo']].append(t)
            for typo, hits in sorted(typo_to_cands.items(), key=lambda x: -x[1][0]['count']):
                cands_str = ' / '.join(f"{h['correct_candidate']} ({h['kind']}, {h['wrong_char']}→{h['correct_char']})" for h in hits)
                print(f'  ⚠ LOW-TYPO: {typo} (×{hits[0]["count"]}) → {cands_str}')
            all_real_typos.append({'title': title, 'obj': obj, 'typos': r['low_typos'], 'kind': 'LOW'})
        if not r['real_typos'] and not r['low_typos']:
            print(f'  ✓ no typos (HIGH or LOW)')
        if r['unverified_names']:
            unv_top = sorted(r['unverified_names'], key=lambda x: -x['count'])[:5]
            print(f'  ℹ unverified (top 5): {[u["name"] for u in unv_top]}')
        print()

    # Save report
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = Path(f'/tmp/name-typo-scan-{ts}.json')
    out.write_text(json.dumps({
        'scanned_at': ts,
        'doc_count': len(nodes),
        'docs_with_high_typos': sum(1 for x in all_real_typos if x['kind'] == 'HIGH'),
        'docs_with_low_typos': sum(1 for x in all_real_typos if x['kind'] == 'LOW'),
        'all_findings': all_real_typos,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n=== Summary: HIGH={sum(1 for x in all_real_typos if x["kind"] == "HIGH")} docs, '
          f'LOW={sum(1 for x in all_real_typos if x["kind"] == "LOW")} docs ===')
    print(f'Report: {out}')
    return 1 if all_real_typos else 0


if __name__ == '__main__':
    sys.exit(main())
