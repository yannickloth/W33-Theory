from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_hessian_exhaustive_artifact_exists_and_counts():
    p = Path("artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2.json")
    if not p.exists():
        pytest.skip(
            "exhaustive artifact missing: skip unless the exhaustive enumerator is run"
        )
    j = json.loads(p.read_text(encoding="utf-8"))
    assert j.get("status") == "ok"
    assert j.get("distinct_canonical_representatives_found") == 256
    assert j.get("combinations_that_cover") == 273
