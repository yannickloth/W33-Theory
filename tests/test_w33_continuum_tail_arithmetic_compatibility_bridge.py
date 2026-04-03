from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_arithmetic_compatibility_bridge import (  # noqa: E402
    build_continuum_tail_arithmetic_compatibility_summary,
)


def test_transport_and_matter_arithmetic_profiles_are_exact() -> None:
    summary = build_continuum_tail_arithmetic_compatibility_summary()
    profiles = summary["tail_arithmetic_compatibility"]

    assert profiles["transport_profile"] == {
        "denominator_lcm": 12,
        "cleared_coordinates": ["169260", "1723848", "13584200", "11713443"],
        "cleared_coordinate_gcd": 217,
        "primitive_direction": ["780", "7944", "62600", "53979"],
        "recovered_scale": "217/12",
    }
    assert profiles["matter_profile"] == {
        "denominator_lcm": 4,
        "cleared_coordinates": ["4570020", "46543896", "366773400", "316262961"],
        "cleared_coordinate_gcd": 5859,
        "primitive_direction": ["780", "7944", "62600", "53979"],
        "recovered_scale": "5859/4",
    }


def test_arithmetic_compatibility_theorem_is_exact() -> None:
    theorem = build_continuum_tail_arithmetic_compatibility_summary()[
        "continuum_tail_arithmetic_compatibility_theorem"
    ]
    assert theorem[
        "on_the_fixed_primitive_tail_line_the_reduced_fraction_scale_equals_cleared_gcd_over_denominator_lcm"
    ] is True
    assert theorem[
        "the_exact_transport_realization_has_compatibility_pair_lcm12_gcd217"
    ] is True
    assert theorem[
        "the_exact_matter_realization_has_compatibility_pair_lcm4_gcd5859"
    ] is True
    assert theorem[
        "the_matter_compatibility_pair_is_the_exact_81_fold_lift_of_the_transport_pair"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_now_tail_line_membership_plus_one_exact_denominator_gcd_compatibility_pair"
    ] is True
