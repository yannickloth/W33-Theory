from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_analyze_s12_jacobi_failure_pattern_cli_smoke(tmp_path: Path) -> None:
    out_json = tmp_path / "jacobi_pattern.json"
    out_md = tmp_path / "jacobi_pattern.md"
    cmd = [
        sys.executable,
        "tools/analyze_s12_jacobi_failure_pattern.py",
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
    assert payload["jacobi_failure_count_reported"] == 6
    assert payload["jacobi_failure_count_observed"] == 6
    assert payload["pattern_match"] is True
    assert payload["two_of_one_one_of_other_match"] is True
    assert payload["s3_orbit_count"] == 2
    assert payload["claim_holds"] is True

    text = out_md.read_text(encoding="utf-8")
    assert "# s12 Jacobi Failure Pattern" in text
    assert "predicate match" in text
    assert "S3 Orbits" in text
