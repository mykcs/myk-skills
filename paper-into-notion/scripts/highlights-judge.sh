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

# 跑 LLM (主: 抓 abstract → 中文 takeaway)
if command -v mmx >/dev/null 2>&1; then
  LLM_OUTPUT=$(mmx chat "$PROMPT" 2>/dev/null || echo "")
fi

HIGHLIGHT=""
if [ -n "$LLM_OUTPUT" ]; then
  HIGHLIGHT="$LLM_OUTPUT"
else
  # Fallback 第 1 层: mmx 翻译 abstract 第 1 句 → 中文
  FIRST_SENTENCE=$(echo "$ABSTRACT_TRIM" | sed -n '1p' | head -c 300)
  if command -v mmx >/dev/null 2>&1; then
    TRANSLATED=$(mmx chat "Translate this English sentence to Chinese, plain text only: $FIRST_SENTENCE" 2>/dev/null || echo "")
    if [ -n "$TRANSLATED" ]; then
      HIGHLIGHT="$TRANSLATED"
      echo "⚠️ highlights-judge fallback → mmx 翻译 abstract 第 1 句" >&2
    fi
  fi
fi

# Fallback 第 2 层: heuristic 检测, 不可翻译时留中文提示
if [ -z "$HIGHLIGHT" ]; then
  FIRST_SENTENCE=$(echo "$ABSTRACT_TRIM" | sed -n '1p' | head -c 100)
  # 检测中文字符比例 (>30% = 已经是中文, 直接用)
  CHINESE_RATIO=$(echo "$FIRST_SENTENCE" | python3 -c "
import sys
text = sys.stdin.read()
chinese = sum(1 for c in text if '一' <= c <= '鿿')
total = len(text.replace(' ', ''))
print(chinese / total if total > 0 else 0)
")
  if [ "$(echo "$CHINESE_RATIO > 0.3" | python3 -c 'import sys; print(sys.stdin.read() and \"yes\" or \"no\")' 2>/dev/null)" = "yes" ]; then
    HIGHLIGHT="$FIRST_SENTENCE"
    echo "⚠️ highlights-judge fallback → abstract 第 1 句已是中文" >&2
  else
    # 英文 + 无 mmx → 留中文提示, 你后填
    HIGHLIGHT="(需 mmx 翻译: $FIRST_SENTENCE)"
    echo "⚠️ highlights-judge fallback → mmx 不可用, 留英文占位待你后填" >&2
  fi
fi

# 截断到 200 字符
echo "${HIGHLIGHT:0:200}"