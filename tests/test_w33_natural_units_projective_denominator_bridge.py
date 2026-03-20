from w33_natural_units_projective_denominator_bridge import (
    build_natural_units_projective_denominator_summary,
)


def test_projective_denominator_rebuilds_from_natural_units_shells() -> None:
    summary = build_natural_units_projective_denominator_summary()
    shell = summary["metrology_shell_dictionary"]
    proj = summary["projective_denominator_dictionary"]

    assert shell["fano_selector_formula"] == "B B^T = 2I + J"
    assert shell["metrology_selector_formula"] == "B B^T = (R_K G_0) I + J"
    assert shell["toroidal_shell_formula"] == "L_K7 = Phi_6 I - J"
    assert shell["local_sum_formula"] == "B B^T + L_K7 = (R_K G_0 + Phi_6) I = q^2 I"
    assert shell["q_from_selector_and_metrology_formula"] == "q = 1 + R_K G_0"
    assert shell["shared_six_formula"] == "6 = 1 + q + R_K G_0"
    assert shell["selector_line"] == 1
    assert shell["q"] == 3
    assert shell["rk_times_g0"]["exact"] == "2"
    assert shell["phi6"] == 7
    assert shell["q_squared"] == 9

    assert proj["phi3_formula"] == "Phi_3 = 1 + q + R_K G_0 + Phi_6"
    assert proj["theta_formula"] == "Theta(W33) = 1 + R_K G_0 + Phi_6"
    assert proj["phi3"] == 13
    assert proj["theta_w33"] == 10
    assert proj["selector_plus_projective_plus_shells"]["exact"] == "13"
    assert proj["theta_from_selector_and_shells"]["exact"] == "10"


def test_electroweak_ratios_match_projective_denominator_split() -> None:
    summary = build_natural_units_projective_denominator_summary()
    proj = summary["projective_denominator_dictionary"]
    exact = summary["exact_factorizations"]

    assert proj["sin2_theta_w_formula"] == "sin^2(theta_W) = q / (1 + q + R_K G_0 + Phi_6)"
    assert proj["cos2_theta_w_formula"] == "cos^2(theta_W) = (1 + R_K G_0 + Phi_6) / (1 + q + R_K G_0 + Phi_6)"
    assert proj["sin2_theta_w"]["exact"] == "3/13"
    assert proj["cos2_theta_w"]["exact"] == "10/13"
    assert proj["q_over_projective_denominator"]["exact"] == "3/13"
    assert proj["theta_over_projective_denominator"]["exact"] == "10/13"

    assert exact["selector_coefficient_equals_metrology_coefficient"] is True
    assert exact["q_equals_selector_line_plus_metrology_shell"] is True
    assert exact["shared_six_equals_selector_plus_projective_plus_metrology_shell"] is True
    assert exact["metrology_plus_qcd_shell_equals_q_squared"] is True
    assert exact["phi3_equals_selector_plus_projective_plus_shells"] is True
    assert exact["theta_equals_selector_plus_shells"] is True
    assert exact["weinberg_equals_q_over_projective_denominator"] is True
    assert exact["cosine_equals_theta_over_projective_denominator"] is True
    assert exact["weinberg_plus_cosine_equals_unity"] is True
    assert exact["projective_denominator_rebuilds_from_natural_units_shells"] is True
