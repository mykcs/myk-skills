# 5. 格式/前置元数据 (Frontmatter Consistency)

> Consistency 父维度 20% → 子维度 5: ~3-4%

## 检查对象

- `~/.claude/rules/*.md` 必须有 frontmatter (name/description/metadata)
- `~/.claude/memory/*.md` frontmatter 完整
- `~/.agents/skills/*/SKILL.md` frontmatter (name/description/metadata.version/triggers/tags)
- `~/.claude/settings.json` JSON 合法 (用 `python3 -m json.tool`)
- `~/.claude/hooks/*.py` Python 语法 (`python3 -m py_compile`)

## 检查命令

```bash
# 检查所有 .md 是否有 frontmatter (--- 开头)
for f in ~/.claude/rules/*.md ~/.claude/memory/*.md; do
  head -1 "$f" | grep -q '^---$' || echo "NO FRONTMATTER: $f"
done

# 检查 settings.json 合法
python3 -m json.tool ~/.claude/settings.json > /dev/null || echo "INVALID JSON: settings.json"

# 检查 hook 脚本语法
for f in ~/.claude/hooks/*.py; do
  python3 -m py_compile "$f" 2>/dev/null || echo "SYNTAX ERROR: $f"
done
```

## 已知反例

- session-start linter 噪音 vs Claude 主动编辑混进 settings.json (`CASE-INJECT-HOT-FACTS-DEPLOYMENT-20260608`)

## 自动修复

- **Level 1**: 缺 frontmatter 的 .md, 套用模板自动补
- **Level 2**: 备份 + `jq` 重写 settings.json (per `~/.claude/rules/settings-json-edit-sop.md`)
