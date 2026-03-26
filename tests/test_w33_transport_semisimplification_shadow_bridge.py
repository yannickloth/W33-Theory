from __future__ import annotations

from w33_transport_semisimplification_shadow_bridge import (
    build_transport_semisimplification_shadow_bridge_summary,
)


def test_transport_semisimplification_shadow_bridge_summary() -> None:
    summary = build_transport_semisimplification_shadow_bridge_summary()
    theorem = summary["transport_semisimplification_shadow_theorem"]

    assert summary["internal_transport_semisimplification"] == [81, 81]
    assert summary["external_split_shadow"] == [81, 81]
    assert theorem["internal_semisimplification_is_81_plus_81"] is True
    assert theorem["external_split_shadow_is_81_plus_81"] is True
    assert theorem["internal_and_external_objects_match_exactly_at_semisimplified_shadow_level"] is True
    assert theorem["internal_extension_class_is_nonzero"] is True
    assert theorem["external_extension_class_is_zero"] is True
    assert theorem["transport_k3_match_is_semisimplified_shadow_not_extension_identity"] is True
