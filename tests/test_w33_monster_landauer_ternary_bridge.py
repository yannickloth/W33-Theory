from __future__ import annotations

from w33_monster_landauer_ternary_bridge import build_monster_landauer_ternary_bridge_summary


def test_monster_local_shell_is_ternary_and_local() -> None:
    summary = build_monster_landauer_ternary_bridge_summary()
    shell = summary["monster_local_shell"]

    assert shell["monster_class"] == "3B"
    assert shell["extraspecial_shell"]["states"] == 3**13
    assert shell["extraspecial_shell"]["trits"] == 13
    assert shell["extraspecial_shell"]["landauer_over_kT"]["exact"] == "13 ln(3)"
    assert shell["heisenberg_irrep"]["states"] == 3**6
    assert shell["heisenberg_irrep"]["trits"] == 6
    assert shell["shell_complement"]["states"] == 3**7
    assert shell["shell_complement"]["trits"] == 7


def test_ternary_lock_dictionary_matches_live_q3_data() -> None:
    summary = build_monster_landauer_ternary_bridge_summary()
    bridge = summary["ternary_lock_dictionary"]

    assert bridge["q"] == 3
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["phi3_equals_shell_trits"] is True
    assert bridge["shared_six_equals_irrep_trits"] is True
    assert bridge["phi6_equals_complement_trits"] is True
    assert bridge["phi6_equals_shell_minus_irrep"] is True
    assert bridge["logical_qutrits"] == 81
    assert bridge["logical_trits"] == 4
    assert bridge["heisenberg_irrep_equals_q_squared_times_logical_qutrits"] is True


def test_landauer_ratio_dictionary_recovers_promoted_values() -> None:
    summary = build_monster_landauer_ternary_bridge_summary()
    ratios = summary["landauer_ratio_dictionary"]

    assert ratios["weinberg_from_generation_over_shell"]["exact"] == "3/13"
    assert ratios["tan_theta_c_from_generation_over_shell"]["exact"] == "3/13"
    assert ratios["theta12_from_logical_over_shell"]["exact"] == "4/13"
    assert ratios["theta23_from_complement_over_shell"]["exact"] == "7/13"
    assert ratios["weinberg_matches_promoted_value"] is True
    assert ratios["cabibbo_matches_promoted_value"] is True
    assert ratios["theta12_matches_promoted_value"] is True
    assert ratios["theta23_matches_promoted_value"] is True
    assert ratios["discrete_to_continuum_ratio"]["exact"] == "39"
    assert ratios["discrete_to_continuum_equals_shell_times_generation_trits"] is True
    assert ratios["topological_over_continuum"]["exact"] == "7"
    assert ratios["topological_over_continuum_equals_complement_trits"] is True
