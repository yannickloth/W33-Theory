from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_k3_tail_arithmetic_obstruction_bridge import (  # noqa: E402
    build_continuum_k3_tail_arithmetic_obstruction_summary,
)


def test_fixed_k3_realization_channel_is_exact() -> None:
    summary = build_continuum_k3_tail_arithmetic_obstruction_summary()
    channel = summary["fixed_k3_realization_channel"]

    assert channel["carrier_plane"] == "U1"
    assert channel["ordered_filtration_dimensions"] == [81, 162, 81]
    assert channel["slot_direction"] == "tail_to_head"
    assert channel["slot_shape"] == [81, 81]
    assert channel["tail_channel_dimension"] == 81
    assert channel["transport_arithmetic_pair"] == {
        "denominator_lcm": 12,
        "cleared_coordinate_gcd": 217,
        "recovered_scale": "217/12",
    }
    assert channel["matter_arithmetic_pair"] == {
        "denominator_lcm": 4,
        "cleared_coordinate_gcd": 5859,
        "recovered_scale": "5859/4",
    }


def test_k3_tail_arithmetic_obstruction_theorem_is_exact() -> None:
    theorem = build_continuum_k3_tail_arithmetic_obstruction_summary()[
        "continuum_k3_tail_arithmetic_obstruction_theorem"
    ]
    assert theorem[
        "the_external_k3_carrier_package_is_already_fixed_before_realization"
    ] is True
    assert theorem[
        "the_remaining_k3_realization_channel_is_exactly_the_curvature_sensitive_tail_81"
    ] is True
    assert theorem[
        "any_exact_k3_side_realization_must_satisfy_the_transport_arithmetic_pair_lcm12_gcd217"
    ] is True
    assert theorem[
        "the_induced_matter_side_realization_then_has_pair_lcm4_gcd5859"
    ] is True
    assert theorem[
        "therefore_the_live_external_wall_is_existence_of_genuine_k3_data_satisfying_the_fixed_tail_arithmetic_obstruction"
    ] is True
