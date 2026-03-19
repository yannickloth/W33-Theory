from __future__ import annotations

from w33_klein_hurwitz_extremal_bridge import build_klein_hurwitz_extremal_summary


def test_klein_hurwitz_extremal_bridge_closes_exactly() -> None:
    summary = build_klein_hurwitz_extremal_summary()
    assert summary["status"] == "ok"

    packet = summary["hurwitz_extremal_dictionary"]
    factors = summary["exact_factorizations"]

    assert packet["klein_quartic_genus"] == 3
    assert packet["hurwitz_coefficient"] == 84
    assert packet["heawood_preserving_order"] == 168
    assert packet["heawood_full_order"] == 336
    assert packet["standard_model_gauge_dimension"] == 12
    assert packet["phi6"] == 7
    assert packet["g2_dimension"] == 14

    assert factors["preserving_order_equals_hurwitz_bound_at_genus_3"] is True
    assert factors["preserving_order_equals_two_times_hurwitz_coefficient"] is True
    assert factors["preserving_order_equals_2_k_phi6"] is True
    assert factors["preserving_order_equals_k_times_g2_dimension"] is True
    assert factors["full_order_equals_two_times_preserving_order"] is True
    assert factors["full_order_equals_four_times_hurwitz_coefficient"] is True
