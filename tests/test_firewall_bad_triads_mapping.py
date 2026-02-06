from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_firewall_bad_triads_map_to_9_of_45():
    repo_root = Path(__file__).resolve().parents[1]
    # Skip if upstream artifacts not present (CI-friendly)
    required = [
        repo_root / "artifacts" / "selection_rules_report.json",
        repo_root / "artifacts" / "we6_signed_action_on_27.json",
        repo_root / "artifacts" / "canonical_su3_gauge_and_cubic.json",
    ]
    for p in required:
        if not p.exists():
            pytest.skip(
                f"Missing upstream artifact {p.name}; skipping firewall mapping test in this environment"
            )

    tool = _load_module(
        repo_root / "tools" / "map_firewall_bad_triangles_to_cubic_triads.py",
        "map_firewall_bad_triangles_to_cubic_triads",
    )
    tool.main()
    out_path = repo_root / "artifacts" / "firewall_bad_triads_mapping.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["bad_triangles"] == 9
    assert data["counts"]["triads_total"] == 45
    assert len(data["bad_triangles_Schlafli_e6id"]) == 9
