from __future__ import annotations

from w33_eh_continuum_lock_bridge import build_eh_continuum_lock_summary


def test_discrete_eh_mode_is_rank_39_multiple_of_continuum_coefficient() -> None:
    summary = build_eh_continuum_lock_summary()
    lock = summary["continuum_lock"]
    assert lock["a0_f"] == 480
    assert lock["a2_f"] == 2240
    assert lock["continuum_eh_coefficient"] == {"exact": "320", "float": 320.0}
    assert lock["discrete_eh_6_mode_coefficient"] == {"exact": "12480", "float": 12480.0}
    assert lock["discrete_equals_rank_factor_times_continuum"] is True
    assert lock["rank_factor"] == {"exact": "39", "float": 39.0}


def test_rank_39_has_all_native_w33_identifications() -> None:
    summary = build_eh_continuum_lock_summary()
    identifications = summary["rank_39_identifications"]
    assert identifications["v_minus_1"] == 39
    assert identifications["rank_d1"] == 39
    assert identifications["rank_mod_3_adjacency"] == 39
    assert identifications["nontrivial_adjacency_multiplicity_sum"] == 39
    assert identifications["all_equal_39"] is True


def test_topological_mode_locks_to_q_cubic_plus_one_times_abs_chi() -> None:
    summary = build_eh_continuum_lock_summary()
    topological = summary["topological_lock"]
    assert topological["topological_1_mode_coefficient"] == {"exact": "2240", "float": 2240.0}
    assert topological["absolute_euler_characteristic"] == 80
    assert topological["q_cubic_plus_1"] == 28
    assert topological["topological_equals_q_cubic_plus_1_times_abs_chi"] is True
