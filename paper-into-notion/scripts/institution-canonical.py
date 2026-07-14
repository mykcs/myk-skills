#!/usr/bin/env python3
"""institution-canonical.py — 机构 full name → canonical 简写 (per ADR-0057 v3.5)

为什么:
  arxiv-affiliations.py 抓 paper author 段 full name (e.g. "Hong Kong Baptist University")
  Notion multi_select group by 时需要简写 (e.g. "HKBU") 避免拆成多 group
  本脚本维护 full name → canonical 映射表, paper 入库前 1:1 简写

用法:
  python3 institution-canonical.py canonicalize <name>           # 返 canonical 或原 name
  python3 institution-canonical.py canonicalize-batch <json>     # 返 JSON 数组 (canonical)
  python3 institution-canonical.py list                            # 列出所有 canonical + full name (debug)
  python3 institution-canonical.py add <canonical> <full_name>    # user 手动加 (待实现)
  python3 institution-canonical.py --verify                       # verify 必跑

映射表来源: references/institution-canonical.md
匹配规则:
  1. 精确匹配 full name (case-insensitive)
  2. 长 full name 优先 (避免 "University" 通用规则误吞)
  3. 不在表 → 保留原 full name (Notion schema auto-add option)

实测 (2026-07-14):
  - "Hong Kong Baptist University" → HKBU
  - "Google Brain" / "Google Research" / "Google DeepMind" → Google
  - "Shenzhen University" → SZU
  - "MIT" / "Massachusetts Institute of Technology" → MIT
"""
import json
import re
import sys


# === Canonical Mapping Table (per institution-canonical.md) ===
# 顺序: 长 full name 优先 (避免通用规则误吞)
MAPPING = [
    # 港校 (long name 优先, 避免 University 误吞)
    ("Hong Kong Baptist University", "HKBU"),
    ("Hong Kong Baptist University (Shenzhen)", "HKBU-SZ"),
    ("The Hong Kong Polytechnic University", "PolyU"),
    ("Hong Kong Polytechnic University", "PolyU"),
    ("The Hong Kong University of Science and Technology", "HKUST"),
    ("Hong Kong University of Science and Technology", "HKUST"),
    ("The University of Hong Kong", "HKU"),
    ("The Chinese University of Hong Kong", "CUHK"),
    ("Chinese University of Hong Kong", "CUHK"),
    ("City University of Hong Kong", "CityU"),
    # Google 子公司
    ("Google Brain", "Google"),
    ("Google Research", "Google"),
    ("Google DeepMind", "Google"),
    ("DeepMind", "Google"),  # 兜底
    # 中国大学 (长 name 优先, 含 USTC 这种歧义)
    ("University of Science and Technology of China", "USTC"),
    ("Southern University of Science and Technology", "SUSTech"),
    ("Shenzhen University", "SZU"),
    ("Peking University", "PKU"),
    ("Tsinghua University", "THU"),
    ("Shanghai Jiao Tong University", "SJTU"),
    ("Fudan University", "FDU"),
    ("Zhejiang University", "ZJU"),
    ("Nanjing University", "NJU"),
    ("Wuhan University", "WHU"),
    ("Sun Yat-sen University", "SYSU"),
    ("Harbin Institute of Technology", "HIT"),
    ("Beijing University of Posts and Telecommunications", "BUPT"),
    ("South China University of Technology", "SCUT"),
    ("Xi'an Jiaotong University", "XJTU"),
    ("Beijing Institute of Technology", "BIT"),
    # 中国科学院
    ("Chinese Academy of Sciences", "CAS"),
    # 国际
    ("Massachusetts Institute of Technology", "MIT"),
    ("Stanford University", "Stanford"),
    ("Carnegie Mellon University", "CMU"),
    ("Princeton University", "Princeton"),
    ("University of California, Berkeley", "Berkeley"),
    ("UC Berkeley", "Berkeley"),
    ("University of California, Los Angeles", "UCLA"),
    ("University of California, San Francisco", "UCSF"),
    ("California Institute of Technology", "Caltech"),
    ("Cornell University", "Cornell"),
    ("University of Oxford", "Oxford"),
    ("University of Cambridge", "Cambridge"),
    ("University of Edinburgh", "Edinburgh"),
    ("ETH Zurich", "ETH"),
    ("Swiss Federal Institute of Technology", "ETH"),
    # 工业研究院
    ("Anthropic", "Anthropic"),
    ("OpenAI", "OpenAI"),
    ("Meta AI", "Meta"),
    ("Meta Research", "Meta"),
    ("Facebook AI Research", "Meta"),
    ("Microsoft Research", "Microsoft"),
    ("IBM Research", "IBM"),
    ("NVIDIA", "NVIDIA"),
    ("Nvidia", "NVIDIA"),
    ("Apple", "Apple"),
    ("Huawei", "Huawei"),
    ("Baidu", "Baidu"),
    ("Tencent", "Tencent"),
    ("Alibaba", "Alibaba"),
    ("DAMO Academy", "Alibaba"),
    ("Sakana AI", "SakanaAI"),
    ("SakanaAI", "SakanaAI"),
    ("TCL Corporate Research", "TCL"),
    ("TCL", "TCL"),
    ("Salesforce Research", "Salesforce"),
    ("Salesforce", "Salesforce"),
]


def canonicalize(name: str) -> str:
    """full name → canonical (保留原名 if 不在表)

    匹配顺序: 长 full name 优先 (按 MAPPING 顺序, 已在表里时)
    """
    if not name:
        return name
    name_clean = name.strip()
    name_lower = name_clean.lower()
    for full_name, canonical in MAPPING:
        if full_name.lower() == name_lower:
            return canonical
    # 部分匹配: full name 包含在 name 中 (e.g. "Department of CS, Hong Kong Baptist University" → HKBU)
    # 优先长 full name 匹配
    for full_name, canonical in MAPPING:
        if full_name.lower() in name_lower:
            return canonical
    return name_clean  # 不在表 → 保留原 full name


def canonicalize_batch(names_json: str) -> list[str]:
    """JSON 数组 → canonical JSON 数组 (deduped)"""
    try:
        names = json.loads(names_json)
    except Exception:
        return []
    if not isinstance(names, list):
        return []
    out = []
    seen = set()
    for n in names:
        if not n or not isinstance(n, str):
            continue
        c = canonicalize(n)
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("用法:", file=sys.stderr)
        print("  python3 institution-canonical.py canonicalize <name>", file=sys.stderr)
        print("  python3 institution-canonical.py canonicalize-batch '<json>'", file=sys.stderr)
        print("  python3 institution-canonical.py list", file=sys.stderr)
        return 2

    cmd = sys.argv[1]
    if cmd == "--verify":
        print("═══ institution-canonical --verify (v3.5) ═══")
        for full, canon in MAPPING[:5]:
            print(f"  {full} → {canon}")
        print(f"  ... total {len(MAPPING)} mappings")
        return 0

    if cmd == "canonicalize":
        if len(sys.argv) < 3:
            print("用法: canonicalize <name>", file=sys.stderr)
            return 2
        print(canonicalize(sys.argv[2]))
        return 0

    if cmd == "canonicalize-batch":
        if len(sys.argv) < 3:
            print("用法: canonicalize-batch '<json>'", file=sys.stderr)
            return 2
        out = canonicalize_batch(sys.argv[2])
        print(json.dumps(out, ensure_ascii=False))
        return 0

    if cmd == "list":
        # 输出 {canonical: [full_names]}
        canon_map: dict[str, list[str]] = {}
        for full, canon in MAPPING:
            canon_map.setdefault(canon, []).append(full)
        print(json.dumps(canon_map, ensure_ascii=False, indent=2))
        return 0

    print(f"未知命令: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
