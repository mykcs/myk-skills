#!/bin/bash
set -e

REPO_DIR="$HOME/Repo/mykcs/cc_switch_20260407"
DATE_DIR=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d-%H%M)
SETTINGS_SRC="$HOME/.claude/settings.json"
CLAUDE_JSON_GLOBAL="$HOME/.claude/.claude.json"
CLAUDE_JSON_PROJECT="$HOME/.claude.json"

# CLI flag: --force-first skips the "no previous backup" guard
FORCE_FIRST=false
if [ "$1" = "--force-first" ]; then
    FORCE_FIRST=true
fi

# 1. 检测 API 提供商（通用正则提取域名前缀）
API_URL=$(grep -o '"ANTHROPIC_BASE_URL"[[:space:]]*:[[:space:]]*"[^"]*"' "$SETTINGS_SRC" 2>/dev/null | sed 's/.*"https:\/\/\([^\/]*\)\/.*/\1/' | head -1 || true)

if [ -n "$API_URL" ]; then
    PROVIDER=$(echo "$API_URL" | sed -E 's/^([a-zA-Z0-9-]+\.)?([a-zA-Z0-9-]+)\..*/\2/')
else
    PROVIDER="unknown"
fi

# 2. 防重复：如果文件已存在，追加秒级后缀
BACKUP_NAME="${PROVIDER}-${TIMESTAMP}.json"
if [ -f "$REPO_DIR/$DATE_DIR/$BACKUP_NAME" ]; then
    BACKUP_NAME="${PROVIDER}-${TIMESTAMP}-$(date +%S).json"
fi

mkdir -p "$REPO_DIR/$DATE_DIR"

# 3. 备份 settings.json
cp "$SETTINGS_SRC" "$REPO_DIR/$DATE_DIR/$BACKUP_NAME"
echo "settings.json -> $BACKUP_NAME"

# 4. 备份 .claude.json（权限配置）
if [ -f "$CLAUDE_JSON_GLOBAL" ]; then
    cp "$CLAUDE_JSON_GLOBAL" "$REPO_DIR/$DATE_DIR/claude-json-global-${TIMESTAMP}.json"
    echo ".claude.json (global) -> claude-json-global-${TIMESTAMP}.json"
fi

if [ -f "$CLAUDE_JSON_PROJECT" ]; then
    cp "$CLAUDE_JSON_PROJECT" "$REPO_DIR/$DATE_DIR/claude-json-project-${TIMESTAMP}.json"
    echo ".claude.json (project) -> claude-json-project-${TIMESTAMP}.json"
fi

# 5. 强制对比审计（[BLOCKING] — 不可跳过）
CURRENT_FILE="$REPO_DIR/$DATE_DIR/$BACKUP_NAME"

# 先在同日期目录找上一次备份
LAST_BACKUP=$(ls -1 "$REPO_DIR/$DATE_DIR/${PROVIDER}"-*.json 2>/dev/null | sort | tail -2 | head -1 || true)
# 同目录没有则跨所有日期目录找该 provider 最新备份
if [ -z "$LAST_BACKUP" ] || [ "$LAST_BACKUP" = "$CURRENT_FILE" ]; then
    LAST_BACKUP=$(find "$REPO_DIR" -maxdepth 2 -name "${PROVIDER}-*.json" -type f ! -path "$CURRENT_FILE" 2>/dev/null | sort | tail -1 || true)
fi

AUDIT_LOG="$REPO_DIR/$DATE_DIR/audit-diff-${TIMESTAMP}.log"

if [ -z "$LAST_BACKUP" ]; then
    echo ""
    echo "⚠️  未找到上一次同 provider（${PROVIDER}）备份。"
    if [ "$FORCE_FIRST" = true ]; then
        echo "✅ --force-first 已启用，跳过确认，视为基准状态。"
        echo "基准状态（首次备份）" > "$AUDIT_LOG"
    else
        echo "❌ 审计阻断：无法验证与历史状态的差异。"
        echo "   如果是首次备份，请使用 --force-first 参数显式确认："
        echo ""
        echo "       bash ~/.claude/scripts/backup-settings.sh --force-first"
        echo ""
        exit 1
    fi
else
    echo ""
    echo "--- diff vs 上一次备份 ($(basename "$LAST_BACKUP")) ---"
    DIFF_OUTPUT=$(diff -u "$LAST_BACKUP" "$CURRENT_FILE" 2>&1 || true)
    DIFF_EXIT=$?

    if [ "$DIFF_EXIT" -eq 0 ]; then
        echo "✅ 与上一次备份（$(basename "$LAST_BACKUP")）对比：无差异"
        echo "无差异" > "$AUDIT_LOG"
    else
        echo "$DIFF_OUTPUT" | head -60
        echo "--- end diff ---"
        echo "$DIFF_OUTPUT" > "$AUDIT_LOG"
    fi
    echo "审计日志已生成：$AUDIT_LOG"
    echo ""
fi

# 6. Git 提交推送（带重试）
cd "$REPO_DIR"
git add "$DATE_DIR/"
COMMIT_MSG="backup(${PROVIDER}): Claude settings $(date '+%Y-%m-%d %H:%M')"
git commit -m "$COMMIT_MSG" || true

for i in 1 2 3; do
    if git push; then
        echo ""
        echo "备份完成并推送: $BACKUP_NAME"
        echo "审计日志: $AUDIT_LOG"
        exit 0
    else
        echo "Push 失败，第 ${i} 次重试..."
        sleep 2
    fi
done

echo "Push 多次失败，请手动检查网络或代理配置。"
exit 1
