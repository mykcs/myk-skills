#!/usr/bin/env bash
# education-type-judge.sh — LLM judge 抓 abstract → 1-2 个 教育类型 标签 (per ADR-0057 v1.2)
# 用法: bash education-type-judge.sh <ABSTRACT_TEXT>
#       bash education-type-judge.sh --verify
# 输出: JSON 数组 ["综述", "实验"] (1-2 个, 从 13 选项白名单里)
# 跟 knowledge-tag-judge.sh 同模式, 但选 1-2 个 (教育类型粒度更粗)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 13 教育类型白名单 (per Notion schema 2026-07-14, 跟飞书 1:1 加 Notion 原有)
WHITELIST=(
  教授 课 基础知识 手把手实现 入门扫盲
  讲座讨论 PR 综述 实验 meeting insight
  论文阅读 项目
)

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ education-type-judge --verify ═══"
  if command -v mmx >/dev/null 2>&1; then
    mmx --version 2>&1 | head -1
    echo "    ✅ mmx found"
  else
    echo "    ⚠️ mmx not found, fallback: 关键词匹配"
  fi
  echo "[13 标签白名单]: ${WHITELIST[*]}"
  echo "    ✅ whitelist = 13"
  exit 0
fi

ABSTRACT="${1:-}"
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash education-type-judge.sh <ABSTRACT_TEXT>" >&2
  echo "      bash education-type-judge.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# LLM judge prompt: 选 1-2 个 (粒度比知识点粗)
PROMPT=$(cat <<EOF
You are a paper-type classifier. Read this paper abstract and pick 1-2 most relevant tags from this whitelist ONLY:

$(printf '%s\n' "${WHITELIST[@]}")

Return ONLY a JSON array, nothing else. Example: ["综述", "实验"]

Abstract:
$ABSTRACT_TRIM
EOF
)

# 跑 LLM (优先 mmx MiniMax-M3, fallback 关键词)
TAGS=()
if command -v mmx >/dev/null 2>&1; then
  LLM_OUTPUT=$(mmx chat "$PROMPT" 2>/dev/null || echo "")
fi

if [ -n "$LLM_OUTPUT" ]; then
  JSON_ARR=$(echo "$LLM_OUTPUT" | grep -oE '\[[^]]*\]' | head -1)
  if [ -n "$JSON_ARR" ]; then
    while IFS= read -r tag; do
      tag_clean=$(echo "$tag" | tr -d ' "[],' | head -c 30)
      for w in "${WHITELIST[@]}"; do
        if [ "$tag_clean" = "$w" ]; then
          TAGS+=("$w")
          break
        fi
      done
    done < <(echo "$JSON_ARR" | tr ',' '\n')

    # 限 2 个 (教育类型粒度粗)
    if [ ${#TAGS[@]} -gt 2 ]; then
      TAGS=("${TAGS[@]:0:2}")
    fi
  fi
fi

# Fallback: 关键词匹配
if [ ${#TAGS[@]} -eq 0 ]; then
  echo "⚠️ LLM judge fallback → 关键词匹配" >&2
  for w in "${WHITELIST[@]}"; do
    if echo "$ABSTRACT_TRIM" | grep -qi "$w"; then
      TAGS+=("$w")
      [ ${#TAGS[@]} -ge 2 ] && break
    fi
  done
  [ ${#TAGS[@]} -eq 0 ] && TAGS=("论文阅读")  # 最终 fallback (中性)
fi

# 输出 JSON 数组
if [ ${#TAGS[@]} -eq 0 ]; then
  echo "[]"
else
  printf '%s\n' "${TAGS[@]}" | python3 -c "
import json, sys
tags = [l.strip() for l in sys.stdin if l.strip()]
print(json.dumps(tags, ensure_ascii=False))
"
fi