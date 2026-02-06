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


def test_bad_triads_vs_double_sixes_universal_invariants():
    repo_root = Path(__file__).resolve().parents[1]
    # Skip if prerequisites missing
    required = [
        repo_root / "artifacts" / "selection_rules_report.json",
        repo_root / "artifacts" / "canonical_su3_gauge_and_cubic.json",
    ]
    for p in required:
        if not p.exists():
            pytest.skip(
                f"Missing upstream artifact {p.name}; skipping bad triads vs double sixes test in this environment"
            )

    tool = _load_module(
        repo_root / "tools" / "analyze_bad_triads_vs_double_sixes.py",
        "analyze_bad_triads_vs_double_sixes",
    )
    tool.main()

    out_path = repo_root / "artifacts" / "bad_triads_vs_double_sixes.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["double_sixes"] == 36
    assert data["counts"]["bad_triads"] == 9

    inv = data["invariants_over_all_double_sixes"]
    assert len(inv["bad_pattern_histograms"]) == 1
    assert len(inv["bad_rrr_pg32_type_histograms"]) == 1

    hist0 = dict(inv["bad_pattern_histograms"][0]["hist"])
    assert inv["bad_pattern_histograms"][0]["count"] == 36
    assert hist0 == {"A0B0R3": 3, "A1B1R1": 6}

    types0 = dict(inv["bad_rrr_pg32_type_histograms"][0]["types"])
    assert inv["bad_rrr_pg32_type_histograms"][0]["count"] == 36
    assert types0 == {"matching": 3}

    for row in data["per_double_six"]:
        assert row["bad_rrr_count"] == 3
        assert row["bad_pattern_hist"] == {"A0B0R3": 3, "A1B1R1": 6}
        assert row["bad_rrr_pg32_types"] == {"matching": 3}
