from __future__ import annotations

from w33_k3_primitive_plane_three_u_alignment_bridge import (
    build_k3_primitive_plane_three_u_alignment_bridge_summary,
)


def test_k3_primitive_plane_three_u_alignment_bridge_identifies_the_global_plane() -> None:
    summary = build_k3_primitive_plane_three_u_alignment_bridge_summary()
    theorem = summary["primitive_plane_three_u_alignment_theorem"]

    assert summary["status"] == "ok"
    assert summary["selector_three_u_shadow_reconstruction_error_linf"] < 1e-10
    assert theorem["primitive_plane_equals_the_first_explicit_u_factor"] is True
    assert theorem["selector_three_u_shadow_decomposes_exactly_across_the_three_u_factors"] is True
    assert theorem["selector_has_nonzero_projection_on_u_factor_one"] is True
    assert theorem["selector_has_nonzero_projection_on_u_factor_two"] is True
    assert theorem["selector_has_nonzero_projection_on_u_factor_three"] is True
    assert theorem["selector_three_u_shadow_is_not_supported_on_the_primitive_plane_alone"] is True
    assert theorem["primitive_plane_is_distinguished_but_not_equal_to_the_selector_positive_channel"] is True
    assert theorem["all_three_u_factor_shadows_are_mixed_signature"] is True


def test_k3_primitive_plane_three_u_alignment_bridge_records_the_first_u_factor_exactly() -> None:
    summary = build_k3_primitive_plane_three_u_alignment_bridge_summary()
    assert summary["primitive_plane_coefficients"] == summary["three_u_factor_one_coefficients"]
