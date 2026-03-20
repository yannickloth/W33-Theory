from exploration.w33_heawood_clifford_bridge import build_heawood_clifford_summary


def test_heawood_middle_shell_is_clifford_packet():
    summary = build_heawood_clifford_summary()
    shell = summary["clifford_dictionary"]
    facts = summary["exact_factorizations"]

    assert shell["gamma_formula"] == "Gamma = diag(I_7,-I_7)"
    assert shell["gamma_mid_formula"] == "Gamma_mid = P_mid Gamma P_mid"
    assert shell["j_mid_formula"] == "J_mid = P_mid (L_H - qI) P_mid / sqrt(lambda)"
    assert shell["k_mid_formula"] == "K_mid = Gamma_mid J_mid"
    assert shell["pi_plus_formula"] == "Pi_+ = (P_mid + J_mid)/2"
    assert shell["pi_minus_formula"] == "Pi_- = (P_mid - J_mid)/2"
    assert shell["middle_shell_rank"] == 12
    assert shell["complex_rank"] == 6
    assert all(facts.values())
