#!/usr/bin/env bash
# get-page-props.sh — 判定 Notion page 8 个 auto+llm 字段是否为空 (per ADR-0057 v3.1)
# 用法: bash get-page-props.sh <PAGE_ID>
# 输出: 8 行 "FIELD=<empty|filled>" (title / status / modal / link / knowledge / education / highlights / org)
# 用途: PATCH 时按"空才填"原则, 只把 LLM 算的字段填到 Notion 字段值仍空的 page 上,
#       已存在的值永不覆盖 (跟 v1.4 multi_select 保护 grader 协同)
# 联动: paper-into-notion v3.0 增量 (user 拍板 "默认 PATCH 时「空才填」") + v3.1 加 org 机构字段

set -euo pipefail
PAGE_ID="${1:?用法: bash get-page-props.sh <PAGE_ID>}"

ntn api --method GET "/v1/pages/$PAGE_ID" | python3 - <<'PYEOF'
import json, sys

page = json.load(sys.stdin)
props = page.get("properties", {})

def is_empty(prop):
    """判定 single field 的 '空' 形态 (Notion API 行为)."""
    if not prop:
        return True
    t = prop.get("type")
    if t == "title":
        return not prop.get("title", [])
    if t == "status":
        return prop.get("status") is None
    if t == "select":
        return prop.get("select") is None
    if t == "multi_select":
        return len(prop.get("multi_select", [])) == 0
    if t == "rich_text":
        return not prop.get("rich_text", [])
    if t == "url":
        return not prop.get("url")
    return True

import os
title_prop = os.environ.get("NOTION_TITLE_PROPERTY") or os.environ.get("TITLE_PROP") or "页面"
modal_prop = os.environ.get("NOTION_MODAL_PROPERTY") or os.environ.get("MODAL_PROP") or "平台"
org_prop = os.environ.get("NOTION_ORG_PROPERTY") or os.environ.get("ORG_PROP") or "机构"
keyword_prop = os.environ.get("NOTION_KEYWORD_PROPERTY") or os.environ.get("KEYWORD_PROP") or "关键词"  # v3.6
growth_prop = os.environ.get("NOTION_KNOWLEDGE_GROWTH_PROPERTY") or os.environ.get("KNOWLEDGE_GROWTH_PROP") or "知识等级形态"  # v3.7

print(f"title={'empty' if is_empty(props.get(title_prop)) else 'filled'}")
status_prop = props.get("状态")
print(f"status={'empty' if is_empty(status_prop) else 'filled'}")
print(f"modal={'empty' if is_empty(props.get(modal_prop)) else 'filled'}")

# link url 字段
print(f"link={'empty' if is_empty(props.get('link')) else 'filled'}")

# 4 LLM judge 字段: 关键词 / 知识等级形态 (v3.7 新, 旧 展现形式 已删) / 亮点 / 机构
print(f"knowledge={'empty' if is_empty(props.get(keyword_prop)) else 'filled'}")
print(f"growth={'empty' if is_empty(props.get(growth_prop)) else 'filled'}")
print(f"highlights={'empty' if is_empty(props.get('亮点')) else 'filled'}")
print(f"org={'empty' if is_empty(props.get(org_prop)) else 'filled'}")
PYEOF
