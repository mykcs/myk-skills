# Wasted Context Tokens Detection (v2.6.10, 2026-06-10)

> ⚠️ [历史快照 2026-06-10] Tri-Search Protocol v2.6 已于 2026-06-12 重命名为 Force-All-Search Protocol v2.7; 本文档保留历史命名作为 audit trail.
> 来源: 4-tool Tri-Search 2026-06-10 找到的 v2.6.1 候选 C
> 对标: jarodtaylor gist "dead weight, conflicts, stale rules, wasted context tokens"
> 检测: `scripts/waste_token_detector.py`

## 检测对象

- `~/.agents/skills/*/SKILL.md` (per-skill token cost)
- `~/.claude/rules/*.md` (per-rule token cost, 加载到每次 session)
- `~/.claude/memory/*.md` (per-memory token cost, 加载到每次 session)
- `~/.claude/CLAUDE.md` + `CLAUDE.local.md` (per-prompt cost)

## 估算方法

- 简化: `len(text) // 4` (1 token ≈ 4 chars, 英文主导)
- 实际: 4 chars/token (英文), 1.5 chars/token (中文)

```python
def estimate_tokens(text: str) -> int:
    return len(text) // 4
```

## 关键指标 (3 类)

### 1. Per-file token cost
- SKILL.md > 1500 tokens: 警告
- rules/*.md > 200 行: 警告 (per `architecture-health`)
- MEMORY.md > 200 行: 已超 (2026-06-10 现状)

### 2. Loaded-per-session cost
- 每次 session 自动加载: CLAUDE.md + CLAUDE.local.md + 所有 rules/*.md
- 不自动加载: SKILL.md (按需)
- **热路径** (high cost, high frequency): rules + CLAUDE.md + memory/*.md
- 优化目标: 把不常用的内容下沉到 `references/` 或 `archive/`

### 3. Stale content
- 文件 > 30 天没修改: 标 stale
- 引用已删的 case / skill: dead reference (跟 dead_code_detector overlap)

## 检测命令 (Python)

```python
# In scripts/waste_token_detector.py
from pathlib import Path
import time

HOT_PATHS = [
    Path.home() / ".claude" / "rules",
    Path.home() / ".claude" / "memory",
    Path.home() / ".claude" / "CLAUDE.md",
    Path.home() / ".claude" / "CLAUDE.local.md",
]
COLD_PATHS = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "knowledge" / "cases" / "wiki",
]

STALE_DAYS = 30
WARN_TOKENS = 1500

def main():
    findings = []
    # 1. Hot path cost
    for p in HOT_PATHS:
        if p.is_file():
            tokens = estimate_tokens(p.read_text())
            if tokens > WARN_TOKENS:
                findings.append({"type": "hot_path_heavy", "path": str(p), "tokens": tokens})
    # 2. Cold path cost (per skill)
    for skill_dir in COLD_PATHS[0].iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            tokens = estimate_tokens(skill_md.read_text())
            if tokens > WARN_TOKENS:
                findings.append({"type": "skill_too_heavy", "path": skill_dir.name, "tokens": tokens})
    # 3. Stale content
    for p in HOT_PATHS[0].glob("*.md") if HOT_PATHS[0].exists() else []:
        age_days = (time.time() - p.stat().st_mtime) / 86400
        if age_days > STALE_DAYS:
            findings.append({"type": "stale_hot_path", "path": str(p), "age_days": round(age_days, 1)})
    return findings
```

## 已知反例

- `~/.claude/memory/MEMORY.md` 202 行超 200 行阈值 (case 已知)
- 部分 skills > 1500 tokens (rich-audit SKILL.md 本身 ~400 行 ≈ 1500 tokens)
- rules/ 11 个文件, 单次 session 全部加载

## 自动修复 (Level 分级)

- **Level 1**: 列 token 重 + stale 清单
- **Level 2 (提议)**: 提议下沉到 `references/` 或拆 SKILL.md
- **Level 3**: 自动 archive, **需用户授权**

## 互补关系

- 跟 `consistency-6d/2-cross-references.md` 互补 (本文件看 size, 2 看引用)
- 跟 `consistency-6d/4-index-validity.md` 互补 (本文件看 stale, 4 看指针)
- 跟 `architecture-health` (per SKILL.md) 互补 (本文件 token 维度, architecture-health 行数维度)
