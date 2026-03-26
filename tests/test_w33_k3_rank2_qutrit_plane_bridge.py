from __future__ import annotations

from w33_k3_rank2_qutrit_plane_bridge import (
    build_k3_rank2_qutrit_plane_bridge_summary,
)


def _plane(summary: dict, plane_type: str) -> dict:
    for plane in summary["rank2_plane_types"]:
        if plane["plane_type"] == plane_type:
            return plane
    raise AssertionError(f"missing plane type {plane_type}")


def test_k3_rank2_qutrit_plane_bridge_classifies_minimal_branch_types() -> None:
    summary = build_k3_rank2_qutrit_plane_bridge_summary()
    assert summary["status"] == "ok"

    host = summary["k3_middle_degree_host"]
    assert host["logical_qutrits"] == 81
    assert host["b2_plus"] == 3
    assert host["b2_minus"] == 19
    assert host["total_middle_degree_qutrit_channel"] == 1782

    positive = _plane(summary, "positive_rank2")
    assert positive["positive_h2_directions"] == 2
    assert positive["negative_h2_directions"] == 0
    assert positive["positive_qutrit_modes"] == 162
    assert positive["negative_qutrit_modes"] == 0
    assert positive["total_qutrit_modes"] == 162

    mixed = _plane(summary, "mixed_rank2")
    assert mixed["positive_h2_directions"] == 1
    assert mixed["negative_h2_directions"] == 1
    assert mixed["positive_qutrit_modes"] == 81
    assert mixed["negative_qutrit_modes"] == 81
    assert mixed["total_qutrit_modes"] == 162

    negative = _plane(summary, "negative_rank2")
    assert negative["positive_h2_directions"] == 0
    assert negative["negative_h2_directions"] == 2
    assert negative["positive_qutrit_modes"] == 0
    assert negative["negative_qutrit_modes"] == 162
    assert negative["total_qutrit_modes"] == 162

    constraints = summary["bridge_constraints"]
    assert constraints["k3_supports_positive_rank2_plane"] is True
    assert constraints["k3_supports_mixed_rank2_plane"] is True
    assert constraints["k3_supports_negative_rank2_plane"] is True
    assert constraints["minimal_rank2_qutrit_branch_dimension"] == 162
    assert constraints["mixed_rank2_qutrit_split"] == [81, 81]
    assert constraints["minimal_rank2_branch_matches_transport_extension_size"] is True
