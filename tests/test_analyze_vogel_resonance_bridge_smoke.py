from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_vogel_resonance_bridge_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "vogel_resonance_bridge.json"
    out_md = tmp_path / "vogel_resonance_bridge.md"
    cmd = [
        sys.executable,
        "tools/analyze_vogel_resonance_bridge.py",
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
    assert payload["target_nearest_vogel_hits"]["grade0"]["nearest"]["hit_dim"] == 248
    assert (
        payload["target_nearest_vogel_hits"]["quotient_by_grade0"]["nearest"]["hit_dim"]
        == 484
    )
    assert (
        payload["target_nearest_vogel_hits"]["total_nonzero"]["nearest"]["hit_dim"]
        == 782
    )
    checks = payload["resonance_checks"]
    assert checks["grade0_gap_abs_equals_jacobi_failure_count"] is True
    assert checks["quotient_gap_abs_equals_nonzero_grade_count"] is True
    assert checks["total_gap_abs_equals_2x_checked_grade_triples"] is True
    assert checks["total_nearest_integral_root_matches_a_family_rank"] is True
    assert checks["grade0_nearest_direct_hit_contains_E8"] is True

    orbit = payload["orbit_bridge"]
    assert orbit["block_size_r_from_grade1_equals_3r2"] == 9
    assert orbit["r_squared"] == 81
    assert orbit["all_orbits_multiple_of_r_squared"] is True
    assert orbit["all_integer_factors_power_of_two"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "Vogel Resonance Bridge" in text
    assert "Nearest Vogel Hits" in text
