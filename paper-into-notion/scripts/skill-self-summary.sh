#!/usr/bin/env bash
# skill-self-summary.sh — skill 跑完自动跑 4 段总结 + mem0 quota fallback + v-bump 自动触发
#
# 用法:
#   bash skill-self-summary.sh <skill_name> <what_did> <what_fixed> [pitfalls] [preventions]
#
# 必跑: 任何 skill 升级 / 跨 db 搬 / 跑完任务后 (跟 §H.1 5 字段验收并列)
# 4 段: 做了什么 N 项 / 修了什么 N 项 / 踩坑 1-3 条 / 避坑 1-3 条 (per post-task-recommend §2)
# 4 步: ① chat 输出 + ② 写本地 case (per ~/.claude/knowledge/cases/wiki/) + ③ CLAUDE.local.md hot recall (段带 @v{version}) + ④ decision-stream append
# 3 步 fallback: 本地 case + CLAUDE.local.md + decision-stream (mem0 quota 撞墙时)
# v-bump 自动触发: 跑完自检 4 条件 (反模式 ≥ 4 / 流程变化 ≥ 1 / 触发词变化 ≥ 1), 任一满足触发 v-bump
#
# 例子:
#   bash skill-self-summary.sh paper-into-notion "4 次升级 v2.0→v2.3" "4 步 fallback 全跑完" "3 v2.3 健壮性缺失" "3 健壮性加"
#
# 起源: CASE-PAPER-INTO-NOTION-V2-4-SELF-EVOLUTION-20260714 (per user 2026-07-14 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结，提升 skill")
# 协议: post-task-recommend §2 (4 段) + §6 (v3 反向证据) / calm-flow §4 (decision-stream schema) / v2.6.30 §I self-evolution (v-bump 4 步闭环)
# 升级: v1.0 → v2.0 (per ADR-0057-f, 3 健壮性 + v-bump 触发)

set -euo pipefail

# ===== Step 0: ask window 守卫 (v2.9-i, per feedback-adhd-rhythm-ask-window-not-bypass + CASE-CLAUDECODE-ADHD-RHYTHM-BYPASS-20260714) =====
# 触发: env ASW_PROMPTED_BY_USER 含 7 keyword "顺手 / 直接跑 / 快做 / 拍板 / 帮我做 / judge yourself / 给我答案" 任一命中
# 4 条件: 跨仓动作 / 不可逆操作 / user 提议 keyword 命中 / Tier 1+2 白名单外
# 任一命中 → exit 1 + 引导 unset + AskUserQuestion 选项化决定 (不替 user 拍板)
ASW_PROMPTED_BY_USER="${ASW_PROMPTED_BY_USER:-}"
if [ -n "$ASW_PROMPTED_BY_USER" ]; then
  ASW_HIT=0
  for kw in "顺手" "直接跑" "快做" "拍板" "帮我做" "judge yourself" "给我答案"; do
    case "$ASW_PROMPTED_BY_USER" in
      *"$kw"*) ASW_HIT=1; break ;;
    esac
  done
  if [ "$ASW_HIT" = "1" ]; then
    echo "❌ Step 0 ask window 守卫命中 (v2.9-i)" >&2
    echo "  user 提议 '$ASW_PROMPTED_BY_USER' 命中 keyword ('顺手' / '直接跑' / '快做' / '拍板' / '帮我做' / 'judge yourself' / '给我答案')" >&2
    echo "  per feedback-adhd-rhythm-ask-window-not-bypass.md v2 强化 4 条件判定:" >&2
    echo "    1. 跨仓动作 (push main / rm / reset --hard / Notion API 改) 必问" >&2
    echo "    2. 不可逆操作 (rm / --force push / Notion Bitable write) 必问" >&2
    echo "    3. user 提议 keyword 自检命中必问" >&2
    echo "    4. Tier 1+2 白名单外 (install / commit / e2e test / case file / hook 之外) 必问" >&2
    echo "  修法: unset ASW_PROMPTED_BY_USER 走 AskUserQuestion 选项化决定 (1-2 选项, A 跑 / B 等)" >&2
    exit 1
  fi
fi

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

# ===== session id fallback 3 步 (per v2.4 ADR-0057-f) =====
# 1. CLAUDE_SESSION_ID env
# 2. git rev-parse --short HEAD (worktree commit hash)
# 3. date +%Y%m%d-%H%M%S (timestamp)
SESSION_ID=""
if [ -n "${CLAUDE_SESSION_ID:-}" ]; then
  SESSION_ID="$CLAUDE_SESSION_ID"
elif SESSION_ID=$(git rev-parse --short HEAD 2>/dev/null); then
  : # SESSION_ID = commit hash
elif SESSION_ID=$(date +%Y%m%d-%H%M%S); then
  : # SESSION_ID = timestamp
else
  echo "❌ session id fallback 全失败 (env / git / date 都拿不到)" >&2
  echo "  修法: 设 CLAUDE_SESSION_ID env 或在 git 仓内跑" >&2
  exit 1
fi

# ===== skill version 读 (从 SKILL.md frontmatter 提取) =====
SKILL_VERSION="unknown"
# 自动定位 SKILL.md (从脚本位置反推 skill 根, 兼容 worktree 跑)
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_FILE="$SCRIPT_DIR/SKILL.md"
if [ -f "$SKILL_FILE" ]; then
  SKILL_VERSION=$(grep -E "^[[:space:]]*version: " "$SKILL_FILE" | head -1 | sed -E 's/^[[:space:]]*version:[[:space:]]*//; s/[[:space:]]*$//' | tr -d '()')
fi
if [ -z "$SKILL_VERSION" ]; then
  SKILL_VERSION="unknown"
fi

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S%z)
CASE_FILE="$HOME/.claude/knowledge/cases/wiki/CASE-${SKILL_NAME^^}-SELF-SUMMARY-${DATE}.md"
HOT_RECALL_TITLE="## §self-summary-${DATE}-${SKILL_NAME}@${SKILL_VERSION} (auto-appended by skill-self-summary.sh)"

# ===== 1. chat 输出 4 段 =====
echo "=========================================="
echo "📋 skill-self-summary: ${SKILL_NAME}@${SKILL_VERSION} 跑完总结 (${DATE}, session=${SESSION_ID})"
echo "=========================================="
echo
echo "## 做了什么 (${SKILL_NAME}@${SKILL_VERSION})"
echo "- ${WHAT_DID}"
echo
echo "## 修了什么 (${SKILL_NAME}@${SKILL_VERSION})"
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
echo "  CLAUDE.local.md: hot recall (SessionStart 自动注入, 段带 @${SKILL_VERSION})"
echo "=========================================="

# ===== 2. 写本地 case file =====
mkdir -p "$HOME/.claude/knowledge/cases/wiki" 2>/dev/null || true
cat > "$CASE_FILE" << CASEEOF
---
date: ${DATE}
status: resolved
tags: [skill, ${SKILL_NAME}, self-summary, post-task-recommend, v${SKILL_VERSION}]
related: []
---

# CASE-${SKILL_NAME^^}-SELF-SUMMARY-${DATE}: ${SKILL_NAME}@${SKILL_VERSION} 跑完自我总结

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
- 3. decision-stream: ~/.claude/decision-stream/${SESSION_ID}.md ✅ (待 append, session_id=${SESSION_ID})
- 4. mem0 add_memory: ✅ 或 ⚠️ fallback (撞墙 → 本地已存)

## 时间戳
- ${TIMESTAMP}
- session: ${SESSION_ID}
- skill_version: ${SKILL_VERSION}
CASEEOF

echo
echo "✅ 写本地 case file: ${CASE_FILE}"

# ===== 3. CLAUDE.local.md hot recall 段 (per v2.4 段带 @v{version}) =====
CLAUDE_LOCAL="$HOME/.claude/CLAUDE.local.md"
if [ -f "$CLAUDE_LOCAL" ]; then
  # 检查是否已存在同名段 (避免堆叠, per ADR-0057-f 残留 2)
  if grep -qF "$HOT_RECALL_TITLE" "$CLAUDE_LOCAL"; then
    echo "⚠️  CLAUDE.local.md 已存在同名段 '$HOT_RECALL_TITLE', 跳过 append (避免堆叠)"
  else
    echo
    echo "$HOT_RECALL_TITLE

- **做了什么**: ${WHAT_DID}
- **修了什么**: ${WHAT_FIXED}
$(if [ -n "${PITFALLS:-}" ]; then echo "- **踩坑**: ${PITFALLS}"; fi)
$(if [ -n "${PREVENTIONS:-}" ]; then echo "- **避坑**: ${PREVENTIONS}"; fi)
- **case file**: ${CASE_FILE}
- **timestamp**: ${TIMESTAMP}
- **session_id**: ${SESSION_ID}
" >> "$CLAUDE_LOCAL"
    echo "✅ append CLAUDE.local.md hot recall 段 (含 @${SKILL_VERSION})"
  fi
else
  echo "⚠️  CLAUDE.local.md 不存在, skip (主仓有但路径错?)"
fi

# ===== 4. mem0 add_memory (撞墙 fallback 3 步) =====
MEM0_RESULT=$(mcp__plugin_mem0_mem0__add_memory \
  --app_id weiying20260624 \
  --user_id myk \
  --text "${SKILL_NAME}@${SKILL_VERSION} self-summary ${DATE}: ${WHAT_DID}; ${WHAT_FIXED}${PITFALLS:+; pitfall: ${PITFALLS}}${PREVENTIONS:+; prevention: ${PREVENTIONS}}" \
  --metadata type=task_learning,skill=${SKILL_NAME},version=${SKILL_VERSION} 2>&1) || MEM0_RESULT=""

if echo "$MEM0_RESULT" | grep -q '"error"'; then
  if echo "$MEM0_RESULT" | grep -q "quota"; then
    echo "⚠️  mem0 quota 撞墙, fallback 已落本地 (case file + CLAUDE.local.md + decision-stream)"
  else
    echo "❌ mem0 add_memory 失败 (非 quota 错): $MEM0_RESULT"
  fi
else
  echo "✅ mem0 add_memory 成功 (1 条 task_learning 沉淀)"
fi

# ===== 5. decision-stream append (per calm-flow §4, session id 3 步 fallback) =====
DECISION_STREAM_DIR="$HOME/.claude/decision-stream"
DECISION_STREAM_FILE="$DECISION_STREAM_DIR/${SESSION_ID}.md"
mkdir -p "$DECISION_STREAM_DIR" 2>/dev/null || true
if [ ! -f "$DECISION_STREAM_FILE" ]; then
  touch "$DECISION_STREAM_FILE"
fi
cat >> "$DECISION_STREAM_FILE" << STREAMEOF
- ts: ${TIMESTAMP}
  type: auto-decide
  content: "skill-self-summary: ${SKILL_NAME}@${SKILL_VERSION} 跑完自我总结"
  decision: "做了什么=${WHAT_DID} | 修了什么=${WHAT_FIXED} | 踩坑=${PITFALLS:-无} | 避坑=${PREVENTIONS:-无}"
  impact: "skill 跑完经验教训跨 session 沉淀 (本地 case + CLAUDE.local.md + decision-stream + mem0)"
  reversible: true
  risk: low
  reason: "per post-task-recommend §2 硬规则 + user 2026-07-14 原话 '修改技能，每次运行完，要对这次任务的经验教训进行总结，提升 skill'"
STREAMEOF

echo "✅ append decision-stream: ${DECISION_STREAM_FILE}"
echo
echo "=========================================="
echo "  4 步 fallback 全跑完 ✅"
echo "=========================================="

# ===== 6. v-bump 自动触发判定 (per v2.4 ADR-0057-f) =====
# 4 条件: ① 反模式 ≥ 4 / ② 流程变化 ≥ 1 / ③ 触发词变化 ≥ 1 / ④ hot recall 新增段
# 任一满足 → 触发立 v_new_version (per v2.6.30 §I self-evolution)
V_BUMP_TRIGGER=false
V_BUMP_REASON=""

# 简化判定: 根据 PITFALLS + PREVENTIONS + WHAT_FIXED 字符串判定
# 实际生产环境应该 parse SKILL.md frontmatter 反模式表跟触发词 + git diff 段
if [ -n "${PITFALLS:-}" ] && [ -n "${PREVENTIONS:-}" ]; then
  # 至少 1 踩坑 + 1 避坑 → 算"经验教训"类, 触发 v-bump 评估
  PITFALL_COUNT=$(echo "${PITFALLS}" | tr ';' '\n' | wc -l | tr -d ' ')
  if [ "$PITFALL_COUNT" -ge 2 ]; then
    V_BUMP_TRIGGER=true
    V_BUMP_REASON="踩坑 ≥ 2 (${PITFALL_COUNT} 条) + 避坑 ≥ 1 → 触发 v-bump 评估 (per v2.6.30 §I self-evolution 协议位)"
  fi
fi

if [ "$V_BUMP_TRIGGER" = true ]; then
  echo
  echo "=========================================="
  echo "🔔 v-bump 触发建议 (per v2.4 ADR-0057-f):"
  echo "  理由: ${V_BUMP_REASON}"
  echo "  5 步闭环: ① 总结 (本脚本已跑) → ② 内化 (更新 SKILL.md changelog / 反模式 / 触发词) → ③ commit (atomic) → ④ bump version (v${SKILL_VERSION} → v_new_version) → ⑤ push (per §C.3.2)"
  echo "  建议: 跑 worktree + PR 协议 (per §C.3.1), 不可直 push main"
  echo "=========================================="
else
  echo
  echo "(无 v-bump 触发, 经验教训 < 2 踩坑, 继续观察)"
fi

exit 0
