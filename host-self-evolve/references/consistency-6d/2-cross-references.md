# 2. 交叉引用完整性 (Cross-Reference Integrity)

> Consistency 父维度 20% → 子维度 2: ~3-4%

## 检查对象

- `MEMORY.md` → case 文件链接 (`~/.claude/knowledge/cases/wiki/CASE-*.md`)
- `CLAUDE.md` → `behavioral-*.md` 引用
- `behavioral-*.md` → 其他文件引用
- `SKILL.md` → `references/*.md` 引用
- `MEMORY.md` line 6-50 (🔥 HOT FACTS) ↔ `CLAUDE.local.md` (强制加载副本)

## 检查命令

```bash
# 抓所有 [[wiki-style]] 引用
rg -o '\[\[([a-zA-Z0-9_-]+)\]\]' ~/.claude/memory/*.md ~/.claude/rules/*.md

# 抓所有 markdown 链接
rg -o '\]\((~/.claude/[^)]+)\)' ~/.claude/**/*.md

# 验证引用文件存在
while read -r ref; do
  test -e "$ref" || echo "MISSING: $ref"
done < <(rg -o '\(~?(\.?\.?/?~/.claude/[^)]+)\)' ~/.claude/**/*.md)
```

## 已知反例

- `CASE-MEMORY-MD-PHANTOM-RULES-20260517` 197 phantom entries
- `mem0 L3 gap` 已知 (consolidated case)
- `CLAUDE.local.md` line 1-9 强引用为 source-of-truth, `MEMORY.md` line 6-50 是另一份, 双份靠 linter 同步

## 自动修复

- **Level 1**: 检测 phantom 引用, 提示用户确认删除或重建
- **Level 2**: 检测 MEMORY.md ↔ CLAUDE.local.md 不一致, 触发 linter re-sync
