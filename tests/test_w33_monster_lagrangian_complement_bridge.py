from __future__ import annotations

from fractions import Fraction

from exploration.w33_monster_lagrangian_complement_bridge import (
    build_monster_lagrangian_complement_summary,
)


def test_lagrangian_realization_matches_monster_complement() -> None:
    summary = build_monster_lagrangian_complement_summary()
    realization = summary["lagrangian_realization"]
    assert realization["local_shell_label"] == "3^(1+12)"
    assert realization["shell_states"] == 3**13
    assert realization["complement_states"] == 3**7
    assert realization["max_abelian_subgroup_order"] == 3**7
    assert realization["center_states"] == 3
    assert realization["lagrangian_quotient_states"] == 3**6
    assert realization["lagrangian_quotient_trits"] == 6
    assert realization["complement_equals_lifted_max_abelian_exactly"] is True


def test_lagrangian_quotient_matches_heisenberg_golay_and_sl27() -> None:
    summary = build_monster_lagrangian_complement_summary()
    realization = summary["lagrangian_realization"]
    assert realization["lagrangian_quotient_equals_heisenberg_irrep"] is True
    assert realization["lagrangian_quotient_equals_golay_codewords"] is True
    assert realization["lagrangian_quotient_equals_sl27_operator_basis"] is True
    assert realization["center_times_lagrangian_quotient_equals_complement"] is True


def test_dual_factorization_is_exact() -> None:
    summary = build_monster_lagrangian_complement_summary()
    factorization = summary["dual_factorization"]
    assert factorization["logical_states"] == 3**4
    assert factorization["generation_states"] == 3**3
    assert factorization["center_states"] == 3
    assert factorization["heisenberg_irrep_states"] == 3**6
    assert factorization["selector_line_dimension"] == 1
    assert factorization["active_heisenberg_trits"] == 6
    assert factorization["logical_plus_generation_trits"] == [4, 3]
    assert factorization["center_plus_heisenberg_trits"] == [1, 6]
    assert factorization["complement_equals_logical_times_generation"] is True
    assert factorization["complement_trits_equal_logical_plus_generation"] is True
    assert factorization["complement_trits_equal_center_plus_heisenberg"] is True
    assert factorization["dual_trit_splits_agree_exactly"] is True


def test_curved_dictionary_matches_dual_factorization() -> None:
    summary = build_monster_lagrangian_complement_summary()
    curved = summary["curved_dictionary"]
    assert Fraction(curved["topological_over_continuum"]["exact"]) == 7
    assert curved["topological_equals_complement_trits"] is True
    assert curved["topological_equals_logical_plus_generation"] is True
    assert curved["topological_equals_center_plus_heisenberg"] is True

