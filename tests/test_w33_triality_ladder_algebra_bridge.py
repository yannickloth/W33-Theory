from __future__ import annotations

from w33_triality_ladder_algebra_bridge import build_triality_ladder_algebra_summary


def test_triality_ladder_blocks_close_exactly() -> None:
    summary = build_triality_ladder_algebra_summary()
    ladder = summary["triality_ladder"]
    assert ladder["q8_d4_24cell_vertex_block"]["value"] == 24
    assert ladder["tomotope_aut_block"]["value"] == 96
    assert ladder["d4_weyl_flag_block"]["value"] == 192
    assert ladder["rotational_24cell_block"]["value"] == 576
    assert ladder["f4_weyl_block"]["value"] == 1152
    assert ladder["e6_weyl_closure"]["value"] == 51840


def test_ladder_matches_live_rank_factorizations() -> None:
    summary = build_triality_ladder_algebra_summary()
    ladder = summary["triality_ladder"]
    assert ladder["tomotope_aut_block"]["equals_a2_rank_times_a2_block_rank"] is True
    assert ladder["d4_weyl_flag_block"]["equals_d4_roots_times_cartan_rank"] is True
    assert ladder["rotational_24cell_block"]["equals_e6_root_support_times_cartan_rank"] is True
    assert ladder["f4_weyl_block"]["equals_e6_root_support_times_a2_block_rank"] is True


def test_e6_closure_matches_all_three_stabilizer_forms() -> None:
    summary = build_triality_ladder_algebra_summary()
    closure = summary["triality_ladder"]["e6_weyl_closure"]
    assert closure["tritangents"] == 45
    assert closure["directed_transport_edges"] == 270
    assert closure["transport_edges"] == 720
    assert closure["equals_tritangents_times_wf4"] is True
    assert closure["equals_directed_transport_edges_times_wd4"] is True
    assert closure["equals_e6_root_support_times_transport_edges"] is True
