from fractions import Fraction

from exploration.w33_yukawa_a4_entry_bridge import (
    build_yukawa_a4_entry_summary,
)


def test_yukawa_a4_entry_summary():
    summary = build_yukawa_a4_entry_summary()
    theorem = summary["a4_entry_theorem"]

    assert theorem["A0_is_family_blind"] is True
    assert theorem["A2_is_family_blind"] is True
    assert theorem["A4_is_first_family_entry_point"] is True
    assert theorem["delta_A4_equals_81_epsilon_squared_a0"] is True
    assert theorem["delta_A4_is_1209_over_9194_times_a0"] is True
    assert theorem["remaining_continuum_wall_is_refined_a4_density"] is True

    coeffs = summary["product_heat_coefficients"]
    assert coeffs["A0"] == "81 a0"
    assert coeffs["A2"] == "-459 a0 + 81 a2"
    assert coeffs["delta_A4"] == "1209/9194 a0"

    expected = 81 * Fraction(403, 248238)
    assert expected == Fraction(1209, 9194)
