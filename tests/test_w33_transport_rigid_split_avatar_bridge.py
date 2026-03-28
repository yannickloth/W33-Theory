from w33_transport_rigid_split_avatar_bridge import (
    build_transport_rigid_split_avatar_bridge_summary,
)


def test_transport_rigid_split_avatar_bridge_summary() -> None:
    summary = build_transport_rigid_split_avatar_bridge_summary()
    theorem = summary["transport_rigid_split_avatar_theorem"]

    assert summary["canonical_external_transport_avatar"]["head_line"] == [
        0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0
    ]
    assert summary["canonical_external_transport_avatar"]["tail_line"] == [
        0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0
    ]
    assert summary["canonical_external_transport_avatar"]["ordered_filtration_dimensions"] == [
        81, 162, 81
    ]
    assert summary["canonical_external_transport_avatar"]["glue_direction"] == (
        "tail_to_head"
    )
    assert summary["canonical_external_transport_avatar"]["external_glue_rank"] == 0
    assert summary["canonical_external_transport_avatar"]["external_glue_state"] == (
        "zero_by_splitness"
    )
    assert theorem["current_bridge_fixes_a_head_compatible_external_head_line"] is True
    assert theorem["current_bridge_fixes_a_canonical_external_tail_line"] is True
    assert theorem[
        "current_bridge_fixes_the_ordered_81_in_162_out_81_split_avatar_dimensions"
    ] is True
    assert theorem["current_bridge_forces_the_external_glue_of_that_avatar_to_be_zero"] is True
    assert theorem[
        "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
    ] is True
    assert theorem["that_avatar_is_still_not_the_internal_nonsplit_transport_object"] is True
