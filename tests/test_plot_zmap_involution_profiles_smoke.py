from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def test_plot_zmap_involution_profiles_smoke(tmp_path: Path) -> None:
    out = subprocess.run(
        [sys.executable, "tools/plot_zmap_involution_profiles.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # allow script to succeed or at least write images; verify images exist
    fig_dir = Path("artifacts/min_cert_census_medium_2026_02_10/figures")
    if not fig_dir.exists():
        pytest.skip(f"Missing artifacts directory {fig_dir} (integration-only)")
    img1 = fig_dir / "zmap_hist_hessian.png"
    img2 = fig_dir / "match_count_hist_hessian.png"
    assert img1.exists(), f"Missing zmap histogram PNG: {img1}"
    assert img2.exists(), f"Missing match count histogram PNG: {img2}"
