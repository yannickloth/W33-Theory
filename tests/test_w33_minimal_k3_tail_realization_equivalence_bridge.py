from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_minimal_k3_tail_realization_equivalence_bridge import (  # noqa: E402
    build_minimal_k3_tail_realization_equivalence_summary,
)


def test_minimal_datum_already_satisfies_exact_tail_line_and_pair() -> None:
    summary = build_minimal_k3_tail_realization_equivalence_summary()

    assert summary["primitive_generator_syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }
    assert summary["minimal_k3_tail_enhancement_datum"]["transport_arithmetic_pair"] == {
        "denominator_lcm": 12,
        "cleared_coordinate_gcd": 217,
        "recovered_scale": "217/12",
    }


def test_minimal_k3_tail_realization_equivalence_theorem_holds() -> None:
    theorem = build_minimal_k3_tail_realization_equivalence_summary()[
        "minimal_k3_tail_realization_equivalence_theorem"
    ]

    assert theorem[
        "the_unique_minimal_tail_datum_already_lies_on_the_exact_tail_line"
    ] is True
    assert theorem[
        "the_unique_minimal_tail_datum_already_has_the_exact_transport_pair_lcm12_gcd217"
    ] is True
    assert theorem[
        "therefore_realizing_the_unique_minimal_tail_datum_is_sufficient_for_exact_tail_realization_on_the_fixed_package"
    ] is True
    assert theorem[
        "by_cccxcviii_any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_exactly_existence_of_that_one_minimal_datum"
    ] is True
