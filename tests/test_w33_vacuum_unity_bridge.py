from __future__ import annotations

from decimal import Decimal

from w33_vacuum_unity_bridge import build_vacuum_unity_summary


def test_vacuum_unity_relations_are_exact() -> None:
    summary = build_vacuum_unity_summary()
    bridge = summary["vacuum_unity_relations"]

    assert bridge["c_squared_mu0_epsilon0"]["exact"] == "1"
    assert bridge["z0_times_y0"]["exact"] == "1"
    assert bridge["z0_equals_mu0_c"] is True
    assert bridge["z0_equals_one_over_epsilon0_c"] is True
    assert bridge["mu0_formula_matches_exactly"] is True
    assert bridge["epsilon0_formula_matches_exactly"] is True
    assert bridge["z0_formula_matches_exactly"] is True
    assert bridge["y0_formula_matches_exactly"] is True


def test_w33_alpha_input_matches_live_fraction() -> None:
    summary = build_vacuum_unity_summary()
    alpha = summary["w33_alpha_input"]

    assert alpha["alpha_inverse"]["exact"] == "152247/1111"
    assert alpha["alpha"]["exact"] == "1111/152247"


def test_vacuum_predictions_track_codata_2022_with_alpha_error() -> None:
    summary = build_vacuum_unity_summary()
    comparison = summary["codata_2022_comparison"]

    assert comparison["alpha_inverse_official"] == "137.035999177"
    assert comparison["mu0_official"] == "0.00000125663706127"
    assert comparison["epsilon0_official"] == "8.8541878188E-12"
    assert comparison["z0_official"] == "376.730313412"
    assert comparison["mu0_error_tracks_alpha"] is True
    assert comparison["epsilon0_error_tracks_negative_alpha"] is True
    assert comparison["z0_error_tracks_alpha"] is True

    alpha_inverse_error = Decimal(comparison["alpha_inverse_relative_error"])
    mu0_error = Decimal(comparison["mu0_relative_error"])
    epsilon0_error = Decimal(comparison["epsilon0_relative_error"])
    z0_error = Decimal(comparison["z0_relative_error"])

    assert alpha_inverse_error > 0
    assert mu0_error < 0
    assert epsilon0_error > 0
    assert z0_error < 0
    assert abs(mu0_error) < Decimal("5e-8")
    assert abs(epsilon0_error) < Decimal("5e-8")
    assert abs(z0_error) < Decimal("5e-8")


def test_selector_cross_bridge_keeps_rank_one_vacuum_line() -> None:
    summary = build_vacuum_unity_summary()
    selector = summary["selector_cross_bridge"]

    assert selector["selector_line_dimension"] == 1
    assert selector["vacuum_unity_dimensionless_product"] == "1"
    assert selector["vacuum_unity_matches_selector_rank"] is True
    assert selector["transport_selector_is_unique"] is True
    assert selector["w33_all_ones_spans_mod_3_kernel"] is True
