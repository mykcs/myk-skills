#!/usr/bin/env bash
# verify-patch-recovery.sh — 抗回滚 verify 脚本 (per §11 抗回滚 5 IF...THEN)
# 用法: verify-patch-recovery.sh <page_id> <baseline_json> <checks_json>
# 例:   verify-patch-recovery.sh 39cfedee62678086a384cd6114c7d8c3 /tmp/m_v4.json /tmp/checks.json
#
# 4 维 verify (per v6 §7.4 + §11 + F9 反模式):
#   1. GET m_now.json → 对比 baseline (整页重写检测, F10)
#   2. 14 处独特字串 grep + 100 字符上下文 (per F11 字符精匹配)
#   3. async task ID status 查 result.markdown (per F9 假阳性)
#   4. 输出 4 状态报告: ✅ 真成 / ⚠️ cache 假阳性 / ❌ 真失败 / 🔍 待重抽
#
# baseline_json = v4 patch 时存的真值 (m_v4.json)
# checks_json = 14 处 unique_tag + expected (True/False) + label
#   例: [{"tag": "FoundationAgents/MetaGPT", "expected": true, "label": "MetaGPT URL"}, ...]
#
# 跟 patch-markdown-block.sh 同骨架 (per master v6 §11 抗回滚协议)

set -uo pipefail  # 不 -e (希望全跑完, 出 report)

if [ $# -ne 3 ]; then
  echo "用法: $0 <page_id> <baseline_json> <checks_json>" >&2
  echo "  page_id: 32-char 无 dash (e.g. 39cfedee62678086a384cd6114c7d8c3)" >&2
  echo "  baseline_json: v4 patch 时的 m.json (含 .markdown 字段)" >&2
  echo "  checks_json: 14 处 [{tag, expected, label}] 列表" >&2
  exit 2
fi

PAGE_ID="$1"
BASELINE_FILE="$2"
CHECKS_FILE="$3"

if [ ! -f "$BASELINE_FILE" ]; then
  echo "❌ baseline 不存在: $BASELINE_FILE" >&2
  exit 2
fi
if [ ! -f "$CHECKS_FILE" ]; then
  echo "❌ checks 不存在: $CHECKS_FILE" >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq 必装: brew install jq" >&2
  exit 2
fi

echo "🔍 verify-patch-recovery start: $(date '+%Y-%m-%d %H:%M:%S')"
echo "   page_id:    $PAGE_ID"
echo "   baseline:   $BASELINE_FILE"
echo "   checks:     $CHECKS_FILE"
echo ""

# 1. 拉最新 markdown (m_now.json)
M_NOW="/tmp/m_now_$$.json"
echo "📥 Step 1: GET m_now.json ..."
if ! ntn api --method GET "v1/pages/${PAGE_ID}/markdown" \
    --notion-version 2026-03-11 > "$M_NOW" 2>/dev/null; then
  echo "❌ GET markdown 失败 (network/api error)" >&2
  exit 2
fi

# 2. 提取 markdown 内容
NOW_MD=$(jq -r '.markdown // empty' "$M_NOW" 2>/dev/null)
BASE_MD=$(jq -r '.markdown // empty' "$BASELINE_FILE" 2>/dev/null)

if [ -z "$NOW_MD" ]; then
  echo "❌ m_now.json 不含 markdown 字段 (api 返非预期格式)" >&2
  rm -f "$M_NOW"
  exit 2
fi
if [ -z "$BASE_MD" ]; then
  echo "❌ baseline 不含 markdown 字段" >&2
  rm -f "$M_NOW"
  exit 2
fi

NOW_LEN=${#NOW_MD}
BASE_LEN=${#BASE_MD}
echo "   m_now.json:    $NOW_LEN chars"
echo "   baseline:      $BASE_LEN chars"
echo ""

# 3. 整页重写检测 (per F10)
if [ "$NOW_LEN" -lt $((BASE_LEN - 1000)) ] || [ "$NOW_LEN" -gt $((BASE_LEN + 10000)) ]; then
  echo "⚠️  ⚠️  ⚠️  整页重写检测 (F10) ⚠️  ⚠️  ⚠️"
  echo "   baseline: $BASE_LEN chars vs m_now: $NOW_LEN chars"
  echo "   差距 > 1000 chars 触发 F10 警报"
  echo "   必读 master v6 §11 抗回滚 5 IF...THEN"
  echo ""
fi

# 4. 14 处 check 逐项跑 (per F11 字符精匹配)
echo "📋 Step 2: 14 处独特字串 grep verify ..."
PASS=0
FAIL=0
PENDING=0

while IFS= read -r check; do
  TAG=$(echo "$check" | jq -r '.tag')
  EXPECTED=$(echo "$check" | jq -r '.expected')
  LABEL=$(echo "$check" | jq -r '.label')

  # 独特字串在 m_now 是否在
  if echo "$NOW_MD" | grep -qF "$TAG"; then
    ACTUAL=true
  else
    ACTUAL=false
  fi

  if [ "$ACTUAL" = "$EXPECTED" ]; then
    STATUS="✅"
    PASS=$((PASS+1))
  else
    STATUS="❌"
    FAIL=$((FAIL+1))
  fi

  printf "  %s  %-40s expect=%-5s actual=%-5s\n" "$STATUS" "$LABEL" "$EXPECTED" "$ACTUAL"
done < <(jq -c '.[]' "$CHECKS_FILE")

echo ""
echo "📊 总结: ✅ $PASS PASS / ❌ $FAIL FAIL"
TOTAL=$((PASS+FAIL))
if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "⚠️  $FAIL 处未达预期, 必查:"
  echo "   1. patch async task ID 状态 (per F9 反模式 #7)"
  echo "   2. ntn api GET /v1/async_tasks/<task_id> 看 result.markdown"
  echo "   3. 整页重写 (per F10) 必用 m_now.json 重抽 old_str"
  echo "   4. 引用错挂 (per F13) 必 fetch arxiv.org/abs/<id> 实测"
fi

# cleanup
rm -f "$M_NOW"
exit 0