from __future__ import annotations

from w33_e13_visibility_obstruction_bridge import (
    build_e13_visibility_obstruction_bridge_summary,
)


def test_e13_visibility_obstruction_bridge_summary() -> None:
    summary = build_e13_visibility_obstruction_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["internal_common_square"] == [[0, 0, 2], [0, 0, 0], [0, 0, 0]]
    assert summary["internal_common_line_generator"] == [1, 1, 0]
    assert summary["external_canonical_carrier_plane"] == "U1"
    assert summary["external_canonical_line_candidate"] == [0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    assert summary["external_graded_shadow"] == [81, 81]
    theorem = summary["e13_visibility_obstruction_theorem"]
    assert theorem["internal_common_square_is_exact_central_2e13_channel"] is True
    assert theorem["image_of_the_common_square_is_the_internal_common_line"] is True
    assert theorem["current_external_bridge_fixes_the_canonical_u1_carrier_plane"] is True
    assert theorem["current_external_bridge_picks_a_canonical_line_candidate_for_the_e13_image"] is True
    assert theorem["exact_external_identification_of_the_e13_image_with_the_internal_common_line_is_not_yet_supported"] is True
    assert theorem["current_external_bridge_matches_only_the_graded_shadow_of_the_transport_channel"] is True
    assert theorem["current_bridge_captures_carrier_plane_line_candidate_and_graded_shadow_of_the_central_channel"] is True
    assert theorem["exact_external_realization_of_the_central_2e13_channel_is_not_yet_supported"] is True
