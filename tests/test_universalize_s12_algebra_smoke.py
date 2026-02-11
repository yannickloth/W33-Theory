from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_universalize_s12_algebra_cli_smoke(tmp_path: Path):
    out_json = tmp_path / "s12_report.json"
    out_md = tmp_path / "s12_report.md"
    cmd = [
        sys.executable,
        "tools/universalize_s12_algebra.py",
        "--jordan-sample-limit",
        "120",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert run.returncode == 0, run.stderr
    assert out_json.exists()
    assert out_md.exists()

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["code_size"] == 729
    assert payload["universal_grade_laws"]["jacobi_coefficient_identity_holds"] is False
    assert payload["universal_grade_laws"]["jacobi_failure_count"] == 6
    assert payload["exhaustive_checks"]["ad3_zero_on_g1"]["holds"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "# s12 Universalization Report" in text
    assert "Jacobi coefficient identity" in text
    assert "`ad^3=0` on `g1`" in text
