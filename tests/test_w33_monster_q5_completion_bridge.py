from __future__ import annotations

from w33_monster_q5_completion_bridge import build_monster_q5_completion_summary


def test_q5_restoration_recovers_three_q5_blocks() -> None:
    summary = build_monster_q5_completion_summary()
    bridge = summary["q5_restoration"]
    assert bridge["q"] == 3
    assert bridge["q5"] == 243
    assert bridge["q7"] == 2187
    assert bridge["grade_split"] == [242, 243, 243]
    assert bridge["selector_line_dimension"] == 1
    assert bridge["grade0_equals_q5_minus_1"] is True
    assert bridge["grade1_equals_q5"] is True
    assert bridge["grade2_equals_q5"] is True
    assert bridge["restored_blocks"] == [243, 243, 243]
    assert bridge["restored_blocks_are_three_q5_blocks"] is True
    assert bridge["full_codewords"] == 729
    assert bridge["full_codewords_equal_3q5"] is True


def test_monster_completion_dictionary_reaches_q7() -> None:
    summary = build_monster_q5_completion_summary()
    bridge = summary["monster_completion_dictionary"]
    assert bridge["complement_states"] == 2187
    assert bridge["complement_equals_center_times_full_codewords"] is True
    assert bridge["complement_equals_q_times_three_q5_blocks"] is True
    assert bridge["complement_equals_q7"] is True


def test_transport_curvature_dictionary_matches_semisimple_split() -> None:
    summary = build_monster_q5_completion_summary()
    bridge = summary["transport_curvature_dictionary"]
    assert bridge["semisimple_curved_states"] == 2160
    assert bridge["generation_states"] == 27
    assert bridge["semisimple_curved_equals_q_squared_times_edges"] is True
    assert bridge["semisimple_curved_equals_q7_minus_q3"] is True
    assert bridge["complement_equals_semisimple_curved_plus_generation"] is True
    assert bridge["complement_equals_q_squared_edges_plus_q_cubed"] is True


def test_w33_q5_dictionary_matches_edge_count() -> None:
    summary = build_monster_q5_completion_summary()
    bridge = summary["w33_q5_dictionary"]
    assert bridge["edge_count"] == 240
    assert bridge["edge_count_equals_q5_minus_q"] is True
    assert bridge["grade0_minus_edge_count"] == 2
    assert bridge["restored_block_minus_edge_count"] == 3
