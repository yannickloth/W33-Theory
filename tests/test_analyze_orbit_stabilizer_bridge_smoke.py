from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_orbit_stabilizer_bridge_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "orbit_stabilizer_bridge.json"
    out_md = tmp_path / "orbit_stabilizer_bridge.md"
    cmd = [
        sys.executable,
        "tools/analyze_orbit_stabilizer_bridge.py",
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

    action = payload["action_model"]
    assert action["total_action_size"] == 2592

    hessian = payload["spaces"]["hessian"]
    agl = payload["spaces"]["agl"]
    assert hessian["orbit_size_histogram"] == {"1296": 11, "2592": 68}
    assert hessian["stabilizer_size_histogram"] == {"1": 68, "2": 11}
    assert agl["orbit_size_histogram"] == {"2592": 7}
    assert agl["stabilizer_size_histogram"] == {"1": 7}

    checks = payload["claim_checks"]
    assert checks["orbit_stabilizer_identity_holds_all_spaces"] is True
    assert checks["hessian_reduced_orbits_have_stabilizer_2"] is True
    assert checks["full_orbits_have_stabilizer_1"] is True
    assert checks["nontrivial_stabilizers_only_in_hessian"] is True
    assert checks["all_hessian_nontrivial_linear_parts_are_det2_order2"] is True
    assert checks["hessian_nontrivial_cycle_signatures_match_gl2_bridge"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "Orbit-Stabilizer Bridge" in text
    assert "hessian" in text
