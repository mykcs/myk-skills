# rich-audit

三层进化系统: **审计** (发现问题) → **修复** (解决问题) → **进化** (主动获取外部先进知识并应用).

双模审计: Claude Code 配置审计 + Python/ML 项目审计.

## 触发词

- **中文**: `rich审计` / `进化`
- **英文**: `/rich-audit` / `rich audit` / `claude 审计` / `audit claude files`

## 快速开始

```bash
# 一键 (推荐) — 根目录 Makefile
make help         # 列出所有 target
make test         # 跑 10 unittest
make audit        # 跑 7 detection scripts (Layer 1)
make modernize    # 验证 Force-All-Search + 6 维 + 8 脚本存在
make propose-fix  # dead_code → auto_fix_proposer (141 proposals, 待用户审)

# 单跑 (不进 make)
python3 ~/.agents/skills/rich-audit/scripts/dead_code_detector.py
python3 ~/.agents/skills/rich-audit/scripts/commands_to_skills_migrator.py
python3 ~/.agents/skills/rich-audit/scripts/lint_runner.py
python3 ~/.agents/skills/rich-audit/scripts/memory_audit_runner.py

# 跑测试
cd ~/.agents/skills/rich-audit && python3 -m unittest scripts.test_detection_scripts -v
```

## 版本

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **v2.6.17** | **2026-06-12** | **加 exa 为第 5 工具** (combo `mcp__exa__web_search_exa` + `mcp__exa__web_fetch_exa`, 算法/索引独立); Force-All-Search 升级 v2.7 → v2.8 (5-tool parallel fan-out) |
| **v2.6.16** | **2026-06-12** | **Tri-Search → Force-All-Search Protocol 重命名** (数字 tri=3 误导实际 4-tool); 拆降级矩阵为 Layer 1 (已注册暂不可用) / Layer 2 (未注册 fail-fast); 全局规则 `behavioral-process-trisearch.md` → `behavioral-process-forceallsearch.md` |
| v2.6.15 | 2026-06-10 | README 引用 Makefile (一键操作) |
| v2.6.14 | 2026-06-10 | 根目录 `Makefile` (test/lint/audit/modernize/propose-fix) |
| v2.6.13 | 2026-06-10 | Layer 1 真跑报告 (1007 findings, 7 detection scripts) |
| v2.6.12 | 2026-06-10 | GitHub Actions CI (`.github/workflows/rich-audit-ci.yml`) |
| v2.6.11 | 2026-06-10 | auto_fix_proposer (Level 2, 141 proposals 待用户审) |
| v2.6.10 | 2026-06-10 | B (skill_overlap_enhancer) + C (waste_token_detector) |
| v2.6.7 | 2026-06-10 | D (skill_authoring_checker) |
| v2.6.5 | 2026-06-10 | memory_audit_runner (集成 `~/.claude/scripts/memory-audit.sh`) |
| v2.6.4 | 2026-06-10 | unittest 烟测覆盖 4 个检测脚本 (6 tests) |
| v2.6.3 | 2026-06-10 | lint_runner (shellcheck + py_compile) |
| v2.6.2 | 2026-06-10 | dead-code + commands-to-skills 升级为可执行 Python 脚本 |
| v2.6.1 | 2026-06-10 | dead-code-orphan + commands-to-skills-migration detection docs |
| v2.6.0 | 2026-06-10 | [历史: 已改 Force-All-Search v2.6.17 5-tool, 2026-06-12] Tri-Search Protocol v2.6 (4-tool parallel fan-out) + consistency 6 维 |
| v2.5.0 | (历史) | 3-tool cascade + 8 维加权模型 |

## 架构

```
SKILL.md (主入口)
├── references/
│   ├── force-all-search-protocol.md   (Phase A/B/C 协议 + Layer 1/2 fail-fast, 49 行, v2.7 2026-06-12)
│   ├── consistency-6d/                (6 个子模块, 34-37 行 × 6)
│   │   ├── 1-terminology.md
│   │   ├── 2-cross-references.md
│   │   ├── 3-rule-conflicts.md
│   │   ├── 4-index-validity.md
│   │   ├── 5-frontmatter.md
│   │   └── 6-priority-scope.md
│   ├── dead-code-orphan.md            (v2.6.1+)
│   ├── commands-to-skills-migration.md (v2.6.1+)
│   ├── audit-patterns.md              (历史, 663 行)
│   ├── memory-alignment.md            (历史)
│   ├── agent-strategy.md              (历史)
│   ├── auto-fix.md                    (历史)
│   ├── verification-gates.md          (历史)
│   ├── cascade-reports.md             (历史)
│   ├── evolution-sources.md           (历史)
│   └── python-checklist.md            (历史)
└── scripts/
    ├── dead_code_detector.py          (v1.0.0, 死代码 + orphan)
    ├── commands_to_skills_migrator.py (v1.0.0, 命令→skill 迁移 + 重叠)
    ├── lint_runner.py                 (v1.0.0, shellcheck + py_compile)
    ├── memory_audit_runner.py         (v1.0.0, 集成 memory-audit.sh)
    ├── test_detection_scripts.py     (6 unittest 烟测)
    ├── rich_audit.py                  (历史主脚本, 76KB)
    └── __pycache__/                   (gitignore)
```

## 协议 (v2.8, 5-tool)

| Phase | 行为 | 工具 |
|-------|------|------|
| A. Parallel Fan-out | 5 工具**并行**同 query | `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` ∥ `exa` (`web_search_exa` + `web_fetch_exa`) |
| B. Merge + Compare | 共识 (≥3 源) / 冲突 | 内部 |
| C. Conflict Resolve | Phase A 递归 ≤2 层 | 同 A |

**输出契约 (3 字段必填)**: 工具 / 搜索内容 / 结论

**降级 (两层)**:
- Layer 1 (已注册但暂不可用): 同源替代, 报告标注
- Layer 2 (未注册 / MCP server 缺席): **fail-fast**, 报告"❌ BLOCKED: 缺失 N 个工具"; 唯一例外: 用户显式说"接受降级"

完整协议见 `references/force-all-search-protocol.md` (v2.7, 2026-06-12 重命名自 Tri-Search v2.6), 全局化在 `~/.claude/rules/behavioral-process-forceallsearch.md`.

## 测试

```bash
cd ~/.agents/skills/rich-audit && python3 -m unittest scripts.test_detection_scripts -v
```

6 tests, stdlib only (无 pytest 依赖), 覆盖 4 个检测脚本的 schema + finding types.

## License

MIT
