from __future__ import annotations


def test_monster_prime_centralizer_sporadic_ladder_hits_known_rungs() -> None:
    from scripts.w33_leech_monster import (
        analyze_monster_prime_centralizer_sporadic_ladder,
    )

    rep = analyze_monster_prime_centralizer_sporadic_ladder()
    assert rep.get("available") is True

    matches = rep.get("matches", {})
    assert isinstance(matches, dict)

    expected_exact = {
        "2A": "B",
        "3A": "Fi24",
        "3C": "Th",
        "5A": "HN",
        "7A": "He",
        "11A": "M12",
    }
    for cls, group in expected_exact.items():
        info = matches.get(cls, {})
        assert isinstance(info, dict)
        assert info.get("exact_sporadic_match") == group

    info_2b = matches.get("2B", {})
    assert isinstance(info_2b, dict)
    pow2 = info_2b.get("power_of_two_sporadic_matches", [])
    assert isinstance(pow2, list)
    best = pow2[0]
    assert isinstance(best, dict)
    assert best.get("group") == "Co1"
    assert int(best.get("two_power", 0) or 0) == 24
