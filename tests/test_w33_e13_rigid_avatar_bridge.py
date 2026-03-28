from w33_e13_rigid_avatar_bridge import build_e13_rigid_avatar_bridge_summary


def test_e13_rigid_avatar_bridge_summary() -> None:
    summary = build_e13_rigid_avatar_bridge_summary()
    theorem = summary["e13_rigid_avatar_theorem"]

    assert summary["internal_central_channel"]["common_square"] == [
        [0, 0, 2],
        [0, 0, 0],
        [0, 0, 0],
    ]
    assert summary["internal_central_channel"]["common_line_generator"] == [1, 1, 0]
    assert summary["current_external_avatar_realization"]["head_line"] == [
        0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0
    ]
    assert summary["current_external_avatar_realization"]["tail_line"] == [
        0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0
    ]
    assert summary["current_external_avatar_realization"]["ordered_filtration_dimensions"] == [
        81, 162, 81
    ]
    assert summary["current_external_avatar_realization"]["external_glue_state"] == (
        "zero_by_splitness"
    )
    assert theorem["internal_central_2e13_channel_is_exact"] is True
    assert theorem[
        "the_unique_bridge_compatible_external_image_of_the_internal_common_line_is_the_head_line_of_the_rigid_avatar"
    ] is True
    assert theorem[
        "the_current_external_realization_of_the_central_channel_factors_through_the_canonical_rigid_split_avatar"
    ] is True
    assert theorem[
        "exact_external_realization_of_the_central_2e13_channel_would_require_a_nonsplit_deformation_of_that_avatar"
    ] is True
    assert theorem[
        "any_exact_completion_of_that_avatar_has_the_unique_full_rank_glue_normal_form_two_power_81"
    ] is True
