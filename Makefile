.DEFAULT_GOAL := help
.PHONY: bootstrap doctor audit full-audit browser-audit generate-summary test check-json verify-root-edge build-pdf

PYTHON ?= python3

help:
	@printf '%s\n' \
	"bootstrap           Create/reuse .venv and install requirements-dev.txt" \
	"doctor              Check dependencies, heavy data resolution, and repo hygiene" \
	"audit               Classify dirty worktree entries without modifying anything" \
	"full-audit          Run doctor, cleanup audit, and browser audit together" \
	"browser-audit       Run desktop/mobile browser audit over docs pages" \
	"generate-summary    Refresh summary artifacts" \
	"test                Run pytest after summary generation" \
	"check-json          Run JSON-safety checks" \
	"verify-root-edge    Verify root-edge mapping script" \
	"build-pdf           Build the PDF surface"

bootstrap:
	./scripts/bootstrap_repo_env.sh

doctor:
	$(PYTHON) tools/repo_doctor.py

audit:
	$(PYTHON) tools/repo_cleanup_audit.py

full-audit:
	$(PYTHON) tools/repo_doctor.py
	$(PYTHON) tools/repo_cleanup_audit.py
	$(PYTHON) tools/browser_docs_audit.py

browser-audit:
	$(PYTHON) tools/browser_docs_audit.py

generate-summary:
	python scripts/collect_results.py
	python scripts/make_numeric_comparisons_from_summary.py || true

# Run tests after generating summary artifacts
test: generate-summary
	pytest -q

check-json:
	python -m pytest -q tests/test_json_serialization.py tests/test_json_safe.py -q

verify-root-edge:
	./scripts/verify_root_edge_mapping.sh

build-pdf:
	./scripts/build_toe_pdf.sh

prepare-w33-bundle:
	python tools/prepare_w33_analysis_bundle.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --out-dir analysis/w33_bundle_temp --v0 0
