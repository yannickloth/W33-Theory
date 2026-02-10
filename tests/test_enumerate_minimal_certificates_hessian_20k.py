from __future__ import annotations

import json
from pathlib import Path


def test_hessian_20k_artifact_exists_and_counts():
    p = Path("artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json")
    assert (
        p.exists()
    ), "Expected artifact missing: run the enumerator with seed=42, workers=4"
    j = json.loads(p.read_text(encoding="utf-8"))
    assert j.get("status") == "ok"
    assert j.get("distinct_canonical_representatives_found") == 134
