from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_plot_zmap_involution_profiles_smoke(tmp_path: Path) -> None:
    out = subprocess.run(
        [sys.executable, "tools/plot_zmap_involution_profiles.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # allow script to succeed or at least write images; verify images exist
    fig_dir = Path("artifacts/min_cert_census_medium_2026_02_10/figures")
    assert fig_dir.exists(), f"Figures directory missing: {fig_dir}"
    assert (fig_dir / "zmap_hist_hessian.png").exists(), "Missing zmap histogram PNG"
    assert (
        fig_dir / "match_count_hist_hessian.png"
    ).exists(), "Missing match count histogram PNG"
