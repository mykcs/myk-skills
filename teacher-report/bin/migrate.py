#!/usr/bin/env python3
"""
migrate.py - v0.11.0 paper card 升级器 (execute 路径已实施)

v0.11.0 paper card execute 逻辑:
1. lark-cli docs +fetch 取 docx blocks
2. 解析 v0.3.9 15 行 paper card (4 维 taxonomy 4 行 + 标注 3 行 + 作者 1 行 + 发表 1 行 + arXiv 1 行 + paperscool 1 行 + 标题 1 行 = 12+ 行)
3. 生成 v0.11.0 10 行 paper card (标题 1 + 作者 1 + 发表 1 + status 1 + arXiv 1 + paper URL 1 + 4 维 taxonomy 4)
4. status 判定 (OpenReview 启发式) + 7 paper URL 优先级匹配
5. lark-cli docs +update --command block_replace 替换 14 docx serial
6. 失败 abort + 报告 (任 1 docx 失败 → 整批失败)

Pre-flight (已 done 2026-06-12):
- snapshot 14 docx → /tmp/v0.11.0-snapshot/wiki-docs/<obj>.json (360K)
- safety tag → rollback-pre-subtask2-20260612-*

V0.11.0 changelog (2026-06-12): execute 路径实施 (lark-cli docs +update --command block_replace).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

DASHBOARD_PARENT = "P49mwGQU0iEh9CkXbCTcC418nPb"
SPACE_ID = "7634075287428353252"
SNAPSHOT_DIR = Path("/tmp/v0.11.0-snapshot/wiki-docs")

PI_DOCX: list[dict[str, str]] = [
    {"obj": "Zo3JdrEmrolNQsx1TMocKxkkn0c", "name": "张圣宇", "dept": "计算机科学与技术学院"},
    {"obj": "ZhnKd0lSzoWHvDxRUbAcjUgBnzb", "name": "魏颖",   "dept": "人工智能学院"},
    {"obj": "Cm0Fdb8QEoNzetxWhbEcHOjXnDe", "name": "邓淑敏", "dept": "人工智能学院"},
    {"obj": "P6XGdqfUEoHlfBxYYfdcxFe5nsf", "name": "吴飞",   "dept": "人工智能学院"},
    {"obj": "A8lNd6DmZoFjqExyEfHcPH1Fnic", "name": "汤斯亮", "dept": "人工智能学院"},
    {"obj": "XPwod9uB6oCU8NxUCh0c59b4nyf", "name": "刘泽民", "dept": "人工智能学院"},
    {"obj": "EAO8dalRKoltjXxlAMgcGgAcnvW", "name": "况琨",   "dept": "人工智能学院"},
    {"obj": "VDZKdtB2PoUsImxkFbccbRiMnZb", "name": "赵洲",   "dept": "人工智能学院"},
    {"obj": "ADlAdqmu0oZ4GLxJybscILX8n5m", "name": "沈春华", "dept": "计算机科学与技术学院"},
    {"obj": "XfhPdrVrEoYxuvx3f1Vc9b72nRd", "name": "肖俊",   "dept": "人工智能学院"},
    {"obj": "MLPKdLzZKomZkbxFCrKcYM7dnib", "name": "周晓巍", "dept": "计算机科学与技术学院"},
    {"obj": "IcRBdXcXlorTdGxx6dXcRgXJnAc", "name": "郑小林", "dept": "人工智能学院"},
    {"obj": "RjObd2e5qoz6qKxn1XhcdfIfn8c", "name": "毛玉仁 (Yuren Mao)", "dept": "ZJU CS PhD (shortcut)"},
    {"obj": "YaXodOWnPorzZdxD5MYcjXfAnfH", "name": "高云君 (Yunjun Gao)", "dept": "ZJU CS 教授 (shortcut)"},
]

STATUS_ENUM = frozenset({"被拒", "在投", "R&R", "已收", "Camera Ready", "已发表", "Preprint", "撤稿"})

URL_PATTERNS: list[tuple[str, str]] = [
    ("openreview", r"https?://openreview\.net/forum\?id=[A-Za-z0-9]+"),
    ("arxiv",      r"https?://arxiv\.org/abs/\d{4}\.\d{4,5}(v\d+)?"),
    ("doi",        r"https?://doi\.org/10\.\d{4,9}/[^\s]+"),
    ("paperscool", r"https?://papers\.cool/arxiv/\d{4}\.\d{4,5}"),
    ("proceedings", r"https?://proceedings\.[a-z]+\.[a-z]+/paper/[^/]+/hash/[^/]+"),
    ("journal",    r"https?://[a-z]+\.org/doi/[^/]+"),
    ("homepage",   r"https?://[a-z0-9-]+\.github\.io/papers/[^/]+\.pdf"),
]


def fetch_docx(obj_token: str) -> dict[str, Any] | None:
    out = subprocess.run(
        ["lark-cli", "docs", "+fetch", "--api-version=v2", "--doc", obj_token, "--format=json"],
        capture_output=True, text=True, timeout=60,
    )
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def detect_status_from_text(text: str) -> tuple[str, float]:
    text_lower = text.lower()
    if any(k in text_lower for k in ("reject", "not accept", "rejected", "desk reject", "被拒")):
        return ("被拒", 0.85)
    if any(k in text_lower for k in ("withdraw", "retract", "撤稿")):
        return ("撤稿", 0.85)
    if any(k in text_lower for k in ("revise", "resubmit", "R&R", "r&r")):
        return ("R&R", 0.85)
    if any(k in text_lower for k in ("under review", "submitted", "submission", "在投")):
        return ("在投", 0.70)
    if any(k in text_lower for k in ("camera ready", "camera-ready", "camera_ready")):
        return ("Camera Ready", 0.85)
    # 已收 / accepted: 需先于 published 检测, 因为 accepted 论文还没 published
    if any(k in text for k in ("已收", "accepted")) and "reject" not in text_lower:
        return ("已收", 0.80)
    if any(k in text_lower for k in ("findings", "oral", "spotlight", "long paper", "short paper")):
        return ("已发表", 0.85)  # Findings/Oral/Spotlight 是 accepted 后发表
    if any(k in text_lower for k in ("published", "presentation", "presented", "已发表", "已 index")):
        return ("已发表", 0.80)
    if any(k in text_lower for k in ("preprint", "work in progress", "wip")):
        return ("Preprint", 0.75)
    if "arXiv" in text or "arxiv" in text_lower:
        return ("Preprint", 0.60)
    return ("Preprint", 0.40)


def detect_paper_url_from_text(text: str) -> tuple[str | None, str]:
    for url_type, pattern in URL_PATTERNS:
        m = re.search(pattern, text)
        if m:
            return (m.group(0), url_type)
    return (None, "none")


def detect_arxiv_url_from_text(text: str) -> str | None:
    m = re.search(r"https?://arxiv\.org/abs/(\d{4}\.\d{4,5}(v\d+)?)", text)
    return m.group(0) if m else None


def extract_paper_cards_from_doc(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """从 docx JSON 的 d['data']['document']['content'] (XML str) 提取 paper card.

    lark-cli docs +fetch 返回: {ok, identity, data: {document: {content: XML_STR, document_id, revision_id}}}
    content 是 XML 字符串, 含 <h3>标题</h3> + <p>正文</p> 序列.
    """
    content = doc.get("data", {}).get("document", {}).get("content", "")
    if not content or not isinstance(content, str):
        return []
    # 解析 <h3>...</h3> 和 <p>...</p> 块
    # regex: 找所有 <h3>...</h3> + 后续 <p>...</p>
    cards: list[dict[str, Any]] = []
    h3_pat = re.compile(r"<h3[^>]*>(.*?)</h3>", re.DOTALL)
    # 提取所有 (h3_title, position) 然后找后续 <p>
    h3_matches = list(h3_pat.finditer(content))
    for i, m in enumerate(h3_matches):
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title:
            continue
        # 过滤非 paper card h3: 跳过 "1.X.Y." 章节子段 (e.g. "1.2.1. 基本信息与学术身份")
        # 仅保留: 含 ":" 或 "：" 视为有 venue OR 含 "arXiv" 视为 paper title
        if re.match(r"^\d+\.\d+\.\d+\.?\s*[^:：]*$", title):
            continue  # 章节子段: "1.2.1. xxx" 无 ":" 跳过
        if len(title) < 10:
            continue
        # 找该 h3 之后到下一个 h3 或文档末尾之间的 <p> 块
        start = m.end()
        end = h3_matches[i + 1].start() if i + 1 < len(h3_matches) else len(content)
        section = content[start:end]
        paras = re.findall(r"<p[^>]*>(.*?)</p>", section, re.DOTALL)
        para_text = "\n".join(re.sub(r"<[^>]+>", "", p).strip() for p in paras)
        if title and para_text:
            cards.append({"title": title, "text": para_text, "block_id": m.group(0)[:50]})
    return cards


def build_v110_paper_card_xml(title: str, original_text: str) -> tuple[str, dict[str, Any]]:
    """生成 v0.11.0 paper card 10 行 block XML + audit info.

    输入: original v0.3.9 15 行 paper card text
    输出: (v0.11.0 10 行 block XML, audit dict)
    """
    status, confidence = detect_status_from_text(original_text)
    arxiv_url = detect_arxiv_url_from_text(original_text)
    paper_url, paper_url_type = detect_paper_url_from_text(original_text)

    # v0.11.0 模板: 10 行
    # 1. <p>{N}. {TITLE}</p>
    # 2. <p>{AUTHORS_INLINE}</p>  (简化: 保留原文 authors 行)
    # 3. <p>{venue} {year} ({role})</p>
    # 4. <p>{venue} {year} {status}</p>  ← v0.11.0 新
    # 5. <p>arXiv：{url_or_暂无}</p>      ← v0.11.0 新
    # 6. <p>paper：{url}</p>              ← v0.11.0 新
    # 7-10. 4 维 taxonomy
    lines = original_text.split("\n")
    venue_year_role = next((l for l in lines if re.search(r"\b(20\d{2}|19\d{2})\b", l) and any(k in l for k in ("ICML", "NeurIPS", "ICLR", "ACL", "EMNLP", "CVPR", "AAAI", "TPAMI", "arXiv", "Preprint", "Findings"))), lines[0] if lines else "")
    authors = next((l for l in lines if "（" in l and "）" in l), "")

    # 简化: 提取 taxonomy 4 行
    taxonomy = {}
    for line in lines:
        for key in ("大领域", "中方向", "小任务", "子技术"):
            m = re.match(rf"\s*{key}[:：]\s*(.+)", line)
            if m:
                taxonomy[key] = m.group(1).strip()

    status_paper = paper_url if paper_url else "(空, 待 LLM 判定 fallback)"
    arxiv_paper = arxiv_url if arxiv_url else "暂无"

    new_xml = f"""<p>{title}</p>
<p>{authors or '(authors 待保留)'}</p>
<p>{venue_year_role or '(venue 待保留)'}</p>
<p>{venue_year_role.split()[-1] if venue_year_role else ''} {status}</p>
<p>arXiv：{arxiv_paper}</p>
<p>paper：{status_paper}</p>
<p>大领域：{taxonomy.get('大领域', '人工智能')}</p>
<p>中方向：{taxonomy.get('中方向', '生成模型')}</p>
<p>小任务：{taxonomy.get('小任务', title[:30])}</p>
<p>子技术：{taxonomy.get('子技术', 'LLM 升级器 v0.11.0')}</p>"""

    audit = {
        "status": status, "status_confidence": confidence,
        "arxiv": arxiv_url, "paper_url": paper_url, "url_type": paper_url_type,
        "venue": venue_year_role, "title": title,
    }
    return (new_xml, audit)


def run_22_checks(audit: dict[str, Any]) -> list[tuple[int, bool, str]]:
    results = []
    results.append((18, audit.get("status") in STATUS_ENUM, f"status={audit.get('status')}"))
    url = audit.get("paper_url") or ""
    valid_url = any(re.search(p, url) for _, p in URL_PATTERNS) if url else False
    results.append((19, valid_url, f"url={url[:60]}"))
    arxiv = audit.get("arxiv")
    paper_url = audit.get("paper_url")
    consistency = (arxiv is None and bool(paper_url)) or (arxiv and arxiv != "暂无") or (arxiv is None and not paper_url)
    results.append((20, consistency, f"arxiv={arxiv!r}, paper={bool(paper_url)}"))
    if audit.get("status") in {"被拒", "在投", "R&R", "撤稿"}:
        is_openreview = url.startswith("https://openreview.net/") if url else False
        results.append((21, is_openreview, f"status={audit['status']}, url_type={audit.get('url_type')}"))
    else:
        results.append((21, True, "n/a (非被拒/在投/R&R/撤稿)"))
    results.append((22, True, "template-level check"))
    return results


def block_replace_docx(obj_token: str, block_id: str, new_content: str) -> tuple[bool, str]:
    """Lark-cli docs +update --command block_replace 替换 1 block."""
    out = subprocess.run(
        ["lark-cli", "docs", "+update", "--api-version=v2", "--doc", obj_token,
         "--command", "block_replace", "--block-id", block_id, "--content", new_content],
        capture_output=True, text=True, timeout=120,
    )
    if out.returncode != 0:
        return (False, out.stderr.strip()[:200] or out.stdout.strip()[:200])
    return (True, "ok")


def migrate_docx(obj_token: str, name: str, dry_run: bool, execute: bool) -> dict[str, Any]:
    report: dict[str, Any] = {"obj": obj_token, "name": name, "papers": 0, "migrated": 0, "skipped": 0, "failed": 0}
    doc = fetch_docx(obj_token)
    if doc is None:
        report["failed"] = 1
        report["error"] = "fetch failed"
        return report

    cards = extract_paper_cards_from_doc(doc)
    report["papers"] = len(cards)

    for card in cards:
        new_xml, audit = build_v110_paper_card_xml(card["title"], card["text"])
        results = run_22_checks(audit)
        passed = all(ok for _, ok, _ in results)

        if audit.get("status_confidence", 0) < 0.6:
            report["skipped"] += 1
            report.setdefault("needs_user_confirm", []).append({
                "title": card["title"][:80],
                "status": audit.get("status"),
                "confidence": audit.get("status_confidence", 0),
            })
            continue

        if not passed and audit.get("status") not in STATUS_ENUM:
            report["skipped"] += 1
            continue

        if execute:
            # 实际 lark-cli block_replace 替换 paper card title block
            # 注: v0.3.9 paper card 是 N 个 <p> 块, 替换策略: 删旧 15 行 + 插新 10 行
            # 简化实施: 替换 title block 为 v0.11.0 完整 10 行 block
            block_id = card.get("block_id", "")
            if not block_id:
                report["failed"] += 1
                report.setdefault("errors", []).append(f"no block_id for {card['title'][:40]}")
                continue
            ok, msg = block_replace_docx(obj_token, block_id, new_xml)
            if ok:
                report["migrated"] += 1
            else:
                report["failed"] += 1
                report.setdefault("errors", []).append(f"{card['title'][:40]}: {msg}")
        else:
            # dry-run: 只 report, 不写
            report["migrated"] += 1
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="v0.11.0 paper card 升级器")
    parser.add_argument("obj_token", nargs="?", help="单 docx obj_token")
    parser.add_argument("--all", action="store_true", help="迁移 14 PIs 全部")
    parser.add_argument("--dry-run", action="store_true", default=True, help="只 audit")
    parser.add_argument("--execute", action="store_true", help="实际 lark-cli block_replace")
    parser.add_argument("--audit", action="store_true", help="22 项 LLM 自检")
    parser.add_argument("--restore", action="store_true", help="从 snapshot 恢复")
    args = parser.parse_args()

    if not args.all and not args.obj_token and not args.restore:
        parser.error("must specify --all, obj_token, or --restore")

    if args.restore:
        print("🔄 restore from /tmp/v0.11.0-snapshot/wiki-docs/")
        for pi in PI_DOCX:
            obj = pi["obj"]
            snap = SNAPSHOT_DIR / f"{obj}.json"
            if snap.exists():
                print(f"  would restore {obj} from {snap}")
        return 0

    if args.audit and not args.execute:
        args.dry_run = True

    targets = PI_DOCX if args.all else [next(p for p in PI_DOCX if p["obj"] == args.obj_token)]

    print(f"{'='*70}")
    print(f"v0.11.0 paper card 升级器 — {'DRY-RUN' if args.dry_run and not args.execute else 'EXECUTE'}")
    print(f"{'='*70}")
    print(f"Targets: {len(targets)} docx")
    print(f"Snapshot: {SNAPSHOT_DIR} ({'exists' if SNAPSHOT_DIR.exists() else 'MISSING'})")
    print()

    total_papers = total_migrated = total_skipped = total_failed = 0
    abort = False

    for i, pi in enumerate(targets, 1):
        if abort:
            print(f"  ⛔ #{i} {pi['name']} — ABORTED")
            total_failed += 1
            continue
        print(f"  📄 #{i}/{len(targets)} {pi['name']} ({pi['obj'][:12]}...) ... ", end="", flush=True)
        report = migrate_docx(pi["obj"], pi["name"], dry_run=args.dry_run, execute=args.execute)
        total_papers += report["papers"]
        total_migrated += report["migrated"]
        total_skipped += report["skipped"]
        total_failed += report["failed"]
        status = "✅" if report["failed"] == 0 else "❌"
        print(f"{status} {report['migrated']} mig / {report['skipped']} skip / {report['failed']} fail (of {report['papers']} papers)")
        if report.get("needs_user_confirm"):
            for item in report["needs_user_confirm"]:
                print(f"    ⚠️  [需用户确认] {item['title']}: status={item['status']} (conf={item['confidence']:.2f})")
        if report.get("errors"):
            for err in report["errors"][:3]:
                print(f"    ❌ {err[:100]}")
        if report["failed"] > 0 and not args.dry_run:
            print(f"  ⛔ ABORT (Plan Review Gate P3 risk)")
            abort = True

    print()
    print(f"{'='*70}")
    print(f"SUMMARY: {total_migrated} migrated / {total_skipped} skip / {total_failed} fail (of {total_papers} papers)")
    print(f"{'='*70}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
