from __future__ import annotations

from w33_curved_h2_cup_plane_bridge import build_curved_h2_cup_plane_bridge_summary


def test_curved_h2_cup_plane_bridge_recovers_seed_signatures_and_canonical_k3_plane() -> None:
    summary = build_curved_h2_cup_plane_bridge_summary()
    assert summary["status"] == "ok"

    cp2, k3 = summary["seed_profiles"]

    assert cp2["name"] == "CP2_9"
    assert cp2["harmonic_h2_dimension"] == 1
    assert cp2["positive_h2_directions"] == 1
    assert cp2["negative_h2_directions"] == 0
    assert cp2["signature"] == 1
    assert cp2["fundamental_cycle_is_closed"] is True
    assert cp2["cup_symmetry_max_abs_error"] < 1e-12

    assert k3["name"] == "K3_16"
    assert k3["harmonic_h2_dimension"] == 22
    assert k3["positive_h2_directions"] == 3
    assert k3["negative_h2_directions"] == 19
    assert k3["signature"] == -16
    assert k3["fundamental_cycle_is_closed"] is True
    assert k3["cup_symmetry_max_abs_error"] < 1e-12

    plane = summary["k3_canonical_mixed_plane"]
    assert plane["selector_triangle"] == (1, 2, 3)
    assert plane["mixed_signature"] == (1, 1)
    assert plane["qutrit_lift_split"] == (81, 81)
    assert plane["total_qutrit_lift_dimension"] == 162
    assert plane["split_qutrit_package"] is True
    assert plane["positive_line_q_norm"] > 0.0
    assert plane["negative_line_q_norm"] < 0.0

    normalized = plane["normalized_restricted_intersection_matrix"]
    assert abs(normalized[0][0] - 1.0) < 1e-12
    assert abs(normalized[1][1] + 1.0) < 1e-12
    assert abs(normalized[0][1]) < 1e-12
    assert abs(normalized[1][0]) < 1e-12
    assert abs(plane["normalized_restricted_determinant"] + 1.0) < 1e-12

    constraints = summary["bridge_constraints"]
    assert constraints["cup_form_recovers_recorded_seed_signatures"] is True
    assert constraints["cp2_h2_signature_from_cup_form"] == 1
    assert constraints["k3_h2_signature_from_cup_form"] == -16
    assert constraints["k3_positive_h2_directions_from_cup_form"] == 3
    assert constraints["k3_negative_h2_directions_from_cup_form"] == 19
    assert constraints["canonical_k3_mixed_plane_has_nonzero_intersection_determinant"] is True
    assert constraints["canonical_k3_mixed_plane_is_split_as_positive_plus_negative_line"] is True
