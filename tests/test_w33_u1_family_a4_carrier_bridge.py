from __future__ import annotations

from w33_u1_family_a4_carrier_bridge import (
    build_u1_family_a4_carrier_bridge_summary,
)


def test_u1_family_a4_carrier_bridge_summary() -> None:
    summary = build_u1_family_a4_carrier_bridge_summary()
    theorem = summary["u1_family_a4_carrier_theorem"]

    assert summary["internal_family_entry"]["delta_A4"] == "1209/9194 a0"
    assert summary["canonical_external_carrier"]["plane_name"] == "U1"
    assert summary["canonical_external_carrier"]["normalized_global_prefactor"] == "351/(4 pi^2)"
    assert summary["internal_family_boundary_condition"]["common_line_generator"] == [1, 1, 0]
    assert summary["internal_family_boundary_condition"]["common_plane_equation"] == "x = y"
    assert summary["internal_family_boundary_condition"]["distinguished_generation"] == 2
    assert theorem["first_family_entry_is_a4_only"] is True
    assert theorem["canonical_external_carrier_equals_u_factor_one"] is True
    assert theorem["canonical_u1_carrier_has_exact_351_over_4_pi_squared_coupling"] is True
    assert theorem["canonical_u1_carrier_has_positive_seed_and_first_refinement_quantum"] is True
    assert theorem["u1_is_nonzero_piece_of_full_selector_packet"] is True
    assert theorem["full_selector_packet_is_not_supported_on_u1_alone"] is True
    assert theorem["internal_family_side_has_exact_one_vs_two_flag_boundary_condition"] is True
    assert theorem["exact_identification_of_u1_with_transport_162_extension_is_obstructed"] is True
    assert theorem["minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"] is True
