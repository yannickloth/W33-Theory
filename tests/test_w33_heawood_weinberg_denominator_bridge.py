from w33_heawood_weinberg_denominator_bridge import (
    build_heawood_weinberg_denominator_summary,
)


def test_heawood_shell_reconstructs_projective_denominator() -> None:
    summary = build_heawood_weinberg_denominator_summary()
    shell = summary["heawood_shell_dictionary"]

    assert shell["middle_quadratic_polynomial"] == "x^2 - 6x + 7"
    assert shell["shared_six_channel"] == 6
    assert shell["phi6"] == 7
    assert shell["phi3"] == 13
    assert shell["theta_w33"] == 10
    assert shell["denominator_formula"] == "Phi_3 = 6 + Phi_6"
    assert shell["theta_formula"] == "Theta(W33) = q + Phi_6"


def test_electroweak_ratios_from_heawood_denominator_are_exact() -> None:
    summary = build_heawood_weinberg_denominator_summary()
    ew = summary["electroweak_from_heawood_dictionary"]

    assert ew["weinberg_from_heawood_formula"] == "sin^2(theta_W) = q / (6 + Phi_6)"
    assert ew["cosine_from_heawood_formula"] == "cos^2(theta_W) = (q + Phi_6) / (6 + Phi_6)"
    assert ew["pmns23_from_heawood_formula"] == "sin^2(theta_23) = Phi_6 / (6 + Phi_6)"
    assert ew["sin2_theta_w"]["exact"] == "3/13"
    assert ew["cos2_theta_w"]["exact"] == "10/13"
    assert ew["sin2_theta_23"]["exact"] == "7/13"
    assert ew["q_over_heawood_denominator"]["exact"] == "3/13"
    assert ew["theta_over_heawood_denominator"]["exact"] == "10/13"
    assert ew["phi6_over_heawood_denominator"]["exact"] == "7/13"


def test_heawood_factorizations_hold() -> None:
    summary = build_heawood_weinberg_denominator_summary()
    exact = summary["exact_factorizations"]

    assert exact["heawood_linear_term_is_shared_six"] is True
    assert exact["heawood_constant_term_is_phi6"] is True
    assert exact["phi3_equals_shared_six_plus_phi6"] is True
    assert exact["theta_equals_q_plus_phi6"] is True
    assert exact["cosine_equals_theta_over_heawood_denominator"] is True
    assert exact["weinberg_equals_q_over_heawood_denominator"] is True
    assert exact["pmns23_equals_phi6_over_heawood_denominator"] is True
    assert exact["weinberg_plus_cosine_equals_unity"] is True
    assert exact["surface_shell_reconstructs_projective_denominator"] is True
