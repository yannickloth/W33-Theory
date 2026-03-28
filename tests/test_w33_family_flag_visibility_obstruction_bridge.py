from __future__ import annotations

from w33_family_flag_visibility_obstruction_bridge import (
    build_family_flag_visibility_obstruction_bridge_summary,
)


def test_family_flag_visibility_obstruction_bridge_summary() -> None:
    summary = build_family_flag_visibility_obstruction_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["internal_common_line_generator"] == [1, 1, 0]
    assert summary["internal_common_plane_equation"] == "x = y"
    assert summary["external_canonical_carrier_plane"] == "U1"
    assert summary["external_canonical_line_candidate"] == [0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    assert summary["external_sign_ordered_line_candidate"] == [0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    assert summary["external_semisimplified_shadow"] == [81, 81]
    assert summary["external_filtered_split_shadow"] == [81, 162, 81]
    assert summary["external_nilpotent_glue_visibility"] == {
        "matches_internal_nilpotent_glue": False,
        "reason": "external_filtered_shadow_is_split",
    }
    theorem = summary["family_flag_visibility_obstruction_theorem"]
    assert theorem["internal_family_flag_is_exact_line_in_plane_data"] is True
    assert theorem["external_side_fixes_a_canonical_carrier_plane_u1"] is True
    assert theorem["carrier_metric_alone_is_line_blind_inside_u1"] is True
    assert theorem["full_external_packet_selects_a_canonical_line_candidate_inside_u1"] is True
    assert theorem["filtered_shadow_sign_order_fixes_the_same_canonical_u1_line_candidate"] is True
    assert theorem["external_side_still_matches_the_graded_shadow_of_the_transport_162_sector"] is True
    assert theorem["external_side_matches_a_canonical_filtered_split_shadow_of_the_transport_162_sector"] is True
    assert theorem["external_side_does_not_yet_realize_the_internal_rank_81_nilpotent_glue"] is True
    assert theorem["exact_external_identification_of_the_internal_common_line_is_not_yet_supported"] is True
    assert theorem["exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported"] is True
    assert theorem["current_bridge_fixes_plane_line_candidate_and_filtered_shadow_but_not_full_extension_object"] is True
