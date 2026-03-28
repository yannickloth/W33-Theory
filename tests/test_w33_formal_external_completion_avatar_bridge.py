from w33_formal_external_completion_avatar_bridge import (
    build_formal_external_completion_avatar_bridge_summary,
)


def test_formal_external_completion_avatar_bridge_summary() -> None:
    summary = build_formal_external_completion_avatar_bridge_summary()
    theorem = summary["formal_external_completion_avatar_theorem"]

    assert summary["formal_external_completion_avatar"][
        "ordered_filtration_dimensions"
    ] == [81, 162, 81]
    assert summary["formal_external_completion_avatar"]["carrier_plane"] == "U1"
    assert summary["formal_external_completion_avatar"]["slot_direction"] == (
        "tail_to_head"
    )
    assert summary["formal_external_completion_avatar"]["slot_matrix_normal_form"] == (
        "I_81"
    )
    assert summary["formal_external_completion_avatar"][
        "polarized_nilpotent_normal_form"
    ] == "J2^81"
    assert theorem[
        "the_forced_image_line_and_the_nonzero_glue_live_on_one_common_formal_external_object"
    ] is True
    assert theorem[
        "the_missing_piece_is_now_current_k3_realization_not_common_object_design"
    ] is True
