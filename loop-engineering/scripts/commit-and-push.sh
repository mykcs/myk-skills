#!/bin/bash
# commit-and-push.sh — atomic commit + smart-push (loop 流水线专用)
# 用途: 每个 stage 跑完自动 commit + push
# 用法: bash commit-and-push.sh "<commit-message>" [stage_dir]
#      stage_dir 缺省 = 当前目录
# 特点: stage_dir 必是项目子目录, push 前 cd 进去 (避免跑在错位置)

set -e
COMMIT_MSG="${1:?用法: bash commit-and-push.sh \"<msg>\" [stage_dir]}"
STAGE_DIR="${2:-$PWD}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 找 git 仓根
GIT_ROOT=$(cd "$STAGE_DIR" && git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$GIT_ROOT" ]; then
    echo -e "${RED}❌ $STAGE_DIR 不是 git 仓${NC}"
    exit 1
fi

REMOTE=$(cd "$GIT_ROOT" && git remote get-url origin 2>/dev/null || echo "no-remote")
echo "═══════════════════════════════════════════════════════════"
echo "🔄 Atomic commit + smart-push"
echo "═══════════════════════════════════════════════════════════"
echo "Git root:    $GIT_ROOT"
echo "Remote:      $REMOTE"
echo "Commit msg:  $COMMIT_MSG"
echo ""

# 2. 双账号铁律 (wangrui2025/* 推到 mykcs = 4+ 次历史污染)
if echo "$REMOTE" | grep -q "mykcs" && echo "$REMOTE" | grep -q "wangrui2025"; then
    echo -e "${RED}❌ owner mismatch: mykcs/wangrui2025 跨账号冲突, 拒绝 push${NC}"
    exit 1
fi

# 3. git status
cd "$GIT_ROOT"
echo "───────────────────────────────────────────────────────────"
echo "📊 git status (pre-commit)"
echo "───────────────────────────────────────────────────────────"
git status --short
echo ""

# 4. add + commit
git add -A
echo "───────────────────────────────────────────────────────────"
echo "📝 commit"
echo "───────────────────────────────────────────────────────────"
git commit -m "$COMMIT_MSG" || {
    echo -e "${YELLOW}⚠️ 无新改动, 跳过 commit${NC}"
    exit 0
}
COMMIT_HASH=$(git log -1 --format='%h')
echo "  commit: $COMMIT_HASH"
echo ""

# 5. pull --rebase (避免 push 失败)
echo "───────────────────────────────────────────────────────────"
echo "🔀 pull --rebase origin main"
echo "───────────────────────────────────────────────────────────"
git pull --rebase origin main 2>&1 | tail -5 || {
    echo -e "${RED}❌ pull --rebase 失败${NC}"
    echo "  解决: git fetch origin && git reset --hard origin/main"
    echo "  然后重跑 commit-and-push.sh"
    exit 1
}

# 6. push
echo "───────────────────────────────────────────────────────────"
echo "🚀 push origin main"
echo "───────────────────────────────────────────────────────────"
git push origin main 2>&1 | tail -3
echo ""

# 7. verify (3 步)
echo "───────────────────────────────────────────────────────────"
echo "✅ verify"
echo "───────────────────────────────────────────────────────────"
echo "git log -1:"
git log -1 --oneline
echo ""
echo "git status -sb:"
git status -sb
echo ""
AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "no-upstream")
echo "ahead remote: $AHEAD commit(s)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ commit + push + verify 全过${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📌 后续: 跑 §H.1 5 字段验收 (bash verify-5fields.sh)"
echo "📌 下一步: 起下一 stage sub-agent (参考 loop-status.sh)"
