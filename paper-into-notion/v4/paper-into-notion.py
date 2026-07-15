#!/usr/bin/env python3
"""paper-into-notion v4 — 单入口 Python (替代 v3.x 11 shell).

Usage:
  python paper-into-notion.py <URL> [--dry-run] [--verify]

Examples:
  python paper-into-notion.py "https://arxiv.org/abs/2603.26188"
  python paper-into-notion.py --dry-run "https://arxiv.org/abs/1706.03762"
  python paper-into-notion.py --verify
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import tomllib  # py 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # py <3.11 fallback

# 同包 import
from schema import FieldMap, SchemaCache, ntn_query_latest_page
from judge import judge_5_fields, JudgeResult
from verify_all_fields import check_all_fields_filled


SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.toml"
CACHE_DIR = SCRIPT_DIR / "cache"


@dataclass
class Paper:
    title: str
    authors: str
    abstract: str
    source_url: str
    modal: str
    highlights: str
    keyword: list[str]
    org: list[str]
    knowledge_growth: list[str]


# === Phase 1: 模态判定 (5 pattern grep) ===

def detect_modal(url: str) -> str:
    u = url.lower()
    if "arxiv.org" in u:
        return "arXiv"
    if "mp.weixin.qq.com" in u:
        return "微信公众号"
    if any(x in u for x in ["twitter.com", "x.com"]):
        return "Twitter"
    if any(x in u for x in ["blog", "medium.com", "juejin.cn", "zhuanlan.zhihu.com", "github.io/posts", "github.com/blog"]):
        return "博客"
    return "其他"


# === Phase 2: arXiv 抓取 (重试 3 次) ===

def fetch_arxiv(arxiv_id: str, rate_limit_sec: int = 3) -> Paper:
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1"
    last_err = None
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-fsSLG", url],
                capture_output=True, text=True, timeout=30,
            )
            r.check_returncode()
            return _parse_arxiv_xml(r.stdout, arxiv_id)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            last_err = e
            time.sleep(rate_limit_sec)
    raise RuntimeError(f"arXiv 抓取失败 (3 次重试): {arxiv_id}, err={last_err}")


def _parse_arxiv_xml(xml: str, arxiv_id: str) -> Paper:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml)
    entry = root.find("atom:entry", ns)
    if entry is None:
        raise RuntimeError(f"arXiv XML 没 entry: {arxiv_id}")
    title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
    abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
    authors = ", ".join(
        a.findtext("atom:name", default="", namespaces=ns) or ""
        for a in entry.findall("atom:author", ns)
    )
    source_url = f"https://arxiv.org/abs/{arxiv_id}"
    return Paper(
        title=title, authors=authors, abstract=abstract,
        source_url=source_url, modal="arXiv",
        highlights="", keyword=[], org=[], knowledge_growth=[],
    )


def extract_arxiv_id(url: str) -> str:
    """'https://arxiv.org/abs/2603.26188' → '2603.26188'."""
    parts = url.rstrip("/").split("/")
    return parts[-1]


# === Phase 3: LLM judge (5 字段) ===

def run_judge(paper: Paper, config: dict) -> JudgeResult:
    if not config["judge"]["enabled"]:
        return JudgeResult(highlights="", keyword=[], org=[], knowledge_growth=[])
    prompts_dir = SCRIPT_DIR / config["judge"]["prompts_dir"]
    mmx_args = config["judge"]["mmx_subcmd_args"]
    return judge_5_fields(paper.abstract, paper.authors, prompts_dir, mmx_args)


# === Phase 4: 字段级 merge + 写 Notion ===

def ntn_api(method: str, path: str, body: dict | None = None) -> dict:
    cmd = ["ntn", "api", "--method", method, path]
    if body is not None:
        cmd += ["-d", json.dumps(body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"ntn api {method} {path} 失败: {r.stderr}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def find_existing_page(ds_id: str, title: str, title_prop: str) -> str | None:
    """query db 找 title 匹配的 page."""
    body = {
        "filter": {"property": title_prop, "title": {"equals": title}},
        "page_size": 1,
    }
    data = ntn_api("POST", f"/v1/data_sources/{ds_id}/query", body)
    results = data.get("results", [])
    return results[0]["id"] if results else None


def build_properties(paper: Paper, fm: FieldMap, config: dict) -> dict:
    """构造 PATCH/POST body (v4 全部字段都填, per user 2026-07-15 拍板).

    旧 v3.x 铁律 (multi_select 永不传) 在 v4 取消, 因为:
    - user 反馈 "page 里所有字段都应该填上"
    - v4 是新 page POST 居多, 老 page PATCH 用 --force flag 显式覆盖
    """
    props: dict = {
        fm.title: {"title": [{"text": {"content": paper.title}}]},
        fm.status: {"status": {"name": config["status_default"]["name"]}},
        fm.modal: {"select": {"name": paper.modal}},
    }
    # link url (optional)
    if fm.link:
        props[fm.link] = {"url": paper.source_url}
    # rich_text 字段 (highlights)
    if paper.highlights:
        props[fm.highlights] = {"rich_text": [{"text": {"content": paper.highlights}}]}
    # multi_select 字段 (keyword / org / knowledge_growth) — 全填, 不再 strip
    if fm.keyword and paper.keyword:
        props[fm.keyword] = {"multi_select": [{"name": k} for k in paper.keyword]}
    if fm.org and paper.org:
        props[fm.org] = {"multi_select": [{"name": o} for o in paper.org]}
    if fm.knowledge_growth and paper.knowledge_growth:
        props[fm.knowledge_growth] = {"multi_select": [{"name": g} for g in paper.knowledge_growth]}
    return props


def post_new_page(ds_id: str, props: dict) -> dict:
    body = {
        "parent": {"type": "data_source_id", "data_source_id": ds_id},
        "properties": props,
    }
    return ntn_api("POST", "/v1/pages", body)


def patch_existing_page(page_id: str, props: dict) -> dict:
    return ntn_api("PATCH", f"/v1/pages/{page_id}", {"properties": props})


def verify_page(page_id: str, expected_props: dict) -> bool:
    """GET page 比对预期 props (per v3.1 空才填守卫 + verify 二次确认)."""
    data = ntn_api("GET", f"/v1/pages/{page_id}")
    actual = data.get("properties", {})
    for prop_name, expected in expected_props.items():
        actual_prop = actual.get(prop_name, {})
        # 简化: 检查 type + 关键值存在
        for type_key, expected_val in expected.items():
            if type_key == "title":
                if not actual_prop.get("title"):
                    print(f"  ❌ {prop_name} title 空")
                    return False
            elif type_key == "select":
                if not actual_prop.get("select", {}).get("name"):
                    print(f"  ❌ {prop_name} select 空")
                    return False
            elif type_key == "url":
                if not actual_prop.get("url"):
                    print(f"  ❌ {prop_name} url 空")
                    return False
    return True


# === 主入口 ===

def main() -> int:
    parser = argparse.ArgumentParser(description="paper-into-notion v4 (Python single entry)")
    parser.add_argument("url", nargs="?", help="paper URL (arXiv / 公众号 / 博客 / Twitter / 其他)")
    parser.add_argument("--dry-run", action="store_true", help="跑全流程但不写 Notion")
    parser.add_argument("--verify", action="store_true", help="检查 ntn auth + config + 字段映射")
    args = parser.parse_args()

    config = tomllib.loads(CONFIG_FILE.read_text())

    if args.verify:
        print("=== paper-into-notion v4 --verify ===")
        cache = SchemaCache(CACHE_DIR, config["schema_cache"]["ttl_seconds"])
        fm = cache.get_or_fetch(config["notion"]["data_source_id"], ntn_query_latest_page)
        print(json.dumps(asdict(fm), ensure_ascii=False, indent=2))
        return 0

    if not args.url:
        parser.error("URL 必填 (或用 --verify)")

    # Phase 1: 模态
    modal = detect_modal(args.url)
    print(f"[1/4] 模态: {modal}")

    # Phase 2: arXiv 抓 (其他模态 stub)
    if modal == "arXiv":
        arxiv_id = extract_arxiv_id(args.url)
        paper = fetch_arxiv(arxiv_id, config["arxiv"]["rate_limit_sec"])
        paper.modal = modal
        print(f"[2/4] arXiv {arxiv_id}: {paper.title[:60]}...")
    else:
        # 非 arXiv 暂只填 URL 当 title
        paper = Paper(
            title=args.url, authors="", abstract="", source_url=args.url,
            modal=modal, highlights="", keyword=[], org=[], knowledge_growth=[],
        )
        print(f"[2/4] 非 arXiv: 用 URL 当 title")

    # Phase 3: LLM judge 5 字段
    if paper.abstract:
        jr = run_judge(paper, config)
        paper.highlights = jr.highlights
        paper.keyword = jr.keyword
        paper.org = jr.org
        paper.knowledge_growth = jr.knowledge_growth
        print(f"[3/4] LLM judge: 关键词={paper.keyword}, growth={paper.knowledge_growth}")

    # Phase 4: 字段级 merge + 写 Notion
    cache = SchemaCache(CACHE_DIR, config["schema_cache"]["ttl_seconds"])
    fm = cache.get_or_fetch(config["notion"]["data_source_id"], ntn_query_latest_page)
    ds_id = config["notion"]["data_source_id"]
    props = build_properties(paper, fm, config)

    if args.dry_run:
        print(f"[DRY-RUN] ⚠️ 不写 Notion")
        print(f"[DRY-RUN]   title: {paper.title}")
        print(f"[DRY-RUN]   modal: {paper.modal}")
        print(f"[DRY-RUN]   properties keys: {list(props.keys())}")
        print(f"DRY-RUN-PAGE-ID (fake)")
        return 0

    # 找已有 page → PATCH / 新 page → POST
    existing = find_existing_page(ds_id, paper.title, fm.title)
    if existing:
        result = patch_existing_page(existing, props)
        print(f"[4/4] PATCH 已有 page {existing}")
    else:
        result = post_new_page(ds_id, props)
        print(f"[4/4] POST 新 page {result.get('id')}")

    # verify
    if config["behavior"]["verify_5_fields"]:
        page_id = result.get("id") or existing
        if verify_page(page_id, props):
            print("✅ verify_5_fields PASS")
        else:
            print("⚠️ verify_5_fields 部分失败")
            return 1

    # 全字段必填检查 (user 2026-07-15 反馈 "page 里所有字段都应该填上" 后立)
    page_id = result.get("id") or existing
    status, missing = check_all_fields_filled(page_id)
    if missing:
        print(f"❌ {status}: 缺字段 {missing}")
        return 1
    print(f"✅ {status}: 全字段已填 (亮点/关键词/知识等级形态 必填, 机构 LLM 0 候选允许空)")
    return 0


if __name__ == "__main__":
    sys.exit(main())