from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_derive_reduced_orbit_closed_form_smoke(tmp_path: Path):
    out_json = tmp_path / "reduced_rule.json"
    out_md = tmp_path / "reduced_rule.md"
    cmd = [
        sys.executable,
        "tools/derive_reduced_orbit_closed_form.py",
        "--in-json",
        "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert out_json.exists()
    dd = json.loads(out_json.read_text(encoding="utf-8"))
    assert dd.get("status") == "ok"
    # We expect a candidate involution-based rule to be found for the current dataset
    assert dd.get("rule_holds") is True
    assert dd.get("matched_by_involution_count", 0) >= dd.get(
        "reduced_representative_count", 0
    )
