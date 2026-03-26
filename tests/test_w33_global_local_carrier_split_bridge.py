from __future__ import annotations

import pytest

from w33_global_local_carrier_split_bridge import (
    build_global_local_carrier_split_bridge_summary,
)


def test_global_local_carrier_split_bridge_summary() -> None:
    summary = build_global_local_carrier_split_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["canonical_global_carrier"] == "U1"
    assert summary["dominant_hyperbolic_packet_piece"] == "U3"
    assert summary["dominant_exceptional_packet_piece"] == "E8_2"
    assert summary["hyperbolic_dominance_ratio_u3_over_u1"] == pytest.approx(
        4.874090414066333
    )
    assert summary["exceptional_dominance_ratio_e8_factor_two_over_e8_factor_one"] == (
        pytest.approx(8.471158550545743)
    )
    theorem = summary["global_local_carrier_split_theorem"]
    assert theorem["canonical_global_carrier_is_u1"] is True
    assert theorem["dominant_hyperbolic_packet_piece_is_u3"] is True
    assert theorem["dominant_exceptional_packet_piece_is_e8_factor_two"] is True
    assert theorem["canonical_global_carrier_differs_from_dominant_hyperbolic_packet_piece"] is True
    assert theorem["first_family_packet_has_canonical_global_support_but_non_u1_local_dominance"] is True
    assert theorem["global_local_carrier_split_is_refinement_invariant"] is True
