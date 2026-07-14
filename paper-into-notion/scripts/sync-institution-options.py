#!/usr/bin/env python3
"""sync-institution-options.py — auto-add missing institution options to Notion multi_select (per ADR-0057 v3.3)

用法:
  python3 sync-institution-options.py <DS_ID> <NEW_OPTIONS_JSON>
  e.g.: python3 sync-institution-options.py 39dfedee-... '["Bo Han Lab","Google Brain"]'

行为:
  1. GET /v1/data_sources/{id} → 拿 机构 multi_select options
  2. 比对: new - current = missing
  3. PATCH /v1/data_sources/{id} 合并 (保留已有, 新增 gray)
  4. 输出 'OK synced: +[N1,N2]' 或 'NOOP nothing to sync' 或 'ERROR: ...'

设计: 不写死 whitelist, paper 真实机构名入库, Notion API 自动归类
"""
import json
import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python3 sync-institution-options.py <DS_ID> <NEW_OPTIONS_JSON>", file=sys.stderr)
        print('  e.g.: python3 sync-institution-options.py DS_ID \'["Bo Han Lab"]\'', file=sys.stderr)
        return 2

    ds_id = sys.argv[1]
    new_json = sys.argv[2]

    # 1. GET current schema
    r = subprocess.run(
        ["ntn", "api", "--method", "GET", f"/v1/data_sources/{ds_id}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"ERROR: GET schema failed: {r.stderr[:200]}", file=sys.stderr)
        return 1
    try:
        schema = json.loads(r.stdout)
        cur_opts = schema.get("properties", {}).get("机构", {}).get("multi_select", {}).get("options", [])
    except Exception as e:
        print(f"ERROR: parse schema: {e}", file=sys.stderr)
        return 1

    # 2. 比对
    try:
        new_names = set(json.loads(new_json))
    except Exception as e:
        print(f"ERROR: parse new_options: {e}", file=sys.stderr)
        return 1
    cur_names = {o["name"] for o in cur_opts}
    missing = sorted(new_names - cur_names)
    if not missing:
        print("NOOP nothing to sync")
        return 0

    # 3. PATCH (保留已有 option object 含 id/color, 新增 gray)
    merged = list(cur_opts)
    for name in missing:
        merged.append({"name": name, "color": "gray"})
    payload = {"properties": {"机构": {"multi_select": {"options": merged}}}}
    r = subprocess.run(
        ["ntn", "api", "--method", "PATCH", f"/v1/data_sources/{ds_id}", "-d", json.dumps(payload, ensure_ascii=False)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"ERROR: PATCH failed: {r.stderr[:200]}", file=sys.stderr)
        return 1
    print(f"OK synced: +{missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
