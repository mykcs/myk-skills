# 6. 优先级与作用域 (Priority and Scope)

> Consistency 父维度 20% → 子维度 6: ~2-3%

## 检查对象

- settings 层级: Managed > CLI > Local > Project > User (官方)
- 规则优先级: `user.md` > `behavioral-discipline.md` > `behavioral-process.md` > `behavioral-core.md` > `behavioral-output.md`?
- hook 拦截优先级: 多个 PreToolUse hook 拦截同一 event 时的执行顺序
- skill 触发优先级: 同名触发词多个 skill 匹配时
- mem0 vs filesystem memory 冲突时

## 检查命令

```bash
# 抓所有 hard rule 优先级声明
rg -nE '(优先级|优先级表|胜出|when.*conflict|priority)' \
  ~/.claude/rules/*.md ~/.claude/memory/user.md

# 列出所有 hook + 它们的 event + matcher
for f in ~/.claude/hooks/*.py; do
  rg -l "PreToolUse\|PostToolUse\|SessionStart\|Stop" "$f" 2>/dev/null
done | xargs -I{} rg -nE '(def |event|matcher)' {} | head -30
```

## 已知反例

- 2026-06-08 双向保险规则刚加 (`user.md:104-110` 自主 vs `behavioral-discipline §A` 问), 但**优先级表本身未机器化**, 全靠 claudecode 推理
- 多个 PreToolUse hook 拦截同一 event (e.g. `pre-edit-confirm.py` + `inject-hot-facts.sh`) 时, 顺序未文档化

## 自动修复

- **Level 1**: 列出优先级表 (机读 JSON), 跟 claudecode 运行时推理结果对比
- **Level 2**: 提议固化优先级表到 `~/.claude/rules/priority-table.md`, **不自动改** (scope discipline 边界)
