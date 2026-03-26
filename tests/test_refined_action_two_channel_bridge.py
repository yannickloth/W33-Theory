from fractions import Fraction

from exploration.w33_refined_action_two_channel_bridge import (
    build_refined_action_two_channel_summary,
)


def test_refined_action_two_channel_summary():
    summary = build_refined_action_two_channel_summary()
    theorem = summary["two_channel_theorem"]

    assert theorem["delta_A4_fixed_point_is_epsilon_squared_times_A0_fixed_point"] is True
    assert theorem["delta_A4_shares_exact_external_modes_with_A0_for_both_seeds"] is True
    assert theorem["first_family_sensitive_truncated_action_collapses_to_two_external_channels"] is True

    global_data = summary["global_data"]
    assert global_data["epsilon_squared"] == "403/248238"
    assert global_data["A0_fixed_point"] == "9720/19"
    assert global_data["delta_A4_fixed_point"] == "72540/87343"

    cp2 = summary["seeds"]["CP2_9"]
    k3 = summary["seeds"]["K3_16"]
    assert cp2["delta_A4_density"]["formula"] == "72540/87343 + 15717/174686/20^n + 403/36776/120^n"
    assert k3["delta_A4_density"]["formula"] == "72540/87343 + -22165/349372/20^n + 403/36776/120^n"

    expected = Fraction(403, 248238) * Fraction(9720, 19)
    assert expected == Fraction(72540, 87343)
