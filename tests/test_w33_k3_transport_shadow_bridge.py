from __future__ import annotations

from w33_k3_transport_shadow_bridge import build_k3_transport_shadow_bridge_summary


def test_k3_transport_shadow_bridge_records_shadow_match_and_obstruction() -> None:
    summary = build_k3_transport_shadow_bridge_summary()
    assert summary["status"] == "ok"

    canonical = summary["canonical_mixed_plane"]
    assert canonical["source_triangle"] == [1, 2, 3]
    assert canonical["plane_basis_order"] == ["positive_line", "negative_line"]
    assert canonical["positive_qutrit_modes"] == 81
    assert canonical["negative_qutrit_modes"] == 81
    assert canonical["total_qutrit_modes"] == 162
    assert canonical["is_split_two_line_package"] is True

    transport = summary["internal_transport_extension"]
    assert transport["short_exact_sequence_dimensions"] == [81, 162, 81]
    assert transport["is_nonsplit"] is True
    assert transport["invariant_complement_count"] == 0
    assert transport["protected_flat_81_copy"] == 81
    assert transport["curvature_hits_only_other_81_copy"] is True

    theorem = summary["comparison_theorem"]
    assert theorem["two_step_dimension_shadow_matches_exactly"] is True
    assert theorem["canonical_plane_matches_transport_size_shadow"] is True
    assert theorem["canonical_plane_is_split"] is True
    assert theorem["transport_extension_is_nonsplit"] is True
    assert theorem["exact_identification_as_extension_object_is_obstructed"] is True
