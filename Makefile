# myk-skills Makefile
# 一键操作 rich-audit 的所有层 (Layer 1 检测 / Lint / Test / Modernize verify / Auto-fix propose)

SKILL := rich-audit
SCRIPTS := $(SKILL)/scripts
PY := python3
SCRIPTS_LIST := dead_code_detector.py commands_to_skills_migrator.py lint_runner.py memory_audit_runner.py \
                skill_authoring_checker.py skill_overlap_enhancer.py waste_token_detector.py auto_fix_proposer.py

.PHONY: help test lint audit modernize propose-fix clean

help:
	@echo "myk-skills Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make test         run $(SKILL) unittest (10 tests)"
	@echo "  make lint         run $(SKILL) lint_runner (shellcheck + py_compile)"
	@echo "  make audit        run all 7 detection scripts (Layer 1) + aggregate"
	@echo "  make modernize    verify Tri-Search + 6d + 8 scripts present"
	@echo "  make propose-fix  run 6 detection scripts → auto_fix_proposer (Level 2)"
	@echo "  make clean        remove __pycache__"
	@echo ""
	@echo "Skill: $(SKILL) at $(SKILL)/"

test:
	@echo "▶ Running unittest (10 tests)..."
	@cd $(SKILL) && $(PY) -m unittest scripts.test_detection_scripts -v
	@echo ""
	@echo "✅ All tests pass"

lint:
	@echo "▶ Running lint_runner (shellcheck + py_compile)..."
	@$(PY) $(SCRIPTS)/lint_runner.py | $(PY) -c "import json,sys; d=json.load(sys.stdin); print('scanned:',d['scanned_sh'],'sh +',d['scanned_py'],'py'); print('findings:',d['count']); print('by_type:',d['by_type'])"

audit:
	@echo "▶ Running 7 detection scripts (Layer 1)..."
	@total=0; \
	for s in dead_code_detector commands_to_skills_migrator lint_runner memory_audit_runner \
	         skill_authoring_checker skill_overlap_enhancer waste_token_detector; do \
		echo "=== $$s ==="; \
		$(PY) $(SCRIPTS)/$$s.py | $(PY) -c "import json,sys; d=json.load(sys.stdin); c=d.get('count', d.get('migration_count', 0) + d.get('overlap_count', 0)); print('  count:', c, '  by_type:', d.get('by_type', {}))"; \
	done
	@echo ""
	@echo "✅ Layer 1 audit complete"

modernize:
	@echo "▶ Modernization check (Tri-Search + 6d + scripts)..."
	@grep -q "Tri-Search Protocol v2.6" $(SKILL)/SKILL.md || { echo "❌ Tri-Search Protocol v2.6 missing in SKILL.md"; exit 1; }
	@echo "  ✓ Tri-Search Protocol v2.6"
	@for n in 1 2 3 4 5 6; do \
		test -f $(SKILL)/references/consistency-6d/$${n}-*.md || { echo "❌ consistency-6d/$${n} missing"; exit 1; }; \
	done
	@echo "  ✓ 6 consistency sub-modules"
	@for s in $(SCRIPTS_LIST); do \
		test -f $(SCRIPTS)/$$s || { echo "❌ $$s missing"; exit 1; }; \
	done
	@echo "  ✓ 8 detection scripts"
	@echo ""
	@echo "✅ Modernization check passed"

propose-fix:
	@echo "▶ Auto-fix Level 2: 6 detection scripts → auto_fix_proposer..."
	@for s in dead_code_detector commands_to_skills_migrator lint_runner skill_authoring_checker \
	         skill_overlap_enhancer waste_token_detector; do \
		$(PY) $(SCRIPTS)/$$s.py; \
	done | $(PY) $(SCRIPTS)/auto_fix_proposer.py | $(PY) -c "import json,sys; d=json.load(sys.stdin); print('proposals:', d['count']); print('risk:', d['risk_counts']); print('needs_review:', d['requires_user_review_count']); print(''); print('Per scope discipline: NOT auto-applied. Review proposals and apply manual_steps manually.')"

clean:
	@find $(SKILL) -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned __pycache__"
