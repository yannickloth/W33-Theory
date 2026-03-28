from w33_e13_a4_support_stratification_bridge import (
    build_e13_a4_support_stratification_bridge_summary,
)


def test_e13_a4_support_stratification_bridge_summary() -> None:
    summary = build_e13_a4_support_stratification_bridge_summary()
    theorem = summary["e13_a4_support_stratification_theorem"]

    assert summary["support_levels"]["minimal_a4_carrier_plane"] == "U1"
    assert summary["support_levels"]["rigid_transport_avatar_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["support_levels"]["broader_local_packet_dominant_piece"] == "U3"
    assert theorem[
        "the_central_image_side_2e13_channel_localizes_to_the_head_line_in_any_exact_completion"
    ] is True
    assert theorem[
        "the_first_family_sensitive_a4_bridge_packet_has_minimal_canonical_plane_carrier_u1"
    ] is True
    assert theorem[
        "exact_transport_completion_uses_the_full_rigid_avatar_shell_81_to_162_to_81"
    ] is True
    assert theorem[
        "the_broader_five_factor_packet_is_local_selector_context_not_the_minimal_exact_family_carrier"
    ] is True
    assert theorem[
        "the_live_2e13_a4_bridge_is_exactly_stratified_as_head_line_inside_u1_inside_avatar"
    ] is True
