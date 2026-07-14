#!/usr/bin/env bash
# notes-tldr.sh — abstract → 1-2 句话中文笔记摘要 (per ADR-0057 v1.3)
# 用法: bash notes-tldr.sh <ABSTRACT_TEXT>
#       bash notes-tldr.sh --verify
# 输出: 纯文本 (1-2 句话中文, ≤200 字), 写入 Notion 笔记 rich_text
# 跟 knowledge-tag-judge.sh 同模式 (mmx LLM + heuristic fallback)

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
    echo "    ⚠️ mmx not found, fallback: 取 abstract 前 200 字"
  fi
  exit 0
fi

ABSTRACT="${1:-}"
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash notes-tldr.sh <ABSTRACT_TEXT>" >&2
  echo "      bash notes-tldr.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# LLM prompt: 1-2 句中文摘要
PROMPT=$(cat <<EOF
You are a paper note writer. Read this abstract and write 1-2 sentences in Chinese (≤200 chars total) summarizing the key contribution. Plain text only, no JSON, no markdown.

Abstract:
$ABSTRACT_TRIM
EOF
)

# 跑 LLM
if command -v mmx >/dev/null 2>&1; then
  LLM_OUTPUT=$(mmx chat "$PROMPT" 2>/dev/null || echo "")
fi

# Fallback: 取 abstract 前 200 字 (heuristic, 简单粗暴)
if [ -z "$LLM_OUTPUT" ]; then
  echo "⚠️ notes-tldr fallback → 取 abstract 前 200 字" >&2
  NOTE=$(echo "$ABSTRACT_TRIM" | head -c 200)
else
  NOTE="$LLM_OUTPUT"
fi

# 截断到 500 字符 (Notion rich_text 单段上限)
echo "${NOTE:0:500}"