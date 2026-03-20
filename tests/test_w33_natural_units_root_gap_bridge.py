from w33_natural_units_root_gap_bridge import build_natural_units_root_gap_summary


def test_root_gap_quadratic_closes_exactly() -> None:
    summary = build_natural_units_root_gap_summary()
    bridge = summary["root_gap_dictionary"]

    assert bridge["quadratic_formula"] == "t^2 - t + q Theta(W33) / Phi_3^2 = 0"
    assert bridge["sum_formula"] == "x + y = 1"
    assert bridge["product_formula"] == "xy = q Theta(W33) / Phi_3^2"
    assert bridge["discriminant_formula"] == "1 - 4 q Theta(W33) / Phi_3^2 = Phi_6^2 / Phi_3^2"
    assert bridge["gap_formula"] == "y - x = Phi_6 / Phi_3 = sin^2(theta_23)"
    assert bridge["weak_root_formula"] == "x = (1 - Phi_6 / Phi_3) / 2 = q / Phi_3"
    assert bridge["hypercharge_root_formula"] == "y = (1 + Phi_6 / Phi_3) / 2 = Theta(W33) / Phi_3"
    assert bridge["q"] == 3
    assert bridge["theta_w33"] == 10
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["weak_share"]["exact"] == "3/13"
    assert bridge["hypercharge_share"]["exact"] == "10/13"
    assert bridge["neutral_product"]["exact"] == "30/169"
    assert bridge["discriminant"]["exact"] == "49/169"
    assert bridge["root_gap"]["exact"] == "7/13"
    assert bridge["atmospheric_share"]["exact"] == "7/13"


def test_root_gap_factorizations_hold() -> None:
    summary = build_natural_units_root_gap_summary()
    assert all(summary["exact_factorizations"].values())
