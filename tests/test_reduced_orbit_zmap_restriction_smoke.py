from __future__ import annotations

import json
from pathlib import Path


def test_reduced_orbit_zmap_restriction_smoke() -> None:
    """Smoke test: observed matching z-maps in Hessian medium run are a subset of allowed set."""
    p = Path(
        "committed_artifacts/min_cert_census_medium_2026_02_10/e6_f3_trilinear_reduced_orbit_closed_form_equiv_hessian_exact_full.json"
    )
    assert p.exists(), f"Missing artifact: {p}"
    dd = json.loads(p.read_text(encoding="utf-8"))

    observed = set(dd.get("observed_matching_z_maps", []))
    allowed = {"(1, 0)", "(2, 0)", "(2, 1)"}

    # Observed set must be a subset of allowed z-maps
    assert observed.issubset(
        allowed
    ), f"Observed z-maps not subset of allowed: {observed}"

    # Explicitly check (2,2) is not observed
    assert (
        "(2, 2)" not in observed
    ), "(2,2) unexpectedly observed in Hessian reduced-orbit matches"
