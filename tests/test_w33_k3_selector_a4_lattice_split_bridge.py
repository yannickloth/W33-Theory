from __future__ import annotations

import pytest

from w33_k3_selector_a4_lattice_split_bridge import (
    build_k3_selector_a4_lattice_split_bridge_summary,
)


def test_k3_selector_a4_lattice_split_bridge_decomposes_the_packet() -> None:
    summary = build_k3_selector_a4_lattice_split_bridge_summary()
    theorem = summary["selector_a4_lattice_split_theorem"]

    assert summary["status"] == "ok"
    assert summary["common_scalar_prefactor"] == "351/(4 pi^2)"
    assert summary["reconstruction_error_linf"] < 1e-10
    assert theorem["selector_packet_reconstructs_as_three_u_plus_e8_plus_e8"] is True
    assert theorem["three_u_packet_piece_is_positive_definite"] is True
    assert theorem["e8_factor_one_packet_piece_is_negative_definite"] is True
    assert theorem["e8_factor_two_packet_piece_is_negative_definite"] is True
    assert theorem["all_three_packet_pieces_are_nonzero"] is True
    assert theorem["reduced_selector_packet_is_not_carried_by_three_u_alone"] is True
    assert theorem["reduced_selector_packet_is_not_carried_by_a_single_e8_factor"] is True
    assert theorem["reduced_selector_packet_is_tri_supported_across_the_named_k3_split"] is True
    assert theorem["scalar_prefactor_remains_exactly_351_over_4_pi_squared"] is True


def test_k3_selector_a4_lattice_split_bridge_reuses_the_expected_selector_form() -> None:
    summary = build_k3_selector_a4_lattice_split_bridge_summary()

    assert summary["selector_packet_form"] == pytest.approx(
        [
            [0.17052108295416395, 3.017089485800914e-16],
            [3.017089485800914e-16, -0.1262119266964055],
        ]
    )
