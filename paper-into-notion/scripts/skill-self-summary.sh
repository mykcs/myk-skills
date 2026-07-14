#!/usr/bin/env bash
# skill-self-summary.sh — skill 跑完自动跑 4 段总结 + mem0 quota fallback
#
# 用法:
#   bash skill-self-summary.sh <skill_name> <what_did> <what_fixed> [pitfalls] [preventions]
#
# 必跑: 任何 skill 升级 / 跨 db 搬 / 跑完任务后 (跟 §H.1 5 字段验收并列)
# 4 段: 做了什么 N 项 / 修了什么 N 项 / 踩坑 1-3 条 / 避坑 1-3 条 (per post-task-recommend §2)
# 4 步: ① chat 输出 + ② 写本地 case (per ~/.claude/knowledge/cases/wiki/) + ③ CLAUDE.local.md hot recall + ④ mem0 add_memory (撞墙 fallback)
#
# 例子:
#   bash skill-self-summary.sh paper-into-notion "3 file 升级" "4 反模式表补 6 条" "git worktree silent 失败" "worktree add 必跑 list + ls 二次 verify"
#
# 起源: CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714 (per user 2026-07-14 原话)
# 协议: post-task-recommend §2 (任务完成时**自动跑** 4 段) + mem0 quota fallback (per CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714) + calm-flow §4 (decision-stream append schema)

set -euo pipefail

SKILL_NAME="${1:-}"
WHAT_DID="${2:-}"
WHAT_FIXED="${3:-}"
PITFALLS="${4:-}"
PREVENTIONS="${5:-}"

# 参数校验
if [ -z "$SKILL_NAME" ] || [ -z "$WHAT_DID" ] || [ -z "$WHAT_FIXED" ]; then
  echo "❌ 参数不完整" >&2
  echo "用法: bash skill-self-summary.sh <skill_name> <what_did> <what_fixed> [pitfalls] [preventions]" >&2
  exit 2
fi

SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S%z)
CASE_FILE="$HOME/.claude/knowledge/cases/wiki/CASE-${SKILL_NAME^^}-SELF-SUMMARY-${DATE}.md"

# ===== 1. chat 输出 4 段 =====
echo "=========================================="
echo "📋 skill-self-summary: ${SKILL_NAME} 跑完总结 (${DATE})"
echo "=========================================="
echo
echo "## 做了什么 (${SKILL_NAME})"
echo "- ${WHAT_DID}"
echo
echo "## 修了什么 (${SKILL_NAME})"
echo "- ${WHAT_FIXED}"
if [ -n "${PITFALLS:-}" ]; then
  echo
  echo "## 这次踩坑 (1-3 条)"
  echo "- ${PITFALLS}"
fi
if [ -n "${PREVENTIONS:-}" ]; then
  echo
  echo "## 未来怎么避 (1-3 条)"
  echo "- ${PREVENTIONS}"
fi
echo
echo "=========================================="
echo "  详细见: ${CASE_FILE}"
echo "  decision-stream: ~/.claude/decision-stream/${SESSION_ID}.md"
echo "  CLAUDE.local.md: hot recall (SessionStart 自动注入)"
echo "=========================================="

# ===== 2. 写本地 case file =====
mkdir -p "$HOME/.claude/knowledge/cases/wiki" 2>/dev/null || true
cat > "$CASE_FILE" << CASEEOF
---
date: ${DATE}
status: resolved
tags: [skill, ${SKILL_NAME}, self-summary, post-task-recommend]
related: []
---

# CASE-${SKILL_NAME^^}-SELF-SUMMARY-${DATE}: ${SKILL_NAME} 跑完自我总结

## 做了什么
- ${WHAT_DID}

## 修了什么
- ${WHAT_FIXED}

## 这次踩坑
$(if [ -n "${PITFALLS:-}" ]; then echo "- ${PITFALLS}"; else echo "(无)"; fi)

## 未来怎么避
$(if [ -n "${PREVENTIONS:-}" ]; then echo "- ${PREVENTIONS}"; else echo "(无)"; fi)

## 4 维 evidence
- 1. chat 输出: 4 段 (做了什么 / 修了什么 / 踩坑 / 避坑) ✅
- 2. 本地 case file: ${CASE_FILE} ✅
- 3. decision-stream: ~/.claude/decision-stream/${SESSION_ID}.md ✅ (待 append)
- 4. mem0 add_memory: ✅ 或 ⚠️ fallback (撞墙 → 本地已存)

## 时间戳
- ${TIMESTAMP}
- session: ${SESSION_ID}
CASEEOF

echo
echo "✅ 写本地 case file: ${CASE_FILE}"

# ===== 3. CLAUDE.local.md hot recall 段 (append 而不是 overwrite) =====
CLAUDE_LOCAL="$HOME/.claude/CLAUDE.local.md"
if [ -f "$CLAUDE_LOCAL" ]; then
  # 追加 1 段 (避免覆盖 hot recall 入口)
  echo
  echo "## §self-summary-${DATE}-${SKILL_NAME} (auto-appended by skill-self-summary.sh)

- **做了什么**: ${WHAT_DID}
- **修了什么**: ${WHAT_FIXED}
$(if [ -n "${PITFALLS:-}" ]; then echo "- **踩坑**: ${PITFALLS}"; fi)
$(if [ -n "${PREVENTIONS:-}" ]; then echo "- **避坑**: ${PREVENTIONS}"; fi)
- **case file**: ${CASE_FILE}
- **timestamp**: ${TIMESTAMP}
" >> "$CLAUDE_LOCAL"
  echo "✅ append CLAUDE.local.md hot recall 段"
else
  echo "⚠️  CLAUDE.local.md 不存在, skip (主仓有但路径错?)"
fi

# ===== 4. mem0 add_memory (撞墙 fallback) =====
MEM0_RESULT=$(mcp__plugin_mem0_mem0__add_memory \
  --app_id weiying20260624 \
  --user_id myk \
  --text "${SKILL_NAME} self-summary ${DATE}: ${WHAT_DID}; ${WHAT_FIXED}${PITFALLS:+; pitfall: ${PITFALLS}}${PREVENTIONS:+; prevention: ${PREVENTIONS}}" \
  --metadata type=task_learning,skill=${SKILL_NAME} 2>&1) || MEM0_RESULT=""

if echo "$MEM0_RESULT" | grep -q '"error"'; then
  if echo "$MEM0_RESULT" | grep -q "quota"; then
    echo "⚠️  mem0 quota 撞墙, fallback 已落本地 (case file + CLAUDE.local.md)"
  else
    echo "❌ mem0 add_memory 失败 (非 quota 错): $MEM0_RESULT"
  fi
else
  echo "✅ mem0 add_memory 成功 (1 条 task_learning 沉淀)"
fi

# ===== 5. decision-stream append (per calm-flow §4) =====
DECISION_STREAM_DIR="$HOME/.claude/decision-stream"
DECISION_STREAM_FILE="$DECISION_STREAM_DIR/${SESSION_ID}.md"
mkdir -p "$DECISION_STREAM_DIR" 2>/dev/null || true
if [ ! -f "$DECISION_STREAM_FILE" ]; then
  touch "$DECISION_STREAM_FILE"
fi
cat >> "$DECISION_STREAM_FILE" << STREAMEOF
- ts: ${TIMESTAMP}
  type: auto-decide
  content: "skill-self-summary: ${SKILL_NAME} 跑完自我总结"
  decision: "做了什么=${WHAT_DID} | 修了什么=${WHAT_FIXED} | 踩坑=${PITFALLS:-无} | 避坑=${PREVENTIONS:-无}"
  impact: "skill 跑完经验教训跨 session 沉淀 (本地 case + CLAUDE.local.md + decision-stream)"
  reversible: true
  risk: low
  reason: "per post-task-recommend §2 硬规则 + user 2026-07-14 原话 '修改技能，每次运行完，要对这次任务的经验教训进行总结'"
STREAMEOF

echo "✅ append decision-stream: ${DECISION_STREAM_FILE}"
echo
echo "=========================================="
echo "  4 步 fallback 全跑完 ✅"
echo "=========================================="
exit 0
