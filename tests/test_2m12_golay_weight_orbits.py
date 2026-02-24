from __future__ import annotations


def test_2m12_orbit_decomposition_matches_golay_weight_enumerator() -> None:
    from scripts.w33_2m12_golay_weight_orbits import analyze

    rep = analyze()
    assert rep.get("available") is True
    assert int(rep.get("field_p", 0) or 0) == 3
    assert rep.get("orbit_sizes_sorted") == [24, 264, 440]
    assert rep.get("orbits_by_weight") == {6: 264, 9: 440, 12: 24}

