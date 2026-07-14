#!/usr/bin/env bash
# knowledge-growth-judge.sh — LLM judge 抓 abstract → 1-3 个 知识等级形态 标签
# 用法: bash knowledge-growth-judge.sh <ABSTRACT_TEXT>
#       bash knowledge-growth-judge.sh --verify
# 输出: JSON 数组 ["开创新领域"] / ["增量", "综述"] (1-3 个, 从 6 选项白名单里, 默认 1 + 次要维度门槛高)
# v3.7 增量: 新字段 知识等级形态 multi_select 6 项; LLM prompt 含 6 判据 (per user 2026-07-14 拍板 Q6);
#            选 1 个主标签 + 必要时 + 1 个明确次要维度 (Q5A 门槛高, 避免凑数)
# 默认 args 1: paper abstract (从 arxiv-fetch.sh 抓的 <abstract>)
# 后续联动: scripts/field-merge.sh 第 8 参数接收 JSON, scripts/paper-into-notion.sh 调

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 6 知识等级形态白名单 (per Notion schema v3.7 add-property.sh 2026-07-14)
# 顺序按认知深度: 开创新 (最深) → 进阶技巧 / 基础知识 (最浅)
# 关键: 多选仅在次要维度 "门槛高" 时 + 1 (Q5A), 不超过 3 个
WHITELIST=(
  开创新领域
  综述
  增量
  反驳
  进阶技巧
  基础知识
)

# 6 判据 (per user 2026-07-14 grill Q6 拍板 v0)
# 1) 开创新领域: 提出全新问题/范式 (旧有方法无法迁移套用)
# 2) 综述: 系统盘整已有工作 (贡献在结构化梳理 + insight 综合)
# 3) 增量: 沿已有范式/路径推进, 局部可衡量新提升 (指标/效率/泛化)
# 4) 反驳: 主旨对已有工作/共识提出明确质疑或否定, 贡献在指出原方法缺陷
# 5) 进阶技巧: 适合已有领域经验者的避坑 / hack / workflow 优化
# 6) 基础知识: 手把手教程 (step-by-step, 入门)

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ knowledge-growth-judge --verify ═══"
  if command -v mmx >/dev/null 2>&1; then
    mmx --version 2>&1 | head -1
    echo "    ✅ mmx found"
  else
    echo "    ⚠️ mmx not found, fallback: 关键词匹配"
  fi
  echo "[6 标签白名单]: ${WHITELIST[*]}"
  echo "    ✅ whitelist = 6"
  echo "    ✅ 6 判据 (Q6A 拍板 v0): 认知深度 = 开创新 → 综述 → 增量 → 反驳 / 教学形态 = 进阶技巧 + 基础知识"
  exit 0
fi

ABSTRACT="${1:-}"
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash knowledge-growth-judge.sh <ABSTRACT_TEXT>" >&2
  echo "      bash knowledge-growth-judge.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字 (跟 education-type-judge 同模式)
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# LLM judge prompt: 多选 1-3 个 (Q5A 主标签 1 + 次要维度门槛高, 最多 +1 +1 = 3)
# 关键: prompt 必含 6 判据 + Q5A "次要维度门槛高, 不是凑数" 避免 LLM 自由标
PROMPT=$(cat <<EOF
You are a knowledge-classity classifier for academic papers / blogs / tutorials. Read the abstract and pick 1-3 most relevant tags from this whitelist ONLY:

$(printf '%s\n' "${WHITELIST[@]}")

**6 判据 (选什么看什么)**:
- 开创新领域: 提出全新问题/范式 (旧有方法无法迁移套用, e.g. Diffusion/Transformer attention/Test-Time Compute 路线)
- 综述: 系统盘整已有工作 (贡献在结构化梳理 + insight 综合, e.g. survey paper / 知乎专栏入门)
- 增量: 沿已有范式推进, 局部可衡量新提升 (指标/效率/泛化, e.g. post-training/KV-cache 优化/CoT prompt 技巧)
- 反驳: 主旨对已有工作/共识质疑或否定 (贡献在指出原方法缺陷, e.g. "Why X is Wrong" / 重新分析 dataset 得出反结论)
- 进阶技巧: 适合经验者避坑 / hack / workflow 优化 (e.g. Engineer blog / GitHub README caveats / Twitter 经验帖)
- 基础知识: 手把手教程 (step-by-step, 入门 e.g. 教程书 / 入门上手)

**多选规则 (Q5A 门槛高, 必读)**:
1. 先选 1 个主标签 (最强那个)
2. 次要维度必须 "这篇能独立归到这个类、不是凑数" 才 + 1
3. 如果只有 1 个明显归属, 就只返 1 个, 别凑数
4. 通常 1-2 个, 极特殊 case 才 3 个

**例子**:
- 一篇 survey paper 提了新 benchmark → ["综述", "增量"] (新 benchmark 是明确次要维度)
- 一篇反驳 paper 有新理论 → ["反驳", "开创新领域"]
- 一篇单纯 survey → ["综述"] (1 个)
- 一篇 RAG 教程 → ["基础知识"] (1 个)
- 单纯 incremental KV-cache 优化 → ["增量"] (1 个)

Return ONLY a JSON array, nothing else. Example: ["增量"] or ["综述", "增量"]

Abstract:
$ABSTRACT_TRIM
EOF
)

# 跑 LLM (优先 mmx MiniMax-M2.7, fallback 关键词匹配)
# Per v2.7 fix: mmx text chat 真用法 = --non-interactive --output json
TAGS=()
if command -v mmx >/dev/null 2>&1; then
  LLM_OUTPUT=$(mmx text chat --non-interactive --output json --message "$PROMPT" 2>/dev/null \
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

# parse LLM JSON
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
  fi
fi

# 限最多 3 个 (Q5A 主标签 1 + 次要门槛高)
if [ ${#TAGS[@]} -gt 3 ]; then
  TAGS=("${TAGS[@]:0:3}")
fi

# Fallback: 关键词匹配 + 启发式 (Q6A 6 判据字面, 中性 fallback)
if [ ${#TAGS[@]} -eq 0 ]; then
  echo "⚠️ LLM judge fallback → 关键词匹配 (6 判据字面启发)" >&2
  # 综述 (survey/review/comprehensive/systematic)
  if echo "$ABSTRACT_TRIM" | grep -qwE "survey|review|systematic|comprehensive|梳理|盘整"; then
    TAGS+=("综述")
  fi
  # 开创新 (novel/first/paradigm/new framework)
  if echo "$ABSTRACT_TRIM" | grep -qwE "novel framework|new paradigm|first to|开创新|新范式|首次提出"; then
    TAGS+=("开创新领域")
  fi
  # 增量 (improvement/enhance/boost/outperform)
  if echo "$ABSTRACT_TRIM" | grep -qwE "improve|enhance|boost|outperform|state-of-the-art|SOTA|提升|改进|优化"; then
    TAGS+=("增量")
  fi
  # 反驳 (challenge/question/rebut/disprove)
  if echo "$ABSTRACT_TRIM" | grep -qwE "challenge|question|rebut|disprove|refute|反驳|质疑|否定"; then
    TAGS+=("反驳")
  fi
  # 进阶技巧 (engineering/practice/hack/gotcha)
  if echo "$ABSTRACT_TRIM" | grep -qwE "engineering|practice|hack|gotcha|caveat|workflow|技巧|实战"; then
    TAGS+=("进阶技巧")
  fi
  # 基础知识 (tutorial/introductory/step-by-step/手把手/入门)
  if echo "$ABSTRACT_TRIM" | grep -qwE "tutorial|introductory|step-by-step|beginner|get started|手把手|入门"; then
    TAGS+=("基础知识")
  fi
  # 最终 fallback (按 v3.0 LLM 默认 mode 缺失时给中性值)
  if [ ${#TAGS[@]} -eq 0 ]; then
    TAGS=("增量")
  fi
  # 限最多 3 个
  if [ ${#TAGS[@]} -gt 3 ]; then
    TAGS=("${TAGS[@]:0:3}")
  fi
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
