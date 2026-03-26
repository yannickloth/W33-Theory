from __future__ import annotations

from w33_k3_canonical_plane_a4_bridge import build_k3_canonical_plane_a4_bridge_summary


def test_k3_canonical_plane_a4_bridge_resolves_81_vs_162() -> None:
    summary = build_k3_canonical_plane_a4_bridge_summary()
    assert summary["status"] == "ok"

    plane = summary["canonical_mixed_plane"]
    assert plane["source_triangle"] == [1, 2, 3]
    assert plane["split_qutrit_lines"] == [81, 81]
    assert plane["total_qutrit_size"] == 162
    assert plane["realizes_universal_rank2_factor"] == 2

    a4 = summary["local_a4_data"]
    assert a4["finite_multiplier"] == 81
    assert a4["delta_A4"] == "1209/9194 a0"
    assert a4["after_rank2_factor_prefactor"] == "27/(16 pi^2)"
    assert a4["local_gauge_packet_is_pure_A4"] is True

    transport = summary["curved_transport_split"]
    assert transport["protected_flat_81_copy"] == 81
    assert transport["curvature_hits_only_other_81_copy"] is True

    theorem = summary["resolution_theorem"]
    assert theorem["canonical_plane_realizes_universal_rank2_factor_two"] is True
    assert theorem["curvature_sensitive_internal_multiplier_is_81"] is True
    assert theorem["total_branch_size_162_is_not_the_finite_multiplier"] is True
    assert theorem["local_A4_packet_counts_81_times_rank2_factor_2"] is True
