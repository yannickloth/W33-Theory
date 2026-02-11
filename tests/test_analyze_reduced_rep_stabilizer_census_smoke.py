from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_reduced_rep_stabilizer_census_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "reduced_rep_stabilizer_census.json"
    out_md = tmp_path / "reduced_rep_stabilizer_census.md"
    cmd = [
        sys.executable,
        "tools/analyze_reduced_rep_stabilizer_census.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    assert out_json.exists()
    assert out_md.exists()

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload.get("status") == "ok"
    assert payload.get("claim_holds") is True
    assert payload["reduced_rep_count"] == 55
    assert payload["stabilizer_found_count_histogram"] == {"1": 55}
    assert payload["z_map_histogram"] == {
        "[1, 0]": 49,
        "[2, 0]": 5,
        "[2, 1]": 1,
    }
    assert payload["fixed_witness_row_count_histogram"] == {"1": 8, "3": 26, "5": 21}
    assert payload["claim_checks"]["zmap_22_absent"] is True
    assert payload["claim_checks"]["axis_type_ne_striation_type"] is True
    assert payload["fixed_striation_type_histogram"] == {
        "x": 34,
        "y": 5,
        "y=1x": 7,
        "y=2x": 9,
    }
    assert (
        payload["cross_tabs"]["axis_type_vs_fixed_striation_type"]["['y=1x', 'x']"]
        == 16
    )
    assert payload["cross_tabs"]["z_map_vs_fixed_striation_type"]["[[1, 0], 'x']"] == 33

    text = out_md.read_text(encoding="utf-8")
    assert "Reduced-Rep Stabilizer Census" in text
