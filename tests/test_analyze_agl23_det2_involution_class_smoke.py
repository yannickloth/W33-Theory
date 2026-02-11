from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_agl23_det2_involution_class_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "agl23_det2_inv.json"
    out_md = tmp_path / "agl23_det2_inv.md"
    cmd = [
        sys.executable,
        "tools/analyze_agl23_det2_involution_class.py",
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

    inv = payload["det2_involutions"]
    assert inv["candidate_count"] == 36
    assert inv["conjugacy_class_count"] == 1
    assert inv["class_sizes"] == [36]

    cent = inv["centralizer"]
    assert cent["size"] == 12
    assert cent["order_histogram"] == {"1": 1, "2": 7, "3": 2, "6": 2}
    assert cent["matches_d12_fingerprint"] is True

    rep = inv["representative"]
    assert rep["point_cycle_signature"] == [1, 1, 1, 2, 2, 2]
    assert rep["line_cycle_signature"] == [1, 1, 1, 1, 2, 2, 2, 2]
    assert len(rep["fixed_points"]) == 3
    assert len(rep["fixed_lines"]) == 4

    fiber = inv["fixed_point_line_fiber"]
    assert fiber["distinct_fixed_lines"] == 12
    assert fiber["uniform_count_is_three"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "AGL(2,3) det=2 Involution Class" in text
