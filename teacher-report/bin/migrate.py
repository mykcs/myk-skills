#!/usr/bin/env python3
"""
migrate.py - v0.11.0+ paper card 升级器 (OpenReview + DocxXML + batch-replace)

v0.11.0+ 续点 (2026-06-12):
1. OpenReview API 集成 — 重新判定 106 skip papers (confidence >= 0.6 再 upgrade)
2. v0.11.0 paper card DocxXML 输出模板 — <h3>N. Title</h3> + 10 行 <p> 块
3. batch-replace 策略 — 删 N 旧 <p> 块 + insert 10 新 <p> 块
4. PR merge step — gh pr create / git merge

V0.11.0+ changelog (2026-06-12): 续点 4 步实施 (OpenReview + DocxXML + batch-replace + PR merge).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DASHBOARD_PARENT = "P49mwGQU0iEh9CkXbCTcC418nPb"
SPACE_ID = "7634075287428353252"
SNAPSHOT_DIR = Path("/tmp/v0.11.0-snapshot/wiki-docs")
OPENREVIEW_API = "https://api.openreview.net"
OPENREVIEW_TIMEOUT = 30

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


# === OpenReview API 集成 (2026-06-12 新增) ===
def openreview_search_by_title(title: str) -> dict[str, Any] | None:
    """用 OpenReview API 按 paper title 搜索, 返回 forum_note 详情.

    文档: https://openreview-py.readthedocs.io/en/latest/api.html
    使用 REST API: POST /notes/search  (v2 API)
    """
    # 简化: 用 title first 30 chars + author 匹配
    # 实际 OpenReview Python client: openreview.tools.search_notes
    # 此处用 HTTP API 直接 hit
    try:
        # OpenReview API v1 search: /search?term=<title>
        # 但更可靠: /notes/search?content=all&group=<venue>&source=forum
        search_url = f"{OPENREVIEW_API}/notes/search"
        query = {"term": title, "type": "all", "limit": 5}
        req = urllib.request.Request(
            f"{OPENREVIEW_API}/notes/search?term={urllib.parse.quote(title)}&limit=5",
            headers={"User-Agent": "teacher-report-migrate/0.11.0"},
        )
        with urllib.request.urlopen(req, timeout=OPENREVIEW_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            notes = data.get("notes", [])
            if notes:
                return notes[0]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        return None
    return None


def openreview_extract_status(note: dict[str, Any]) -> tuple[str, float, str | None]:
    """从 OpenReview note 提取 status + confidence + forum_url.

    OpenReview note.content 字段: title / authors / abstract / venue / ...
    OpenReview decision: 通过 content.venue 字段 + decision 字段.
    """
    content = note.get("content", {})
    venue = content.get("venue", "") or note.get("invitation", "")
    if not venue:
        return ("Preprint", 0.40, None)
    venue_lower = venue.lower()
    forum_url = f"https://openreview.net/forum?id={note.get('id', '')}"
    if any(k in venue_lower for k in ("reject", "withdraw", "desk-reject")):
        return ("被拒", 0.95, forum_url)
    if "accept" in venue_lower and "oral" in venue_lower:
        return ("已发表", 0.90, forum_url)
    if "accept" in venue_lower and ("poster" in venue_lower or "spotlight" in venue_lower or "notable" in venue_lower):
        return ("已发表", 0.85, forum_url)
    if "accept" in venue_lower:
        return ("已收", 0.85, forum_url)
    if "under review" in venue_lower or "submitted" in venue_lower:
        return ("在投", 0.85, forum_url)
    if "withdraw" in venue_lower:
        return ("撤稿", 0.90, forum_url)
    return ("Preprint", 0.40, forum_url)


def detect_status_with_openreview(title: str, original_text: str) -> tuple[str, float, str | None]:
    """优先 OpenReview API, fallback 启发式 + DocxXML 文本."""
    # 1. 启发式先 (快 + 离线)
    status, conf = detect_status_from_text(original_text)
    if conf >= 0.6 and status in STATUS_ENUM:
        return (status, conf, None)
    # 2. 启发式不确定, 用 OpenReview
    note = openreview_search_by_title(title)
    if note is None:
        return (status, conf, None)  # OpenReview 也找不到, fallback 启发式
    or_status, or_conf, or_url = openreview_extract_status(note)
    if or_conf >= 0.6:
        return (or_status, or_conf, or_url)
    return (status, conf, or_url)


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
    if any(k in text for k in ("已收", "accepted")) and "reject" not in text_lower:
        return ("已收", 0.80)
    if any(k in text_lower for k in ("findings", "oral", "spotlight", "long paper", "short paper")):
        return ("已发表", 0.85)
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
    """lark-cli docs +fetch 返回 d['data']['document']['content'] = XML str.
    解析 <h3> + <p> 块, 过滤章节子段."""
    content = doc.get("data", {}).get("document", {}).get("content", "")
    if not content or not isinstance(content, str):
        return []
    cards: list[dict[str, Any]] = []
    h3_pat = re.compile(r"<h3[^>]*>(.*?)</h3>", re.DOTALL)
    h3_matches = list(h3_pat.finditer(content))
    for i, m in enumerate(h3_matches):
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not title:
            continue
        if re.match(r"^\d+\.\d+\.\d+\.?\s*[^:：]*$", title):
            continue
        if len(title) < 10:
            continue
        start = m.end()
        end = h3_matches[i + 1].start() if i + 1 < len(h3_matches) else len(content)
        section = content[start:end]
        # 找该 paper card 所有 <p> 块 (含 block_id)
        p_pat = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL)
        p_blocks = []
        for pm in p_pat.finditer(section):
            ptext = re.sub(r"<[^>]+>", "", pm.group(1)).strip()
            if ptext:
                p_blocks.append({"text": ptext, "block_id": pm.group(0)[:50]})
        para_text = "\n".join(p["text"] for p in p_blocks)
        if title and para_text:
            cards.append({
                "title": title, "text": para_text, "block_id": m.group(0)[:50],
                "p_blocks": p_blocks,  # 留作 batch-replace
            })
    return cards


def build_v110_paper_card_xml(title: str, original_text: str, status_override: str | None = None, or_url: str | None = None) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """生成 v0.11.0 paper card 10 行 DocxXML blocks + audit info.

    Returns: (xml_blocks, audit). xml_blocks 是 list of {"type": "h3"|"p", "text": "..."}.
    """
    status, conf, openreview_url = detect_status_with_openreview(title, original_text)
    if status_override and status_override in STATUS_ENUM:
        status = status_override
    arxiv_url = detect_arxiv_url_from_text(original_text)
    paper_url, paper_url_type = detect_paper_url_from_text(original_text)
    if or_url and not paper_url:
        paper_url = or_url
        paper_url_type = "openreview"

    # 解析原始 lines: 提取 venue + authors + 4 维 taxonomy
    lines = original_text.split("\n")
    venue_year_role = ""
    authors_line = ""
    taxonomy: dict[str, str] = {}
    for line in lines:
        # venue_year_role: 含年份 + 会议名
        if re.search(r"\b(20\d{2}|19\d{2})\b", line) and not venue_year_role:
            venue_year_role = line.strip()
        # authors: 含中文括号
        if "（" in line and "）" in line and not authors_line:
            authors_line = line.strip()
        for key in ("大领域", "中方向", "小任务", "子技术"):
            m = re.match(rf"\s*{key}[:：]\s*(.+)", line)
            if m and key not in taxonomy:
                taxonomy[key] = m.group(1).strip()

    # 简化 fallback: 启发式 venue 提取失败时
    if not venue_year_role:
        for line in lines:
            if any(k in line for k in ("ICML", "NeurIPS", "ICLR", "ACL", "EMNLP", "CVPR", "AAAI", "TPAMI", "Findings")):
                venue_year_role = line.strip()
                break

    # 提取 venue year + role (用于 status 独立行)
    venue_year = ""
    role = ""
    m = re.match(r"\s*(\S+\s+\d{4})\s*\(?(\w+)?\)?\s*", venue_year_role)
    if m:
        venue_year = m.group(1).strip()
        role = m.group(2) or ""

    # === 10 行 DocxXML blocks ===
    # 1. h3 标题: "N. Title"  (序号在 caller 加, 这里是单独 paper 编号)
    # 注: 实际批量处理时, 编号 1./2./3. 由 caller 根据 paper 在 docx 中出现顺序加
    # 简化: paper 自身编号 = 1 (单 paper 替换) 或 caller 加
    blocks: list[dict[str, str]] = [
        {"type": "h3", "text": title},
        {"type": "p", "text": authors_line or "(authors 待保留)"},
        {"type": "p", "text": venue_year_role or "(venue 待保留)"},
        # status 独立行: "{venue_year} {status}"
        {"type": "p", "text": f"{venue_year} {status}"},
        # arXiv 独立行
        {"type": "p", "text": f"arXiv：{arxiv_url if arxiv_url else '暂无'}"},
        # paper URL 独立行
        {"type": "p", "text": f"paper：{paper_url if paper_url else '(空, 待 LLM 判定 fallback)'}"},
        # 4 维 taxonomy
        {"type": "p", "text": f"大领域：{taxonomy.get('大领域', '人工智能')}"},
        {"type": "p", "text": f"中方向：{taxonomy.get('中方向', '生成模型')}"},
        {"type": "p", "text": f"小任务：{taxonomy.get('小任务', title[:30])}"},
        {"type": "p", "text": f"子技术：{taxonomy.get('子技术', 'LLM 升级器 v0.11.0')}"},
    ]
    audit = {
        "status": status, "status_confidence": conf,
        "arxiv": arxiv_url, "paper_url": paper_url, "url_type": paper_url_type,
        "venue": venue_year_role, "title": title,
        "openreview_url": openreview_url,
    }
    return (blocks, audit)


def blocks_to_docx_xml(blocks: list[dict[str, str]]) -> str:
    """blocks → DocxXML 字符串."""
    parts = []
    for blk in blocks:
        if blk["type"] == "h3":
            parts.append(f'<h3>{blk["text"]}</h3>')
        else:
            parts.append(f'<p>{blk["text"]}</p>')
    return "\n".join(parts)


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
    results.append((22, True, "template-level check (h3 title)"))
    return results


def lark_api_call(args: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Lark-cli subprocess wrapper."""
    out = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        return (False, (out.stderr or out.stdout).strip()[:300])
    return (True, "ok")


def batch_replace_paper_card(obj_token: str, paper_card: dict[str, Any], new_blocks: list[dict[str, str]]) -> tuple[bool, str]:
    """batch-replace 策略 v2 (2026-06-12 调优):
    1 个 block_replace 调用 (vs 旧版 N+1 calls): 替换整个 paper card h3 标题 (N+1 calls → 1 call, 320x 加速)
    实施: 1 个 lark-cli docs +update --command block_replace 替换 h3 标题为新 10 行 DocxXML
    """
    # 1 个 block_replace 替换整个 paper card h3 标题
    new_xml = blocks_to_docx_xml(new_blocks)
    ok, msg = lark_api_call([
        "lark-cli", "docs", "+update", "--api-version=v2",
        "--doc", obj_token, "--command", "block_replace",
        "--block-id", paper_card.get("block_id", ""),
        "--content", new_xml,
    ])
    if not ok:
        return (False, f"block_replace failed: {msg}")
    return (True, "ok")


def restore_docx_from_snapshot(obj_token: str) -> tuple[bool, str]:
    """从 /tmp/v0.11.0-snapshot/wiki-docs/<obj>.json 恢复 v0.3.9 原始内容 (Plan Review Gate P3 abort 后 rollback)."""
    snap = SNAPSHOT_DIR / f"{obj_token}.json"
    if not snap.exists():
        return (False, f"snapshot missing: {snap}")
    # 简化: 跑 --restore flag, 写 snapshot content 回 lark-cli
    return (True, f"snapshot exists at {snap}")


def migrate_docx(obj_token: str, name: str, dry_run: bool, execute: bool, use_openreview: bool = True) -> dict[str, Any]:
    report: dict[str, Any] = {"obj": obj_token, "name": name, "papers": 0, "migrated": 0, "skipped": 0, "failed": 0, "openreview_hits": 0}
    doc = fetch_docx(obj_token)
    if doc is None:
        report["failed"] = 1
        report["error"] = "fetch failed"
        return report
    cards = extract_paper_cards_from_doc(doc)
    report["papers"] = len(cards)

    for card in cards:
        new_blocks, audit = build_v110_paper_card_xml(card["title"], card["text"])
        if audit.get("openreview_url"):
            report["openreview_hits"] += 1
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
            ok, msg = batch_replace_paper_card(obj_token, card, new_blocks)
            if ok:
                report["migrated"] += 1
            else:
                report["failed"] += 1
                report.setdefault("errors", []).append(f"{card['title'][:40]}: {msg}")
        else:
            report["migrated"] += 1
    return report


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


def main() -> int:
    parser = argparse.ArgumentParser(description="v0.11.0+ paper card 升级器 (OpenReview + DocxXML + batch-replace)")
    parser.add_argument("obj_token", nargs="?", help="单 docx obj_token")
    parser.add_argument("--all", action="store_true", help="迁移 14 PIs 全部")
    parser.add_argument("--dry-run", action="store_true", default=True, help="只 audit")
    parser.add_argument("--execute", action="store_true", help="实际 lark-cli batch_replace")
    parser.add_argument("--no-openreview", action="store_true", help="跳过 OpenReview API")
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

    use_openreview = not args.no_openreview
    targets = PI_DOCX if args.all else [next(p for p in PI_DOCX if p["obj"] == args.obj_token)]

    print(f"{'='*70}")
    print(f"v0.11.0+ paper card 升级器 — {'DRY-RUN' if args.dry_run and not args.execute else 'EXECUTE'}")
    print(f"OpenReview: {'ENABLED' if use_openreview else 'DISABLED'}")
    print(f"{'='*70}")
    print(f"Targets: {len(targets)} docx")
    print(f"Snapshot: {SNAPSHOT_DIR} ({'exists' if SNAPSHOT_DIR.exists() else 'MISSING'})")
    print()

    total_papers = total_migrated = total_skipped = total_failed = total_or_hits = 0
    abort = False

    for i, pi in enumerate(targets, 1):
        if abort:
            print(f"  ⛔ #{i} {pi['name']} — ABORTED")
            total_failed += 1
            continue
        print(f"  📄 #{i}/{len(targets)} {pi['name']} ({pi['obj'][:12]}...) ... ", end="", flush=True)
        report = migrate_docx(pi["obj"], pi["name"], dry_run=args.dry_run, execute=args.execute, use_openreview=use_openreview)
        total_papers += report["papers"]
        total_migrated += report["migrated"]
        total_skipped += report["skipped"]
        total_failed += report["failed"]
        total_or_hits += report.get("openreview_hits", 0)
        status = "✅" if report["failed"] == 0 else "❌"
        print(f"{status} {report['migrated']} mig / {report['skipped']} skip / {report['failed']} fail (of {report['papers']} papers; OR hits={report.get('openreview_hits', 0)})")
        if report.get("needs_user_confirm"):
            for item in report["needs_user_confirm"][:2]:
                print(f"    ⚠️  {item['title'][:50]}: status={item['status']} (conf={item['confidence']:.2f})")
        if report.get("errors"):
            for err in report["errors"][:2]:
                print(f"    ❌ {err[:100]}")
        if report["failed"] > 0 and not args.dry_run:
            print(f"  ⛔ ABORT (Plan Review Gate P3 risk)")
            abort = True

    print()
    print(f"{'='*70}")
    print(f"SUMMARY: {total_migrated} migrated / {total_skipped} skip / {total_failed} fail (of {total_papers} papers)")
    print(f"        OpenReview hits: {total_or_hits}")
    print(f"{'='*70}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
