#!/usr/bin/env python3
"""
teacher-report v0.3.0 Paper Card 批量规范化脚本
SOP: ~/.agents/skills/teacher-report/SOP-v0.3.0-normalize.md

Usage:
  python3 scripts/normalize_v0.3.0.py --doc <doc_token> [--year-range 2023 2026] [--workers 4] [--output /tmp/cards.md] [--dry-run]

Phases:
  1. EXTRACT  - 用 lark-cli docs +fetch 拉取文档 §4.x 表格, 解析所有论文 (序号, 标题, 时间, venue, 等级)
  2. LOOKUP   - 并行查 arXiv API (export.arxiv.org/api/query) 获取 arXiv ID + 完整作者列表
  3. BUILD    - 按 v0.3.0 paper card 6 行格式生成 markdown
  4. APPEND   - 用 lark-cli docs +update --command append 把 paper cards 段 append 到文档末尾
  5. REPORT   - 输出统计报告 (已查/未查/失败) 到 stdout + /tmp/normalize-report-*.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------- Constants ----------

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom", "a": "http://arxiv.org/schemas/atom"}
DEFAULT_WORKERS = 4
RATE_LIMIT_S = 3.0  # arXiv API rate limit per request
TIMEOUT_S = 15

# ---------- Data model ----------


@dataclass
class Paper:
    """一篇论文的提取/查找结果"""

    seq: str  # 序号 (e.g. "1", "47")
    title_table: str  # 表格中的标题
    year: str  # 时间列 (e.g. "2024", "2025.8")
    venue: str  # 会议/期刊列 (e.g. "ICLR 2026", "Cell Patterns")
    tier: str  # 等级列
    sort: str  # 排序列
    students: str  # 学生标注列
    # Lookup result
    arxiv_id: str = ""  # e.g. "2508.04482"
    arxiv_url: str = ""
    paperscool_url: str = ""
    doi: str = ""
    title_verified: str = ""  # arXiv 返回的精确标题
    authors: list[str] = field(default_factory=list)  # 完整作者列表
    primary_category: str = ""
    year_arxiv: str = ""  # arXiv 首次提交年
    status: str = "pending"  # pending / found / not_found / ambiguous / error
    error: str = ""


# ---------- Phase 1: EXTRACT ----------


def fetch_doc_xml(doc_id: str) -> str:
    """lark-cli docs +fetch 拉取完整文档 XML"""
    cwd = "/tmp"  # 为 @-file 相对路径, lark-cli 限制
    cmd = [
        "lark-cli",
        "docs",
        "+fetch",
        "--api-version",
        "v2",
        "--doc",
        doc_id,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"lark-cli docs +fetch failed: {result.stderr}")
    data = json.loads(result.stdout)
    content = data.get("data", {}).get("document", {}).get("content", {})
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    return content


def parse_papers_from_xml(xml_text: str, year_range: tuple[int, int] = (2023, 2026)) -> list[Paper]:
    """从文档 XML 提取所有论文元数据, 限定在 §4.x 表格内"""
    papers: list[Paper] = []
    # 找到所有 <table> 块 + 紧邻的 H3 (年份标题) + 表格内的 <tr>
    # 简化: 用 regex 抓所有 <tr> 块, 然后判断是否在 §4 范围内 (用前后 H3 / H4 锚定)
    rows = re.findall(r"<tr>(.*?)</tr>", xml_text, re.DOTALL)
    # 先找每个 H3 + 后续 <table> 的范围
    sections = re.split(r'<h3[^>]*>(.*?)</h3>', xml_text, flags=re.DOTALL)
    # sections[0] = 文档开头, 然后 [h3_title, body_after_h3, h3_title, body_after_h3, ...]
    section_year: dict[int, str] = {}  # row_idx -> year (from H3 title)
    pos = 0
    row_iter = list(re.finditer(r"<tr>(.*?)</tr>", xml_text, re.DOTALL))
    for i in range(1, len(sections), 2):
        h3_title = sections[i]
        body = sections[i + 1] if i + 1 < len(sections) else ""
        # 提取年份 (e.g. "4.1 2026 年（13 篇）" -> 2026)
        m = re.search(r"(20\d{2})", h3_title)
        if not m:
            continue
        year = int(m.group(1))
        if year < year_range[0] or year > year_range[1]:
            continue
        # 找 body 内所有 <tr> 的 row_idx
        for ri, row_match in enumerate(row_iter):
            row_start = row_match.start()
            if row_start > pos and (pos + len(sections[i]) + body.find("<table")):
                pass
        # 简化: 直接给所有 row_iter 里行号 < body_end 的行设 year
        body_start = xml_text.find(h3_title, pos) + len(h3_title)
        # 找下一个 H3 或文档末尾
        next_h3 = re.search(r"<h3[^>]*>", xml_text[body_start:])
        body_end = body_start + (next_h3.start() if next_h3 else len(xml_text) - body_start)
        for ri, row_match in enumerate(row_iter):
            if body_start <= row_match.start() < body_end:
                section_year[id(row_match)] = str(year)
        pos = body_end

    # 解析每个 row
    headers = {
        "序号",
        "论文标题",
        "时间",
        "会议/期刊",
        "等级",
        "排序",
        "学生标注",
        "大领域",
        "中方向",
        "小任务",
        "子技术",
        "姓名（拼音）",
        "身份",
        "主要方向",
        "代表作",
        "篇数",
        "领域",
        "代表性合作",
        "数量",
        "占比",
        "说明",
        "核心会议",
        "大方向",
        "论文数",
        "项目",
        "内容",
    }
    for row_match in row_iter:
        row_id = id(row_match)
        if row_id not in section_year:
            continue
        year = section_year[row_id]
        row = row_match.group(1)
        cells = re.findall(r"<p[^>]*>(.*?)</p>", row, re.DOTALL)
        cells_clean = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        if len(cells_clean) < 3:
            continue
        if all(c in headers for c in cells_clean):
            continue
        # Row format: [序号, 标题, 时间, 会议/期刊, 等级, 排序, 学生标注, 大领域, 中方向, 小任务, 子技术]
        if len(cells_clean) < 7:
            continue
        seq = cells_clean[0]
        title = cells_clean[1]
        time_cell = cells_clean[2]
        venue = cells_clean[3]
        tier = cells_clean[4]
        sort = cells_clean[5]
        students = cells_clean[6]
        if not re.match(r"^\d+$", seq):
            continue  # 跳过非论文行 (e.g. 学生代表作)
        if title and not title.startswith("一、"):  # 跳过目录型
            papers.append(
                Paper(
                    seq=seq,
                    title_table=title,
                    year=time_cell or year,
                    venue=venue,
                    tier=tier,
                    sort=sort,
                    students=students,
                )
            )
    return papers


# ---------- Phase 2: LOOKUP (arXiv API) ----------


_last_request_t: float = 0.0


def _throttle():
    """arXiv 官方限流: 1 req / 3s, 不能并发 outstanding"""
    global _last_request_t
    now = time.time()
    elapsed = now - _last_request_t
    if elapsed < RATE_LIMIT_S:
        time.sleep(RATE_LIMIT_S - elapsed)
    _last_request_t = time.time()


def _arxiv_request_with_retry(url: str, max_retries: int = 3) -> Optional[bytes]:
    """带 retry + backoff 的 arXiv API 请求"""
    for attempt in range(max_retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "teacher-report-v0.3.0-normalize/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait = 10 * (attempt + 1)
                print(f"      429 rate-limit, sleeping {wait}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            elif e.code >= 500:
                wait = 5 * (attempt + 1)
                print(f"      {e.code} server error, sleeping {wait}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise  # 4xx 不重试
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 3 * (attempt + 1)
            print(f"      network error: {type(e).__name__}, sleeping {wait}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
    return None


def arxiv_lookup(paper: Paper) -> Paper:
    """查 arXiv API by title, 填充 arxiv_id + authors (串行 + 重试)"""
    if not paper.title_table:
        paper.status = "error"
        paper.error = "empty title"
        return paper
    # 清理标题 (去掉粗体/特殊字符)
    q_title = re.sub(r"\s+", " ", paper.title_table).strip()
    # arXiv API 查询: ti:"exact title" + max_results=1
    params = urllib.parse.urlencode({"search_query": f'ti:"{q_title}"', "max_results": "1"})
    url = f"{ARXIV_API}?{params}"

    data = _arxiv_request_with_retry(url)
    if data is None:
        paper.status = "error"
        paper.error = "max retries exceeded"
        return paper

    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        paper.status = "error"
        paper.error = f"xml: {e}"
        return paper

    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = root.findall("a:entry", ns)
    if not entries:
        paper.status = "not_found"
        return paper
    entry = entries[0]
    # 找 arXiv ID
    eid = entry.findtext("a:id", "", ns)  # http://arxiv.org/abs/2508.04482v1
    m = re.search(r"arxiv\.org/abs/([\w./\-]+)", eid)
    if not m:
        paper.status = "error"
        paper.error = "no arxiv id in entry"
        return paper
    paper.arxiv_id = m.group(1).rstrip("v")
    paper.arxiv_url = f"https://arxiv.org/abs/{paper.arxiv_id}"
    paper.paperscool_url = f"https://papers.cool/arxiv/{paper.arxiv_id}"
    paper.title_verified = entry.findtext("a:title", "", ns).strip()
    # 作者列表
    for author in entry.findall("a:author/a:name", ns):
        if author.text:
            paper.authors.append(author.text.strip())
    # 首次提交年
    pub = entry.findtext("a:published", "", ns)
    if pub:
        paper.year_arxiv = pub[:4]
    # 主分类
    cat = entry.find("a:category", ns)
    if cat is not None:
        paper.primary_category = cat.attrib.get("term", "")
    paper.status = "found"
    # title similarity check (fuzzy)
    if paper.title_verified.lower() != q_title.lower():
        # arXiv search 用 ti:"..." 是 literal match, 通常等价; 但允许大小写/标点差异
        sim_chars = sum(1 for a, b in zip(paper.title_verified.lower(), q_title.lower()) if a == b)
        sim = sim_chars / max(len(paper.title_verified), len(q_title))
        if sim < 0.9:
            paper.status = "ambiguous"
    return paper


def lookup_batch(papers: list[Paper], workers: int = 1) -> list[Paper]:
    """串行查 arXiv, 严格遵守 1 req / 3s 限流
    workers 参数保留为兼容接口, 实际强制 1 (arXiv 不容忍并发)"""
    if workers > 1:
        print(f"  ⚠️ arXiv 限流: workers > 1 会触发 429, 强制使用 1 worker")
        workers = 1
    print(f"  Looking up {len(papers)} papers on arXiv (serial, 3s/rate-limit)...")
    t0 = time.time()
    results: list[Paper] = []
    for i, p in enumerate(papers, 1):
        arxiv_lookup(p)
        results.append(p)
        if i % 10 == 0 or i == len(papers):
            elapsed = time.time() - t0
            est_total = elapsed * len(papers) / i
            print(f"    [{i}/{len(papers)}] elapsed {elapsed:.0f}s, ETA total {est_total:.0f}s, last: {p.status} {p.title_table[:50]!r}")
    return results


# ---------- Phase 3: BUILD ----------


def format_paper_card(p: Paper, index: int) -> str:
    """v0.3.0 6 行 paper card format"""
    title = p.title_verified or p.title_table
    venue = p.venue or "arXiv preprint"
    year = p.year_arxiv or p.year
    # 作者: 把 arXiv 名单用逗号+空格串起来, Fei Wu 显式标
    authors_str = ", ".join(p.authors) if p.authors else "（❓ 待核 — arXiv 无数据）"
    # 标注 Fei Wu（吴飞）
    if "Fei Wu" in authors_str and "（吴飞）" not in authors_str:
        # 把 'Fei Wu' 替换为 'Fei Wu（吴飞）'
        authors_str = re.sub(r"\bFei Wu\b", "Fei Wu（吴飞）", authors_str, count=1)
    # 角色
    role = "（preprint）"
    if "ICLR" in venue:
        role = "（preprint）"
    elif "Nature" in venue or "Cell" in venue:
        role = ""
    # 状态标记
    status_tag = ""
    if p.status == "ambiguous":
        status_tag = " ⚠️"
    elif p.status == "not_found":
        status_tag = " ❓ arXiv 未找到"
    elif p.status == "error":
        status_tag = f" ❓ {p.error}"
    arxiv_line = p.arxiv_url or "（❓ 待核）"
    paperscool_line = p.paperscool_url or "（❓ 待核 — 无 arXiv ID）"
    return (
        f"#### {index}. {title}{status_tag}\n\n"
        f"作者：\n\n"
        f"{authors_str}\n\n"
        f"发表：{venue} ({year}){role}\n\n"
        f"arXiv：<{arxiv_line}>\n\n"
        f"paperscool：<{paperscool_line}>\n\n"
        f"---\n\n"
    )


def build_section(papers: list[Paper], section_no: str = "7") -> str:
    """生成完整 v0.3.0 paper card section"""
    found = [p for p in papers if p.status == "found" or p.status == "ambiguous"]
    found.sort(key=lambda p: p.year_arxiv or p.year, reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(f"## {section_no}. v0.3.0 Paper Card 详展（批量规范化产物，{today}）\n\n")
    lines.append(
        f"> 本节由 `teacher-report v0.3.0 normalize.py` 批量生成，含 {len(found)}/{len(papers)} 篇已找到 arXiv ID 的论文 paper card。\n\n"
    )
    lines.append(
        f"> 6 行 paper card 格式：① verbatim 标题 ② 完整作者列表（Fei Wu 显式标 `（吴飞）`） ③ 发表 venue/year/role ④ arXiv URL ⑤ papers.cool URL。\n\n"
    )
    lines.append(f"### {section_no}.1 顶会 / arXiv 论文（{len(found)} 篇，按发表时间倒序）\n\n")
    for i, p in enumerate(found, 1):
        lines.append(format_paper_card(p, i))
    not_found = [p for p in papers if p.status not in ("found", "ambiguous")]
    if not_found:
        lines.append(f"### {section_no}.2 ❓ arXiv 未找到（{len(not_found)} 篇，需人工核）\n\n")
        for p in not_found:
            lines.append(f"- 序号 {p.seq}: {p.title_table} ({p.venue} {p.year}) — {p.status} {p.error}\n")
    return "".join(lines)


# ---------- Phase 4: APPEND ----------


def append_to_doc(doc_id: str, content: str, output_path: str = "/tmp/paper-cards-batch.md") -> str:
    """保存到文件 + 用 lark-cli append 到文档"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    # lark-cli 限制 @-file 用相对路径
    cmd = [
        "lark-cli",
        "docs",
        "+update",
        "--api-version",
        "v2",
        "--doc",
        doc_id,
        "--command",
        "append",
        "--content",
        f"@{path.name}",  # 相对路径
        "--doc-format",
        "markdown",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(path.parent))
    if result.returncode != 0:
        raise RuntimeError(f"lark-cli append failed: {result.stderr}")
    data = json.loads(result.stdout)
    rev = data.get("data", {}).get("document", {}).get("revision_id")
    return f"appended OK, revision_id={rev}"


# ---------- Phase 5: REPORT ----------


def save_report(papers: list[Paper], output: str) -> None:
    """保存 JSON 报告"""
    by_status: dict[str, int] = {}
    for p in papers:
        by_status[p.status] = by_status.get(p.status, 0) + 1
    report = {
        "ts": datetime.now().isoformat(),
        "total": len(papers),
        "by_status": by_status,
        "papers": [asdict(p) for p in papers],
    }
    Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Report saved to: {output}")


# ---------- Main ----------


def main() -> int:
    ap = argparse.ArgumentParser(description="v0.3.0 Paper Card 批量规范化")
    ap.add_argument("--doc", required=True, help="飞书 doc token / URL")
    ap.add_argument("--year-range", nargs=2, type=int, default=[2023, 2026], help="年份范围 (默认 2023 2026)")
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="arXiv lookup 并发数 (默认 4, 建议 ≤ 4)")
    ap.add_argument("--output", default="/tmp/paper-cards-batch.md", help="paper cards 输出文件")
    ap.add_argument("--report", default="/tmp/normalize-report.json", help="报告输出")
    ap.add_argument("--dry-run", action="store_true", help="只生成不 append")
    args = ap.parse_args()

    print(f"=== teacher-report v0.3.0 Paper Card Normalize ===")
    print(f"Doc: {args.doc}")
    print(f"Year range: {args.year_range[0]} - {args.year_range[1]}")
    print(f"Workers: {args.workers}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Phase 1: EXTRACT
    print("[Phase 1/5] EXTRACT — fetching doc & parsing tables")
    xml_text = fetch_doc_xml(args.doc)
    papers = parse_papers_from_xml(xml_text, tuple(args.year_range))
    print(f"  Extracted {len(papers)} papers from §4 tables")
    if not papers:
        print("  No papers found, exit.")
        return 1

    # Phase 2: LOOKUP
    print(f"\n[Phase 2/5] LOOKUP — querying arXiv API (sleep {RATE_LIMIT_S}s between batches)")
    papers = lookup_batch(papers, workers=args.workers)

    # Phase 3: BUILD
    print(f"\n[Phase 3/5] BUILD — formatting {len(papers)} papers as paper cards")
    section_md = build_section(papers)
    Path(args.output).write_text(section_md, encoding="utf-8")
    print(f"  Section markdown saved to: {args.output} ({len(section_md)} bytes)")

    # Phase 4: APPEND (skip if dry-run)
    if args.dry_run:
        print(f"\n[Phase 4/5] APPEND — SKIPPED (dry-run)")
    else:
        print(f"\n[Phase 4/5] APPEND — appending to doc {args.doc}")
        result = append_to_doc(args.doc, section_md, args.output)
        print(f"  {result}")

    # Phase 5: REPORT
    print(f"\n[Phase 5/5] REPORT — saving migration report")
    save_report(papers, args.report)

    # Summary
    by_status: dict[str, int] = {}
    for p in papers:
        by_status[p.status] = by_status.get(p.status, 0) + 1
    print(f"\n=== Summary ===")
    print(f"  Total: {len(papers)}")
    for st, n in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {st}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
