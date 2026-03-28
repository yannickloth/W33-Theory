from __future__ import annotations

from w33_transport_filtered_shadow_bridge import (
    build_transport_filtered_shadow_bridge_summary,
)


def test_transport_filtered_shadow_bridge_summary() -> None:
    summary = build_transport_filtered_shadow_bridge_summary()
    theorem = summary["transport_filtered_shadow_theorem"]

    assert summary["internal_transport_filtration"]["short_exact_sequence_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["internal_transport_filtration"]["distinguished_invariant_line"] == [1, 2]
    assert summary["external_canonical_split_filtration"]["ordered_filtration_dimensions"] == [
        81,
        162,
        81,
    ]
    assert summary["external_canonical_split_filtration"]["ordered_line_types"] == [
        "positive",
        "negative",
    ]
    assert theorem["internal_transport_has_canonical_ordered_81_in_162_out_81_filtration"] is True
    assert theorem["external_k3_mixed_plane_has_canonical_ordered_split_81_in_162_out_81_filtration"] is True
    assert theorem["internal_and_external_match_at_ordered_filtered_dimension_level"] is True
    assert theorem["external_filtered_shadow_refines_old_81_plus_81_graded_shadow"] is True
    assert theorem["external_filtered_shadow_is_first_refinement_rigid"] is True
    assert theorem["extension_class_mismatch_remains_exact"] is True
    assert theorem["current_bridge_reaches_filtered_split_shadow_but_not_nonsplit_extension_identity"] is True
