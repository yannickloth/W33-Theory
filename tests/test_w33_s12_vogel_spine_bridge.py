from __future__ import annotations

from w33_s12_vogel_spine_bridge import build_s12_vogel_spine_summary


def test_s12_shell_lands_on_a26_not_positive_exceptional_line() -> None:
    summary = build_s12_vogel_spine_summary()
    a_line = summary["vogel_a_line_dictionary"]
    firewall = summary["exceptional_line_firewall"]
    assert a_line["sl27_dimension"] == 728
    assert a_line["a_family_rank"] == 26
    assert a_line["sl27_is_exactly_a26"] is True
    assert firewall["dim_242_in_positive_exceptional_hit_set"] is False
    assert firewall["dim_486_in_positive_exceptional_hit_set"] is False
    assert firewall["dim_728_in_positive_exceptional_hit_set"] is False
    assert firewall["nearest_positive_exceptional_hits_to_728"] == [782]
    assert firewall["distance_from_728_to_nearest_positive_exceptional_hit"] == 54


def test_s12_vogel_bridge_records_exact_mixed_classical_exceptional_factors() -> None:
    summary = build_s12_vogel_spine_summary()
    bridge = summary["vogel_a_line_dictionary"]
    assert bridge["projective_shell_dimension"] == 364
    assert bridge["g2_dimension"] == 14
    assert bridge["d4_dimension"] == 28
    assert bridge["f4_dimension"] == 52
    assert bridge["e8_dimension"] == 248
    assert bridge["finite_w33_dimension"] == 480
    assert bridge["projective_shell_equals_g2_times_a26_rank"] is True
    assert bridge["sl27_equals_d4_dimension_times_a26_rank"] is True
    assert bridge["sl27_equals_g2_times_f4"] is True
    assert bridge["sl27_equals_finite_w33_plus_e8"] is True
