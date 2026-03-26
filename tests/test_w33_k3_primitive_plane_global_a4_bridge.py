from __future__ import annotations

from w33_k3_primitive_plane_global_a4_bridge import (
    build_k3_primitive_plane_global_a4_bridge_summary,
)


def test_k3_primitive_plane_global_a4_bridge_fixes_reduced_external_prefactor() -> None:
    summary = build_k3_primitive_plane_global_a4_bridge_summary()
    assert summary["status"] == "ok"

    assert summary["primitive_plane_seed_form"] == [[0, 1], [1, 0]]
    assert summary["primitive_plane_first_refinement_form"] == [[0, 120], [120, 0]]
    assert summary["curvature_quantum_lock"]["Q_curv"] == "52"
    assert summary["reduced_prefactors"]["local"] == "27/(16 pi^2)"
    assert summary["reduced_prefactors"]["normalized_global"] == "351/(4 pi^2)"
    assert summary["reduced_prefactors"]["raw_first_refinement"] == "10530/pi^2"

    theorem = summary["global_a4_coupling_theorem"]
    assert theorem["primitive_plane_seed_quantum_is_plus_one"] is True
    assert theorem["primitive_plane_first_refinement_quantum_is_plus_120"] is True
    assert theorem["normalized_plane_quantum_is_refinement_invariant"] is True
    assert theorem["coupling_to_Q_curv_is_exact"] is True
    assert theorem["reduced_global_prefactor_is_351_over_4_pi_squared"] is True
    assert theorem["raw_sd1_prefactor_is_10530_over_pi_squared"] is True
    assert theorem["sign_is_fixed_positive_on_the_canonical_oriented_plane"] is True
