from w33_natural_units_unit_balance_bridge import (
    build_natural_units_unit_balance_summary,
)


def test_natural_units_unit_balance_dictionary() -> None:
    summary = build_natural_units_unit_balance_summary()
    bridge = summary["unit_balance_dictionary"]

    assert bridge["reduced_balance_formula"] == "I_2 = (2 M_EW - I_2)^2 + 4 det(M_EW) I_2"
    assert bridge["lifted_balance_formula"] == "P_mid = (2 R_EW - P_mid)^2 + ((Phi_3^2 - Phi_6^2)/Phi_3^2) P_mid"
    assert bridge["mixed_product_formula"] == "I_2 - (2 M_EW - I_2)^2 = 4 M_EW (I_2 - M_EW)"
    assert bridge["fraction_formula"] == "1 = (Phi_6/Phi_3)^2 + (Phi_3^2 - Phi_6^2)/Phi_3^2"
    assert bridge["numerator_formula"] == "Phi_3^2 = Phi_6^2 + (Phi_3^2 - Phi_6^2)"
    assert bridge["shell_balance_formula"] == "169 = 84 + 36 + 49"
    assert bridge["shell_formula"] == "169 = 84 + 36 + 42 + 7"
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["denominator_square"] == 169
    assert bridge["polarization_fraction"]["exact"] == "49/169"
    assert bridge["cosmological_fraction"]["exact"] == "120/169"
    assert bridge["polarization_numerator"] == 49
    assert bridge["cosmological_numerator"] == 120
    assert bridge["single_surface_flags"] == 84
    assert bridge["heawood_middle_trace"] == 36
    assert bridge["toroidal_trace"] == 42
    assert bridge["qcd_selector"] == 7


def test_natural_units_unit_balance_factorizations_hold() -> None:
    summary = build_natural_units_unit_balance_summary()
    assert all(summary["exact_factorizations"].values())
