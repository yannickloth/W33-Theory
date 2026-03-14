from __future__ import annotations

from w33_monster_transport_shell_bridge import build_monster_transport_shell_summary


def test_transport_shell_dictionary_closes_exactly() -> None:
    summary = build_monster_transport_shell_summary()
    bridge = summary["transport_shell_dictionary"]
    assert bridge["q"] == 3
    assert bridge["w33_edge_count"] == 240
    assert bridge["transport_edge_count"] == 720
    assert bridge["local_line_bundle_dimension"] == 135
    assert bridge["a2_transfer_block_rank"] == 16
    assert bridge["semisimple_transport_shell"] == 2160
    assert bridge["generation_states"] == 27
    assert bridge["monster_complement_states"] == 2187
    assert bridge["semisimple_equals_q_squared_times_w33_edges"] is True
    assert bridge["semisimple_equals_q_times_transport_edges"] is True
    assert bridge["semisimple_equals_a2_block_rank_times_bundle_dimension"] is True


def test_monster_transport_completion_closes_all_forms() -> None:
    summary = build_monster_transport_shell_summary()
    bridge = summary["monster_transport_completion"]
    assert bridge["complement_equals_semisimple_plus_generation"] is True
    assert bridge["complement_equals_q_squared_edges_plus_q_cubed"] is True
    assert bridge["complement_equals_q_transport_edges_plus_q_cubed"] is True
    assert bridge["complement_equals_block_bundle_plus_generation"] is True
