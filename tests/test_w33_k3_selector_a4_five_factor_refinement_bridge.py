from __future__ import annotations

import pytest

from w33_k3_selector_a4_five_factor_refinement_bridge import (
    build_k3_selector_a4_five_factor_refinement_bridge_summary,
)


def test_selector_a4_five_factor_refinement_bridge_summary() -> None:
    summary = build_k3_selector_a4_five_factor_refinement_bridge_summary()
    theorem = summary["selector_a4_five_factor_refinement_theorem"]

    assert summary["u_factor_one_seed_form"][0][0] == pytest.approx(0.469558153807232)
    assert summary["u_factor_one_first_refinement_form"][0][0] == pytest.approx(56.34697845686784)
    assert summary["u_factor_three_first_refinement_form"][0][0] == pytest.approx(278.412508703683)
    assert summary["e8_factor_two_first_refinement_form"][0][0] == pytest.approx(-287.40674423320713)
    assert theorem["u_factor_one_packet_piece_scales_by_120"] is True
    assert theorem["u_factor_two_packet_piece_scales_by_120"] is True
    assert theorem["u_factor_three_packet_piece_scales_by_120"] is True
    assert theorem["e8_factor_one_packet_piece_scales_by_120"] is True
    assert theorem["e8_factor_two_packet_piece_scales_by_120"] is True
    assert theorem["all_five_normalized_packet_forms_are_refinement_invariant"] is True
    assert theorem["all_three_u_factor_packet_pieces_stay_mixed_signature"] is True
    assert theorem["both_e8_packet_pieces_stay_negative_definite"] is True
    assert theorem["fine_selector_packet_split_is_first_refinement_rigid"] is True
