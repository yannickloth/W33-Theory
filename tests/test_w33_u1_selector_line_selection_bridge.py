from __future__ import annotations

import pytest

from w33_u1_selector_line_selection_bridge import (
    build_u1_selector_line_selection_bridge_summary,
)


def test_u1_selector_line_selection_bridge_summary() -> None:
    summary = build_u1_selector_line_selection_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["dominant_isotropic_line_index"] == 0
    assert summary["recessive_isotropic_line_index"] == 1
    assert summary["u1_isotropic_line_weights"][0] == pytest.approx(0.29249916729399683)
    assert summary["u1_isotropic_line_weights"][1] == pytest.approx(0.22063099582377832)
    assert summary["dominance_ratio"] == pytest.approx(1.3257392335192142)
    assert summary["u1_first_refinement_form"] == [[0.0, 120.0], [120.0, 0.0]]
    assert summary["u1_selector_first_refinement_packet_form"][0][0] == pytest.approx(
        56.34697845686784
    )
    assert summary["u1_selector_first_refinement_packet_form"][1][1] == pytest.approx(
        4.367635590969976
    )
    theorem = summary["u1_selector_line_selection_theorem"]
    assert theorem["carrier_metric_alone_is_line_blind"] is True
    assert theorem["canonical_selector_u1_component_has_full_rank_2"] is True
    assert theorem["canonical_selector_u1_component_assigns_unequal_weights_to_the_two_isotropic_lines"] is True
    assert theorem["there_is_a_unique_dominant_isotropic_line_inside_u1"] is True
    assert theorem["dominant_isotropic_line_is_the_first_u1_line_in_the_current_canonical_basis"] is True
    assert theorem["selector_line_weights_are_invariant_under_selector_basis_signs_and_swap"] is True
    assert theorem["u1_carrier_form_scales_by_120_at_first_refinement"] is True
    assert theorem["u1_selector_packet_form_scales_by_120_at_first_refinement"] is True
    assert theorem["dominant_line_candidate_is_first_refinement_rigid"] is True
    assert theorem["full_current_external_packet_selects_a_canonical_isotropic_line_candidate_inside_u1"] is True
