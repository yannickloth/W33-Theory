from __future__ import annotations

import pytest

from w33_u1_filtered_shadow_line_order_bridge import (
    build_u1_filtered_shadow_line_order_bridge_summary,
)


def test_u1_filtered_shadow_line_order_bridge_summary() -> None:
    summary = build_u1_filtered_shadow_line_order_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["ordered_filtered_shadow_line_types"] == ["positive", "negative"]
    assert summary["u1_positive_selector_weights"][0] == pytest.approx(0.2773869501109481)
    assert summary["u1_positive_selector_weights"][1] == pytest.approx(0.19871596313260903)
    assert summary["u1_negative_selector_weights"][0] == pytest.approx(0.015112217183048728)
    assert summary["u1_negative_selector_weights"][1] == pytest.approx(0.021915032691169296)
    assert summary["u1_positive_minus_negative_selector_gaps"][0] == pytest.approx(
        0.2622747329278994
    )
    assert summary["u1_positive_minus_negative_selector_gaps"][1] == pytest.approx(
        0.17680093044143974
    )
    assert summary["dominant_isotropic_line_index"] == 0
    assert summary["recessive_isotropic_line_index"] == 1
    theorem = summary["u1_filtered_shadow_line_order_theorem"]
    assert theorem["filtered_shadow_basis_is_canonically_ordered_positive_then_negative"] is True
    assert theorem["dominant_u1_line_has_strictly_larger_positive_selector_weight"] is True
    assert theorem["dominant_u1_line_has_strictly_smaller_negative_selector_contamination"] is True
    assert theorem["dominant_u1_line_maximizes_positive_minus_negative_selector_gap"] is True
    assert theorem["sign_order_refines_total_weight_order"] is True
    assert theorem["sign_ordered_line_candidate_is_first_refinement_rigid"] is True
    assert theorem["current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"] is True
