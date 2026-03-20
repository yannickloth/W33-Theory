from w33_natural_units_electroweak_split_bridge import (
    build_natural_units_electroweak_split_summary,
)


def test_nested_complement_dictionary_is_exact() -> None:
    summary = build_natural_units_electroweak_split_summary()
    bridge = summary["nested_complement_dictionary"]

    assert bridge["q"] == 3
    assert bridge["lambda"] == 2
    assert bridge["phi6"] == 7
    assert bridge["q_squared"] == 9
    assert bridge["theta_w33"] == 10
    assert bridge["phi3"] == 13
    assert bridge["local_unit_formula"] == "(lambda + Phi_6) / q^2 = 1"
    assert bridge["electroweak_unit_formula"] == "1 = q/Phi_3 + Theta(W33)/Phi_3"
    assert bridge["local_unit_value"]["exact"] == "1"
    assert bridge["electroweak_unit_value"]["exact"] == "1"


def test_electroweak_split_dictionary_is_exact() -> None:
    summary = build_natural_units_electroweak_split_summary()
    split = summary["electroweak_split_dictionary"]

    assert split["weinberg_formula"] == "sin^2(theta_W) = q / Phi_3"
    assert split["cosine_formula"] == "cos^2(theta_W) = Theta(W33) / Phi_3"
    assert split["electric_reciprocal_formula"] == "(4 pi alpha) / e^2 = 1"
    assert split["weak_reciprocal_formula"] == "(4 pi alpha) / g^2 = q / Phi_3"
    assert split["hypercharge_reciprocal_formula"] == "(4 pi alpha) / g'^2 = Theta(W33) / Phi_3"
    assert split["neutral_reciprocal_formula"] == "(4 pi alpha) / g_Z^2 = q Theta(W33) / Phi_3^2"
    assert split["sin2_theta_w"]["exact"] == "3/13"
    assert split["cos2_theta_w"]["exact"] == "10/13"
    assert split["q_over_phi3"]["exact"] == "3/13"
    assert split["theta_over_phi3"]["exact"] == "10/13"
    assert split["reciprocal_g"]["exact"] == "3/13"
    assert split["reciprocal_gprime"]["exact"] == "10/13"
    assert split["reciprocal_gz"]["exact"] == "30/169"
    assert split["tan2_theta_w"]["exact"] == "3/10"
    assert split["theta_over_q"]["exact"] == "10/3"


def test_nested_unit_factorizations_hold() -> None:
    summary = build_natural_units_electroweak_split_summary()
    exact = summary["exact_factorizations"]

    assert exact["lambda_plus_phi6_equals_q_squared"] is True
    assert exact["theta_equals_q_plus_phi6"] is True
    assert exact["q_plus_theta_equals_phi3"] is True
    assert exact["phi3_equals_2q_plus_phi6"] is True
    assert exact["weinberg_equals_q_over_phi3"] is True
    assert exact["cosine_equals_theta_over_phi3"] is True
    assert exact["sin2_plus_cos2_equals_unity"] is True
    assert exact["weak_reciprocal_matches_weinberg"] is True
    assert exact["hypercharge_reciprocal_matches_cosine"] is True
    assert exact["electric_reciprocal_harmonic_sum_closes"] is True
    assert exact["g_squared_over_gprime_squared_equals_theta_over_q"] is True
    assert exact["neutral_reciprocal_equals_q_theta_over_phi3_squared"] is True
    assert exact["local_and_electroweak_are_nested_unit_laws"] is True
