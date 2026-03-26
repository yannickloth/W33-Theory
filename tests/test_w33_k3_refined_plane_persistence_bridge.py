from __future__ import annotations

import numpy as np

from w33_k3_refined_plane_persistence_bridge import (
    build_k3_refined_plane_persistence_bridge_summary,
)


def test_k3_refined_plane_persistence_bridge_scales_by_120() -> None:
    summary = build_k3_refined_plane_persistence_bridge_summary()
    assert summary["status"] == "ok"

    seed = np.array(summary["seed_restricted_form"]["matrix"], dtype=float)
    refined = np.array(summary["first_refinement_restricted_form"]["matrix"], dtype=float)

    assert summary["first_refinement_scale_factor"] == 120
    assert np.allclose(refined, 120.0 * seed)

    theorem = summary["refinement_theorem"]
    assert theorem["first_barycentric_pullback_scales_restricted_form_by_120"] is True
    assert theorem["restricted_determinant_scales_by_120_squared"] is True
    assert theorem["normalized_restricted_form_is_refinement_invariant"] is True
    assert theorem["mixed_signature_survives_first_refinement"] is True
    assert theorem["top_simplex_multiplier_matches_restricted_form_scale"] is True
