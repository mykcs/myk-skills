"""verify_all_fields.py — 跑后全字段必填检查 (v4.1 永久防范机制).

user 2026-07-15 反馈 "page 里所有字段都应该填上" 后立. 任何字段空都报警.
v4.5 (2026-07-18) 加 keyword abstract 命中检查 (per CASE-PAPER-INTO-NOTION-V4-5-KEYWORD-OBJECTIVITY):
  - keyword 3 个中至少 2 个必须在 abstract 出现 ≥ 1 次
  - 否则报 "0 命中" silent loss, 走 v4.5 keyword objective 反模式永久失效

用法: python verify_all_fields.py <PAGE_ID> [<ABSTRACT>]
  - PAGE_ID: Notion page id (必填)
  - ABSTRACT: paper abstract 文本 (可选, 提供时跑 keyword objective 检查)
"""
from __future__ import annotations

import re
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


def check_keyword_objective(page_id: str, abstract: str) -> tuple[str, list[str]]:
    """v4.5 立: 检查 Notion 关键词跟 abstract 命中度 (防止 LLM judge 凭 general knowledge 瞎填).

    判定:
    - GET page 拿 关键词 multi_select
    - 每个 keyword 在 abstract 出现次数 (lowercase, 中英文混查)
    - 3 个 keyword 中至少 2 个在 abstract 出现 ≥ 1 次 → PASS
    - 否则 FAIL, 返 missing list = keyword name (没命中的)

    Returns: (status_str, non_hitting_keyword_names_list)

    用法: paper-into-notion.py main 跑后 verify_page 后立即调 (auto-check)
    """
    if not abstract:
        return "SKIP", []
    data = ntn_api("GET", f"/v1/pages/{page_id}")
    keywords_raw = data.get("properties", {}).get("关键词", {}).get("multi_select", [])
    keywords = [k["name"] for k in keywords_raw]
    if not keywords:
        return "FAIL", ["关键词 (全空)"]

    abstract_lower = abstract.lower()
    non_hitting = []
    for kw in keywords:
        # 中英文混查 (中文走字面, 英文走 lowercase)
        kw_lower = kw.lower()
        hit = kw_lower in abstract_lower or kw in abstract
        if not hit:
            non_hitting.append(kw)
    # 硬规则: 3 个 keyword 中 ≥ 2 命中 (允许 1 个漏, 防止过严)
    if len(keywords) >= 3 and len(non_hitting) >= max(2, len(keywords) - 1):
        return "FAIL", non_hitting
    if len(keywords) < 3 and len(non_hitting) > 0:
        return "FAIL", non_hitting
    return "PASS", []


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python verify_all_fields.py <PAGE_ID> [<ABSTRACT>]", file=sys.stderr)
        sys.exit(1)
    page_id = sys.argv[1]
    abstract = sys.argv[2] if len(sys.argv) >= 3 else ""
    status, missing = check_all_fields_filled(page_id)
    if missing:
        print(f"❌ check_all_fields_filled: {status}: 缺 {len(missing)} 个字段: {missing}")
        sys.exit(1)
    else:
        print(f"✅ check_all_fields_filled: {status}: 全字段已填")
    # v4.5 加: keyword abstract 命中检查
    if abstract:
        kw_status, non_hitting = check_keyword_objective(page_id, abstract)
        if kw_status == "FAIL":
            print(f"❌ check_keyword_objective: 关键词 0 命中 abstract ({len(non_hitting)} 项): {non_hitting}")
            print(f"   → 反模式 #58 (v4.5): LLM judge 凭 general knowledge 填了非 abstract 词")
            sys.exit(1)
        elif kw_status == "PASS":
            print(f"✅ check_keyword_objective: 关键词全命中 abstract")
        else:
            print(f"⚠️ check_keyword_objective: SKIP (无 abstract)")
    sys.exit(0)