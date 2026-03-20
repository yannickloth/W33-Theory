from w33_heawood_involution_bridge import build_heawood_involution_summary


def test_heawood_middle_shell_normalizes_to_involution() -> None:
    summary = build_heawood_involution_summary()
    shell = summary["centered_shell_dictionary"]
    exact = summary["exact_factorizations"]

    assert shell["middle_quadratic_polynomial"] == "x^2 - 6x + 7"
    assert shell["centered_quadratic_formula"] == "(x - q)^2 = lambda"
    assert shell["operator_formula"] == "(P_mid (L_H - qI) P_mid)^2 = lambda P_mid"
    assert shell["normalized_involution_formula"] == "J_mid = P_mid (L_H - qI) P_mid / sqrt(lambda)"
    assert shell["q"] == 3
    assert shell["lambda"] == 2
    assert shell["phi6"] == 7
    assert shell["adjacency_quartic_polynomial"] == "x^4 - 11*x^2 + 18"
    assert shell["middle_projector_rank"] == 12

    assert exact["q_squared_minus_phi6_equals_lambda"] is True
    assert exact["centered_shell_relation_holds"] is True
    assert exact["normalized_operator_is_involution"] is True
    assert exact["middle_projector_is_idempotent"] is True
    assert exact["middle_shell_rank_is_12"] is True
