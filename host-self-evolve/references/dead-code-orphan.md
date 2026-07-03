# Dead Code / Orphan Detection (v2.6.1, 2026-06-10)

> ⚠️ [历史快照 2026-06-10] Tri-Search Protocol v2.6 已于 2026-06-12 重命名为 Force-All-Search Protocol v2.7; 本文档保留历史命名作为 audit trail.
> 来源: 4-tool Tri-Search 2026-06-10 找到的提升方向
> 互补: 跟 consistency-6d (看"对得上") 互补, 本文件看"没人在用"

## Dead Code 类型 (5 类)

### 1. 死 hooks
- `~/.claude/hooks/*.py` 没被 `~/.claude/settings.json` 的 `hooks` 字段引用
- 检测: 抓 `settings.json.hooks[*].hooks[*].command` 路径, 跟 `hooks/*.py` 文件名 glob 比对

### 2. 死 scripts
- `~/.claude/scripts/*.sh` / `*.py` 没被 settings.json / case / 其他脚本引用
- 检测: 抓 settings.json 里的 `command` 字段, 跟 scripts 目录文件名 glob 比对

### 3. 死 i18n keys (项目级, 条件触发)
- `zh.json` / `en.json` 里有 key 但代码里没用
- 检测: `rg -o 't\("[^"]+"\)|i18n\.[a-z.]+' src/ --no-filename | sort -u` 跟 i18n keys 比对
- **本 skill 不直接跑** (项目级, 仅当 working dir 有 i18n 文件时启用)

### 4. orphan case files
- `~/.claude/knowledge/cases/wiki/CASE-*.md` 存在但没被任何 MEMORY.md / 其他 case 引用
- 检测: `rg -l 'CASE-[A-Z0-9_-]+' ~/.claude/` 跟 wiki/ glob 求差集

### 5. orphan skills
- `~/.agents/skills/*/SKILL.md` 存在但 0 触发 / 0 引用
- 检测: 抓 SKILL.md 的 `triggers` 字段, 跟 mem0 / MEMORY.md / rules 比对

## 已知反例 (case 库)

- `CASE-FAVICON-CONSOLIDATED` — favicon 缓存死引用
- `CASE-DEDUP-CONSOLIDATED` — Avatar 重复 / 样式块重复
- `CASE-SYMLINK-SUBMODULE-CONSOLIDATED` — 死 symlink
- `CASE-MCP-CONSOLIDATED` — 死 MCP ref

## 自动修复 (Level 分级)

- **Level 1 (机械)**: 列 orphan 清单 + 标记 "candidate for delete", **不删**
- **Level 2 (AI 语义)**: 提议把 orphan 移到 `archive-*/` 子目录, **不删**
- **Level 3 (需用户授权)**: 真实删除 (按 scope discipline, 用户没明确要求不动)

## 检测脚本骨架 (待实现)

```python
# ~/.agents/skills/rich-audit/scripts/dead_code_detector.py
import json
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = Path.home() / ".agents" / "skills"
WIKI_DIR = CLAUDE_DIR / "knowledge" / "cases" / "wiki"

def detect_orphan_cases() -> list[str]:
    """返回所有 orphan case 文件路径 (存在但没被引用)"""
    referenced = set()
    for md in CLAUDE_DIR.rglob("*.md"):
        for match in md.read_text().split():
            if match.startswith("CASE-"):
                referenced.add(match.rstrip(".,;:") + ".md")
    return [str(p) for p in WIKI_DIR.glob("CASE-*.md") if p.name not in referenced]
```
