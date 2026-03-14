from __future__ import annotations

from fractions import Fraction

from exploration.w33_monster_3adic_closure_bridge import build_monster_3adic_closure_summary


def test_monster_3_primary_order_is_exact() -> None:
    summary = build_monster_3adic_closure_summary()
    order = summary["monster_3_primary_order"]
    assert order["order_factorization_verifies_exactly"] is True
    assert order["three_primary_part"]["states"] == 3**20
    assert order["three_primary_part"]["trits"] == 20
    assert order["three_primary_part"]["landauer_over_kT"]["exact"] == "20 ln(3)"


def test_local_global_ternary_closure_is_exact() -> None:
    summary = build_monster_3adic_closure_summary()
    closure = summary["local_global_ternary_closure"]
    assert closure["shell_states"] == 3**13
    assert closure["complement_states"] == 3**7
    assert closure["heisenberg_states"] == 3**6
    assert closure["logical_states"] == 3**4
    assert closure["generation_states"] == 3**3
    assert closure["full_three_primary_equals_shell_times_complement"] is True
    assert closure["full_three_primary_equals_heisenberg_times_logical_squared_times_generation_squared"] is True
    assert closure["full_three_primary_trits_equal_phi3_plus_phi6"] is True
    assert closure["shell_trits_equal_phi3"] is True
    assert closure["complement_trits_equal_phi6"] is True
    assert closure["shell_plus_complement_trits_equals_monster_three_primary"] is True
    assert closure["shell_complement_matches_factorized_logical_generation_block"] is True


def test_landauer_budget_additivity_and_shares() -> None:
    summary = build_monster_3adic_closure_summary()
    budget = summary["landauer_budget"]
    assert budget["landauer_additivity_exact"] is True
    assert Fraction(budget["shell_share_of_full_monster_three_primary"]["exact"]) == Fraction(13, 20)
    assert Fraction(budget["complement_share_of_full_monster_three_primary"]["exact"]) == Fraction(7, 20)


def test_curved_dictionary_reconstructs_full_monster_three_part() -> None:
    summary = build_monster_3adic_closure_summary()
    curved = summary["curved_thermodynamic_dictionary"]
    assert curved["q"] == 3
    assert curved["phi3"] == 13
    assert curved["phi6"] == 7
    assert Fraction(curved["discrete_to_continuum_ratio"]["exact"]) == 39
    assert Fraction(curved["gravity_over_q"]["exact"]) == 13
    assert Fraction(curved["topological_over_continuum"]["exact"]) == 7
    assert curved["shell_from_curved_gravity_exact"] is True
    assert curved["complement_from_curved_topology_exact"] is True
    assert curved["full_monster_three_primary_from_curved_coefficients_exact"] is True
    assert curved["monster_three_trits_equal_phi3_plus_phi6"] is True
