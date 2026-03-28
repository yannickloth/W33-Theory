from w33_common_line_exact_image_bridge import (
    build_common_line_exact_image_bridge_summary,
)


def test_common_line_exact_image_bridge_summary() -> None:
    summary = build_common_line_exact_image_bridge_summary()
    theorem = summary["common_line_exact_image_theorem"]

    assert summary["internal_common_line"]["generator"] == [1, 1, 0]
    assert summary["internal_common_line"]["fiber_shift_matrix"] == [[0, 1], [0, 0]]
    assert summary["forced_external_image_line"]["carrier_plane"] == "U1"
    assert theorem[
        "internal_common_line_is_exactly_the_image_of_the_common_square"
    ] is True
    assert theorem[
        "internal_transport_operator_image_is_the_head_invariant_line"
    ] is True
    assert theorem[
        "any_exact_external_completion_has_the_same_transport_operator_normal_form_up_to_basis_gauge"
    ] is True
    assert theorem[
        "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
    ] is True
    assert theorem[
        "what_remains_open_is_existence_of_that_exact_completion_not_choice_of_image_line"
    ] is True
