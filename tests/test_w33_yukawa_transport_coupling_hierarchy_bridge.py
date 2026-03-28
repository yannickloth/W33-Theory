from w33_yukawa_transport_coupling_hierarchy_bridge import (
    build_yukawa_transport_coupling_hierarchy_bridge_summary,
)


def test_yukawa_transport_coupling_hierarchy_bridge_summary() -> None:
    summary = build_yukawa_transport_coupling_hierarchy_bridge_summary()
    theorem = summary["yukawa_transport_coupling_hierarchy_theorem"]

    assert summary["coupling_levels"]["plane_level"] == "U1"
    assert summary["coupling_levels"]["avatar_level"] == [81, 162, 81]
    assert summary["coupling_levels"]["broader_local_context"] == "U3"
    assert theorem["the_central_image_channel_couples_at_line_level"] is True
    assert theorem["the_first_family_sensitive_a4_entry_couples_at_plane_level"] is True
    assert theorem["non_split_transport_identity_requires_avatar_level_support"] is True
    assert theorem[
        "the_broader_five_factor_packet_remains_local_context_not_the_minimal_exact_coupling_target"
    ] is True
    assert theorem[
        "the_live_unresolved_family_closure_is_support_filtered_as_line_inside_plane_inside_avatar"
    ] is True
    assert theorem[
        "the_unresolved_family_packet_does_not_reduce_to_u3_even_though_u3_is_locally_dominant"
    ] is True
