from w33_heawood_electroweak_polarization_bridge import (
    build_heawood_electroweak_polarization_summary,
)


def test_heawood_electroweak_polarization_dictionary() -> None:
    summary = build_heawood_electroweak_polarization_summary()
    bridge = summary["polarization_dictionary"]
    reduced = summary["reduced_packet_dictionary"]

    assert bridge["operator_formula"] == "R_EW = (q Pi_- + Theta(W33) Pi_+) / Phi_3"
    assert bridge["projector_form_formula"] == "R_EW = P_mid/2 + (Phi_6 / (2 Phi_3)) J_mid"
    assert bridge["centered_gap_formula"] == "2 R_EW - P_mid = (Phi_6 / Phi_3) J_mid"
    assert bridge["quadratic_formula"] == "R_EW^2 - R_EW + (q Theta(W33)/Phi_3^2) P_mid = 0"
    assert bridge["reduced_packet_formula"] == "M_EW = [[1/2, Phi_6/(2 Phi_3)], [Phi_6/(2 Phi_3), 1/2]]"
    assert bridge["q"] == 3
    assert bridge["theta_w33"] == 10
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["middle_rank"] == 12
    assert bridge["complex_rank"] == 6
    assert bridge["weak_share"]["exact"] == "3/13"
    assert bridge["hypercharge_share"]["exact"] == "10/13"
    assert bridge["neutral_product"]["exact"] == "30/169"
    assert bridge["root_gap"]["exact"] == "7/13"
    assert bridge["polarization_amplitude"]["exact"] == "7/26"
    assert bridge["middle_trace"] == 36
    assert reduced["trace"]["exact"] == "1"
    assert reduced["determinant"]["exact"] == "30/169"
    assert reduced["eigenvalue_minus"]["exact"] == "3/13"
    assert reduced["eigenvalue_plus"]["exact"] == "10/13"


def test_heawood_electroweak_polarization_factorizations_hold() -> None:
    summary = build_heawood_electroweak_polarization_summary()
    assert all(summary["exact_factorizations"].values())
