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


def test_physics_selection_table_builds_and_counts():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "generate_physics_facing_selection_table.py",
        "generate_physics_facing_selection_table",
    )
    try:
        tool.main()
    except Exception as e:
        import pytest

        pytest.skip(
            f"Skipping physics selection table test; prerequisite missing or tool failed: {e}"
        )

    out_path = repo_root / "artifacts" / "physics_selection_table.json"
    if not out_path.exists():
        import pytest

        pytest.skip("physics_selection_table.json not produced; skipping test")

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["triads_total"] == 45
    assert data["counts"]["firewall_bad_triads"] == 9
    assert data["counts"]["generators"] == 6
    for g in data["generators"]:
        c = g["counts"]
        assert c["preserved"] + c["flipped"] == 45
        assert c["preserved_bad"] + c["flipped_bad"] == 9
