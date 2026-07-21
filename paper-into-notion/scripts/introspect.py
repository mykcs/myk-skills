#!/usr/bin/env python3
"""introspect.py — 自动读 Notion data source schema, 输出 property 名 + status default.

v4.0 升级 (per CASE-NOTION-PAPER-COL-ENRICH-20260719 + ADR-0075-b):
- 缓存 TTL 24h → 5min (per CASE-NOTION-PAPER-COL-ENRICH, 24h 太长 → schema drift silent loss)
- 新增 verify_schema() 函数: 写入 PATCH 前必 query 1 个 page 反推字段, 防止字段名 silent drift
- 新增 --no-cache flag: 调试用, 跳过 cache 直读 schema
- 新增 --verify-page flag: 跑 schema.FieldMap.from_page 模式 (query page 反推字段, 5min TTL)

用法:
  python3 introspect.py <DS_ID> [CACHE_FILE] [--no-cache] [--verify-page]
输出:
  KEY=VALUE 行 (TITLE_PROP / STATUS_PROP / STATUS_DEFAULT / MODAL_PROP / KNOWLEDGE_GROWTH_PROP)
"""
import json
import subprocess
import sys
import os
import time
from typing import Optional


# v4.0: TTL 24h → 5min (per CASE-NOTION-PAPER-COL-ENRICH-20260719)
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_schema(ds_id: str) -> dict:
    """GET /v1/data_sources/{ds_id} via ntn CLI."""
    result = subprocess.run(
        ["ntn", "api", "--method", "GET", f"/v1/data_sources/{ds_id}",
         "--notion-version", "2026-03-11"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def verify_schema(ds_id: str, expected: dict) -> bool:
    """v4.0 新增: query 1 个 page 反推字段, verify schema 字段名还匹配.

    per CASE-NOTION-PAPER-COL-ENRICH-20260719 (paper-into-notion v3.x wrapper
    8 行 PATCH 全过, 3 行因平台跳过 = schema.FieldMap.from_page silent loss).

    Args:
        ds_id: data source ID
        expected: dict from parse_schema()

    Returns:
        True if schema still matches (字段名 + 默认值), False if drift detected.
    """
    try:
        # query page 反推字段 (per ntn-cli §1.1 + paper-into-notion v4 协议)
        result = subprocess.run(
            ["ntn", "api", "--method", "POST",
             f"/v1/data_sources/{ds_id}/query",
             "--notion-version", "2026-03-11",
             "-d", json.dumps({"page_size": 1})],
            capture_output=True, text=True, check=True, timeout=30,
        )
        page_data = json.loads(result.stdout)
        results = page_data.get("results", [])
        if not results:
            # 0 pages = schema 字段名不在 page 中暴露, 但 query 没报错 = 字段名 OK
            return True
        # 取第一个 page 的 properties, verify expected 字段名都在
        page_props = results[0].get("properties", {})
        for key, expected_val in expected.items():
            # KEY 是字段名, expected_val 是字段值或默认值
            if key.endswith("_PROP"):
                # PROP 是字段名, verify 字段真存在
                if expected_val not in page_props:
                    print(f"⚠️ verify_schema 失败: {key}={expected_val} 不在 page properties 中", file=sys.stderr)
                    return False
        return True
    except Exception as e:
        print(f"⚠️ verify_schema 异常 (视为 schema 不匹配, 阻止写入): {e}", file=sys.stderr)
        return False


def parse_schema(schema: dict) -> dict:
    """Extract property names + status default from schema."""
    props = schema.get("properties", {})
    out = {}
    # Title property (only 1 per db)
    out["TITLE_PROP"] = next(
        (k for k, v in props.items() if v.get("type") == "title"), "页面"
    )
    # Status property + first option as default
    out["STATUS_PROP"] = "状态"
    out["STATUS_DEFAULT"] = "未开始"
    for k, v in props.items():
        if v.get("type") == "status":
            out["STATUS_PROP"] = k
            opts = v.get("status", {}).get("options", [])
            if opts:
                out["STATUS_DEFAULT"] = opts[0].get("name", "未开始")
            break
    # Select: 模态字段 (db 字段真名"平台形式" 必含"形式", 不能再 filter 掉)
    select_props = [(k, v) for k, v in props.items() if v.get("type") == "select"]

    def _modal_options_match(item):
        k, v = item
        opts = v.get("select", {}).get("options", [])
        return any(o.get("name") == "arXiv" for o in opts)

    out["MODAL_PROP"] = next(
        (k for k, _ in select_props if _modal_options_match((k, v))),
        next((k for k, _ in select_props if "平台" in k or "模态" in k),
             next((k for k, _ in select_props), "平台形式"))
    )
    # v3.7: FORM_PROP 弃用 (旧 展现形式 select 已 user UI 删)
    # v3.7: KB_GROWTH_PROP auto-detect 唯一 multi_select (name 含 知识/形态)
    multi_select_props = [k for k, v in props.items() if v.get("type") == "multi_select"]
    kb_growth = next((k for k in multi_select_props if "知识" in k or "形态" in k), None)
    out["KNOWLEDGE_GROWTH_PROP"] = kb_growth or (multi_select_props[0] if multi_select_props else "知识等级形态")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 introspect.py <DS_ID> [CACHE_FILE] [--no-cache] [--verify-page]", file=sys.stderr)
        return 1
    ds_id = sys.argv[1]
    cache = None
    no_cache = "--no-cache" in sys.argv
    verify_page = "--verify-page" in sys.argv
    # parse positional cache arg (第二参数, 非 flag)
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        cache = sys.argv[2]

    # Check cache (v4.0: TTL 24h → 5min)
    if cache and not no_cache and os.path.exists(cache):
        age = time.time() - os.path.getmtime(cache)
        if age < CACHE_TTL_SECONDS:
            with open(cache) as f:
                sys.stdout.write(f.read())
            return 0
        else:
            print(f"⚠️ cache 过期 (age={age:.0f}s > {CACHE_TTL_SECONDS}s), 重新 fetch", file=sys.stderr)

    # Fetch + parse + cache
    try:
        schema = get_schema(ds_id)
    except Exception as e:
        print(f"❌ introspect 失败: {e}", file=sys.stderr)
        return 1
    result = parse_schema(schema)
    output = "\n".join(f"{k}={v}" for k, v in result.items()) + "\n"

    # v4.0 新增: verify-page 模式 (query page 反推字段, 防 schema drift silent loss)
    if verify_page:
        if not verify_schema(ds_id, result):
            print("❌ verify_schema 失败, 字段名疑似 drift, 阻止写入", file=sys.stderr)
            return 2

    sys.stdout.write(output)
    if cache:
        with open(cache, "w") as f:
            f.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())