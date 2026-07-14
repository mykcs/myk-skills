#!/usr/bin/env bash
# institutions-judge.sh — abstract+authors → 机构 multi_select (per ADR-0057 v3.1)
# 用法: bash institutions-judge.sh <ABSTRACT_TEXT> [<AUTHORS_LINE>]
# 输出: JSON 数组字符串 (e.g. ["SZU"] 或 ["SZU","PolyU"] 或 ["其他机构"])
# 写字段: Notion 机构 multi_select (per db schema v3.2 实测 2026-07-14)
#   whitelist: Anthropic / SZU / PolyU / 其他机构 (4 options)
#   - 前 3 个 LLM/邮箱判, 命中精确 (Anthropic/SZU/PolyU)
#   - LLM 判出机构但不在 whitelist → 标 "其他机构" (避免丢 paper)
#   - LLM 判空 → []
# 跟 v1.4 multi_select 保护 grader 协同: PATCH 时 body 只在 机构字段为空时才传 (per v3.0 空才填)
# 跟 db schema 同步: 必须先 PATCH /v1/data_sources/{id} 写完整 options list
#   (否则 Notion API 400: option name "X" not found in target data source)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# --verify 子命令
if [ "${1:-}" = "--verify" ]; then
  echo "═══ institutions-judge --verify ═══"
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
if [ -z "$ABSTRACT" ]; then
  echo "用法: bash institutions-judge.sh <ABSTRACT_TEXT> [<AUTHORS_LINE>]" >&2
  echo "      bash institutions-judge.sh --verify" >&2
  exit 1
fi

# 截断 abstract 前 1500 字
ABSTRACT_TRIM=$(echo "$ABSTRACT" | head -c 1500)

# Layer 1: email 域名 grep (强信号, 优先) — 不调用 mmx, 立即快
INSTITUTIONS=""
if [ -n "$AUTHORS" ]; then
  if echo "$AUTHORS" | grep -qiE 'anthropic\.com|anthropic\b' 2>/dev/null; then
    INSTITUTIONS="Anthropic"
  fi
  if echo "$AUTHORS" | grep -qiE 'szu\.edu\.cn|szu\.edu\b|szu\b|sou\.edu|szu\.edu\.hk|南方医科大学|深圳大学|southern university' 2>/dev/null; then
    INSTITUTIONS="${INSTITUTIONS:+$INSTITUTIONS,}SZU"
  fi
  if echo "$AUTHORS" | grep -qiE 'polyu\.edu\.hk|polyu\.edu\b|polyu\b|理大|香港理工大学|hong kong polytechnic' 2>/dev/null; then
    INSTITUTIONS="${INSTITUTIONS:+$INSTITUTIONS,}PolyU"
  fi
fi

# Layer 2: LLM 判 (机构隶属 + 邮箱 fallback)
if [ -z "$INSTITUTIONS" ]; then
  PROMPT=$(cat <<EOF
You are a research institution classifier. Read this paper abstract + author list and return ONLY the institutions.

Output strict JSON format, no markdown, no comments:
{"institutions": ["SZU"]} or {"institutions": ["SZU","PolyU"]} or {"institutions": ["Anthropic"]} or {"institutions": ["其他机构"]} or {"institutions": []}

Decide based on author affiliations/affiliation emails:
- szu.edu.cn / szu.edu / szu → SZU (深圳大学)
- polyu.edu.hk / polyu → PolyU (香港理工大学)
- anthropic.com → Anthropic
- 其他任何机构 (Google / Meta / Stanford / Princeton / SakanaAI / MIT / ETH / DeepMind / ...) → "其他机构"
- 都不是 (e.g. 没有作者邮箱) → []

Abstract:
$ABSTRACT_TRIM

Authors line:
$AUTHORS
EOF
)

  if command -v mmx >/dev/null 2>&1; then
    LLM_OUTPUT=$(mmx text chat --non-interactive --output json --message "$PROMPT" 2>/dev/null \
      | python3 -c "
import json, sys, re
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
    # 从 LLM 输出解析 institutions 数组
    PARSED=$(echo "$LLM_OUTPUT" | python3 -c "
import json, sys, re
text = sys.stdin.read().strip()
VALID = {'Anthropic','SZU','PolyU','其他机构'}
# 1. 直接 json.loads 看是不是纯 JSON 格式
try:
    d = json.loads(text)
    if isinstance(d, dict) and 'institutions' in d:
        inst = [i for i in d['institutions'] if i in VALID]
        if inst:
            print(','.join(inst))
        raise SystemExit(0)
except: pass
# 2. strip markdown code fence (\`\`\`json ... \`\`\`) 后再 parse
m = re.search(r'\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`', text, re.DOTALL)
if m:
    try:
        d = json.loads(m.group(1))
        if isinstance(d, dict) and 'institutions' in d:
            inst = [i for i in d['institutions'] if i in VALID]
            if inst:
                print(','.join(inst))
            raise SystemExit(0)
    except: pass
# 3. fallback: 在 text 里 grep VALID 关键词
out = []
for kw in ['Anthropic','SZU','PolyU','其他机构']:
    if re.search(r'\b' + re.escape(kw) + r'\b', text):
        out.append(kw)
# v3.2: 都没匹配 + text 含机构相关词 → 其他机构 fallback
if not out and re.search(r'(University|Institute|Polytechnic|理工|大学|学院|AI Lab|Research)', text):
    out.append('其他机构')
print(','.join(out))
" 2>/dev/null || echo "")
    if [ -n "$PARSED" ]; then
      INSTITUTIONS="$PARSED"
    fi
  fi
fi

# Layer 3: fallback 已知 (空 → 返 [])
echo "[$INSTITUTIONS]" | python3 -c "
import json, sys
text = sys.stdin.read().strip()
# 清理: 'SZU,PolyU' → 'SZU','PolyU'
inner = text.strip('[]').strip()
if not inner:
    print('[]')
else:
    VALID = {'Anthropic','SZU','PolyU','其他机构'}
    items = [x.strip().strip('\"').strip(\"'\") for x in inner.split(',') if x.strip()]
    valid = [x for x in items if x in VALID]
    print(json.dumps(valid, ensure_ascii=False))
"
