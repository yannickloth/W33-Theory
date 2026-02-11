from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_reduced_rep_stabilizer_outliers_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "outliers.json"
    out_md = tmp_path / "outliers.md"
    cmd = [
        sys.executable,
        "tools/analyze_reduced_rep_stabilizer_outliers.py",
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

    # Full histogram matches the census.
    assert payload["z_map_histogram_all_reduced"] == {
        "[1, 0]": 49,
        "[2, 0]": 5,
        "[2, 1]": 1,
    }
    assert payload["outlier_z_map_histogram"] == {"[2, 0]": 5, "[2, 1]": 1}

    outliers = payload["outliers"]
    assert len(outliers) == 6
    assert sum(1 for o in outliers if o["stabilizer"]["z_map"] == [2, 0]) == 5
    assert sum(1 for o in outliers if o["stabilizer"]["z_map"] == [2, 1]) == 1

    # Every outlier has at least one fixed row, and reconstruction works.
    assert all(len(o["fixed_rows"]) >= 1 for o in outliers)
    assert all(o["stabilizer"]["reconstruction_matches"] is True for o in outliers)

    text = out_md.read_text(encoding="utf-8")
    assert "Reduced-Rep Stabilizer Outliers" in text
