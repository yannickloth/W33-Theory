from w33_minimal_external_completion_data_bridge import (
    build_minimal_external_completion_data_bridge_summary,
)


def test_minimal_external_completion_data_bridge_summary() -> None:
    summary = build_minimal_external_completion_data_bridge_summary()
    theorem = summary["minimal_external_completion_data_theorem"]

    assert summary["locked_external_transport_shell"]["ordered_filtration_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["locked_external_transport_shell"]["slot_direction"] == (
        "tail_to_head"
    )
    assert summary["locked_external_transport_shell"]["slot_shape"] == [81, 81]
    assert summary["locked_external_transport_shell"]["current_external_slot_state"] == (
        "zero_by_splitness"
    )
    assert summary["minimal_new_external_data"]["slot_matrix_normal_form"] == "I_81"
    assert summary["minimal_new_external_data"][
        "polarized_nilpotent_normal_form"
    ] == "J2^81"
    assert theorem[
        "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
    ] is True
    assert theorem[
        "no_additional_line_plane_or_dimension_choice_remains_after_the_current_bridge_reductions"
    ] is True
