from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "lean4.yml"


def test_lean_workflow_has_path_filters() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "paths:" in text
    assert '- "proofs/lean/**"' in text
    assert '- ".github/workflows/lean4.yml"' in text


def test_lean_workflow_has_cache_and_mathlib_cache_get() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache@v4" in text
    assert "lake exe cache get" in text
    assert "concurrency:" in text
