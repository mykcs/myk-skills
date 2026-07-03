## v2.6.2+ 新增检测脚本 (2026-06-10)

3 个可执行 Python 脚本, Layer 1 模式 A 直接调用, 输出 JSON findings:

| 脚本 | 版本 | 检测对象 | 输出字段 |
|------|------|---------|---------|
| [`scripts/dead_code_detector.py`](scripts/dead_code_detector.py) | v1.0.0 | 死 hooks / 死 scripts / orphan cases / orphan skills | `by_type` 分组 |
| [`scripts/commands_to_skills_migrator.py`](scripts/commands_to_skills_migrator.py) | v1.0.0 | 旧 commands 迁移候选 + skill trigger 重叠 | `migration_count` + `overlap_count` |
| [`scripts/lint_runner.py`](scripts/lint_runner.py) | v1.0.0 | shellcheck (.sh) + py_compile (.py) on scripts/ 跟 hooks/ | `by_type` 分组 (per `~/.claude/rules/behavioral-core.md` shellcheck 硬规则) |
| [`scripts/memory_audit_runner.py`](scripts/memory_audit_runner.py) | v1.0.0 | 调用 `~/.claude/scripts/memory-audit.sh` 并解析输出 | `summary_pass` + `missing_files_count` |
| [`scripts/skill_authoring_checker.py`](scripts/skill_authoring_checker.py) | v1.0.0 | per `platform.claude.com/docs/.../agent-skills/best-practices` (v2.6.7): frontmatter 完整性 + 简洁性 + description 质量 + semver | `by_type` 分组 (5 类) |
| [`scripts/skill_overlap_enhancer.py`](scripts/skill_overlap_enhancer.py) | v1.0.0 | B (v2.6.10): trigger 前缀重叠 (≥3 共享) + description Jaccard 相似度 (≥0.3) | `by_type` 分组 (2 类) |
| [`scripts/waste_token_detector.py`](scripts/waste_token_detector.py) | v1.0.0 | C (v2.6.10): hot path >1500 tokens + skill 太重 + stale >30 天 | `by_type` 分组 (3 类) + `total_hot_path_tokens` |
| [`scripts/auto_fix_proposer.py`](scripts/auto_fix_proposer.py) | v1.0.0 | Auto-fix Level 2 (v2.6.11): stdin 接收 findings JSON, 生成 risk 分级提议, **不自动应用** | `risk_counts` + `requires_user_review_count` |

**用法**:
```bash
python3 ~/.agents/skills/rich-audit/scripts/dead_code_detector.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('count:',d['count']); print('by_type:',d['by_type'])"
python3 ~/.agents/skills/rich-audit/scripts/commands_to_skills_migrator.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('migration:',d['migration_count'],'overlap:',d['overlap_count'])"
python3 ~/.agents/skills/rich-audit/scripts/lint_runner.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('scanned:',d['scanned_sh'],'sh+',d['scanned_py'],'py'); print('count:',d['count']); print('by_type:',d['by_type'])"
python3 ~/.agents/skills/rich-audit/scripts/memory_audit_runner.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('pass:',d.get('summary_pass'),'missing:',d.get('missing_files_count'))"
python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('scanned:',d['skills_scanned'],'findings:',d['count']); print('by_type:',d['by_type'])"
python3 ~/.agents/skills/rich-audit/scripts/skill_overlap_enhancer.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('count:',d['count'],'by_type:',d['by_type'])"
python3 ~/.agents/skills/rich-audit/scripts/waste_token_detector.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('count:',d['count'],'hot_path_tokens:',d['total_hot_path_tokens']); print('by_type:',d['by_type'])"
# auto_fix Level 2 提议 (per scope discipline: 不自动应用, 仅生成)
python3 ~/.agents/skills/rich-audit/scripts/dead_code_detector.py | python3 ~/.agents/skills/rich-audit/scripts/auto_fix_proposer.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('proposals:',d['count'],'risk:',d['risk_counts'],'needs_review:',d['requires_user_review_count'])"
```

**实测 (2026-06-10)**:
- `dead_code_detector.py`: 141 findings (17 orphan_case + 2 dead_hook + 23 dead_script + 99 orphan_skill)
- `commands_to_skills_migrator.py`: 72 migration candidates + 0 overlaps
- `lint_runner.py`: 19 shellcheck findings (28 .sh + 17 .py scanned, 0 py errors)
- `memory_audit_runner.py`: ✅ pass (0 missing files)
- `skill_authoring_checker.py`: 690 findings (129 skills scanned; 621 missing_field + 31 body_long + 17 desc_short + 21 missing_skill_md)
- `skill_overlap_enhancer.py`: 47 findings (9 prefix_overlap + 38 description_overlap)
- `waste_token_detector.py`: 38 findings (1 hot_path_heavy + 37 skill_too_heavy) + 20097 hot path tokens
- `auto_fix_proposer.py`: 141 proposals (18 low + 121 medium + 2 high risk, 141 需用户 review)

**测试 (v2.6.4, 5 个 unittest)**:
```bash
cd ~/.agents/skills/rich-audit && python3 -m unittest scripts.test_detection_scripts -v
```

详见 `references/dead-code-orphan.md` 跟 `references/commands-to-skills-migration.md`.

---
