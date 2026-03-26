from __future__ import annotations

from w33_k3_e8_factor_refinement_bridge import build_k3_e8_factor_refinement_bridge_summary


def test_k3_e8_factor_refinement_bridge_lifts_the_named_split() -> None:
    summary = build_k3_e8_factor_refinement_bridge_summary()
    theorem = summary["e8_factor_refinement_theorem"]

    assert summary["status"] == "ok"
    assert theorem["factor_one_seed_form_is_exact_negative_e8_cartan"] is True
    assert theorem["factor_two_seed_form_is_exact_negative_e8_cartan"] is True
    assert theorem["factor_one_refined_form_is_exact_120_times_negative_e8_cartan"] is True
    assert theorem["factor_two_refined_form_is_exact_120_times_negative_e8_cartan"] is True
    assert theorem["e8_factors_remain_exactly_orthogonal_after_refinement"] is True
    assert theorem["full_named_split_scales_by_120"] is True
    assert theorem["normalized_named_split_is_refinement_invariant"] is True
    assert theorem["explicit_named_k3_split_is_first_refinement_rigid"] is True


def test_k3_e8_factor_refinement_bridge_records_expected_seed_blocks() -> None:
    summary = build_k3_e8_factor_refinement_bridge_summary()
    expected_e8 = [
        [-2, 1, 0, 0, 0, 0, 0, 0],
        [1, -2, 1, 0, 0, 0, 0, 0],
        [0, 1, -2, 1, 0, 0, 0, 1],
        [0, 0, 1, -2, 1, 0, 0, 0],
        [0, 0, 0, 1, -2, 1, 0, 0],
        [0, 0, 0, 0, 1, -2, 1, 0],
        [0, 0, 0, 0, 0, 1, -2, 0],
        [0, 0, 1, 0, 0, 0, 0, -2],
    ]

    assert summary["e8_factor_one_seed_form"] == expected_e8
    assert summary["e8_factor_two_seed_form"] == expected_e8
    assert summary["e8_factor_cross_seed_form"] == [[0] * 8 for _ in range(8)]
