from w33_natural_units_custodial_bridge import build_natural_units_custodial_summary


def test_custodial_split_matches_natural_units_denominator() -> None:
    summary = build_natural_units_custodial_summary()
    shell = summary["custodial_shell_dictionary"]
    weak = summary["weak_mass_dictionary"]
    exact = summary["exact_factorizations"]

    assert shell["phi3"] == 13
    assert shell["theta_w33"] == 10
    assert shell["selector_line"] == 1
    assert shell["q"] == 3
    assert shell["rk_times_g0"]["exact"] == "2"
    assert shell["phi6"] == 7
    assert shell["custodial_numerator_formula"] == "Theta(W33) = 1 + R_K G_0 + Phi_6"
    assert shell["denominator_formula"] == "Phi_3 = 1 + q + R_K G_0 + Phi_6"
    assert shell["mass_ratio_formula"] == "m_W^2 / m_Z^2 = Theta(W33) / Phi_3"
    assert shell["gap_formula"] == "(m_Z^2 - m_W^2) / m_Z^2 = q / Phi_3"

    assert weak["mw_squared_over_mz_squared"]["exact"] == "10/13"
    assert weak["z_gap_over_z_squared"]["exact"] == "3/13"
    assert weak["sin2_theta_w"]["exact"] == "3/13"
    assert weak["cos2_theta_w"]["exact"] == "10/13"
    assert weak["theta_over_phi3"]["exact"] == "10/13"
    assert weak["q_over_phi3"]["exact"] == "3/13"
    assert weak["rho_parameter"]["exact"] == "1"

    assert exact["theta_equals_selector_plus_metrology_plus_qcd"] is True
    assert exact["phi3_equals_selector_plus_projective_plus_metrology_plus_qcd"] is True
    assert exact["mw_over_mz_squared_equals_cos2_theta_w"] is True
    assert exact["z_gap_over_z_squared_equals_sin2_theta_w"] is True
    assert exact["cos2_equals_theta_over_phi3"] is True
    assert exact["sin2_equals_q_over_phi3"] is True
    assert exact["custodial_split_sums_to_unity"] is True
    assert exact["rho_equals_one"] is True
