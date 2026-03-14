from __future__ import annotations

from fractions import Fraction

from exploration.w33_monster_3b_centralizer_bridge import build_monster_3b_centralizer_summary


def test_centralizer_three_primary_matches_monster() -> None:
    summary = build_monster_3b_centralizer_summary()
    centralizer = summary["three_b_centralizer"]
    assert centralizer["centralizer_label"] == "3^(1+12).2Suz"
    assert centralizer["monster_three_primary_part"]["states"] == 3**20
    assert centralizer["centralizer_three_primary_part"]["states"] == 3**20
    assert centralizer["centralizer_three_primary_matches_monster"] is True


def test_two_suz_supplies_exact_complement() -> None:
    summary = build_monster_3b_centralizer_summary()
    factorization = summary["centralizer_factorization"]
    assert factorization["shell_states"] == 3**13
    assert factorization["shell_trits"] == 13
    assert factorization["two_suz_three_primary_states"] == 3**7
    assert factorization["two_suz_three_primary_trits"] == 7
    assert factorization["logical_states"] == 3**4
    assert factorization["generation_states"] == 3**3
    assert factorization["centralizer_three_primary_equals_shell_times_two_suz_three_primary"] is True
    assert factorization["two_suz_three_primary_equals_logical_times_generation"] is True


def test_landauer_budget_is_additive() -> None:
    summary = build_monster_3b_centralizer_summary()
    budget = summary["landauer_budget"]
    assert budget["centralizer_three_primary"]["landauer_over_kT"]["exact"] == "20 ln(3)"
    assert budget["shell"]["landauer_over_kT"]["exact"] == "13 ln(3)"
    assert budget["two_suz_three_primary"]["landauer_over_kT"]["exact"] == "7 ln(3)"
    assert budget["landauer_additivity_exact"] is True


def test_curved_dictionary_recovers_centralizer_split() -> None:
    summary = build_monster_3b_centralizer_summary()
    curved = summary["curved_dictionary"]
    assert Fraction(curved["gravity_over_q"]["exact"]) == 13
    assert Fraction(curved["topology_over_continuum"]["exact"]) == 7
    assert curved["shell_from_curved_gravity_exact"] is True
    assert curved["two_suz_from_curved_topology_exact"] is True
    assert curved["centralizer_three_primary_from_curved_coefficients_exact"] is True
