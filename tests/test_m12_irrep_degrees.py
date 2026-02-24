from __future__ import annotations

import json
from pathlib import Path


def test_m12_irrep_degrees_sumsq_and_11a_ratio_hit() -> None:
    payload = json.loads(
        Path("data/m12_irrep_degrees.json").read_text(encoding="utf-8")
    )
    degrees = payload.get("degrees", [])
    assert isinstance(degrees, list)
    degrees_int = [int(x) for x in degrees]

    assert int(payload.get("order", 0) or 0) == 95040
    assert int(payload.get("n_conjugacy_classes", 0) or 0) == 15
    assert len(degrees_int) == 15
    assert sum(d * d for d in degrees_int) == 95040

    # Bridge: Monster 11A centralizer factors as 11×M12 (from bundled ATLAS data).
    from scripts.w33_leech_monster import load_monster_atlas_ccls

    atlas = load_monster_atlas_ccls()
    assert atlas is not None
    classes = atlas.get("classes", {})
    assert isinstance(classes, dict)
    cent_11a = int(classes["11A"]["centralizer_order"])
    assert cent_11a == 11 * 95040

    # Bridge: the 2A×3B prime-ratio signature for 11A is r_11=144, and 144 is
    # an M12 irrep degree (striking compatibility check).
    from scripts.w33_leech_monster import (
        analyze_monster_2a3b_class_algebra_partial_distribution,
    )

    dist = analyze_monster_2a3b_class_algebra_partial_distribution()
    assert dist.get("available") is True
    info = dist["classes"]["11A"]
    n = int(info["structure_constant_per_element"])
    assert n == 11 * 144
    assert 144 in degrees_int

    # Phase bridge: the M12 symmetry of the ternary Golay code is most natural as
    # a monomial action (permutation + diagonal signs). This is exactly the
    # pattern the repo exploits: "grade-only" isn't enough; the phase matters.
    from scripts.w33_monster_11a_m12_golay_bridge import analyze as analyze_bridge

    bridge = analyze_bridge()
    assert bridge.get("available") is True

    golay = bridge.get("golay", {})
    assert isinstance(golay, dict)
    perm_only = golay.get("perm_only_preserves_code_rows", {})
    assert isinstance(perm_only, dict)
    # At least one generator needs a sign lift (permutation-only fails).
    assert (perm_only.get("b11_code") is False) or (perm_only.get("b21_code") is False)

    lifts = golay.get("monomial_lift_signs", {})
    assert isinstance(lifts, dict)
    s11 = lifts.get("b11_code", [])
    s21 = lifts.get("b21_code", [])
    assert isinstance(s11, list) and len(s11) == 12 and set(map(int, s11)).issubset({1, 2})
    assert isinstance(s21, list) and len(s21) == 12 and set(map(int, s21)).issubset({1, 2})
