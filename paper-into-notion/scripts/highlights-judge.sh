#!/usr/bin/env bash
# highlights-judge.sh — abstract → 1 句话中文 takeaway (per ADR-0057 v1.3)
# 用法: bash highlights-judge.sh <ABSTRACT_TEXT>
#       bash highlights-judge.sh --verify
# 输出: 纯文本 (1 句话, ≤100 字), 写入 Notion 亮点 rich_text
# 跟 notes-tldr 区别: notes-tldr 是详细摘要, highlights 是一句话 takeaway

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ highlights-judge --verify ═══"
  if command -v mmx >/dev/null 2>&1; then
    mmx --version 2>&1 | head -1
    echo "    ✅ mmx found"
  else
    echo "    ⚠️ mmx not found, fallback: 取 abstract 第 1 句"
  fi
  exit 0
fi

ABSTRACT="${1:-}"
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash highlights-judge.sh <ABSTRACT_TEXT>" >&2
  echo "      bash highlights-judge.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# LLM prompt: 1 句 takeaway
PROMPT=$(cat <<EOF
You are a paper TLDR writer. Read this abstract and write 1 sentence (≤100 chars Chinese) capturing the most important takeaway. Plain text only, no JSON, no markdown.

Abstract:
$ABSTRACT_TRIM
EOF
)

# 跑 LLM
if command -v mmx >/dev/null 2>&1; then
  LLM_OUTPUT=$(mmx chat "$PROMPT" 2>/dev/null || echo "")
fi

# Fallback: 取 abstract 第 1 句 (heuristic)
if [ -z "$LLM_OUTPUT" ]; then
  echo "⚠️ highlights-judge fallback → 取 abstract 第 1 句" >&2
  HIGHLIGHT=$(echo "$ABSTRACT_TRIM" | sed -n '1p' | head -c 100)
else
  HIGHLIGHT="$LLM_OUTPUT"
fi

# 截断到 200 字符
echo "${HIGHLIGHT:0:200}"