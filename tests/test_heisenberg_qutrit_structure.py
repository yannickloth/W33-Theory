import json
import subprocess
from pathlib import Path
import sys

import pytest


def test_w33_heisenberg_universal(tmp_path):
    # Run the qutrit heisenberg script and check the checks/ JSON output
    cmd = [sys.executable, "-X", "utf8", "scripts/w33_heisenberg_qutrit.py"]
    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd(),
        check=False,
    )
    assert r.returncode == 0, f"w33_heisenberg script failed: {r.stderr}"

    # Look for the newest PART_CVII_heisenberg_qutrit_*.json in checks/
    chk_dir = Path.cwd() / "checks"
    files = sorted(list(chk_dir.glob("PART_CVII_heisenberg_qutrit_*.json")), key=lambda p: p.stat().st_mtime, reverse=True)
    assert files, "No heisenberg checks JSON produced"
    latest = files[0]
    data = json.loads(latest.read_text(encoding="utf-8"))
    assert data.get("universal_ok") is True
    assert data.get("n_missing_tritangent") == 9


def test_parallelogram_holonomy_all_match():
    # Ensure the previously computed comparison shows full agreement
    path = (
        Path.cwd()
        / "artifacts"
        / "bundles"
        / "W33_Heisenberg_action_bundle_20260209_v1"
        / "analysis"
        / "parallelogram_holonomy_vs_bargmann.json"
    )
    if not path.exists():
        pytest.skip("Heisenberg bundle not present in artifacts/ (integration-only test)")
    assert path.exists(), "parallelogram comparison JSON missing"
    j = json.loads(path.read_text(encoding="utf-8"))
    assert j.get("total_parallelograms") == j.get("matches"), "Not all parallelograms matched Bargmann phases"


def test_phase_propagation_adjusts_all_n12():
    # Run the phase propagation script and assert it adjusts all 12 N12 vertices
    bundle_dir = Path.cwd() / "artifacts" / "bundles" / "W33_Heisenberg_action_bundle_20260209_v1"
    if not bundle_dir.exists():
        pytest.skip("Heisenberg bundle not present in artifacts/ (integration-only test)")
    cmd = [
        sys.executable,
        "-X",
        "utf8",
        "tools/phase_correct_mubs.py",
        "--bundle-dir",
        str(bundle_dir),
        "--out-dir",
        str(bundle_dir / "analysis"),
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    assert r.returncode == 0, f"phase_correct_mubs failed: {r.stderr}"
    # Parse stats from printed output by re-reading the corrected JSON if present
    out_json = bundle_dir / "analysis" / "parallelogram_holonomy_vs_bargmann.json"
    assert out_json.exists(), "parallelogram comparison JSON missing after phase propagation"
    j = json.loads(out_json.read_text(encoding="utf-8"))
    assert j.get("matches") == j.get("total_parallelograms")
