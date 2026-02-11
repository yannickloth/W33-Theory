from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.global_sign_rigidity_dual_profile import build_report


def test_dual_profile_flags() -> None:
    payload = build_report(max_examples=2, top_k=4)
    assert payload["status"] == "ok"
    flags = payload["theorem_flags"]
    assert flags["nontrivial_unsat_baseline_3_in_agl_hessian"] is True
    assert flags["nontrivial_unsat_striation_4_in_agl_hessian"] is True
    assert flags["identity_positive_6_vs_5"] is True
    assert flags["identity_positive_gap_robust_under_striation"] is True
    assert flags["dual_gap_shrinks_by_one_under_striation"] is True

    derived = payload["derived"]
    assert derived["all_agl_positive_minus_negative_unconstrained"] == 3
    assert derived["all_agl_positive_minus_negative_striation_complete"] == 2
    assert derived["hessian_positive_minus_negative_unconstrained"] == 2
    assert derived["hessian_positive_minus_negative_striation_complete"] == 1


def test_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "dual.json"
    out_md = tmp_path / "dual.md"
    cmd = [
        sys.executable,
        "tools/global_sign_rigidity_dual_profile.py",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
        "--max-examples",
        "2",
        "--top-k",
        "4",
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert out_md.exists()
