from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.classify_nontrivial_unsat_core_geometry import build_report


def test_nontrivial_core_geometry_flags() -> None:
    payload = build_report()
    assert payload["status"] == "ok"
    flags = payload["theorem_flags"]
    assert flags["all_cells_parallel_class_triplets"] is True
    assert flags["core_counts_match_between_agl_and_hessian"] is True
    assert flags["core_signatures_match_between_agl_and_hessian"] is True

    expected = {
        "(1,1)": 6,
        "(1,2)": 2,
        "(2,0)": 4,
        "(2,1)": 2,
        "(2,2)": 2,
    }
    for key, count in expected.items():
        assert payload["matrix"]["all_agl"][key]["minimal_core_count"] == count
        assert payload["matrix"]["hessian216"][key]["minimal_core_count"] == count
        assert (
            payload["matrix"]["all_agl"][key][
                "all_min_cores_are_parallel_class_triplets"
            ]
            is True
        )


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "core_geometry.json"
    out_md = tmp_path / "core_geometry.md"
    cmd = [
        sys.executable,
        "tools/classify_nontrivial_unsat_core_geometry.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert out_md.exists()
