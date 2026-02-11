import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_plot_feature_mapping_cli_smoke(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    out_fig1 = Path("artifacts/figures/feature_embeddings.png")
    out_fig2 = Path("artifacts/figures/adj_preservation_heatmap.png")
    # Remove if present
    try:
        out_fig1.unlink()
    except Exception:
        pass
    try:
        out_fig2.unlink()
    except Exception:
        pass

    cmd = [sys.executable, "scripts/plot_feature_mapping.py"]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    run = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=env,
    )
    assert run.returncode == 0, run.stderr
    assert out_fig1.exists() or out_fig2.exists()
