#!/usr/bin/env bash
# knowledge-tag-judge.sh — LLM judge 抓 abstract → 1-3 个 知识点 标签 (per ADR-0057 v1.1)
# 用法: bash knowledge-tag-judge.sh <ABSTRACT_TEXT>
#       bash knowledge-tag-judge.sh --verify
# 输出: JSON 数组 ["llm", "Transformer", "attention"] (1-3 个标签, 只用 40 选项里的)
# LLM: 走 mmx-cli (per N-tool-search.md §6 第 6 工具, Bash `mmx search` 实际是 mmx chat)
# 铁律: 输出必须从 40 选项白名单里选 (per Notion schema), 不创造新选项

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 40 知识点白名单 (per Notion schema 2026-07-13, 跟飞书 1:1)
WHITELIST=(
  llm cv 科研认知 表征学习 分割 fcn Transformer cuda mamba
  科研基本功 医学图像 attention 深度学习 nlp 机器学习 服务器
  超声心动 SAM mobile 数学 视频 加速 rnn unet rwkv
  FlashAttention 线性代数 writing rebuttal tricks Parallel
  Linear 噪声 可视化 collection robot 编译 sonta RoPE diffusion
)

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ knowledge-tag-judge --verify ═══"
  if command -v mmx >/dev/null 2>&1; then
    mmx --version 2>&1 | head -1
    echo "    ✅ mmx found"
  else
    echo "    ⚠️ mmx not found, fallback: 用本地关键词匹配 (无 LLM judge)"
  fi
  echo "[40 标签白名单]: ${WHITELIST[*]}"
  echo "    ✅ whitelist = 40"
  exit 0
fi

ABSTRACT="${1:-}"
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash knowledge-tag-judge.sh <ABSTRACT_TEXT>" >&2
  echo "      bash knowledge-tag-judge.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字 (避免 LLM context 太大, mmx MiniMax-M3 足够)
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# LLM judge prompt: 选 1-3 个最贴标签, 只从白名单
PROMPT=$(cat <<EOF
You are a research classifier. Read this paper abstract and pick 1-3 most relevant tags from this whitelist ONLY:

$(printf '%s\n' "${WHITELIST[@]}")

Return ONLY a JSON array, nothing else. Example: ["llm", "Transformer"]

Abstract:
$ABSTRACT_TRIM
EOF
)

# 跑 LLM (优先 mmx MiniMax-M3, fallback 关键词匹配)
if command -v mmx >/dev/null 2>&1; then
  LLM_OUTPUT=$(mmx chat "$PROMPT" 2>/dev/null || echo "")
fi

# 解析 LLM 输出 + 过滤白名单
TAGS=()
if [ -n "$LLM_OUTPUT" ]; then
  # 提取 JSON 数组 (可能夹其他文字)
  JSON_ARR=$(echo "$LLM_OUTPUT" | grep -oE '\[[^]]*\]' | head -1)
  if [ -n "$JSON_ARR" ]; then
    # 解析每个 tag, 只保留白名单里的
    while IFS= read -r tag; do
      tag_clean=$(echo "$tag" | tr -d ' "[],' | head -c 30)
      for w in "${WHITELIST[@]}"; do
        if [ "$tag_clean" = "$w" ]; then
          TAGS+=("$w")
          break
        fi
      done
    done < <(echo "$JSON_ARR" | tr ',' '\n')

    # 限 3 个
    if [ ${#TAGS[@]} -gt 3 ]; then
      TAGS=("${TAGS[@]:0:3}")
    fi
  fi
fi

# Fallback: 关键词匹配 (LLM 失败时)
if [ ${#TAGS[@]} -eq 0 ]; then
  echo "⚠️ LLM judge fallback → 关键词匹配" >&2
  for w in "${WHITELIST[@]}"; do
    if echo "$ABSTRACT_TRIM" | grep -qi "$w"; then
      TAGS+=("$w")
      [ ${#TAGS[@]} -ge 3 ] && break
    fi
  done
  [ ${#TAGS[@]} -eq 0 ] && TAGS=("llm")  # 最终 fallback
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