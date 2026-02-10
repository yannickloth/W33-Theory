from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_hessian_20k_with_geotypes_exists_and_has_fields():
    p = Path(
        "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json"
    )
    if not p.exists():
        pytest.skip(
            "classification artifact missing: run tools/classify_canonical_reps.py"
        )
    j = json.loads(p.read_text(encoding="utf-8"))
    reps = j.get("representatives", [])
    assert len(reps) >= 1
    first = reps[0]
    assert "geotype" in first
    assert "orbit_size" in first


def test_hessian_exhaustive_with_geotypes_exists_and_counts():
    p = Path(
        "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json"
    )
    if not p.exists():
        pytest.skip(
            "exhaustive classification artifact missing: run tools/classify_canonical_reps.py"
        )
    j = json.loads(p.read_text(encoding="utf-8"))
    assert j.get("distinct_representatives") == 256
    reps = j.get("representatives", [])
    assert len(reps) == 256
