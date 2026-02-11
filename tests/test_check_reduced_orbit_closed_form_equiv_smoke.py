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
    assert dd.get("equivalent") is True
    assert dd.get("mismatch_count") == 0

    # New: verify pulled-back matrices were observed and are conjugate to diag(-1,1)
    assert dd.get("pulled_back_matrix_count", 0) > 0
    for rec in dd.get("pulled_back_matrices", []):
        assert (
            rec.get("conjugate_to_diag") is True
        ), f"Matrix not conjugate to diag: {rec}"
