from __future__ import annotations

from math import isclose

from w33_k3_selector_shadow_refinement_bridge import (
    build_k3_selector_shadow_refinement_bridge_summary,
)


def test_k3_selector_shadow_refinement_bridge_scales_all_three_forms_by_120() -> None:
    summary = build_k3_selector_shadow_refinement_bridge_summary()
    theorem = summary["selector_shadow_refinement_theorem"]

    assert summary["status"] == "ok"
    assert theorem["selector_plane_scales_by_120"] is True
    assert theorem["three_u_shadow_scales_by_120"] is True
    assert theorem["rank16_residual_scales_by_120"] is True
    assert theorem["normalized_selector_form_is_refinement_invariant"] is True
    assert theorem["normalized_three_u_shadow_form_is_refinement_invariant"] is True
    assert theorem["normalized_rank16_residual_form_is_refinement_invariant"] is True
    assert theorem["three_u_shadow_stays_positive_definite"] is True
    assert theorem["rank16_residual_stays_negative_definite"] is True


def test_k3_selector_shadow_refinement_bridge_records_expected_seed_and_refined_forms() -> None:
    summary = build_k3_selector_shadow_refinement_bridge_summary()

    selector_seed = summary["selector_seed_form"]
    selector_refined = summary["selector_first_refinement_form"]
    shadow_seed = summary["three_u_shadow_seed_form"]
    shadow_refined = summary["three_u_shadow_first_refinement_form"]
    residual_seed = summary["rank16_residual_seed_form"]
    residual_refined = summary["rank16_residual_first_refinement_form"]

    assert isclose(selector_seed[0][0], 0.17052108282296116, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(selector_seed[1][1], -0.12621192674615103, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(selector_refined[0][0], 120.0 * selector_seed[0][0], rel_tol=0.0, abs_tol=1e-8)
    assert isclose(selector_refined[1][1], 120.0 * selector_seed[1][1], rel_tol=0.0, abs_tol=1e-8)

    assert isclose(shadow_seed[0][0], 2.80248518688132, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(shadow_seed[1][1], 0.2518300163799555, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(shadow_refined[0][1], 120.0 * shadow_seed[0][1], rel_tol=0.0, abs_tol=1e-7)

    assert isclose(residual_seed[0][0], -2.6319641040583783, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(residual_seed[1][1], -0.3780419431261282, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(residual_refined[0][1], 120.0 * residual_seed[0][1], rel_tol=0.0, abs_tol=1e-7)
