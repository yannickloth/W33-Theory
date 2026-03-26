from __future__ import annotations

from w33_k3_three_u_refinement_bridge import build_k3_three_u_refinement_bridge_summary


def test_k3_three_u_refinement_bridge_preserves_the_full_hyperbolic_core() -> None:
    summary = build_k3_three_u_refinement_bridge_summary()
    theorem = summary["three_u_refinement_theorem"]

    assert summary["status"] == "ok"
    assert theorem["three_u_block_scales_by_120"] is True
    assert theorem["seed_form_is_exact_3u"] is True
    assert theorem["first_refinement_form_is_exact_120_times_3u"] is True
    assert theorem["normalized_three_u_block_is_refinement_invariant"] is True
    assert theorem["three_u_signature_survives_first_refinement"] is True
    assert theorem["three_u_determinant_scales_by_120_to_the_6"] is True


def test_k3_three_u_refinement_bridge_records_exact_seed_and_refined_forms() -> None:
    summary = build_k3_three_u_refinement_bridge_summary()

    assert summary["three_u_seed_form"] == [
        [0, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0],
    ]
    assert summary["three_u_first_refinement_form"] == [
        [0, 120, 0, 0, 0, 0],
        [120, 0, 0, 0, 0, 0],
        [0, 0, 0, 120, 0, 0],
        [0, 0, 120, 0, 0, 0],
        [0, 0, 0, 0, 0, 120],
        [0, 0, 0, 0, 120, 0],
    ]
