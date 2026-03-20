from w33_natural_units_cosmological_complement_bridge import (
    build_natural_units_cosmological_complement_summary,
)


def test_natural_units_cosmological_complement_dictionary() -> None:
    summary = build_natural_units_cosmological_complement_summary()
    bridge = summary["cosmological_complement_dictionary"]

    assert bridge["reduced_complement_formula"] == "I_2 - (2 M_EW - I_2)^2 = ((Phi_3^2 - Phi_6^2)/Phi_3^2) I_2"
    assert bridge["lifted_complement_formula"] == "P_mid - (2 R_EW - P_mid)^2 = ((Phi_3^2 - Phi_6^2)/Phi_3^2) P_mid"
    assert bridge["numerator_formula"] == "Phi_3^2 - Phi_6^2 = 4 q Theta(W33)"
    assert bridge["surface_formula"] == "120 = 84 + 36"
    assert bridge["q"] == 3
    assert bridge["theta_w33"] == 10
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["root_gap"]["exact"] == "7/13"
    assert bridge["cosmological_fraction"]["exact"] == "120/169"
    assert bridge["cosmological_numerator"] == 120
    assert bridge["single_surface_flags"] == 84
    assert bridge["heawood_middle_trace"] == 36
    assert bridge["middle_rank"] == 12
    assert bridge["external_chain_density_limit"] == "120/19"


def test_natural_units_cosmological_complement_factorizations_hold() -> None:
    summary = build_natural_units_cosmological_complement_summary()
    assert all(summary["exact_factorizations"].values())
