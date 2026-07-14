#!/usr/bin/env python3
"""arxiv-affiliations.py — arXiv HTML 实验版 → author affiliations list (per ADR-0057 v3.4)

为什么:
  v3.3 LLM 自由判机构名容易幻觉 (e.g. TTHE Bo Han 实为 HKBU, 错判成 PolyU).
  v3.4 改用 arXiv HTML 实验版 (LaTeXML 渲染) 1:1 抓 paper author 脚注 affiliations 段.

用法:
  python3 arxiv-affiliations.py <ARXIV_ID>
  e.g.: python3 arxiv-affiliations.py 2607.08124

输出: JSON 数组 (deduped affiliation 字符串列表)
  例: ["Hong Kong Baptist University", "University of Science and Technology of China", ...]

策略 (v3.4 final):
  1. fetch https://arxiv.org/html/<id>v1 实验版 HTML
  2. 抓 <div class="ltx_authors"> 段 (到 ltx_abstract 或 article)
  3. 移除 ltx_personname 段 (作者名 + 上标) — 但要保留 affiliation 脚注
  4. 按 <br ...> 切分, 每段 = 候选 affiliation
  5. 过滤太短 / 含 @ / 起始 "Equal contribution" / "Listing order" 等元描述
  6. dedup

实测 (2026-07-14):
  - 2607.08124 (TTHE, footnote style) → 4: HKBU + USTC + HKUST Generative AI Center + TCL Corp
  - 1706.03762 (Attention, inline style) → 3: Google Brain + Google Research + University of Toronto
  - 2512.10252 (GDKVM) → 3: SZU + PolyU
"""
import json
import re
import subprocess
import sys


def fetch_url(url: str) -> str:
    """GET url → HTML text, return "" if failed (60s timeout)"""
    r = subprocess.run(
        ["curl", "-fsSL", "--max-time", "60", url],
        capture_output=True, text=True, timeout=70,
    )
    return r.stdout if r.returncode == 0 else ""


def strip_to_text(segment: str) -> str:
    """移除 HTML tags + 实体 + normalize whitespace"""
    text = re.sub(r'<[^>]+>', '', segment)
    text = (text.replace('&amp;', '&').replace('&lt;', '<')
            .replace('&gt;', '>').replace('&quot;', '"'))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_ltx_authors_block(html: str) -> str:
    """抓 <div class="ltx_authors"> 段, 返字符串"""
    m = re.search(r'<div[^>]*ltx_authors[^"]*"[^>]*>', html)
    if not m:
        return ""
    start = m.end()
    end_m = re.search(r'<div[^>]*class="ltx_abstract"|<article', html[start:start+50000])
    if not end_m:
        return ""
    end = start + end_m.start()
    return html[start:end]


def parse_ltx_authors_affiliations(html: str) -> list[str]:
    """从 arXiv HTML 实验版 ltx_authors 段抓 affiliation 列表.

    通用策略 (不依赖 footnote vs inline 结构):
      1. 抓 ltx_authors block
      2. 移除 <span class="ltx_personname">...</span> 段 (作者名)
      3. 移除 email 段 (<span ...ltx_font_typewriter...>@...</span>)
      4. 移除 footnotemark 段 (ltx_note ltx_role_footnotemark)
      5. 按 <br ...> 切 (含 class 属性)
      6. 每段 strip + 过滤 (长度 ≥ 3, 不含 @, 不是元描述)
    """
    block = get_ltx_authors_block(html)
    if not block:
        return []

    # 移除 personname 段 (不跨 <br>, GDKVM style)
    block = re.sub(
        r'<span[^>]*class="ltx_personname[^"]*"[^>]*>(?:(?!<br\b).)*?</span>(?:\s*</span>){0,2}',
        '', block, flags=re.DOTALL,
    )
    # 移除 personname 段 (跨 <br>, TTHE style — personname 内含 <br class="ltx_break">)
    block = re.sub(
        r'<span[^>]*class="ltx_personname[^"]*"[^>]*>(?:(?!<div\b).)*?</span>(?:\s*</span>){0,3}',
        '', block, flags=re.DOTALL,
    )
    # 移除 email 段 (含 @)
    block = re.sub(
        r'<span[^>]*ltx_font_typewriter[^"]*"[^>]*>[^<]*@[^<]*</span>',
        '', block, flags=re.DOTALL,
    )
    # 移除 ltx_note 段
    block = re.sub(
        r'<span[^>]*class="ltx_note[^"]*"[^>]*>.*?</span>\s*</span>\s*</span>',
        '', block, flags=re.DOTALL,
    )

    # 按 <br ...> 切 (含 class)
    parts = re.split(r'<br[^>]*>', block)
    out = []
    seen = set()
    # 第 1 段是 personname 残留的判定: 段内含 <sup>N</sup> 多标号 OR 全是 author 段 (无机构关键词)
    # 否则 (e.g. GDKVM personname 已移除, 第 1 段是 affiliation) 保留
    if len(parts) > 1:
        first = parts[0]
        first_text = strip_to_text(first)
        has_aff_kw = any(kw in first_text for kw in ['University', 'Institute', 'Lab', 'Center',
                                                       'Research', 'College', 'School', 'Inc', 'Corp',
                                                       'Google', 'MIT', 'CMU', 'HKUST', 'HKBU', 'SZU',
                                                       'PolyU', '腾讯', '阿里', '百度', '华为'])
        # 有机构词 = 是 affiliation, 保留
        # 无机构词 + 含 personname 特征 (多个 sup 标号 / ", Lastname") = drop
        if not has_aff_kw and (',' in first_text and any(f'<sup[^>]*>{n}</sup>' in first for n in '12345') or
                                re.search(r',\s*\w+\s+\w+', first_text)):
            parts = parts[1:]
    for p in parts:
        # 按 <sup> 切分 (多 affiliation 同段, e.g. TTHE "1HKBU 2USTC")
        # 模式: <sup>...N...</sup>INSTITUTION (允许多层 <span> 嵌套)
        sub_parts = re.split(r'(?=<sup\b)', p)
        for sp in sub_parts:
            text = strip_to_text(sp)
            if not text or len(text) < 3:
                continue
            if '@' in text:
                continue
            # 去掉前导 sup 标号 (e.g. "1HKBU" → "HKBU", "2USTC" → "USTC")
            # 也处理 "</sup>1College..." 这种内嵌结构
            text = re.sub(r'^(\d+\s*|</?[a-z][^>]*>\s*)+', '', text, flags=re.IGNORECASE).strip()
            # 过滤元描述
            if re.match(r'^(Equal|Listing|Work|These|Contributed|Both|Corresponding|Email|†|‡|&)',
                        text, re.IGNORECASE):
                continue
            # 过滤纯数字/标点
            if re.match(r'^[\d\s,.\-*†‡]+$', text):
                continue
            # 过滤 author 段特征: 以 ", " + Lastname 开头 (TTHE 残留)
            if re.match(r'^,\s*\w+\s+\w+', text):  # ", Jun Song" / ", Qianshu Cai"
                continue
            # 过滤单 Lastname (3-15 chars, 无 University/Institute/Lab/Center 等机构词)
            if not any(kw in text for kw in ['University', 'Institute', 'Lab', 'Center', 'Research',
                                              'College', 'Department', 'School', 'Inc', 'Corp',
                                              'Google', 'MIT', 'CMU', 'HKUST', 'HKBU', 'SZU',
                                              'PolyU', 'University', '腾讯', '阿里', '百度', '华为']):
                if ' ' not in text:  # 单字不包含机构关键词
                    continue
            if text not in seen:
                seen.add(text)
                out.append(text)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 arxiv-affiliations.py <ARXIV_ID>", file=sys.stderr)
        return 2

    arxiv_id = sys.argv[1]

    html = fetch_url(f"https://arxiv.org/html/{arxiv_id}v1")
    if not html:
        print(json.dumps({"error": f"fetch html failed: {arxiv_id}v1"}))
        return 1

    affiliations = parse_ltx_authors_affiliations(html)
    if not affiliations:
        print(json.dumps({"error": "no affiliations parsed", "arxiv_id": arxiv_id}))
        return 0

    print(json.dumps(affiliations, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
