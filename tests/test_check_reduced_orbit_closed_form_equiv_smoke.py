from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_check_reduced_orbit_closed_form_equiv_smoke(tmp_path: Path):
    out_json = tmp_path / "equiv.json"
    cmd = [
        sys.executable,
        "tools/check_reduced_orbit_closed_form_equiv.py",
        "--in-json",
        "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
        "--sign-map-json",
        "artifacts/e6_f3_trilinear_map.json",
        "--out-json",
        str(out_json),
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert out_json.exists()
    dd = json.loads(out_json.read_text(encoding="utf-8"))
    assert dd.get("status") == "ok"
    assert dd.get("z_map_mode") == "involutions"
    assert dd.get("equivalent") is True
    assert dd.get("mismatch_count") == 0
    assert dd.get("match_count_histogram") == {"0": 201, "1": 55}
    assert dd.get("all_zmaps_equivalent") is True
    assert dd.get("all_zmaps_mismatch_count") == 0
    assert dd.get("zmap_restriction_holds") is True
    assert dd.get("observed_matching_z_maps") == ["(1, 0)", "(2, 0)", "(2, 1)"]

    profile = dd.get("symmetry_profile", {})
    assert profile.get("full_orbit_all_zero_matches") is True
    assert profile.get("reduced_orbit_all_positive_matches") is True
    assert profile.get("reduced_orbit_all_exactly_one_match") is True
    assert profile.get("strict_profile_holds") is True

    # New: verify pulled-back matrices were observed and are conjugate to diag(-1,1)
    assert dd.get("pulled_back_matrix_count", 0) > 0
    for rec in dd.get("pulled_back_matrices", []):
        assert (
            rec.get("conjugate_to_diag") is True
        ), f"Matrix not conjugate to diag: {rec}"

    # Cross-check with all affine z-maps enabled: profile and z-map restriction
    # should stay unchanged on the exhaustive Hessian dataset.
    out_json_all = tmp_path / "equiv_all_zmaps.json"
    cmd_all = [
        sys.executable,
        "tools/check_reduced_orbit_closed_form_equiv.py",
        "--z-map-mode",
        "all",
        "--in-json",
        "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
        "--out-json",
        str(out_json_all),
    ]
    rr = subprocess.run(
        cmd_all, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert rr.returncode == 0, rr.stderr
    dd_all = json.loads(out_json_all.read_text(encoding="utf-8"))
    assert dd_all.get("z_map_mode") == "all"
    assert dd_all.get("equivalent") is True
    assert dd_all.get("all_zmaps_equivalent") is True
    assert dd_all.get("match_count_histogram") == {"0": 201, "1": 55}
    assert dd_all.get("zmap_restriction_holds") is True
    assert dd_all.get("observed_matching_z_maps") == ["(1, 0)", "(2, 0)", "(2, 1)"]
