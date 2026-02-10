from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_e6_f3_trilinear_symmetry_breaking_integration():
    root = Path.cwd()
    in_json = root / "artifacts" / "e6_f3_trilinear_map.json"
    if not in_json.exists():
        pytest.skip("Missing artifacts/e6_f3_trilinear_map.json")

    out_json = root / "artifacts" / "e6_f3_trilinear_symmetry_breaking.json"
    out_md = root / "artifacts" / "e6_f3_trilinear_symmetry_breaking.md"

    cmd = [
        sys.executable,
        "tools/analyze_e6_f3_trilinear_symmetry_breaking.py",
        "--in-json",
        str(in_json),
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=root,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert out_json.exists()
    assert out_md.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["lines"] == 12
    assert data["stabilizers"]["support"]["agl23_size"] == 432
    assert data["stabilizers"]["support"]["hessian216_size"] == 216
    assert data["stabilizers"]["full_sign"]["hessian216_with_z_affine_global_sign"] >= 1
