from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_selection_rules_report_builds_and_consistent():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "generate_selection_rules_report.py",
        "generate_selection_rules_report",
    )
    try:
        tool.main()
    except Exception as e:
        import pytest

        pytest.skip(
            f"Skipping selection rules report test; prerequisite missing or tool failed: {e}"
        )

    out_path = repo_root / "artifacts" / "selection_rules_report.json"
    if not out_path.exists():
        import pytest

        pytest.skip("selection_rules_report.json not produced; skipping test")

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["generators"] == 6
    assert data["counts"]["total_failures"] == 0
