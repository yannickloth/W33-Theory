from __future__ import annotations

from w33_u1_head_compatible_line_bridge import (
    build_u1_head_compatible_line_bridge_summary,
)


def test_u1_head_compatible_line_bridge_summary() -> None:
    summary = build_u1_head_compatible_line_bridge_summary()
    theorem = summary["u1_head_compatible_line_theorem"]

    assert summary["internal_common_line"]["generator"] == [1, 1, 0]
    assert summary["internal_common_line"]["role"] == "image_of_common_square"
    assert summary["internal_transport_polarity"]["head_type"] == "invariant"
    assert summary["internal_transport_polarity"]["tail_type"] == "sign"
    assert summary["internal_transport_polarity"]["glue_direction"] == "tail_to_head"
    assert summary["external_u1_line_roles"]["head_compatible_line_candidate"] == [
        0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0
    ]
    assert summary["external_u1_line_roles"]["tail_line_candidate"] == [
        0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0
    ]
    assert theorem["internal_common_line_is_exact_image_side_data"] is True
    assert theorem["internal_transport_head_is_the_image_side_of_the_current_polarity_dictionary"] is True
    assert theorem["external_bridge_fixes_head_biased_and_tail_biased_u1_lines"] is True
    assert theorem["the_sign_ordered_rigid_u1_line_is_exactly_the_head_biased_line"] is True
    assert theorem["the_tail_biased_u1_line_is_not_compatible_with_an_image_side_realization_of_the_internal_common_line"] is True
    assert theorem["the_current_external_line_ambiguity_collapses_to_one_head_compatible_candidate"] is True
