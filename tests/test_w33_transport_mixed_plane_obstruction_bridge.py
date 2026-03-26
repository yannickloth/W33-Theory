from __future__ import annotations

from w33_transport_mixed_plane_obstruction_bridge import (
    build_transport_mixed_plane_obstruction_summary,
)


def test_transport_mixed_plane_obstruction_bridge_proves_split_vs_nonsplit_gap() -> None:
    summary = build_transport_mixed_plane_obstruction_summary()
    assert summary["status"] == "ok"

    internal = summary["internal_transport_extension"]
    assert internal["short_exact_sequence_dimensions"] == [81, 162, 81]
    assert internal["is_nonsplit_extension_of_sign_by_trivial"] is True
    assert internal["invariant_complement_count"] == 0
    assert internal["nonsplit_extension_witness_count"] > 0

    external = summary["external_canonical_mixed_plane"]
    assert external["selector_triangle"] == (1, 2, 3)
    assert external["qutrit_lift_split"] == (81, 81)
    assert external["total_qutrit_lift_dimension"] == 162
    assert external["split_qutrit_package"] is True
    assert external["mixed_signature"] == (1, 1)

    comparison = summary["comparison_theorem"]
    assert comparison["dimension_pattern_matches_exactly"] is True
    assert comparison["internal_transport_162_is_nonsplit"] is True
    assert comparison["external_mixed_plane_162_is_split"] is True
    assert comparison["exact_identification_between_current_structures_is_supported"] is False
    assert comparison["exact_split_vs_nonsplit_obstruction_is_present"] is True
    assert comparison["only_dimensional_compatibility_is_currently_exact"] is True
