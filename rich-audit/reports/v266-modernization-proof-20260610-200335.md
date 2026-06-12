> ⚠️ [历史快照] 本报告/文档中 "Tri-Search Protocol v2.6" 已于 2026-06-12 重命名为 "Force-All-Search Protocol v2.7"; 保留原命名作为 audit trail.
# rich-audit v2.6.6 现代化实测报告

> 跑于: 2026-06-10 20:03:35
> 范围: `~/.claude/` + `~/.agents/`
> 工具: 4 个 v2.6.2-2.6.5 检测脚本 + 6 个 unittest

## 1. 检测脚本实跑结果

## 1.dead_code_detector

```json
{
  "tool": "dead_code_detector.py",
  "version": "1.0.0",
  "scope": "/Users/myk/.claude",
  "count": 139,
  "by_type": {
    "orphan_case": 17,
    "dead_hook": 2,
    "dead_script": 21,
    "orphan_skill": 99
  },
  "findings_sample": [
    {
      "type": "orphan_case",
      "path": ".claude/knowledge/cases/wiki/CASE-098-usage-report-verification-20260527.md"
    },
    {
      "type": "orphan_case",
      "path": ".claude/knowledge/cases/wiki/CASE-ts-check-hook-missing-20260423.md"
    },
    {
      "type": "orphan_case",
      "path": ".claude/knowledge/cases/wiki/CASE-dotfile-cleanup-20260422.md"
    }
  ],
  "migration_candidates_sample": null,
  "skill_overlaps_sample": null
}
```

## 1.commands_to_skills_migrator

```json
{
  "tool": "commands_to_skills_migrator.py",
  "version": "1.0.0",
  "scope_commands": "/Users/myk/.claude/commands",
  "scope_skills": "/Users/myk/.agents/skills",
  "migration_candidates": [
    {
      "type": "migration_candidate",
      "command": "commands/santa-loop.md",
      "name": "santa-loop",
      "body_lines": 175,
      "target_path": "~/.agents/skills/santa-loop/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/quality-gate.md",
      "name": "quality-gate",
      "body_lines": 29,
      "target_path": "~/.agents/skills/quality-gate/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/rust-review.md",
      "name": "rust-review",
      "body_lines": 142,
      "target_path": "~/.agents/skills/rust-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prompt-optimize.md",
      "name": "prompt-optimize",
      "body_lines": 38,
      "target_path": "~/.agents/skills/prompt-optimize/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/rust-build.md",
      "name": "rust-build",
      "body_lines": 187,
      "target_path": "~/.agents/skills/rust-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/jira.md",
      "name": "jira",
      "body_lines": 106,
      "target_path": "~/.agents/skills/jira/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/instinct-export.md",
      "name": "instinct-export",
      "body_lines": 66,
      "target_path": "~/.agents/skills/instinct-export/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/gan-design.md",
      "name": "gan-design",
      "body_lines": 35,
      "target_path": "~/.agents/skills/gan-design/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prune.md",
      "name": "prune",
      "body_lines": 31,
      "target_path": "~/.agents/skills/prune/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/kotlin-build.md",
      "name": "kotlin-build",
      "body_lines": 174,
      "target_path": "~/.agents/skills/kotlin-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/learn.md",
      "name": "learn",
      "body_lines": 70,
      "target_path": "~/.agents/skills/learn/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/e2e.md",
      "name": "e2e",
      "body_lines": 365,
      "target_path": "~/.agents/skills/e2e/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/loop-start.md",
      "name": "loop-start",
      "body_lines": 32,
      "target_path": "~/.agents/skills/loop-start/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/flutter-review.md",
      "name": "flutter-review",
      "body_lines": 116,
      "target_path": "~/.agents/skills/flutter-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prp-pr.md",
      "name": "prp-pr",
      "body_lines": 184,
      "target_path": "~/.agents/skills/prp-pr/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/claw.md",
      "name": "claw",
      "body_lines": 51,
      "target_path": "~/.agents/skills/claw/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/kotlin-test.md",
      "name": "kotlin-test",
      "body_lines": 312,
      "target_path": "~/.agents/skills/kotlin-test/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/harness-audit.md",
      "name": "harness-audit",
      "body_lines": 71,
      "target_path": "~/.agents/skills/harness-audit/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/gan-build.md",
      "name": "gan-build",
      "body_lines": 99,
      "target_path": "~/.agents/skills/gan-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/devfleet.md",
      "name": "devfleet",
      "body_lines": 92,
      "target_path": "~/.agents/skills/devfleet/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/cpp-build.md",
      "name": "cpp-build",
      "body_lines": 173,
      "target_path": "~/.agents/skills/cpp-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/flutter-test.md",
      "name": "flutter-test",
      "body_lines": 144,
      "target_path": "~/.agents/skills/flutter-test/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/loop-status.md",
      "name": "loop-status",
      "body_lines": 24,
      "target_path": "~/.agents/skills/loop-status/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/kotlin-review.md",
      "name": "kotlin-review",
      "body_lines": 140,
      "target_path": "~/.agents/skills/kotlin-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/eval.md",
      "name": "eval",
      "body_lines": 120,
      "target_path": "~/.agents/skills/eval/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/verify.md",
      "name": "verify",
      "body_lines": 59,
      "target_path": "~/.agents/skills/verify/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/test-coverage.md",
      "name": "test-coverage",
      "body_lines": 69,
      "target_path": "~/.agents/skills/test-coverage/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/multi-frontend.md",
      "name": "multi-frontend",
      "body_lines": 158,
      "target_path": "~/.agents/skills/multi-frontend/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/build-fix.md",
      "name": "build-fix",
      "body_lines": 62,
      "target_path": "~/.agents/skills/build-fix/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prp-prd.md",
      "name": "prp-prd",
      "body_lines": 447,
      "target_path": "~/.agents/skills/prp-prd/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/instinct-import.md",
      "name": "instinct-import",
      "body_lines": 114,
      "target_path": "~/.agents/skills/instinct-import/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/setup-pm.md",
      "name": "setup-pm",
      "body_lines": 80,
      "target_path": "~/.agents/skills/setup-pm/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/update-docs.md",
      "name": "update-docs",
      "body_lines": 84,
      "target_path": "~/.agents/skills/update-docs/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/save-session.md",
      "name": "save-session",
      "body_lines": 275,
      "target_path": "~/.agents/skills/save-session/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/cpp-test.md",
      "name": "cpp-test",
      "body_lines": 251,
      "target_path": "~/.agents/skills/cpp-test/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/projects.md",
      "name": "projects",
      "body_lines": 39,
      "target_path": "~/.agents/skills/projects/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/refactor-clean.md",
      "name": "refactor-clean",
      "body_lines": 80,
      "target_path": "~/.agents/skills/refactor-clean/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prp-plan.md",
      "name": "prp-plan",
      "body_lines": 502,
      "target_path": "~/.agents/skills/prp-plan/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/checkpoint.md",
      "name": "checkpoint",
      "body_lines": 74,
      "target_path": "~/.agents/skills/checkpoint/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/skill-health.md",
      "name": "skill-health",
      "body_lines": 51,
      "target_path": "~/.agents/skills/skill-health/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prp-implement.md",
      "name": "prp-implement",
      "body_lines": 385,
      "target_path": "~/.agents/skills/prp-implement/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/tdd.md",
      "name": "tdd",
      "body_lines": 328,
      "target_path": "~/.agents/skills/tdd/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/instinct-status.md",
      "name": "instinct-status",
      "body_lines": 59,
      "target_path": "~/.agents/skills/instinct-status/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/rules-distill.md",
      "name": "rules-distill",
      "body_lines": 20,
      "target_path": "~/.agents/skills/rules-distill/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/prp-commit.md",
      "name": "prp-commit",
      "body_lines": 112,
      "target_path": "~/.agents/skills/prp-commit/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/go-review.md",
      "name": "go-review",
      "body_lines": 148,
      "target_path": "~/.agents/skills/go-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/learn-eval.md",
      "name": "learn-eval",
      "body_lines": 116,
      "target_path": "~/.agents/skills/learn-eval/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/flutter-build.md",
      "name": "flutter-build",
      "body_lines": 164,
      "target_path": "~/.agents/skills/flutter-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/multi-execute.md",
      "name": "multi-execute",
      "body_lines": 315,
      "target_path": "~/.agents/skills/multi-execute/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/code-review.md",
      "name": "code-review",
      "body_lines": 40,
      "target_path": "~/.agents/skills/code-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/evolve.md",
      "name": "evolve",
      "body_lines": 178,
      "target_path": "~/.agents/skills/evolve/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/sessions.md",
      "name": "sessions",
      "body_lines": 333,
      "target_path": "~/.agents/skills/sessions/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/plan.md",
      "name": "plan",
      "body_lines": 115,
      "target_path": "~/.agents/skills/plan/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/rust-test.md",
      "name": "rust-test",
      "body_lines": 308,
      "target_path": "~/.agents/skills/rust-test/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/promote.md",
      "name": "promote",
      "body_lines": 41,
      "target_path": "~/.agents/skills/promote/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/multi-workflow.md",
      "name": "multi-workflow",
      "body_lines": 191,
      "target_path": "~/.agents/skills/multi-workflow/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/docs.md",
      "name": "docs",
      "body_lines": 31,
      "target_path": "~/.agents/skills/docs/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/go-build.md",
      "name": "go-build",
      "body_lines": 183,
      "target_path": "~/.agents/skills/go-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/orchestrate.md",
      "name": "orchestrate",
      "body_lines": 231,
      "target_path": "~/.agents/skills/orchestrate/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/multi-backend.md",
      "name": "multi-backend",
      "body_lines": 158,
      "target_path": "~/.agents/skills/multi-backend/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/resume-session.md",
      "name": "resume-session",
      "body_lines": 155,
      "target_path": "~/.agents/skills/resume-session/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/aside.md",
      "name": "aside",
      "body_lines": 164,
      "target_path": "~/.agents/skills/aside/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/go-test.md",
      "name": "go-test",
      "body_lines": 268,
      "target_path": "~/.agents/skills/go-test/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/multi-plan.md",
      "name": "multi-plan",
      "body_lines": 268,
      "target_path": "~/.agents/skills/multi-plan/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/cpp-review.md",
      "name": "cpp-review",
      "body_lines": 132,
      "target_path": "~/.agents/skills/cpp-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/pm2.md",
      "name": "pm2",
      "body_lines": 272,
      "target_path": "~/.agents/skills/pm2/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/update-codemaps.md",
      "name": "update-codemaps",
      "body_lines": 72,
      "target_path": "~/.agents/skills/update-codemaps/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/gradle-build.md",
      "name": "gradle-build",
      "body_lines": 70,
      "target_path": "~/.agents/skills/gradle-build/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/python-review.md",
      "name": "python-review",
      "body_lines": 297,
      "target_path": "~/.agents/skills/python-review/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/skill-create.md",
      "name": "skill-create",
      "body_lines": 174,
      "target_path": "~/.agents/skills/skill-create/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/context-budget.md",
      "name": "context-budget",
      "body_lines": 23,
      "target_path": "~/.agents/skills/context-budget/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/model-route.md",
      "name": "model-route",
      "body_lines": 26,
      "target_path": "~/.agents/skills/model-route/SKILL.md"
    }
  ],
  "skill_overlaps": [],
  "migration_count": 72,
  "overlap_count": 0,
  "findings_sample": [],
  "migration_candidates_sample": [
    {
      "type": "migration_candidate",
      "command": "commands/santa-loop.md",
      "name": "santa-loop",
      "body_lines": 175,
      "target_path": "~/.agents/skills/santa-loop/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/quality-gate.md",
      "name": "quality-gate",
      "body_lines": 29,
      "target_path": "~/.agents/skills/quality-gate/SKILL.md"
    },
    {
      "type": "migration_candidate",
      "command": "commands/rust-review.md",
      "name": "rust-review",
      "body_lines": 142,
      "target_path": "~/.agents/skills/rust-review/SKILL.md"
    }
  ],
  "skill_overlaps_sample": []
}
```

## 1.lint_runner

```json
{
  "tool": "lint_runner.py",
  "version": "1.0.0",
  "scanned_sh": 28,
  "scanned_py": 17,
  "count": 19,
  "by_type": {
    "shellcheck": 19
  },
  "findings_sample": [
    {
      "type": "shellcheck",
      "path": ".claude/scripts/hot-facts-drift-check.sh",
      "line": 47,
      "col": 53,
      "code": 2016,
      "level": "info",
      "message": "Expressions don't expand in single quotes, use double quotes for that."
    },
    {
      "type": "shellcheck",
      "path": ".claude/scripts/hot-facts-drift-check.sh",
      "line": 48,
      "col": 51,
      "code": 2016,
      "level": "info",
      "message": "Expressions don't expand in single quotes, use double quotes for that."
    },
    {
      "type": "shellcheck",
      "path": ".claude/scripts/hot-facts-drift-check.sh",
      "line": 74,
      "col": 7,
      "code": 2001,
      "level": "style",
      "message": "See if you can use ${variable//search/replace} instead."
    }
  ],
  "migration_candidates_sample": null,
  "skill_overlaps_sample": null
}
```

## 1.memory_audit_runner

```json
{
  "tool": "memory_audit_runner.py",
  "version": "1.0.0",
  "exit_code": 0,
  "result_line": "✅ MEMORY.md is consistent",
  "summary_pass": true,
  "missing_files_count": 0,
  "findings_sample": [],
  "migration_candidates_sample": null,
  "skill_overlaps_sample": null
}
```


## 2. unittest 测试结果

......
----------------------------------------------------------------------
Ran 6 tests in 95.814s

OK

## 3. v2.5.0 vs v2.6.6 检测能力对比

| 检测维度 | v2.5.0 (旧) | v2.6.6 (新) | 提升 |
|---------|-----------|-----------|------|
| 死 hooks | 无 | 2 | NEW |
| 死 scripts | 无 | 21 | NEW |
| Orphan case files | 部分 (consolidated case) | 17 | 精确化 |
| Orphan skills | 无 | 99 | NEW |
| Commands → Skills 迁移候选 | 无 | 72 | NEW |
| Skill trigger 重叠 | 无 | 0 (干净) | NEW |
| Shellcheck 集成 | 无 | 19 | NEW (per `~/.claude/rules/behavioral-core.md` 硬规则) |
| Python 编译验证 | 无 | 0 errors | NEW |
| Memory-audit.sh 集成 | 手动 | 自动 JSON 输出 | 自动化 |
| Tri-Search Protocol | 3-tool cascade | 4-tool parallel + merge+compare | 加 WebFetch 全文验证 |

## 4. Git 状态 (5 commits pushed)

d2f6748 feat(rich-audit): v2.3.0 fix orphan detection FP — scan memory/ + knowledge/cases/
bd7af2f feat(rich-audit): v2.6.6 add README.md (Agent Skills open standard)
79b7928 feat(rich-audit): v2.6.5 add memory_audit_runner.py + extend tests
9a12374 feat(rich-audit): v2.6.4 add unittest smoke tests for 3 detection scripts
fbd8b5d feat(rich-audit): v2.6.3 add lint_runner.py (shellcheck + py_compile)
1517e0e feat(rich-audit): v2.6.2 implement dead-code-orphan + commands-to-skills-migrator as runnable scripts
24f0b21 feat(rich-audit): v2.6.1 add dead-code-orphan + commands-to-skills-migration detection
