# 4. 索引/指针有效性 (Index/Pointer Validity)

> Consistency 父维度 20% → 子维度 4: ~3-4%

## 检查对象

- `MEMORY.md` "🔥 HOT FACTS" 9 行 5 站点 → `~/Repo/webs/{active,academic,arch}/` 实际路径
- `MEMORY.md` Cases 段 → `~/.claude/knowledge/cases/wiki/CASE-*.md` 实际文件
- `MEMORY.md` Skills 段 → `~/.agents/skills/` 实际目录
- `CLAUDE.md` → `behavioral-*.md` 链接
- `SKILL.md` → `references/*.md` 链接
- mem0 cloud entities ↔ filesystem memory 文件 (L3 gap)

## 检查命令

```bash
# 抓 MEMORY.md 提到的所有 5 站点 + 实际验证
for site in mykcs.github.io GDKVM OSA academic; do
  ls -d ~/Repo/webs/active/*/$site* ~/Repo/webs/academic/$site 2>/dev/null | head -1 || echo "MISSING: $site"
done

# 抓 MEMORY.md 提到的 case 文件
rg -o 'CASE-[A-Z0-9_-]+' ~/.claude/memory/MEMORY.md | sort -u | while read c; do
  test -f ~/.claude/knowledge/cases/wiki/$c.md || echo "MISSING CASE: $c"
done
```

## 已知反例

- `CASE-MEMORY-MD-PHANTOM-RULES-20260517` 197 phantom
- `MEMORY.md` 202 行超限 (line 200 warning 已触发)
- mem0 L3 gap 已知 (consolidated case)

## 自动修复

- **Level 1**: 列出 orphan / phantom, 提示用户删除或重建
- **Level 2**: 触发 `~/.claude/scripts/memory-audit.sh` 跑双轨同步
