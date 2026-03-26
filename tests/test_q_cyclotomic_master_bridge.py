from exploration.w33_q_cyclotomic_master_bridge import (
    build_q_cyclotomic_master_summary,
)


def test_q_cyclotomic_master_summary():
    summary = build_q_cyclotomic_master_summary()

    data = summary["q_cyclotomic_data"]
    assert data == {"q": 3, "phi3": 13, "phi6": 7, "v_of_q": 40}

    internal = summary["internal_q_package"]
    assert internal["matter"] == {"formula": "q^4", "exact": 81}
    assert internal["A2_transport"] == {"formula": "2q", "exact": 6}
    assert internal["Cartan"] == {"formula": "q^2 - 1", "exact": 8}
    assert internal["g0"] == {"formula": "q^4 + 2q - 1", "exact": 86}
    assert internal["E8_dimension"] == {"formula": "3q^4 + 2q - 1", "exact": 248}

    curved = summary["curved_q_package"]
    assert curved["c_EH"] == {"formula": "v(q) * (q^2 - 1)", "exact": 320}
    assert curved["a2"] == {"formula": "Phi_6(q) * c_EH", "exact": 2240}
    assert curved["c6"] == {"formula": "q * Phi_3(q) * c_EH", "exact": 12480}
    assert curved["Q_curv"] == "52"
    assert curved["Q_top"] == "56"

    selection = summary["selection_lock"]
    assert selection["nine_cEH_over_c6"] == "3/13"
    assert selection["general_formula"] == "9 / (q * Phi_3(q))"
    assert selection["selected_formula"] == "q / Phi_3(q)"
    assert selection["weinberg_generator"] == "3/13"

    theorem = summary["q_master_theorem"]
    assert theorem["matter_equals_q4"] is True
    assert theorem["a2_transport_equals_2q"] is True
    assert theorem["cartan_equals_q2_minus_1"] is True
    assert theorem["g0_equals_q4_plus_2q_minus_1"] is True
    assert theorem["e8_equals_3q4_plus_2q_minus_1"] is True
    assert theorem["cEH_equals_v_times_q2_minus_1"] is True
    assert theorem["a2_equals_phi6_times_cEH"] is True
    assert theorem["c6_equals_q_phi3_times_cEH"] is True
    assert theorem["nine_cEH_over_c6_equals_weinberg"] is True
    assert theorem["weinberg_is_q_over_phi3"] is True
    assert theorem["external_quanta_are_52_and_56"] is True
    assert theorem["global_branch_activation_count_remains_open"] is True
