from __future__ import annotations

from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary


def test_surface_physics_shell_bridge_closes_exactly() -> None:
    summary = build_surface_physics_shell_summary()
    assert summary["status"] == "ok"

    gauge = summary["standard_model_gauge_dictionary"]
    shell = summary["surface_physics_shell_dictionary"]
    factors = summary["exact_factorizations"]

    assert gauge["gauge_dimension"] == 12
    assert gauge["gauge_dimension_decomposition"] == [8, 3, 1]
    assert gauge["beta0_qcd"] == 7
    assert gauge["shared_six_channel"] == 6
    assert gauge["g2_dimension"] == 14
    assert gauge["topological_shell"] == 28
    assert gauge["quartic_e7_packet"] == 56

    assert shell["single_surface_flags"] == 84
    assert shell["dual_pair_flags"] == 168
    assert shell["full_heawood_order"] == 336

    assert factors["gauge_dimension_equals_8_plus_3_plus_1"] is True
    assert factors["beta0_qcd_equals_phi6"] is True
    assert factors["single_surface_flags_equals_gauge_dimension_times_beta0"] is True
    assert factors["single_surface_flags_equals_q_times_mu_times_phi6"] is True
    assert factors["single_surface_flags_equals_g2_dimension_times_shared_six"] is True
    assert factors["dual_pair_flags_equals_gauge_dimension_times_g2_dimension"] is True
    assert factors["dual_pair_flags_equals_shared_six_times_topological_shell"] is True
    assert factors["dual_pair_flags_equals_two_single_surface_packets"] is True
    assert factors["full_heawood_order_equals_gauge_dimension_times_topological_shell"] is True
    assert factors["full_heawood_order_equals_shared_six_times_quartic_e7_packet"] is True
    assert factors["full_heawood_order_equals_two_dual_pair_packets"] is True
    assert factors["topological_shell_equals_mu_times_phi6"] is True
    assert factors["quartic_e7_packet_equals_two_times_topological_shell"] is True
