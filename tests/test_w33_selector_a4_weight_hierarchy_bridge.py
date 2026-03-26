from __future__ import annotations

import pytest

from w33_selector_a4_weight_hierarchy_bridge import (
    build_selector_a4_weight_hierarchy_bridge_summary,
)


def test_selector_a4_weight_hierarchy_bridge_summary() -> None:
    summary = build_selector_a4_weight_hierarchy_bridge_summary()
    theorem = summary["selector_a4_weight_hierarchy_theorem"]

    assert summary["factor_frobenius_norms"]["U1"] == pytest.approx(0.5070148472753923)
    assert summary["factor_frobenius_norms"]["U2"] == pytest.approx(0.0814269981830142)
    assert summary["factor_frobenius_norms"]["U3"] == pytest.approx(2.4712362068942952)
    assert summary["factor_frobenius_norms"]["E8_1"] == pytest.approx(0.2957919585266082)
    assert summary["factor_frobenius_norms"]["E8_2"] == pytest.approx(2.505700578655349)
    assert summary["hyperbolic_weight_shares"]["U3"] == pytest.approx(0.8076785088529392)
    assert summary["exceptional_weight_shares"]["E8_2"] == pytest.approx(0.894416296099026)
    assert theorem["hyperbolic_weight_order_is_u3_gt_u1_gt_u2"] is True
    assert theorem["exceptional_weight_order_is_e8_factor_two_gt_e8_factor_one"] is True
    assert theorem["u3_carries_more_than_four_fifths_of_hyperbolic_packet_weight"] is True
    assert theorem["e8_factor_two_carries_more_than_eight_ninths_of_exceptional_packet_weight"] is True
    assert theorem["fine_weight_hierarchy_is_refinement_invariant"] is True
