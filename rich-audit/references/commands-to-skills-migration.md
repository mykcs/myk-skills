# Commands → Skills Migration Detection (v2.6.1, 2026-06-10)

> 来源: 4-tool Tri-Search 2026-06-10 找到的提升方向
> 触发: `code.claude.com/docs/en/skills` 明确说 "Custom commands have been merged into skills"

## 检测对象

- `~/.claude/commands/*.md` (旧 commands 目录, 可能为空或遗留)
- `~/.claude/skills/*/SKILL.md` (新 skills 目录, 当前是 symlink → `~/.agents/skills/`)

## 迁移判定 (3 条同时满足)

1. **单一职责**: command body 不超过 30 行 (skill 推荐 ≤ 50 行)
2. **无 frontmatter 复杂依赖**: command 不依赖特殊 hooks 拦截
3. **有 SKILL.md 等价或可创建**: 已有 `<name>/SKILL.md` 在 skills 目录, 或可一键创建

## 检测命令

```bash
# 抓所有 commands
ls ~/.claude/commands/*.md 2>/dev/null

# 抓所有 skills
ls -d ~/.claude/skills/*/ 2>/dev/null

# 求差集 (有 command 但没对应 skill)
for cmd in ~/.claude/commands/*.md; do
  name=$(basename "$cmd" .md)
  test -d "~/.claude/skills/$name" || echo "MIGRATION CANDIDATE: $name"
done
```

## 迁移模板 (手操作, 脚本不自动跑)

```bash
# 1. 创建 skill 目录
mkdir -p ~/.claude/skills/<name>/

# 2. 迁移文件
mv ~/.claude/commands/<name>.md ~/.claude/skills/<name>/SKILL.md

# 3. 加 frontmatter (从 command 头部提取 description)
# 验证: head -3 ~/.claude/skills/<name>/SKILL.md 显示 ---
```

## 已知现状 (2026-06-10 system reminder 抓)

`~/.agents/skills/` 已有 30+ `source-command-*` skill (e.g. `source-command-aside`, `source-command-claw`, `source-command-cpp-build`...), 表明:
- 大量功能已从旧 commands 迁到新 skills
- `~/.claude/commands/` 目录可能存在遗留 / 重复 / 镜像

## 反向检测: 重复 skill

不止是 command → skill 迁移, 还要检测:
- 多个 skill 触发词 overlap
- 多个 skill 功能描述重复 (e.g. 两个 skill 都做"代码审查")
- 已知反例: `rich-audit` vs `website-improve` 在某些 mode 有 overlap (用户已知)

## 自动修复 (Level 分级)

- **Level 1**: 列迁移候选清单 (有 command 无对应 skill)
- **Level 2**: 提议迁移 + 提议 skill 合并/拆分, **不自动做** (per scope discipline)
- **Level 3**: 真实迁移, **需用户授权** (per scope discipline)

## 与其他子模块的关系

- 跟 `consistency-6d/2-cross-references.md` 互补 (本文件看"遗留" + "重复", cross-ref 看"引用完整性")
- 跟 `dead-code-orphan.md` 互补 (本文件专门管 commands/skills 边界, dead-code 管死代码)
