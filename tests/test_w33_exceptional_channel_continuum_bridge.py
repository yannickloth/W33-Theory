from w33_exceptional_channel_continuum_bridge import (
    build_exceptional_channel_continuum_bridge_summary,
)


def test_base_continuum_channel_is_exact_l6_spinor_e6_times_cartan() -> None:
    summary = build_exceptional_channel_continuum_bridge_summary()
    base = summary["base_continuum_channel"]

    assert base["spinor_e6_rank"] == 40
    assert base["spinor_cartan_rank"] == 8
    assert base["continuum_eh_coefficient"] == 320
    assert base["continuum_equals_spinor_e6_times_cartan"] is True


def test_shared_six_channel_unifies_lie_transport_firewall_and_tomotope() -> None:
    summary = build_exceptional_channel_continuum_bridge_summary()
    shared = summary["shared_six_channel"]

    assert shared["l6_a2_root_support"] == 6
    assert shared["l6_spinor_a2_rank"] == 6
    assert shared["ordered_generation_transfers"] == 6
    assert shared["transport_weyl_a2_order"] == 6
    assert shared["firewall_triplet_fibers"] == 6
    assert shared["tomotope_triality_factor"] == 6
    assert shared["all_equal_to_6"] is True


def test_discrete_curvature_channel_has_both_rank39_and_f4_factorizations() -> None:
    summary = build_exceptional_channel_continuum_bridge_summary()
    discrete = summary["discrete_curvature_channel"]

    assert discrete["discrete_6_mode_coefficient"] == 12480
    assert discrete["rank39_factor"] == 39
    assert discrete["w33_edge_count"] == 240
    assert discrete["f4_dimension"] == 52
    assert discrete["discrete_equals_continuum_times_rank39"] is True
    assert discrete["discrete_equals_edges_times_f4"] is True
    assert discrete["discrete_equals_spinor_e6_times_shared_six_times_f4"] is True
    assert discrete["cartan_rank_times_rank39"] == 312
    assert discrete["shared_six_times_f4"] == 312
    assert discrete["cartan_rank_times_rank39_equals_shared_six_times_f4"] is True


def test_topological_channel_and_tomotope_triality_bridge_are_exact() -> None:
    summary = build_exceptional_channel_continuum_bridge_summary()
    topological = summary["topological_channel"]
    tomotope = summary["tomotope_triality_bridge"]
    crosscheck = summary["transport_lie_crosscheck"]

    assert topological["topological_1_mode_coefficient"] == 2240
    assert topological["e7_fundamental_dimension"] == 56
    assert topological["phi6"] == 7
    assert topological["topological_equals_spinor_e6_times_e7_fund"] is True
    assert topological["topological_equals_continuum_times_phi6"] is True

    assert tomotope["tomotope_automorphism_order"] == 96
    assert tomotope["tomotope_automorphism_equals_16_times_shared_six"] is True
    assert tomotope["universal_cover_automorphism_order"] == 192
    assert tomotope["universal_cover_equals_2_times_tomotope_automorphism"] is True

    assert crosscheck["complete_oriented_three_generation_graph"] is True
    assert crosscheck["all_a2_channels_are_signed_permutation_blocks"] is True
    assert crosscheck["all_cartan_modes_are_generation_diagonal"] is True
    assert crosscheck["firewall_full_clean_quark_block_exists"] is False
