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
