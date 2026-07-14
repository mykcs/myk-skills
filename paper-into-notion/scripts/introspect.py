#!/usr/bin/env python3
"""introspect.py — 自动读 Notion data source schema, 输出 property 名 + status default.
替代 v2.5 的 4 env variable override. 缓存 24h.
用法: python3 introspect.py <DS_ID> [CACHE_FILE]
输出: KEY=VALUE 行 (TITLE_PROP / STATUS_PROP / STATUS_DEFAULT / MODAL_PROP / FORM_PROP)
"""
import json
import subprocess
import sys
import os
import time


def get_schema(ds_id: str) -> dict:
    """GET /v1/data_sources/{ds_id} via ntn CLI."""
    result = subprocess.run(
        ["ntn", "api", "--method", "GET", f"/v1/data_sources/{ds_id}"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


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
    # Select: 模态类型 (arXiv / 公众号 / etc)
    out["MODAL_PROP"] = next(
        (k for k, v in props.items() if v.get("type") == "select"), "平台"
    )
    # Select: 展现形式/教育类型 (form)
    out["FORM_PROP"] = next(
        (
            k for k, v in props.items()
            if v.get("type") == "select" and k != out["MODAL_PROP"]
        ),
        "展现形式",
    )
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python3 introspect.py <DS_ID> [CACHE_FILE]", file=sys.stderr)
        return 1
    ds_id = sys.argv[1]
    cache = sys.argv[2] if len(sys.argv) > 2 else None
    # Check cache
    if cache and os.path.exists(cache):
        age = time.time() - os.path.getmtime(cache)
        if age < 86400:
            with open(cache) as f:
                sys.stdout.write(f.read())
            return 0
    # Fetch + parse + cache
    try:
        schema = get_schema(ds_id)
    except Exception as e:
        print(f"❌ introspect 失败: {e}", file=sys.stderr)
        return 1
    result = parse_schema(schema)
    output = "\n".join(f"{k}={v}" for k, v in result.items()) + "\n"
    sys.stdout.write(output)
    if cache:
        with open(cache, "w") as f:
            f.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
