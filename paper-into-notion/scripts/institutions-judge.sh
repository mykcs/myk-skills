#!/usr/bin/env bash
# institutions-judge.sh — abstract+authors → 机构 multi_select (per ADR-0057 v3.3)
# 用法: bash institutions-judge.sh <ABSTRACT_TEXT> [<AUTHORS_LINE>]
# 输出: JSON 数组字符串 (e.g. ["Bo Han"] / ["Google Brain","Princeton"] / [])
# 写字段: Notion 机构 multi_select (auto-create options per v3.3, 2026-07-14 user 决策)
#   - 不写死 whitelist, LLM 自由判机构名 (paper 真实机构名入库, group by 时 Notion 自动归类)
#   - Notion multi_select PATCH 时 API 自动创不存在的 option (实测)
#   - 邮箱域名 grep: 强信号 (szu.edu.cn / polyu.edu.hk / anthropic.com) → 优先用
#   - LLM 判空 → []
#   - LLM 返 markdown code fence / thinking block → 3 层 fallback parse
# 跟 v1.4 multi_select 保护 grader 协同: PATCH 时 body 只在 机构字段为空时才传 (per v3.0 空才填)
# 历史: v3.1 写死 whitelist (SZU/PolyU), v3.2 加"其他机构"兜底, v3.3 user 决策 "该是什么就是什么" → 不写死

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ institutions-judge --verify (v3.3 不写死 whitelist) ═══"
  if command -v mmx >/dev/null 2>&1; then
    mmx --version 2>&1 | head -1
    echo "    ✅ mmx found"
  else
    echo "    ⚠️ mmx not found, fallback: authors 邮箱域名 grep"
  fi
  exit 0
fi

ABSTRACT="${1:-}"
AUTHORS="${2:-}"
ARXIV_ID="${3:-}"  # v3.4 新增: arXiv ID (e.g. 2607.08124), 优先抓真实 affiliations
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash institutions-judge.sh <ABSTRACT_TEXT> [<AUTHORS_LINE>] [<ARXIV_ID>]" >&2
  echo "      bash institutions-judge.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# v3.4 Layer 0: arxiv-affiliations.py 抓 paper 真实机构 (1:1, 不幻觉)
# 用法: bash institutions-judge.sh <ABSTRACT> <AUTHORS> <ARXIV_ID>
# 优先抓, 失败/空 fallback LLM
if [ -n "$ARXIV_ID" ] && command -v python3 >/dev/null 2>&1; then
  ARXIV_AFF=$(python3 "$SCRIPT_DIR/arxiv-affiliations.py" "$ARXIV_ID" 2>/dev/null || true)
  if [ -n "$ARXIV_AFF" ] && ! echo "$ARXIV_AFF" | grep -q '"error"'; then
    # arxiv-affiliations 成功, 直接用真实机构
    echo "$ARXIV_AFF" | python3 -c "
import json, sys
try:
    arr = json.loads(sys.stdin.read())
    if isinstance(arr, list) and arr:
        print(json.dumps(arr, ensure_ascii=False))
    else:
        print('[]')
except: print('[]')
"
    exit 0
  fi
  # 失败 → fallback LLM
fi

# Layer 1: email 域名 grep (强信号, 优先) — 不调用 mmx, 立即快
# v3.3: 邮箱域名只作 signal 提示 LLM, 不写死 whitelist
INSTITUTIONS=""
HINTS=""
if [ -n "$AUTHORS" ]; then
  echo "$AUTHORS" | grep -qiE 'szu\.edu\.cn|szu\.edu\b' && HINTS="$HINTS szu.edu.cn"
  echo "$AUTHORS" | grep -qiE 'polyu\.edu\.hk' && HINTS="$HINTS polyu.edu.hk"
  echo "$AUTHORS" | grep -qiE 'anthropic\.com' && HINTS="$HINTS anthropic.com"
fi

# Layer 2: LLM 判 (机构隶属 + 邮箱 fallback)
PROMPT=$(cat <<EOF
You are a research institution classifier. Read this paper abstract + author list and identify the actual research institutions the authors are affiliated with.

Email domain hints (strong signal):$HINTS

Output strict JSON format (no markdown code fence, no comments):
{"institutions": ["Bo Han Lab", "MIT CSAIL"]} or {"institutions": ["Google Brain", "Princeton"]} or {"institutions": []}

Rules:
- Use the REAL institution name from the paper / author affiliations / known research groups
- Format examples: "Google Brain" / "MIT CSAIL" / "Tsinghua University" / "PolyU" / "SZU" / "Anthropic" / "DeepMind" / "Stanford" / "SakanaAI" / "Princeton" / "Westlake University" / "Chinese Academy of Sciences"
- Be concise (1-4 words per institution name)
- If you can't determine affiliations confidently (e.g. no author email, abstract doesn't mention), return []
- DO NOT invent institutions. If unsure, return [].

Abstract:
$ABSTRACT_TRIM

Authors line:
$AUTHORS
EOF
)

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
  INSTITUTIONS="$LLM_OUTPUT"
fi

# Layer 3: 解析 LLM 输出 → 输出 JSON 数组
echo "$INSTITUTIONS" | python3 -c "
import json, sys, re
text = sys.stdin.read().strip()

def parse(json_str):
    try:
        d = json.loads(json_str)
        if isinstance(d, dict) and 'institutions' in d:
            inst = [i.strip() for i in d['institutions'] if i and isinstance(i, str)]
            # 过滤太短/太长 (噪音)
            inst = [i for i in inst if 2 <= len(i) <= 50]
            return inst
    except: pass
    return None

# 1. 直接 parse
inst = parse(text)
# 2. strip markdown code fence 后 parse
if inst is None:
    m = re.search(r'\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`', text, re.DOTALL)
    if m:
        inst = parse(m.group(1))
# 3. 都没 → 返 []
if inst is None:
    inst = []
print(json.dumps(inst, ensure_ascii=False))
"