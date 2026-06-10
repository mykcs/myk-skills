# 3. 规则冲突检测 (Rule Conflict Detection)

> Consistency 父维度 20% → 子维度 3: ~3-4%

## 检查对象

- `behavioral-discipline.md` §A (Scope Discipline) ↔ `user.md:104-110` (bug 修复自主)
- `behavioral-process.md` §B (Plan Review Gate) ↔ `behavioral-discipline.md` §A
- `behavioral-core.md` (Coding Style) ↔ 语言特定规则 (`*.md`)
- hook 之间的拦截冲突 (`~/.claude/hooks/*.py` 优先级)

## 检查方法

```bash
# 抓所有 "禁止 / 必须 / 强制 / NEVER / MUST" 类硬规则
rg -nE '(禁止|必须|强制|NEVER|MUST|反例|违反|不得)' \
  ~/.claude/rules/*.md ~/.claude/memory/user.md

# 抓"例外 / 边界 / 冲突消解"段落
rg -nE '(例外|边界|冲突|歧义|胜出|优先级)' \
  ~/.claude/rules/*.md
```

AI 语义检测: 抽取每条硬规则的"作用域 + 触发条件 + 动作", 对所有规则两两比对, 输出冲突表.

## 已知冲突 (案例)

- `behavioral-discipline §A` vs `user.md:104-110` 在边界 case 仍 ambiguity (2026-06-08 已加边界 clause, 未根除)
- 多个 hook 拦截同一 PreToolUse event 时, 优先级未机器化

## 自动修复

- **Level 1**: 列出所有硬规则 + 冲突对, 标 P0/P1 优先级
- **Level 2**: 提议规则合并 / 边界 clause, **不自动改** (scope discipline 边界)
