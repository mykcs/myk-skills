# 记忆系统对齐检测（双轨同步）

> 详细内容参考文件。从主 SKILL.md 拆分（2026-06-02 rich-audit v2.2）。

> **背景**：用户采用双轨记忆系统（mem0 MCP 云端 + 文件系统 markdown），两者需保持同步。

## 三层对齐矩阵

| 层次 | 源 | 目标 | 检测内容 |
|------|-----|------|----------|
| **L1** | `~/.claude/memory/MEMORY.md` | `~/.claude/knowledge/cases/wiki/*.md` | Phantom entries（索引有-link但文件不存在） |
| **L2** | `~/.claude/knowledge/cases/wiki/*.md` | `~/.claude/memory/MEMORY.md` | Missing entries（文件存在但索引无-link） |
| **L3** | mem0 (`case` type) | `~/.claude/knowledge/cases/wiki/*.md` | mem0 有 case 记忆但文件系统无对应文件 |

## 自动修复规则

| 层级 | 发现问题 | 自动修复 |
|------|----------|----------|
| L1 Phantom | MEMORY.md 索引指向不存在的 case 文件 | 从索引中移除该 entry |
| L2 Missing | case 文件存在但 MEMORY.md 未索引 | 添加 entry 到 MEMORY.md |
| L3 Gap | mem0 有 `source: CASE-XXX` 但文件系统无文件 | 创建 case 文件（模板），通知用户补充内容 |

## 审计命令

```bash
# L1: Phantom entries in MEMORY.md
phantom_count=0
while IFS= read -r line; do
  [[ "$line" =~ ^\-\ \[.*\]\((~/.claude/knowledge/cases/wiki/CASE-[^)]+)\) ]] || continue
  file="${BASH_REMATCH[1]/#\~/$HOME}"
  [[ -f "$file" ]] || { echo "[PHANTOM] $file"; ((phantom_count++)); }
done < ~/.claude/memory/MEMORY.md
echo "PHANTOM_COUNT=$phantom_count"

# L2: Missing entries in MEMORY.md
indexed=$(sed -n 's/.*(~\/.claude\/knowledge\/cases\/wiki\/(CASE-[^)]*))/\1/p' ~/.claude/memory/MEMORY.md | sort)
filesystem=$(ls ~/.claude/knowledge/cases/wiki/CASE-*.md 2>/dev/null | xargs -I{} basename {} | sort)
missing=$(comm -23 <(echo "$filesystem") <(echo "$indexed"))
echo "MISSING_COUNT=$(echo "$missing" | wc -l)"
[[ -n "$missing" ]] && echo "$missing"

# L3: mem0 云端 vs case 文件系统对齐
# 使用 mcp__plugin_mem0_mem0__search_memories with query="CASE" top_k=500
# Parse result (JSON string in .result field), extract all metadata.source starting with "CASE-"
# Check each against ~/.claude/knowledge/cases/wiki/ filesystem
# Report: MEM0_CASE_COUNT, MEM0_CASE_MISSING_FILES, [MEM0_GAP] files
```

## Layer 2 修复联动

`Agent-Fix-Memory` 需在 `memory_issues` 中新增 `memory_alignment` 子类：

```python
memory_issues = {
    "phantom_entries": [...],    # L1: MEMORY.md 索引指向不存在的文件
    "missing_entries": [...],     # L2: case 文件存在但未进入 MEMORY.md 索引
    "mem0_gap": {
        "missing_files": [...],  # L3a: mem0 有 source=CASE-XXX 但文件系统无对应文件
        "orphaned_cases": [...], # L3b: case 文件存在但 mem0 无对应 source 记忆
        "total_mem0_cases": N,   # mem0 中 case-type 记忆总数
    }
}
```

**修复策略**：L1/L2 可自动修复；L3 分为两类：
- `mem0 有 source 但文件系统无文件` → 自动从模板生成 case 文件，通知用户补充内容
- `mem0 有 source 但对应 archive 目录已归档` → 更新 mem0 记忆的 source 字段指向 archive 路径

## 已知陷阱（2026-06-02 发现）

**Ghost case 引用误报**：`rich_audit.py:651` 的 glob 模式 `cases_dir / f"*{related}*"` 不递归 `archive-*/` 子目录，导致 197 LOW false positives。修复方法：改用 `cases_dir / f"**/*{related}*"` + `glob.glob(p, recursive=True)`。修复后 ghost case findings 197 → 0。
