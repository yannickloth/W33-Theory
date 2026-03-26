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
    assert summary["external_semisimplified_shadow"] == [81, 81]
    theorem = summary["family_flag_visibility_obstruction_theorem"]
    assert theorem["internal_family_flag_is_exact_line_in_plane_data"] is True
    assert theorem["external_side_fixes_a_canonical_carrier_plane_u1"] is True
    assert theorem["external_side_is_line_blind_inside_u1"] is True
    assert theorem["external_side_matches_only_the_graded_shadow_of_the_transport_162_sector"] is True
    assert theorem["exact_external_identification_of_the_internal_common_line_is_not_yet_supported"] is True
    assert theorem["exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported"] is True
    assert theorem["current_bridge_fixes_plane_and_graded_shadow_but_not_full_internal_flag_object"] is True
