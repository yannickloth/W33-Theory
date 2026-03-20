from w33_heawood_q_center_bridge import build_heawood_q_center_summary


def test_heawood_shell_is_q_centered() -> None:
    summary = build_heawood_q_center_summary()
    shell = summary["heawood_q_center_dictionary"]
    exact = summary["exact_factorizations"]

    assert shell["middle_quadratic_polynomial"] == "x^2 - 6x + 7"
    assert shell["q_centered_formula"] == "x^2 - 2q x + Phi_6"
    assert shell["root_formula"] == "x = q +- sqrt(lambda)"
    assert shell["q"] == 3
    assert shell["lambda"] == 2
    assert shell["phi6"] == 7
    assert shell["phi3"] == 13
    assert shell["middle_branch_minus"] == "3 - sqrt(2)"
    assert shell["middle_branch_plus"] == "3 + sqrt(2)"
    assert shell["middle_shell_trace_exact"] == "36"
    assert shell["middle_shell_pseudodeterminant_exact"] == "117649"

    assert exact["linear_term_equals_2q"] is True
    assert exact["constant_term_equals_phi6"] is True
    assert exact["q_squared_minus_phi6_equals_lambda"] is True
    assert exact["roots_equal_q_plus_minus_sqrt_lambda"] is True
    assert exact["phi3_equals_2q_plus_phi6"] is True
    assert exact["middle_trace_equals_q_times_gauge_dimension"] is True
    assert exact["middle_pseudodeterminant_equals_phi6_to_6"] is True
