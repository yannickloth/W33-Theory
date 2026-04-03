from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_primitive_generator_bridge import (  # noqa: E402
    build_continuum_tail_primitive_generator_summary,
)


def test_primitive_integral_generator_is_exact() -> None:
    summary = build_continuum_tail_primitive_generator_summary()
    generator = summary["tail_primitive_generator"]

    assert generator["clearing_denominator_lcm"] == 12
    assert generator["cleared_transport_coordinates"] == [
        "169260",
        "1723848",
        "13584200",
        "11713443",
    ]
    assert generator["cleared_transport_coordinate_gcd"] == 217
    assert generator["primitive_integral_generator"] == {
        "C": "780",
        "L": "7944",
        "Q_seed": "62600",
        "Q_sd1": "53979",
    }
    assert generator["primitive_generator_syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }


def test_primitive_generator_scales_are_exact() -> None:
    summary = build_continuum_tail_primitive_generator_summary()
    generator = summary["tail_primitive_generator"]
    theorem = summary["continuum_tail_primitive_generator_theorem"]

    assert generator["transport_scale_over_primitive_generator"] == {
        "from_C": "217/12",
        "from_L": "217/12",
        "from_Q_seed": "217/12",
        "from_Q_sd1": "217/12",
    }
    assert generator["matter_scale_over_primitive_generator"] == {
        "from_C": "5859/4",
        "from_L": "5859/4",
        "from_Q_seed": "5859/4",
        "from_Q_sd1": "5859/4",
    }
    assert theorem[
        "the_exact_tail_line_has_a_unique_primitive_integral_generator_up_to_sign"
    ] is True
    assert theorem[
        "the_primitive_integral_generator_satisfies_the_exact_avatar_syzygies"
    ] is True
    assert theorem[
        "the_exact_transport_operator_is_217_over_12_times_the_primitive_generator"
    ] is True
    assert theorem[
        "the_exact_matter_operator_is_the_81_fold_lift_of_the_same_primitive_generator"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_now_a_fixed_primitive_tail_lattice_direction_plus_one_rational_scale"
    ] is True
