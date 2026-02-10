from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_report_min_cert_census_smoke(tmp_path: Path):
    # Input artifacts
    inputs = [
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json"
        ),
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json"
        ),
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k_with_geotypes.json"
        ),
    ]
    inputs_exist = [p for p in inputs if p.exists()]
    if not inputs_exist:
        import pytest

        pytest.skip(
            "classification artifacts missing; run tools/classify_canonical_reps.py first"
        )

    out_md = tmp_path / "MIN_CERT_ORBIT_CENSUS_TEST.md"
    out_dir = tmp_path / "report_dir"

    cmd = (
        [
            sys.executable,
            "tools/report_min_cert_census.py",
            "--out-md",
            str(out_md),
            "--out-dir",
            str(out_dir),
        ]
        + ["--in-json"]
        + [str(p) for p in inputs_exist]
    )

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert out_md.exists()
    # check at least one figure exists
    figs = list((out_dir / "figures").glob("*.png"))
    assert len(figs) >= 1
