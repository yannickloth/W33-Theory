import subprocess
import sys
from pathlib import Path


def test_prepare_w33_bundle_dry_run():
    script = Path("tools/prepare_w33_analysis_bundle.py")
    assert script.exists()
    cmd = [
        sys.executable,
        str(script),
        "--bundle-dir",
        "artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1",  # pragma: allowlist secret
        "--out-dir",
        "analysis/w33_bundle_temp",
        "--dry-run",
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0
    assert "Export H27/N12/MUB CSVs" in r.stdout
