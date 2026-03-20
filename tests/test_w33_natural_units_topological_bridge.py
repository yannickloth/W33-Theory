from exploration.w33_natural_units_topological_bridge import (
    build_natural_units_topological_summary,
)


def test_natural_units_topological_summary() -> None:
    summary = build_natural_units_topological_summary()
    local = summary["local_shell_dictionary"]
    transport = summary["natural_unit_transport_dictionary"]
    topo = summary["topological_unit_dictionary"]
    exact = summary["exact_factorizations"]

    assert local["q"] == 3
    assert local["lambda"] == 2
    assert local["mu"] == 4
    assert local["phi6"] == 7
    assert local["q_squared"] == 9
    assert local["lambda_plus_phi6"] == 9
    assert local["selector_line_dimension"] == 1
    assert local["shared_six_channel"] == 6

    assert transport["rk_formula"] == "1 / (lambda alpha)"
    assert transport["g0_formula"] == "mu alpha"
    assert transport["z0_unit_formula"] == "1 = lambda alpha R_K"
    assert transport["y0_unit_formula"] == "1 = G_0 / (mu alpha)"
    assert transport["flux_josephson_unit_formula"] == "Phi_0 K_J = 1"
    assert transport["rk"]["exact"] == "152247/2222"
    assert transport["g0"]["exact"] == "4444/152247"
    assert transport["rk_times_g0"]["exact"] == "2"
    assert transport["mu_over_lambda"]["exact"] == "2"

    assert topo["packet_dimension"] == 7
    assert topo["fano_selector_formula"] == "2I + J"
    assert topo["toroidal_shell_formula"] == "7I - J"
    assert topo["normalized_unit_formula"] == "I = ((2I + J) + (7I - J)) / 9"
    assert topo["vacuum_unit_from_local_shell"]["exact"] == "1"
    assert topo["fano_nontrivial_trace"] == 12
    assert topo["toroidal_nontrivial_trace"] == 42
    assert topo["combined_nontrivial_trace"] == 54

    assert exact["rk_equals_one_over_lambda_alpha"] is True
    assert exact["g0_equals_mu_alpha"] is True
    assert exact["z0_unit_matches_lambda_alpha_rk"] is True
    assert exact["y0_unit_matches_g0_over_mu_alpha"] is True
    assert exact["rk_times_g0_equals_mu_over_lambda"] is True
    assert exact["lambda_plus_phi6_equals_q_squared"] is True
    assert exact["vacuum_unit_equals_lambda_plus_phi6_over_q_squared"] is True
    assert exact["normalized_complement_is_identity"] is True
    assert exact["flux_josephson_unit_matches_selector_line"] is True
    assert exact["unit_operator_matches_natural_vacuum"] is True
    assert exact["transport_standards_live_on_same_local_shell"] is True
