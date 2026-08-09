# myk-skills convenience targets
# Validation policy lives in scripts/ci_check.py. Keep this file as a thin wrapper
# so local shortcuts cannot drift from Cloudflare or the manual GitHub fallback.

PY ?= python3

.PHONY: help check test ci cloudflare-build clean

help:
	@echo "myk-skills Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make check             run provider-neutral repository validation"
	@echo "  make test              alias for make check"
	@echo "  make ci                alias for make check"
	@echo "  make cloudflare-build  run the Cloudflare build adapter locally"
	@echo "  make clean             remove generated validation state"

check:
	$(PY) scripts/ci_check.py

test: check

ci: check

cloudflare-build:
	npm run cloudflare:build

clean:
	@find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf cloudflare-dist .wrangler
	@echo "Cleaned generated validation state"
