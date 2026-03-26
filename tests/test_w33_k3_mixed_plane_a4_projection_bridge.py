from __future__ import annotations

from w33_k3_mixed_plane_a4_projection_bridge import (
    build_k3_mixed_plane_a4_projection_summary,
)


def test_k3_mixed_plane_a4_projection_bridge_resolves_81_vs_162_exactly() -> None:
    summary = build_k3_mixed_plane_a4_projection_summary()
    assert summary["status"] == "ok"

    plane = summary["canonical_mixed_plane"]
    assert plane["selector_triangle"] == (1, 2, 3)
    assert plane["qutrit_lift_split"] == (81, 81)
    assert plane["total_qutrit_lift_dimension"] == 162
    assert plane["normalized_restricted_determinant"] < 0.0

    a4 = summary["local_a4_packet"]
    assert a4["finite_trace_multiplier"] == 81
    assert a4["rank_two_external_activation_is_required"] is True
    assert a4["exact_reduced_prefactor_is_27_over_16_pi_sq"] is True
    assert a4["bridge_packet_is_purely_a4"] is True

    theorem = summary["projection_theorem"]
    assert theorem["canonical_mixed_plane_is_rank2_active"] is True
    assert theorem["branch_dimension_is_162"] is True
    assert theorem["finite_trace_multiplier_is_81"] is True
    assert theorem["branch_dimension_equals_2_times_trace_multiplier"] is True
    assert theorem["factor_of_two_is_exact_rank2_external_factor"] is True
    assert theorem["projecting_to_canonical_mixed_plane_does_not_promote_multiplier_to_162"] is True
    assert theorem["eightyone_vs_one_sixtytwo_is_dimension_vs_trace_split"] is True
    assert theorem["split_vs_nonsplit_obstruction_remains_after_projection"] is True
