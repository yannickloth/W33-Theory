from w33_transport_avatar_deformation_wall_bridge import (
    build_transport_avatar_deformation_wall_bridge_summary,
)


def test_transport_avatar_deformation_wall_bridge_summary() -> None:
    summary = build_transport_avatar_deformation_wall_bridge_summary()
    theorem = summary["transport_avatar_deformation_wall_theorem"]

    assert summary["canonical_split_avatar"]["ordered_filtration_dimensions"] == [81, 162, 81]
    assert summary["canonical_split_avatar"]["glue_direction"] == "tail_to_head"
    assert summary["canonical_split_avatar"]["external_glue_rank"] == 0
    assert summary["canonical_split_avatar"]["external_glue_state"] == "zero_by_splitness"
    assert summary["remaining_completion_datum"]["slot_direction"] == "tail_to_head"
    assert summary["remaining_completion_datum"]["slot_shape"] == [81, 81]
    assert summary["remaining_completion_datum"]["required_internal_rank"] == 81
    assert summary["remaining_completion_datum"]["required_internal_square_zero"] is True
    assert summary["remaining_completion_datum"]["current_external_rank"] == 0
    assert summary["remaining_completion_datum"]["current_external_state"] == "zero_by_splitness"
    assert theorem["current_bridge_has_already_fixed_one_canonical_rigid_split_transport_avatar"] is True
    assert theorem[
        "exact_transport_identity_would_require_adjoining_a_nonzero_tail_to_head_81_by_81_glue_operator_to_that_avatar"
    ] is True
    assert theorem[
        "any_exact_completion_must_preserve_the_fixed_head_line_tail_line_and_ordered_dimensions_of_the_avatar"
    ] is True
    assert theorem[
        "the_remaining_transport_wall_is_a_nonsplit_deformation_problem_not_a_search_for_an_unfixed_external_packet"
    ] is True
