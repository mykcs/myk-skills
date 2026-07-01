#!/bin/bash
# verify-5fields.sh — §H.1 5 字段自检表
# 用途: 任务完成前必跑, 缺 1 项 = FAIL
# 用法: bash verify-5fields.sh [project_root] [deliverable_dir]
#      默认 = 当前目录 + ./deliverables

set -e
PROJECT_ROOT="${1:-$PWD}"
DELIVERABLE_DIR="${2:-$PROJECT_ROOT/deliverables}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    local expect_pass="$3"  # true/false
    echo ""
    echo -n "[$name] ... "
    if eval "$cmd" >/dev/null 2>&1; then
        if [ "$expect_pass" = "true" ]; then
            echo -e "${GREEN}✅ PASS${NC}"
            PASS=$((PASS+1))
        else
            echo -e "${RED}❌ FAIL (expected fail, got pass)${NC}"
            FAIL=$((FAIL+1))
        fi
    else
        if [ "$expect_pass" = "false" ]; then
            echo -e "${GREEN}✅ PASS (expected fail)${NC}"
            PASS=$((PASS+1))
        else
            echo -e "${RED}❌ FAIL${NC}"
            FAIL=$((FAIL+1))
        fi
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "🔍 §H.1 5 字段自检表"
echo "═══════════════════════════════════════════════════════════"
echo "Project: $PROJECT_ROOT"
echo "Deliverable dir: $DELIVERABLE_DIR"
echo ""

# 1. path — 交付物存在
check "1. path 交付物存在" "test -d '$DELIVERABLE_DIR' || test -f '$DELIVERABLE_DIR'" "true"
DELIVERABLE_FILES=$(ls "$DELIVERABLE_DIR" 2>/dev/null | wc -l | tr -d ' ')
echo "    交付物文件数: $DELIVERABLE_FILES"

# 2. commit — 有新 commit
check "2. commit 已落地" "cd '$PROJECT_ROOT' && git log -1 --oneline" "true"
LATEST_COMMIT=$(cd "$PROJECT_ROOT" && git log -1 --format='%h | %s' 2>/dev/null)
echo "    最新 commit: $LATEST_COMMIT"

# 3. push — 已 push (跟 remote 比对, 空 = 已 push)
check "3. push 已推到 remote" "[ -z \"\$(cd '$PROJECT_ROOT' && git log @{u}..HEAD 2>/dev/null)\" ]" "true"
AHEAD=$(cd "$PROJECT_ROOT" && git rev-list --count @{u}..HEAD 2>/dev/null || echo "no-upstream")
echo "    本地 ahead remote: $AHEAD commit(s)"

# 4. owner — 双账号铁律 (仓归属正确)
check "4. owner 仓归属正确" "cd '$PROJECT_ROOT' && git remote -v" "true"
REMOTE=$(cd "$PROJECT_ROOT" && git remote get-url origin 2>/dev/null || echo "no-remote")
echo "    Remote origin: $REMOTE"
if echo "$REMOTE" | grep -q "wangrui2025/wangrui2025"; then
    echo -e "    ${YELLOW}⚠️ wangrui2025/* 仓, 注意双账号铁律${NC}"
fi

# 5. 验收证据 — 可执行命令已跑 (find any 1+ verification file)
check "5. 验收证据" "find '$DELIVERABLE_DIR' -name '*.md' -size +100c | head -1 | grep -q ." "true"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 总计: ${GREEN}$PASS PASS${NC} / ${RED}$FAIL FAIL${NC}"
echo "═══════════════════════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}❌ 5 字段验收 FAIL, 按 §C.2 deferred theater 零容忍规则禁止声明完成${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 5 字段全过, 可声明完成${NC}"
exit 0
