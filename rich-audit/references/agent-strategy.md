## 并行 Agent 策略

> **核心原则**：无依赖关系的任务必须并行启动 Agent，缩短总耗时；有依赖关系（如修复依赖审计结果、报告依赖修复结果）的任务必须顺序执行。

### Layer 1 审计层 — 双模并行

两个审计模式相互独立，**同时启动**两个 Agent：

| Agent | 名称 | 职责 | 输出格式 |
|-------|------|------|----------|
| `Agent-Audit-A` | 配置审计 | 扫描 `~/.claude/rules/`、`memory/`、`skills/`、`settings.json`，计算架构健康度 | JSON：`{ "architecture_health": N, "rules_issues": [...], "memory_issues": [...] }` |
| `Agent-Audit-C` | ML 审计 | 检测 Python 项目（如有），检查依赖安全、版本一致性、CUDA 兼容、类型检查 | JSON：`{ "python_health": N, "dependency_issues": [...], "type_check_status": "..." }` |

**启动方式**：单次消息内批量发送多个 `Agent` 调用。示例如下：

```
Agent({
  description: "Audit Claude Code config + memory alignment",
  prompt: "Run the mechanical audit script and the memory alignment check:\n\n# 1. Mechanical audit\npython3 ~/.agents/skills/rich-audit/scripts/rich_audit.py --output /tmp/audit-a.json\n\n# 2. Memory alignment check (L1 Phantom + L2 Missing + L3 mem0 gap)\n# L1: phantom in MEMORY.md\nphantom=0; while IFS= read -r line; do [[ \"$line\" =~ ^\\-\ \\\\[.*\\\\]\\\\((~/.claude/knowledge/cases/wiki/CASE-[^)]+)\\\\) ]] || continue; file=\"${BASH_REMATCH[1]/#\\~/$HOME}\"; [[ -f \"$file\" ]] || { echo \"[PHANTOM] $file\"; ((phantom++)); }; done < ~/.claude/memory/MEMORY.md; echo \"L1_PHANTOM=$phantom\"\n\n# L2: missing in MEMORY.md\nindexed=$(sed -n 's/.*(\\/\\/\\/.claude\\/knowledge\\/cases\\/wiki\\/(CASE-[^)]*))/\\/1/p' ~/.claude/memory/MEMORY.md | sort -u)\nfilesystem=$(ls ~/.claude/knowledge/cases/wiki/CASE-*.md 2>/dev/null | xargs -I{} basename {} | sort -u)\nmissing=$(comm -23 <(echo \"$filesystem\") <(echo \"$indexed\"))\necho \"L2_MISSING=$(echo \\\"$missing\\\" | grep -c . 2>/dev/null || echo 0)\"\n\n# L3: mem0 case drift\n# Use mcp__plugin_mem0_mem0__search_memories with query=\"CASE\" top_k=500\n# Parse result (JSON string in .result field), extract all metadata.source starting with \"CASE-\"\n# Check each against ~/.claude/knowledge/cases/wiki/ filesystem\n# Report: MEM0_CASE_COUNT, MEM0_CASE_MISSING_FILES, [MEM0_GAP] files\n\n# Read audit JSON and summarize\\nRead /tmp/audit-a.json and summarize: architecture_health score, top 3 rules_issues, top 3 memory_issues, skill_symlink mismatches, L1_PHANTOM, L2_MISSING, MEM0_CASE_COUNT, MEM0_CASE_MISSING_FILES. Return structured JSON: {architecture_health, rules_issues, memory_issues, skill_symlink, l1_phantom, l2_missing, l3_mem0_gap}."
})
Agent({
  description: "Audit Python/ML project",
  prompt: "Check if current workspace has pyproject.toml or requirements.txt. If yes, run python checks (dependency security, version consistency, CUDA compatibility, type checking) per references/python-checklist.md. Return JSON: {python_health: N, dependency_issues: [...], type_check_status: '...'}. If no Python project, return {python_health: null, skipped: true}."
})
```

**汇总规则**：
- 等待全部 Agent 返回后，合并两份 JSON
- 综合健康分 = weighted_average(8 维度加权模型)
  - architecture 25% | integrity 30% | security 20% | consistency 20%
  - github_sync 5% | timeliness 5% | redundancy 5% | performance 5%
- 脚本层使用 `_FileIndex` 统一预扫描 + `ThreadPoolExecutor(max_workers=4)` 并行执行维度，消除重复 rglob

### Layer 3 进化层 — 多源并行扫描

Layer 2 完成后，**同时启动**多个进化 Agent：

| Agent | 名称 | 职责 | 搜索关键词示例 |
|-------|------|------|----------------|
| `Agent-Evolve-1` | 配置进化 | WebSearch: Claude Code 最新最佳实践、OMC 生态更新 | `"Claude Code best practices 2026"`, `"OMC oh-my-claudecode latest"` |
| `Agent-Evolve-2` | ML 进化 | WebSearch: Python / PyTorch / ML 项目最佳实践（仅 Mode C 触发） | `"PyTorch best practices 2026"`, `"Python project structure 2026"` |
| `Agent-Evolve-3` | 文档进化 | Context7 查询：Python docs / Claude SDK docs | 使用 `mcp__context7__resolve-library-id` + `query-docs` |
**启动方式**：单次消息内批量发送多个 `Agent` 调用。示例如下：

```
Agent({
  description: "Evolve Claude Code config",
  prompt: "WebSearch: 'Claude Code best practices 2026', 'OMC oh-my-claudecode latest updates'. Also check Context7 for Claude SDK latest patterns. Compare findings against current ~/.claude/rules/ and ~/.claude/settings.json. Return: {new_knowledge: [{source, finding, recommendation}], adoptable_items: [...]}."
})
Agent({
  description: "Evolve Python/ML practices",
  prompt: "WebSearch: 'PyTorch best practices 2026', 'Python project structure 2026', 'ML engineering patterns 2026'. Only run if current workspace has Python project. Return: {new_knowledge: [...], adoptable_items: [...]}."
})
Agent({
  description: "Evolve from official docs",
  prompt: "Use mcp__context7__resolve-library-id for 'Claude SDK' and 'Python', then query-docs for latest patterns. Return: {new_knowledge: [...], adoptable_items: [...]}."
})
```

**汇总规则**：
- 收集所有 Agent 返回的 "新知识条目"
- 与当前配置逐项对比，标记：
  - `ADOPTED` — 已采纳并应用
  - `PENDING` — 待用户确认
  - `REJECTED` — 不适用或已过时
  - `NO_CHANGE` — 无新进展（仍需列出搜索证据）

### 可并行的修复子任务（Layer 2 内部并行）

Layer 2 的**优先级排序**必须基于 Layer 1 汇总结果（顺序），但**实际修复操作**可按文件类型并行拆分：

| Agent | 职责 | 并行安全性 |
|-------|------|------------|
| `Agent-Fix-Rules` | 合并重复规则、重写冲突段落、补充 Binary Assertions | 高（仅编辑 `~/.claude/rules/`） |
| `Agent-Fix-Memory` | 更新陈旧记忆引用、修复 MEMORY.md 索引 | 高（仅编辑 `~/.claude/memory/`） |
| `Agent-Fix-Skills` | 修复 skill symlink、清理 orphan | 高（仅编辑 `~/.claude/skills/` 和 `~/.agents/skills/`） |
| `Agent-Fix-Python` | 补充 README、修复 MarkupSafe 约束、添加 requires-python | 高（仅编辑工作区 Python 文件） |

```
Agent({ description: "Fix rules issues", prompt: "Read Layer 1 JSON rules_issues. Fix top 3 issues in ~/.claude/rules/ by editing files directly. Return: {fixed_files: [...], skipped: [...]}." })
Agent({ description: "Fix memory alignment issues (L1/L2/L3)", prompt: "Read Layer 1 JSON memory_issues. Fix all three alignment layers:\n\n1. L1 Phantom: 从 ~/.claude/memory/MEMORY.md 删除指向不存在文件的 entry\n2. L2 Missing: 为存在于 ~/.claude/knowledge/cases/wiki/ 但未进入 MEMORY.md 的 case 文件添加 entry（从 case 文件 frontmatter 提取 title + 首行描述）\n3. L3 mem0 Gap: 对 mem0 有 source=CASE-XXX 但文件系统无对应文件的记忆，生成 case 文件模板到 ~/.claude/knowledge/cases/wiki/CASE-XXX.md，模板包含 frontmatter + '## 症状' + '## 根因（待补充）' + '## 修复（待补充）'，通知用户补充内容\n\nReturn: {l1_fixed: N, l1_remaining: N, l2_added: N, l3_created: N, errors: [...]}." })
Agent({ description: "Fix skill symlinks", prompt: "Run: find ~/.claude/skills -maxdepth 1 -type l | while read f; do ... done. Repair broken/missing symlinks to ~/.agents/skills/. Return: {fixed: N, broken: N}." })
```

### 必须顺序执行的环节

| 环节 | 原因 |
|------|------|
| Layer 2 优先级排序 | 必须基于 Layer 1 完整汇总结果 |
| 生成进化报告 | 必须基于 Layer 2 修复结果 + Layer 3 进化结果 |
| Verification Gates | 必须在所有修改完成后执行 |

---

### Layer 3 进化层详解

进化层是区分"审计"与"自我进化"的核心。详细来源、基准和搜索策略见 [references/evolution-sources.md](references/evolution-sources.md)。

**核心约束**：无论当前健康度多少，每次 `rich审计` 都必须执行 Layer 3 外部扫描。禁止以"分数已经很高"为由跳过 WebSearch / Context7。
