#!/usr/bin/env bash
# institutions-judge.sh — abstract+authors → 机构 multi_select (per ADR-0057 v3.1)
# 用法: bash institutions-judge.sh <ABSTRACT_TEXT> [<AUTHORS_LINE>]
# 输出: JSON 数组字符串 (e.g. ["SZU"] 或 ["SZU","PolyU"] 或 [])
# 写字段: Notion 机构 multi_select (SZU/PolyU 2 个 options per db schema, v2.7 实测)
# 跟 v1.4 multi_select 保护 grader 协同: PATCH 时 body 只在 机构字段为空时才传 (per v3.0 空才填)

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
  if echo "$AUTHORS" | grep -qiE 'szu\.edu\.cn|szu\.edu\b|szu\b|sou\.edu|szu\.edu\.hk|南方医科大学|深圳大学|southern university' 2>/dev/null; then
    INSTITUTIONS="SZU"
  fi
  if echo "$AUTHORS" | grep -qiE 'polyu\.edu\.hk|polyu\.edu\b|polyu\b|理大|香港理工大学|hong kong polytechnic' 2>/dev/null; then
    INSTITUTIONS="${INSTITUTIONS:+$INSTITUTIONS,}PolyU"
  fi
fi

# Layer 2: LLM 判 (机构隶属 + 邮箱 fallback)
if [ -z "$INSTITUTIONS" ]; then
  PROMPT=$(cat <<EOF
You are a research institution classifier. Read this paper abstract + author list and return ONLY the institutions (深圳大学 = SZU, 香港理工大学 = PolyU, 都不是 = empty).

Output strict JSON format, no markdown, no comments:
{"institutions": ["SZU"]} or {"institutions": ["SZU","PolyU"]} or {"institutions": []}

Decide based on author affiliations/affiliation emails. szu.edu.cn / szu.edu / szu → SZU; polyu.edu.hk / polyu → PolyU.

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
# 直接 json.loads 看是不是纯 JSON 格式
try:
    d = json.loads(text)
    if isinstance(d, dict) and 'institutions' in d:
        inst = [i for i in d['institutions'] if i in ('SZU','PolyU')]
        if inst:
            print(','.join(inst))
        raise SystemExit(0)
except: pass
# fallback: 在 text 里 grep 'SZU' / 'PolyU'
out = []
if re.search(r'\bSZU\b', text): out.append('SZU')
if re.search(r'\bPolyU\b', text): out.append('PolyU')
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
    items = [x.strip().strip('\"').strip(\"'\") for x in inner.split(',') if x.strip()]
    valid = [x for x in items if x in ('SZU', 'PolyU')]
    print(json.dumps(valid, ensure_ascii=False))
"
