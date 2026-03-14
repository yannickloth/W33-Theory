from __future__ import annotations

from w33_triality_moonshine_spine_bridge import build_triality_moonshine_spine_summary


def test_compressed_spine_closes_local_shell_exactly() -> None:
    summary = build_triality_moonshine_spine_summary()
    bridge = summary["compressed_spine_dictionary"]
    assert bridge["q8_vertex_block"] == 24
    assert bridge["weyl_e6_order"] == 51840
    assert bridge["monster_semisimple_shell"] == 2160
    assert bridge["monster_local_complement"] == 2187
    assert bridge["weyl_e6_quotiented_by_q8_vertex_block_equals_shell"] is True
    assert bridge["local_complement_equals_shell_plus_generation"] is True


def test_local_shell_has_all_live_factorizations() -> None:
    summary = build_triality_moonshine_spine_summary()
    bridge = summary["compressed_spine_dictionary"]
    assert bridge["tritangents"] == 45
    assert bridge["spinor_dimension"] == 48
    assert bridge["directed_transport_edges"] == 270
    assert bridge["cartan_rank"] == 8
    assert bridge["transport_edges"] == 720
    assert bridge["w33_edge_count"] == 240
    assert bridge["shell_equals_tritangents_times_spinor_dimension"] is True
    assert bridge["shell_equals_directed_transport_edges_times_cartan_rank"] is True
    assert bridge["shell_equals_transport_edges_times_q"] is True
    assert bridge["shell_equals_w33_edges_times_q_squared"] is True


def test_compressed_spine_lifts_to_global_moonshine_exactly() -> None:
    summary = build_triality_moonshine_spine_summary()
    bridge = summary["compressed_spine_dictionary"]
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["leech_kissing_number"] == 196560
    assert bridge["first_moonshine_coefficient"] == 196884
    assert bridge["moonshine_gap"] == 324
    assert bridge["gauge_rank"] == 54
    assert bridge["shared_six"] == 6
    assert bridge["spacetime_factor"] == 4
    assert bridge["logical_qutrits"] == 81
    assert bridge["leech_equals_shell_times_phi3_phi6"] is True
    assert bridge["first_moonshine_equals_leech_plus_gap"] is True
    assert bridge["gap_equals_gauge_rank_times_shared_six"] is True
    assert bridge["gap_equals_spacetime_factor_times_logical_qutrits"] is True
