from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_make_min_cert_gallery_smoke(tmp_path: Path):
    candidates = [
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json"
        ),
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json"
        ),
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k_with_geotypes.json"
        ),
    ]
    inputs = [str(p) for p in candidates if p.exists()]
    if not inputs:
        import pytest

        pytest.skip(
            "classification artifacts missing; run tools/classify_canonical_reps.py first"
        )

    out_md = tmp_path / "GALLERY_TEST.md"
    out_dir = tmp_path / "gallery_out"

    cmd = (
        [
            sys.executable,
            "tools/make_min_cert_gallery.py",
            "--out-md",
            str(out_md),
            "--out-dir",
            str(out_dir),
            "--per-dataset",
            "3",
        ]
        + ["--in-json"]
        + inputs
    )

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert out_md.exists()
    figs = list((out_dir / "figures").glob("*.png"))
    assert len(figs) >= 1
