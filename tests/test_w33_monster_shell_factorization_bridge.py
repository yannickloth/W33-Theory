from __future__ import annotations

from w33_monster_shell_factorization_bridge import build_monster_shell_factorization_summary


def test_shell_factorization_is_exact() -> None:
    summary = build_monster_shell_factorization_summary()
    shell = summary["shell_factorization"]

    assert shell["shell_states"] == 3**13
    assert shell["heisenberg_states"] == 3**6
    assert shell["logical_states"] == 3**4
    assert shell["generation_states"] == 3**3
    assert shell["complement_states"] == 3**7
    assert shell["shell_equals_heisenberg_times_logical_times_generation"] is True
    assert shell["complement_equals_logical_times_generation"] is True
    assert shell["shell_trits_split"] == [6, 4, 3]
    assert shell["shell_trits_factorization_exact"] is True
    assert shell["complement_trits_split"] == [4, 3]
    assert shell["complement_trits_factorization_exact"] is True


def test_promoted_ratios_are_shell_shares() -> None:
    summary = build_monster_shell_factorization_summary()
    ratios = summary["promoted_ratio_factorization"]

    assert ratios["weinberg_from_generation_over_shell"]["exact"] == "3/13"
    assert ratios["theta12_from_logical_over_shell"]["exact"] == "4/13"
    assert ratios["active_heisenberg_share"]["exact"] == "6/13"
    assert ratios["theta23_from_complement_over_shell"]["exact"] == "7/13"
    assert ratios["theta23_equals_theta12_plus_weinberg"] is True
    assert ratios["theta23_plus_active_heisenberg_share_equals_one"] is True


def test_curved_ratios_match_shell_factorization() -> None:
    summary = build_monster_shell_factorization_summary()
    curved = summary["curved_ratio_factorization"]

    assert curved["discrete_to_continuum_ratio"]["exact"] == "39"
    assert curved["topological_over_continuum"]["exact"] == "7"
    assert curved["discrete_to_continuum_equals_shell_times_generation"] is True
    assert curved["topological_over_continuum_equals_logical_plus_generation"] is True
