from __future__ import annotations

from w33_yukawa_active_spectrum_bridge import build_yukawa_active_spectrum_summary


def test_full_active_sector_scaled_spectra_factor_over_z() -> None:
    summary = build_yukawa_active_spectrum_summary()
    theorem = summary["active_spectrum_theorem"]
    factors = summary["slot_factorizations"]

    assert summary["gram_denominator"] == 57600
    assert summary["scaled_variable"] == "y = 57600 * sigma^2"
    assert theorem["all_active_sector_scaled_spectra_factor_over_z"] is True
    assert theorem["max_factor_degree"] == 4

    assert factors["H_2"]["+-"] == [
        "y - 275",
        "y - 169",
        "y**2 - 5350*y + 675625",
        "y**2 - 4946*y + 143761",
    ]
    assert factors["H_2"]["-+"] == [
        "y**2 - 542*y + 61200",
        "y**4 - 7292*y**3 + 7645348*y**2 - 2031422400*y + 153044640000",
    ]
    assert factors["Hbar_2"]["+-"] == [
        "y - 169",
        "y**2 - 1138*y + 143761",
        "y**2 - 982*y + 137232",
        "y**4 - 13100*y**3 + 44831236*y**2 - 23791760064*y + 246961799424",
    ]
    assert factors["Hbar_2"]["-+"] == [
        "y - 323",
        "y**2 - 4646*y + 896329",
    ]


def test_base_packets_survive_as_exact_active_spectrum_factors() -> None:
    summary = build_yukawa_active_spectrum_summary()
    theorem = summary["active_spectrum_theorem"]

    assert theorem["h2_plus_minus_contains_exact_base_scalar_packet"] is True
    assert theorem["h2_minus_plus_contains_exact_base_quadratic_packet"] is True
    assert theorem["hbar2_plus_minus_contains_exact_base_packet"] is True
    assert theorem["hbar2_minus_plus_contains_exact_base_scalar_packet"] is True
    assert theorem["remaining_full_active_frontier_is_finite_algebraic_packet"] is True
