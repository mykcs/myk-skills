#!/bin/bash
# check-run-card-version.sh — lint Run Card 标题版本号跟 SKILL.md frontmatter version 一致
# 触发: 任何改 Run Card / SKILL.md frontmatter 后必跑
# exit 0 = 一致 / exit 1 = drift
#
# 用法:
#   bash scripts/check-run-card-version.sh
#   bash scripts/check-run-card-version.sh --auto-fix   # 改 Run Card 跟 SKILL.md frontmatter 同步
#
# 起源: 2026-07-08 v0.2.2 立 (per user "立 lint 规则")

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_MD="$SKILL_DIR/SKILL.md"
PUBLISH_SH="$SCRIPT_DIR/digest-publish.sh"

AUTO_FIX="false"
[ "${1:-}" = "--auto-fix" ] && AUTO_FIX="true"

# 1. 抓 SKILL.md frontmatter version (line 7 形如 "  version: v0.2.2")
SKILL_VER=$(grep -m1 -E "^  version: v[0-9]+\.[0-9]+\.[0-9]+" "$SKILL_MD" | sed -E 's/.*(v[0-9]+\.[0-9]+\.[0-9]+).*/\1/')
if [ -z "$SKILL_VER" ]; then
    echo "❌ FAIL: SKILL.md frontmatter 没找到 version (期望格式:  version: vX.Y.Z)"
    exit 1
fi

# 2. 抓 publish.sh Run Card 标题 version (line 形如 "🎯 本次运行目标 (Run Card, v0.2.1)")
CARD_VER=$(grep -m1 -E "Run Card, v[0-9]+\.[0-9]+\.[0-9]+" "$PUBLISH_SH" | sed -E 's/.*(v[0-9]+\.[0-9]+\.[0-9]+).*/\1/')
if [ -z "$CARD_VER" ]; then
    echo "❌ FAIL: digest-publish.sh Run Card 标题没找到 version (期望格式: Run Card, vX.Y.Z)"
    exit 1
fi

# 3. 比对
echo "SKILL.md frontmatter: $SKILL_VER"
echo "Run Card 标题:        $CARD_VER"

if [ "$SKILL_VER" = "$CARD_VER" ]; then
    echo "✅ PASS: 版本一致"
    exit 0
fi

# 4. drift 报告
echo ""
echo "⚠️ DRIFT: SKILL.md frontmatter 跟 Run Card 标题版本不一致"
echo "   改法 1: SKILL.md frontmatter version → $CARD_VER (Run Card 是当前真版本)"
echo "   改法 2: Run Card 标题 → $SKILL_VER (SKILL.md 是当前真版本)"
echo ""

if [ "$AUTO_FIX" = "true" ]; then
    # auto-fix: 改 Run Card 跟 SKILL.md 同步 (默认 SKILL.md 是 source of truth)
    echo "🔧 AUTO-FIX: 改 Run Card 标题 → $SKILL_VER"
    sed -i.bak -E "s/(Run Card, )v[0-9]+\.[0-9]+\.[0-9]+/\1$SKILL_VER/" "$PUBLISH_SH"
    rm -f "$PUBLISH_SH.bak"
    echo "✅ 已改, 验证:"
    grep -m1 -E "Run Card, v[0-9]+\.[0-9]+\.[0-9]+" "$PUBLISH_SH"
    exit 0
fi

exit 1
