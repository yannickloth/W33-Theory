from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_enumerate_minimal_certificates_parallel_smoke(tmp_path: Path):
    out = tmp_path / "enum.json"
    cmd = [
        sys.executable,
        "tools/enumerate_minimal_certificates.py",
        "--in-json",
        "artifacts/e6_f3_trilinear_map.json",
        "--candidate-space",
        "hessian",
        "--max-samples",
        "50",
        "--seed",
        "7",
        "--workers",
        "2",
        "--batch-size",
        "10",
        "--checkpoint-interval",
        "10",
        "--out-json",
        str(out),
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr
    assert out.exists()
    j = json.loads(out.read_text(encoding="utf-8"))
    assert j.get("status") == "ok"
    assert j.get("distinct_canonical_representatives_found", 0) >= 1
