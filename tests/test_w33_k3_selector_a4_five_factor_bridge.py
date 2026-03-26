from __future__ import annotations

import pytest

from w33_k3_selector_a4_five_factor_bridge import (
    build_k3_selector_a4_five_factor_bridge_summary,
)


def test_selector_a4_five_factor_bridge_summary() -> None:
    summary = build_k3_selector_a4_five_factor_bridge_summary()
    theorem = summary["selector_a4_five_factor_theorem"]

    assert summary["common_scalar_prefactor"] == "351/(4 pi^2)"
    assert summary["reconstruction_error_linf"] < 1e-10
    assert summary["u_factor_one_packet_form"][0][0] == pytest.approx(0.469558153807232)
    assert summary["u_factor_two_packet_form"][1][1] == pytest.approx(0.06475792755064227)
    assert summary["u_factor_three_packet_form"][0][0] == pytest.approx(2.3201042391973585)
    assert summary["e8_factor_one_packet_form"][0][0] == pytest.approx(-0.2369079021220062)
    assert summary["e8_factor_two_packet_form"][0][0] == pytest.approx(-2.3950562019433925)
    assert theorem["three_u_packet_reconstructs_as_u1_plus_u2_plus_u3"] is True
    assert theorem["selector_packet_reconstructs_as_u1_plus_u2_plus_u3_plus_e8_plus_e8"] is True
    assert theorem["u_factor_one_packet_piece_is_mixed_signature"] is True
    assert theorem["u_factor_two_packet_piece_is_mixed_signature"] is True
    assert theorem["u_factor_three_packet_piece_is_mixed_signature"] is True
    assert theorem["e8_factor_one_packet_piece_is_negative_definite"] is True
    assert theorem["e8_factor_two_packet_piece_is_negative_definite"] is True
    assert theorem["all_five_packet_pieces_are_nonzero"] is True
    assert theorem["distinguished_u1_plane_has_nonzero_selector_packet_piece"] is True
    assert theorem["selector_hyperbolic_packet_is_not_supported_on_u1_alone"] is True
    assert theorem["reduced_selector_packet_is_five_supported_across_u_u_u_e8_e8"] is True
    assert theorem["scalar_prefactor_remains_exactly_351_over_4_pi_squared"] is True
