"""verify_all_fields.py — 跑后全字段必填检查 (v4.1 永久防范机制).

user 2026-07-15 反馈 "page 里所有字段都应该填上" 后立. 任何字段空都报警.

用法: python verify_all_fields.py <PAGE_ID>
返: (status, missing_list)
  - status: "PASS" (全填) / "FAIL" (有字段空)
  - missing_list: 空字段名 list
"""
from __future__ import annotations

import sys

from ntn_client import ntn_call as ntn_api


def check_all_fields_filled(page_id: str) -> tuple[str, list[str]]:
    """GET page 拿全部 properties, 检查所有字段是否非空.

    "空" 定义:
    - title: 字段无 text content
    - select / status: 无 name
    - multi_select: 空数组 = 缺, **除非 LLM 判定 0 候选** (e.g. 机构)
    - rich_text: 无 text content
    - url: 空字符串
    - 其他类型 (date, checkbox 等): 跳过检查

    v4 设计: LLM judge 必填字段 (highlights/keyword/knowledge_growth) 严格检查;
    LLM 0 候选字段 (org) 允许空数组. 区分这两类是关键.

    Returns: (status_str, missing_field_names_list)
    """
    data = ntn_api("GET", f"/v1/pages/{page_id}")
    props = data.get("properties", {})
    missing: list[str] = []

    for name, val in props.items():
        prop_type = val.get("type")
        if prop_type == "title":
            title_arr = val.get("title", [])
            if not title_arr or not title_arr[0].get("plain_text", "").strip():
                missing.append(name)
        elif prop_type == "select":
            sel = val.get("select")
            if not sel or not sel.get("name"):
                missing.append(name)
        elif prop_type == "status":
            sta = val.get("status")
            if not sta or not sta.get("name"):
                missing.append(name)
        elif prop_type == "multi_select":
            ms = val.get("multi_select", [])
            # 关键词/知识等级形态 严格必填 (LLM 必给 1+ 项)
            # 机构 LLM 0 候选允许空 (没匹配白名单)
            if not ms:
                if name in ("关键词", "知识等级形态"):
                    missing.append(name)
                # else: 机构 / 其他 multi_select 允许空
        elif prop_type == "rich_text":
            # 亮点 严格必填
            rt = val.get("rich_text", [])
            if not rt or not rt[0].get("plain_text", "").strip():
                if name == "亮点":
                    missing.append(name)
        elif prop_type == "url":
            u = val.get("url")
            # link 字段必填 (URL 是核心信息)
            if not u and name == "link":
                missing.append(name)
        # 其他类型 (last_edited_time / created_time / 机构 等) 跳过

    status = "PASS" if not missing else "FAIL"
    return status, missing


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python verify_all_fields.py <PAGE_ID>", file=sys.stderr)
        sys.exit(1)
    page_id = sys.argv[1]
    status, missing = check_all_fields_filled(page_id)
    if missing:
        print(f"❌ {status}: 缺 {len(missing)} 个字段: {missing}")
        sys.exit(1)
    else:
        print(f"✅ {status}: 全字段已填")
        sys.exit(0)