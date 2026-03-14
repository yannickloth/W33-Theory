from __future__ import annotations

from w33_exceptional_tensor_rank_bridge import build_exceptional_tensor_rank_summary


def test_tensor_rank_dictionary_recovers_promoted_exceptional_counts() -> None:
    summary = build_exceptional_tensor_rank_summary()
    base = summary["base_ranks"]
    tensor = summary["tensor_rank_dictionary"]
    promoted = summary["promoted_exceptional_lock"]

    assert base["e6_projector_rank"] == 40
    assert base["a2_projector_rank"] == 6
    assert base["cartan_projector_rank"] == 8
    assert base["a2_transfer_block_rank"] == 16
    assert base["all_a2_transfer_blocks_have_rank_16"] is True
    assert tensor["w33_edge_or_e8_root_count"] == 240
    assert tensor["continuum_eh_coefficient"] == 320
    assert tensor["tomotope_automorphism_order"] == 96
    assert tensor["discrete_curvature_coefficient"] == 12480
    assert tensor["topological_coefficient"] == 2240
    assert tensor["edge_count_equals_e6_rank_times_a2_rank"] is True
    assert tensor["continuum_equals_e6_rank_times_cartan_rank"] is True
    assert tensor["tomotope_equals_a2_rank_times_a2_block_rank"] is True
    assert tensor["discrete_equals_edge_count_times_f4"] is True
    assert tensor["topological_equals_e6_rank_times_e7_fund"] is True
    assert all(promoted.values()) is True
