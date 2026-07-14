#!/usr/bin/env bash
# notes-tldr.sh — abstract → 详细中文摘要 (per ADR-0057 v1.3)
# 用法: bash notes-tldr.sh <ABSTRACT_TEXT>
#       bash notes-tldr.sh --verify
# 输出: 多段纯文本 (≤500 字), 写入 Notion 笔记 rich_text
# 跟 highlights-judge 区别: notes-tldr 是详细摘要, highlights 是 1 句话 takeaway
# Per v2.7 fix: mmx v1.0.16 真用法 = mmx text chat --non-interactive --output json
# Per v2.9 (2026-07-14): 立补这个 v1.3 changelog 提到但从来没立过的 script

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ notes-tldr --verify ═══"
  if command -v mmx >/dev/null 2>&1; then
    mmx --version 2>&1 | head -1
    echo "    ✅ mmx found"
  else
    echo "    ⚠️ mmx not found, fallback: 取 abstract 前 300 字"
  fi
  exit 0
fi

ABSTRACT="${1:-}"
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash notes-tldr.sh <ABSTRACT_TEXT>" >&2
  echo "      bash notes-tldr.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 2000 字 (详细摘要要更多 context)
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 2000)

# LLM prompt: 详细中文摘要 3-5 段
PROMPT=$(printf 'You are a paper note writer. Read this abstract and write a detailed Chinese summary (300-500 chars, multi-paragraph). Cover: ① 问题 ② 方法 ③ 实验/结果 ④ 意义. Plain text only, no JSON, no markdown.\n\nAbstract:\n%s\n' "$ABSTRACT_TRIM")

TLDR=""
# 跑 LLM (mmx v1.0.16 真用法: text chat --non-interactive --output json)
if command -v mmx >/dev/null 2>&1; then
  TLDR=$(mmx text chat --non-interactive --output json --message "$PROMPT" 2>/dev/null \
    | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    content = d.get('content', '')
    if isinstance(content, list):
        for item in content:
            if item.get('type') == 'text':
                print(item.get('text', '').strip())
                break
    elif isinstance(content, str):
        print(content.strip())
except Exception:
    pass
" || echo "")
fi

# Fallback: mmx 不可用时截取 abstract 前 300 字
if [ -z "$TLDR" ]; then
  FIRST_PART=$(echo "$ABSTRACT_TRIM" | head -c 300)
  TLDR="$FIRST_PART"
  echo "⚠️ notes-tldr fallback → abstract 前 300 字" >&2
fi

# 截断到 500 字符
echo "${TLDR:0:500}"
