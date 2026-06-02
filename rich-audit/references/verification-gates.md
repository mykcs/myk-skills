# Verification Gates (报告完成前强制检查)

> 详细内容参考文件。从主 SKILL.md 拆分（2026-06-02 rich-audit v2.2）。

**在声明 "审计完成" 前，必须执行以下物理验证并粘贴输出：**

1. **备份确认**: `ls -la ~/.claude/backups/ | head -5` — 确认本次审计备份已创建
2. **规则语法检查**: 如修改了任何 `.md` 规则文件，执行 `head -5 <file>` 确认 frontmatter 未损坏
3. **JSON 有效性**: 如修改了 `settings.json`，执行 `python3 -m json.tool ~/.claude/settings.json > /dev/null && echo "JSON_VALID"` — 确认无语法错误
4. **差异摘要**: `git -C ~/.claude diff --stat 2>/dev/null || echo "NO_GIT_TRACKING"` — 确认变更范围符合预期
5. **GitHub 同步状态**: 执行 `git -C ~/.claude log @{u}..HEAD --oneline 2>/dev/null | wc -l` 和 `git -C ~/.agents/skills log @{u}..HEAD --oneline 2>/dev/null | wc -l` — 确认无未推送提交
6. **项目模式检测验证**: 如当前工作区含 Python 项目，确认 `project_modes` 输出正确标记了对应模式
7. **Skill 目录 Symlink 一致性**: 如修改了 skill 文件，执行以下命令确认 `.claude/skills/` 与 `.agents/skills/` symlink 一致：
   ```bash
   find ~/.claude/skills -maxdepth 1 -type l | while read f; do
     rel=$(basename "$f")
     target=$(readlink "$f")
     expected="$HOME/.agents/skills/$rel"
     [ "$target" = "$expected" ] && echo "[OK] $rel" || echo "[MISMATCH] $rel -> $target (expected $expected)"
   done
   ```
8. **健康分计算**: 重新运行 `python3 ~/.agents/skills/rich-audit/scripts/rich_audit.py`，确认 8 维度分数已正确记录
9. **MCP Server 冲突验证**: 执行 `/doctor`（或在非交互环境运行检测命令）确认无 `same command/URL as already-configured` 类 MCP 冲突错误
10. **MEMORY.md 索引一致性 + 记忆系统对齐**: 执行以下三层验证：
    ```bash
    # L1: Phantom entries（MEMORY.md 索引指向不存在的文件）
    phantom=0; while IFS= read -r line; do [[ "$line" =~ ^\-\ \[.*\]\((~/.claude/knowledge/cases/wiki/CASE-[^)]+)\) ]] || continue; file="${BASH_REMATCH[1]/#\~/$HOME}"; [[ -f "$file" ]] || { echo "[PHANTOM] $file"; ((phantom++)); }; done < ~/.claude/memory/MEMORY.md; echo "L1_PHANTOM=$phantom"

    # L2: Missing entries（case 文件存在但 MEMORY.md 未索引）
    indexed=$(sed -n 's/.*(~\/.claude\/knowledge\/cases\/wiki\/(CASE-[^)]*))/\1/p' ~/.claude/memory/MEMORY.md | sort -u)
    filesystem=$(ls ~/.claude/knowledge/cases/wiki/CASE-*.md 2>/dev/null | xargs -I{} basename {} | sort -u)
    missing=$(comm -23 <(echo "$filesystem") <(echo "$indexed"))
    echo "L2_MISSING_COUNT=$(echo "$missing" | grep -c . 2>/dev/null || echo 0)"
    [[ -n "$missing" ]] && echo "$missing" | head -10

    # L3: mem0 云端 vs case 文件系统对齐
    # Use mcp__plugin_mem0_mem0__search_memories with query="CASE" top_k=500
    # Parse result (JSON string in .result field), extract all metadata.source starting with "CASE-"
    # Check each against ~/.claude/knowledge/cases/wiki/ filesystem
    # Report: MEM0_CASE_COUNT, MEM0_CASE_MISSING_FILES, [MEM0_GAP] files
    - `L1_PHANTOM=0` → 通过；>0 → L1 drift detected
    - `INDEXED_CASES` 应 >= `FILESYSTEM_CASES * 0.9` → 通过；低于说明 L2 gap 严重
    - `MEM0_CASE_MISSING_FILES=0` → 通过；>0 → L3 mem0 drift detected
    ```

**若任何验证失败，审计未完成。** 修复后重新运行验证。

**Why**: rich-audit 自身曾多次出现误报（memory-audit cascade、ghost case detection）。验证门禁防止审计工具自身的幻觉被当作结论输出。
