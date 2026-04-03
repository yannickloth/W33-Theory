from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_reduced_fraction_bridge import (  # noqa: E402
    build_continuum_tail_reduced_fraction_summary,
)


def test_reduced_fraction_scales_are_exact() -> None:
    summary = build_continuum_tail_reduced_fraction_summary()
    coords = summary["tail_reduced_fraction_coordinates"]

    assert coords["transport_reduced_fraction_scale"] == {
        "numerator": 217,
        "denominator": 12,
        "fraction": "217/12",
        "coprime_gcd": 1,
    }
    assert coords["matter_reduced_fraction_scale"] == {
        "numerator": 5859,
        "denominator": 4,
        "fraction": "5859/4",
        "coprime_gcd": 1,
    }


def test_reduced_fraction_theorem_is_exact() -> None:
    theorem = build_continuum_tail_reduced_fraction_summary()[
        "continuum_tail_reduced_fraction_theorem"
    ]
    assert theorem[
        "every_rational_tail_operator_on_the_fixed_primitive_line_has_a_unique_reduced_fraction_description"
    ] is True
    assert theorem[
        "the_exact_transport_realization_has_reduced_fraction_scale_217_over_12"
    ] is True
    assert theorem[
        "the_exact_matter_realization_has_reduced_fraction_scale_5859_over_4"
    ] is True
    assert theorem[
        "the_matter_reduced_fraction_is_the_exact_81_fold_lift_of_the_transport_scale"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_now_one_fixed_primitive_tail_direction_plus_one_exact_reduced_fraction"
    ] is True
