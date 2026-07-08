#!/bin/bash
# check-skill-version.sh — lint 通用: SKILL.md frontmatter version vs 标题/描述里 version 一致
# 触发: 任何改 SKILL.md frontmatter 后必跑
# exit 0 = 一致 / exit 1 = drift
#
# 用法:
#   bash scripts/check-skill-version.sh <skill-name>                  # 默认 lint
#   bash scripts/check-skill-version.sh <skill-name> --auto-fix      # 改 frontmatter 跟标题 sync
#
# 支持的 skill:
#   auto-feishu-digest   (Run Card 标题: "🎯 本次运行目标 (Run Card, vX.Y.Z)")
#   host-self-evolve     (frontmatter description 含 "host-self-evolve vX.Y.X")
#
# 起源: 2026-07-08 v0.2.4 立 (per user "给 host-self-evolve 同步立同样 lint")

set -e

SKILL_NAME="${1:-}"
AUTO_FIX="false"
[ "${2:-}" = "--auto-fix" ] && AUTO_FIX="true"

if [ -z "$SKILL_NAME" ]; then
    echo "用法: $0 <skill-name> [--auto-fix]"
    echo "  支持: auto-feishu-digest | host-self-evolve"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 假设 scripts/ 在 ~/.agents/skills/<skill-name>/scripts/
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_MD="$SKILL_DIR/SKILL.md"

if [ ! -f "$SKILL_MD" ]; then
    echo "❌ FAIL: $SKILL_MD 不存在"
    exit 1
fi

# 1. 抓 SKILL.md frontmatter version (支持 2 种格式)
# 格式 A (auto-feishu-digest): "  version: vX.Y.Z"
# 格式 B (host-self-evolve):   "  version: \"X.Y.Z\"" (metadata 嵌套 + 引号)
SKILL_VER=$(grep -m1 -E "^  version: [\"']?v?[0-9]+\.[0-9]+\.[0-9]+[\"']?" "$SKILL_MD" | sed -E 's/.*[\" ]?(v?[0-9]+\.[0-9]+\.[0-9]+)[\" ]?.*/\1/')

# 补 v 前缀 (host-self-evolve 格式 B 没 v 前缀)
case "$SKILL_VER" in
    v*) ;;
    *) SKILL_VER="v$SKILL_VER" ;;
esac

if [ -z "$SKILL_VER" ] || [ "$SKILL_VER" = "v" ]; then
    echo "❌ FAIL: $SKILL_MD frontmatter 没找到 version 字段"
    echo "   期望 (格式 A): '  version: vX.Y.Z'"
    echo "   期望 (格式 B): '  version: \"X.Y.Z\"' (metadata 嵌套)"
    exit 1
fi

# 2. 按 skill 类型抓 title version
case "$SKILL_NAME" in
    auto-feishu-digest)
        # Run Card 标题: "🎯 本次运行目标 (Run Card, vX.Y.Z)" 在 scripts/digest-publish.sh
        TARGET_FILE="$SKILL_DIR/scripts/digest-publish.sh"
        TARGET_VER=$(grep -m1 -E "Run Card, v[0-9]+\.[0-9]+\.[0-9]+" "$TARGET_FILE" 2>/dev/null | sed -E 's/.*(v[0-9]+\.[0-9]+\.[0-9]+).*/\1/')
        TARGET_LABEL="Run Card 标题"
        if [ -z "$TARGET_VER" ]; then
            echo "❌ FAIL: $TARGET_FILE 没找到 Run Card 标题 version"
            exit 1
        fi
        ;;
    host-self-evolve)
        # frontmatter description 段含 "host-self-evolve vX.Y.X"
        TARGET_VER=$(grep -m1 -oE "host-self-evolve v[0-9]+\.[0-9]+\.[0-9]+" "$SKILL_MD" | sed -E 's/.*(v[0-9]+\.[0-9]+\.[0-9]+).*/\1/')
        TARGET_LABEL="frontmatter description"
        TARGET_FILE="$SKILL_MD"
        if [ -z "$TARGET_VER" ]; then
            echo "❌ FAIL: $SKILL_MD frontmatter description 没找到 host-self-evolve vX.Y.X"
            exit 1
        fi
        ;;
    *)
        echo "❌ 不支持的 skill: $SKILL_NAME (目前: auto-feishu-digest | host-self-evolve)"
        exit 1
        ;;
esac

# 3. 比对
echo "SKILL.md frontmatter version: $SKILL_VER"
echo "$TARGET_LABEL version:        $TARGET_VER"

if [ "$SKILL_VER" = "$TARGET_VER" ]; then
    echo "✅ PASS: 版本一致"
    exit 0
fi

# 4. drift 报告
echo ""
echo "⚠️ DRIFT: frontmatter 跟 $TARGET_LABEL 不一致"

if [ "$AUTO_FIX" = "true" ]; then
    # auto-fix: 改 title 跟 frontmatter 同步
    echo "🔧 AUTO-FIX: 改 $TARGET_LABEL → $SKILL_VER"
    case "$SKILL_NAME" in
        auto-feishu-digest)
            sed -i.bak -E "s/(Run Card, )v[0-9]+\.[0-9]+\.[0-9]+/\1$SKILL_VER/" "$TARGET_FILE"
            rm -f "$TARGET_FILE.bak"
            ;;
        host-self-evolve)
            sed -i.bak -E "s/(host-self-evolve )v[0-9]+\.[0-9]+\.[0-9]+/\1$SKILL_VER/g" "$TARGET_FILE"
            rm -f "$TARGET_FILE.bak"
            ;;
    esac
    echo "✅ 已改, 验证:"
    bash "$0" "$SKILL_NAME"
    exit 0
fi

exit 1