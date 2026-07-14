# Skill Overlap Detection (v2.6.10, 2026-06-10)

> ⚠️ [历史快照 2026-06-10] Tri-Search Protocol v2.6 已于 2026-06-12 重命名为 Force-All-Search Protocol v2.7; 本文档保留历史命名作为 audit trail.
> **历史标 (2026-07-14 ADR-0056 cleanup)**: "4-tool Tri-Search" 是 v2.6.0 命名, 实际跑 N-tool (N 当前 = 6, per [~/.claude/rules/protocols/N-tool-search.md](https://example.invalid/~/.claude/rules/protocols/N-tool-search.md) v1.1.2). 保留旧字面作 audit trail.
> 来源: 4-tool Tri-Search 2026-06-10 找到的 v2.6.1 候选 B
> 对标: `github.com/scottholdren/skill-audit` (scans SKILL.md for conflicts/overlaps/redundancies)
> 强化: 在 `commands_to_skills_migrator.py.detect_skill_overlap` 基础上加 2 类

## 检测对象

`~/.agents/skills/*/SKILL.md` 跟 `~/.claude/skills/*/SKILL.md` (后者是 symlink → 前者)

## 检测维度 (3 类)

### 1. Trigger 重叠 (已有, in `commands_to_skills_migrator.py`)
- 多个 skill 共享同一 trigger 词
- 例: `build` trigger 在 `cpp-build` / `go-build` / `gradle-build` 三个 skill 都出现

### 2. Trigger 前缀重叠 (v2.6.10 新)
- 多个 skill 共享同一 trigger 前缀
- 例: `cpp-` 前缀在 `cpp-build` / `cpp-review` / `cpp-test`
- 检测: `Counter(trigger.split('-')[0])` 取 top N, N>3 报警

### 3. Description 关键词重叠 (v2.6.10 新, 简化 Jaccard)
- 多个 skill 的 description 共享关键词
- 例: "audit" / "config" 关键词在 rich-audit + website-improve 都出现
- 检测: 抓 description 的 noun 词, 计算 Jaccard 相似度, >0.3 报警

## 检测命令 (Python)

```python
# In scripts/skill_overlap_enhancer.py (新建 v2.6.10)
from collections import Counter
import re
from pathlib import Path

SKILLS_DIR = Path.home() / ".agents" / "skills"
MIN_DESC_OVERLAP = 0.3

def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0

NOUNS_RE = re.compile(r"\b[a-z]{4,}\b")  # 简化: 4+ 字母词当 noun proxy

def get_description_nouns(skill_md: Path) -> set[str]:
    text = skill_md.read_text()
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return set()
    desc_match = re.search(r"description:\s*\|?\s*\n?((?:\s+.+\n?)+)", fm_match.group(1))
    if not desc_match:
        return set()
    return set(NOUNS_RE.findall(desc_match.group(1).lower()))

def detect_prefix_overlap() -> list[dict]:
    prefixes: Counter = Counter()
    for skill_dir in SKILLS_DIR.iterdir():
        for prefix in skill_dir.name.split("-")[:-1]:
            prefixes[prefix] += 1
    return [{"type": "trigger_prefix_overlap", "prefix": p, "count": c}
            for p, c in prefixes.most_common() if c >= 3]

def detect_description_overlap() -> list[dict]:
    skill_nouns = {}
    for skill_dir in SKILLS_DIR.iterdir():
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            nouns = get_description_nouns(skill_md)
            if nouns:
                skill_nouns[skill_dir.name] = nouns
    overlaps = []
    names = list(skill_nouns.keys())
    for i, a in enumerate(names):
        for b in names[i+1:]:
            sim = jaccard(skill_nouns[a], skill_nouns[b])
            if sim >= MIN_DESC_OVERLAP:
                shared = skill_nouns[a] & skill_nouns[b]
                overlaps.append({
                    "type": "description_overlap",
                    "skills": [a, b],
                    "jaccard": round(sim, 3),
                    "shared_nouns": sorted(shared)[:10],
                })
    return overlaps
```

## 已知反例

- rich-audit vs website-improve: 在某些 mode 有 overlap (用户已知)
- cpp-build / cpp-review / cpp-test: 共享 `cpp-` 前缀
- 多个 `*deploy` skill 共享 `deploy` trigger

## 互补关系

- 跟 `commands_to_skills_migrator.py.skill_overlap` 互补 (本文件强化)
- 跟 `consistency-6d/3-rule-conflicts.md` 互补 (本文件看 skill 间, 3 看 rule 间)

## 自动修复 (Level 分级)

- **Level 1**: 列 overlap 清单
- **Level 2 (提议)**: 提议 trigger 改名前缀, **用户确认**
- **Level 3**: 自动合并 / 改名, **需用户授权**
