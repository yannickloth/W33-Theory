from __future__ import annotations

import json
import math
from pathlib import Path

from w33_flat_ac_spectral_action import (
    build_flat_product_summary,
    continuum_torus4_heat_trace_dual,
    flat_product_asymptotic_prediction,
    flat_product_coefficients,
    flat_product_heat_trace_dual,
    internal_dirac_moments,
    renormalized_flat_product_heat,
    renormalized_flat_product_prediction,
    write_summary,
)


def test_internal_w33_dirac_moments_are_concrete() -> None:
    moments = internal_dirac_moments()
    assert moments["dim"] == 162.0
    assert moments["tr_d2"] == 61440.0
    assert moments["tr_d4"] == 89217408.0


def test_flat_product_coefficients_match_closed_form() -> None:
    coeffs = flat_product_coefficients()
    prefactor = 1.0 / (16.0 * math.pi**2)
    assert math.isclose(coeffs.heat_leading_t_minus_2, 162.0 * prefactor, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(coeffs.heat_leading_t_minus_1, -61440.0 * prefactor, rel_tol=0.0, abs_tol=1e-9)
    assert math.isclose(coeffs.heat_leading_t_0, 89217408.0 * prefactor / 2.0, rel_tol=0.0, abs_tol=1e-6)


def test_dual_torus_heat_trace_is_positive() -> None:
    assert continuum_torus4_heat_trace_dual(1e-4) > 0.0
    assert continuum_torus4_heat_trace_dual(2e-4) > 0.0


def test_small_time_renormalized_prediction_matches_exact_product() -> None:
    exact = renormalized_flat_product_heat(1e-4)
    predicted = renormalized_flat_product_prediction(1e-4)
    assert abs(exact - predicted) < 3e-4


def test_three_term_asymptotic_is_reasonable_at_two_small_times() -> None:
    for t in (1e-4, 2e-4):
        exact = flat_product_heat_trace_dual(t)
        predicted = flat_product_asymptotic_prediction(t)
        assert abs((t**2) * exact - (t**2) * predicted) < 2e-3


def test_flat_external_factor_has_zero_einstein_hilbert_term() -> None:
    coeffs = flat_product_coefficients()
    assert coeffs.external_scalar_curvature_term == 0.0
    assert coeffs.external_is_flat is True
    assert coeffs.needs_curved_external_geometry is True


def test_summary_records_remaining_curvature_obstruction() -> None:
    summary = build_flat_product_summary()
    assert summary["status"] == "ok"
    assert summary["coefficients"]["external_scalar_curvature_term"] == 0.0
    assert len(summary["samples"]) == 3
    assert "curved external 4D" in summary["verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_flat_ac_spectral_action_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["coefficients"]["trace_d2"] == 61440.0
