from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_gl2_f3_involution_conjugacy_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "gl2_f3_conjugacy.json"
    out_md = tmp_path / "gl2_f3_conjugacy.md"
    cmd = [
        sys.executable,
        "tools/analyze_gl2_f3_involution_conjugacy.py",
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

    group = payload["group_counts"]
    assert group["gl2_3_size"] == 48
    assert group["det2_order2_involution_count"] == 12
    assert group["diag_centralizer_size"] == 4
    assert group["class_size_from_orbit_stabilizer"] == 12

    conj = payload["conjugacy"]
    assert conj["all_candidates_conjugate_to_diag"] is True
    assert conj["uniform_conjugator_count_set"] == [4]

    graph = payload["graph_action_profile"]
    assert graph["unique_point_cycle_signatures"] == [[1, 1, 1, 2, 2, 2]]
    assert graph["unique_line_cycle_signatures"] == [[1, 1, 1, 1, 2, 2, 2, 2]]
    assert graph["all_point_signatures_match_expected"] is True
    assert graph["all_line_signatures_match_expected"] is True
    assert payload["claim_holds"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "GL(2,3) Involution Conjugacy Bridge" in text
    assert "Graph Profile" in text
