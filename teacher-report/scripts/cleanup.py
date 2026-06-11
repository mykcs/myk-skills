#!/usr/bin/env python3
"""
teacher-report v0.3.0 飞书 doc 清理脚本
SOP: ~/.agents/skills/teacher-report/SOP-normalize.md §步骤 0

功能: 一键清理飞书 doc 末尾的 v0.3.0 旧段 (§7/§8), 重生成干净 §7
适用: 之前 batch 跑乱 / 多次 append 产生重复段时

用法:
  python3 scripts/cleanup.py --doc <DOC_TOKEN> [--workers 4] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ---------- Helpers ----------


def lark_fetch_keyword(doc_id: str, keyword: str, context_after: int = 1) -> str:
    """fetch keyword 段 XML"""
    cmd = [
        "lark-cli",
        "docs",
        "+fetch",
        "--api-version",
        "v2",
        "--doc",
        doc_id,
        "--doc-format",
        "xml",
        "--detail",
        "with-ids",
        "--scope",
        "keyword",
        "--keyword",
        keyword,
        "--context-after",
        str(context_after),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"fetch failed: {result.stderr}")
    return result.stdout


def lark_block_delete(doc_id: str, block_id: str) -> bool:
    """block_delete (级联删子块)"""
    cmd = [
        "lark-cli",
        "docs",
        "+update",
        "--api-version",
        "v2",
        "--doc",
        doc_id,
        "--command",
        "block_delete",
        "--block-id",
        block_id,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return False
    return json.loads(result.stdout).get("ok", False)


def lark_block_insert_after(doc_id: str, anchor_id: str, content: str) -> Optional[str]:
    """block_insert_after"""
    cmd = [
        "lark-cli",
        "docs",
        "+update",
        "--api-version",
        "v2",
        "--doc",
        doc_id,
        "--command",
        "block_insert_after",
        "--block-id",
        anchor_id,
        "--content",
        content,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    return str(data.get("data", {}).get("document", {}).get("revision_id"))


def lark_append(doc_id: str, content: str) -> Optional[str]:
    """append content to doc end (用 @file 相对路径)"""
    tmp = Path("/tmp/teacher-report-cleanup-append.md")
    tmp.write_text(content, encoding="utf-8")
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
        f"@{tmp.name}",
        "--doc-format",
        "markdown",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(tmp.parent), timeout=60)
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    return str(data.get("data", {}).get("document", {}).get("revision_id"))


def find_v030_blocks(doc_id: str) -> dict[str, list[str]]:
    """扫描 doc 找 v0.3.0 相关的所有 block_id (H2/H3/footer paragraph)"""
    keywords = [
        "v0.3.0 Paper Card 详展（规范化",
        "v0.3.0 Paper Card 详展（批量规范化",
        "7.4 剩余 92",
        "本文档由 claudecode",
        "重跑 Generation mode",
    ]
    found: dict[str, list[str]] = {}
    for kw in keywords:
        try:
            xml = lark_fetch_keyword(doc_id, kw, context_after=1)
            ids = re.findall(r'<(h[1-6])\s+id="(doxcn[a-zA-Z0-9]+)"[^>]*>([^<]+)</\1>', xml)
            for tag, bid, content in ids:
                if kw[:15] in content or any(part in content for part in kw.split(" ")):
                    found.setdefault(kw, []).append((tag, bid, content[:60]))
        except Exception as e:
            print(f"  fetch '{kw}' failed: {e}")
    return found


# ---------- Main ----------


def main() -> int:
    ap = argparse.ArgumentParser(description="v0.3.0 飞书 doc 清理")
    ap.add_argument("--doc", required=True, help="飞书 doc token")
    ap.add_argument("--workers", type=int, default=4, help="arXiv lookup workers (留作未来重跑 batch 用)")
    ap.add_argument("--dry-run", action="store_true", help="只扫描不删不写")
    args = ap.parse_args()

    print(f"=== teacher-report v0.3.0 Doc Cleanup ===")
    print(f"Doc: {args.doc}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Step 1: 扫描所有 v0.3.0 块
    print("[Step 1/4] SCAN — 扫描 doc 找 v0.3.0 旧段")
    found = find_v030_blocks(args.doc)
    if not found:
        print("  No v0.3.0 blocks found. doc is clean.")
        return 0

    print(f"  Found {sum(len(v) for v in found.values())} v0.3.0 blocks:")
    for kw, items in found.items():
        print(f"    [{kw[:30]}]")
        for tag, bid, content in items:
            print(f"      {tag} {bid}: {content!r}")

    if args.dry_run:
        print(f"\n[DRY-RUN] Would delete {sum(len(v) for v in found.values())} blocks. Exit.")
        return 0

    # Step 2: 删所有 v0.3.0 块 (按 h2 优先 - 级联删子块)
    print(f"\n[Step 2/4] DELETE — 删除所有 v0.3.0 旧块")
    deleted = 0
    for kw, items in found.items():
        # 优先删 h2 块 (级联删子 h3/h4/p)
        h2_blocks = [(t, b, c) for t, b, c in items if t == "h2"]
        for tag, bid, content in h2_blocks:
            ok = lark_block_delete(args.doc, bid)
            if ok:
                print(f"  ✓ Deleted H2 {bid}: {content[:50]!r}")
                deleted += 1
            else:
                print(f"  ✗ Delete H2 {bid} failed")
        # h3 单独删 (如果 h2 删失败, 兜底删 h3)
        h3_blocks = [(t, b, c) for t, b, c in items if t == "h3"]
        for tag, bid, content in h3_blocks:
            ok = lark_block_delete(args.doc, bid)
            if ok:
                print(f"  ✓ Deleted H3 {bid}: {content[:50]!r}")
                deleted += 1
    print(f"  Total deleted: {deleted}")

    # Step 3: 重生成 paper cards (用 §7 模板)
    print(f"\n[Step 3/4] REGENERATE — 重生成 §7 干净 paper cards")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "normalize_v030", "/Users/myk/.agents/skills/teacher-report/scripts/normalize.py"
    )
    N = importlib.util.module_from_spec(spec)
    sys.modules["normalize_v030"] = N
    spec.loader.exec_module(N)

    report_path = "/tmp/normalize-report.json"
    if not Path(report_path).exists():
        print(f"  ✗ Report {report_path} not found. Re-run normalize.py first.")
        return 1

    report = json.load(open(report_path))
    papers = []
    for p_data in report["papers"]:
        p = N.Paper(
            seq=p_data["seq"],
            title_table=p_data["title_table"],
            year=p_data["year"],
            venue=p_data["venue"],
            tier=p_data["tier"],
            sort=p_data["sort"],
            students=p_data["students"],
            arxiv_id=p_data.get("arxiv_id", ""),
            arxiv_url=p_data.get("arxiv_url", ""),
            paperscool_url=p_data.get("paperscool_url", ""),
            title_verified=p_data.get("title_verified", ""),
            authors=p_data.get("authors", []),
            year_arxiv=p_data.get("year_arxiv", ""),
            status=p_data.get("status", "pending"),
            error=p_data.get("error", ""),
        )
        # 剥 arxiv_id 末尾 v\d+ 版本号
        if p.arxiv_id:
            clean = re.sub(r"v\d+$", "", p.arxiv_id)
            if clean != p.arxiv_id:
                p.arxiv_id = clean
                p.arxiv_url = f"https://arxiv.org/abs/{clean}"
                p.paperscool_url = f"https://papers.cool/arxiv/{clean}"
        papers.append(p)

    section_md = N.build_section(papers, section_no="7")
    out_path = "/tmp/paper-cards-section7-clean.md"
    Path(out_path).write_text(section_md, encoding="utf-8")
    print(f"  Section saved: {out_path} ({len(section_md)} bytes)")

    # Step 4: append 到 doc
    print(f"\n[Step 4/4] APPEND — append 干净 §7 到 doc 末尾")
    new_rev = lark_append(args.doc, section_md)
    if new_rev:
        print(f"  ✓ Append OK, revision: {new_rev}")
        print(f"\n=== Cleanup complete ===")
        print(f"  Doc: https://feishu.cn/docx/{args.doc}")
        return 0
    else:
        print(f"  ✗ Append failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
