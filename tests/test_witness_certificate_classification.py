from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _ensure_analysis():
    root = Path.cwd()
    in_json = root / "artifacts" / "e6_f3_trilinear_map.json"
    out_json = root / "artifacts" / "e6_f3_trilinear_symmetry_breaking.json"
    if not in_json.exists():
        # Build the trilinear map if missing
        r = subprocess.run(
            [
                sys.executable,
                "tools/build_e6_f3_trilinear_map.py",
                "--out-json",
                str(in_json),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert r.returncode == 0, r.stderr
        assert in_json.exists()
    if not out_json.exists():
        r = subprocess.run(
            [
                sys.executable,
                "tools/analyze_e6_f3_trilinear_symmetry_breaking.py",
                "--in-json",
                str(in_json),
                "--out-json",
                str(out_json),
                "--out-md",
                str(out_json.with_suffix(".md")),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert r.returncode == 0, r.stderr
        assert out_json.exists()
    return out_json


def test_witness_certificate_geotypes():
    out_json = _ensure_analysis()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    geos = data["cross_checks"].get("full_sign_obstruction_certificate_geotypes")
    assert geos is not None

    h = geos.get("hessian216")
    a = geos.get("agl23")
    assert h is not None and a is not None

    # Hessian216 expected summary
    assert h["unique_lines_count"] == 5
    assert h["lines_with_multiple_z_count"] == 1
    z_h = {int(k): v for k, v in h["z_histogram"].items()}
    assert z_h == {0: 1, 1: 2, 2: 4}
    s_h = {int(k): v for k, v in h["sign_histogram"].items()}
    assert s_h == {-1: 3, 1: 4}

    # AGL23 expected summary
    assert a["unique_lines_count"] == 6
    assert a["lines_with_multiple_z_count"] == 1
    z_a = {int(k): v for k, v in a["z_histogram"].items()}
    assert z_a == {0: 3, 1: 3, 2: 1}
    s_a = {int(k): v for k, v in a["sign_histogram"].items()}
    assert s_a == {-1: 3, 1: 4}

    # Orbit stats (AGL x z-affine)
    orbits = data["cross_checks"].get("full_sign_obstruction_certificate_orbits")
    assert orbits is not None
    h_orb = orbits.get("hessian216")
    a_orb = orbits.get("agl23")
    assert h_orb and a_orb
    assert h_orb["orbit_size"] > 0
    assert a_orb["orbit_size"] > 0
    # canonical representatives should differ between the two minimal certificates
    assert h_orb["canonical_rep"] != a_orb["canonical_rep"]
