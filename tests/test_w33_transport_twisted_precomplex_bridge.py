from __future__ import annotations

from w33_transport_twisted_precomplex_bridge import (
    adapted_transport_precomplex_data,
    build_transport_twisted_precomplex_summary,
)


def test_adapted_twisted_precomplex_has_expected_dimensions_and_ranks() -> None:
    summary = build_transport_twisted_precomplex_summary()

    dims = summary["cochain_dimensions"]
    assert dims["quotient_vertices"] == 45
    assert dims["transport_edges"] == 720
    assert dims["transport_triangles"] == 5280
    assert dims["c0_dimension"] == 90
    assert dims["c1_dimension"] == 1440
    assert dims["c2_dimension"] == 10560

    blocks = summary["adapted_block_decomposition"]
    assert blocks["invariant_line"] == [1, 2]
    assert blocks["d0_lower_left_block_vanishes"] is True
    assert blocks["d1_lower_left_block_vanishes"] is True
    assert blocks["d0_trivial_rank"] == 44
    assert blocks["d0_extension_rank"] == 36
    assert blocks["d0_sign_rank"] == 45
    assert blocks["d1_trivial_rank"] == 676
    assert blocks["d1_extension_rank"] == 457
    assert blocks["d1_sign_rank"] == 717
    assert blocks["full_d0_rank"] == 89
    assert blocks["full_d1_rank"] == 1393


def test_invariant_block_is_exact_but_sign_block_is_curved() -> None:
    summary = build_transport_twisted_precomplex_summary()

    invariant = summary["invariant_line_subcomplex"]
    assert invariant["d1_d0_vanishes_exactly"] is True
    assert invariant["h0_dimension"] == 1
    assert invariant["h1_dimension"] == 0

    sign = summary["sign_shadow_precomplex"]
    assert sign["h0_flat_dimension"] == 0
    assert sign["semisimple_curvature_rank"] == 42
    assert sign["semisimple_curvature_support_triangles"] == 2160
    assert sign["semisimple_curvature_support_equals_parity1_triangles"] is True


def test_full_curvature_factors_through_sign_quotient() -> None:
    summary = build_transport_twisted_precomplex_summary()
    curved = summary["curved_extension_package"]
    assert curved["full_curvature_rank"] == 42
    assert curved["off_diagonal_curvature_rank"] == 36
    assert curved["curvature_kills_invariant_columns"] is True
    assert curved["curvature_factors_through_sign_quotient"] is True
    assert curved["upper_right_curvature_identity_exact"] is True
    assert curved["off_diagonal_curvature_support_rows"] == 4046


def test_curvature_blocks_match_direct_operator_construction() -> None:
    data = adapted_transport_precomplex_data()
    curvature = data["curvature"]
    d0 = data["d0"]
    d1 = data["d1"]
    assert curvature.shape == (10560, 90)
    assert d0.shape == (1440, 90)
    assert d1.shape == (10560, 1440)
    assert ((d1 @ d0) % 3 == curvature).all()
