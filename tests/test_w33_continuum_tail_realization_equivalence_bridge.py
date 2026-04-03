from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_realization_equivalence_bridge import (  # noqa: E402
    build_continuum_tail_realization_equivalence_summary,
)


def test_tail_operator_line_is_one_dimensional_and_forced() -> None:
    summary = build_continuum_tail_realization_equivalence_summary()
    line = summary["tail_operator_line"]

    assert line["dimension"] == 1
    assert line["forced_nonzero_scalar"] == 217
    assert line["normalized_generator"] == {
        "constant_witness": "65",
        "linear_witness": "662",
        "quadratic_seed_witness": "15650/3",
        "quadratic_sd1_witness": "17993/4",
    }
    assert line["realized_transport_operator"]["constant_witness"] == "14105"
    assert line["realized_matter_operator"]["constant_witness"] == "1142505"


def test_tail_realization_equivalence_theorem_is_exact() -> None:
    theorem = build_continuum_tail_realization_equivalence_summary()[
        "continuum_tail_realization_equivalence_theorem"
    ]
    assert theorem[
        "transport_realization_is_equivalent_to_existence_of_a_nonzero_point_on_the_unique_tail_operator_line"
    ] is True
    assert theorem[
        "any_nonzero_realized_point_on_that_line_has_forced_scalar_217"
    ] is True
    assert theorem["that_forces_the_exact_promoted_transport_operator"] is True
    assert theorem[
        "and_the_exact_matter_operator_then_follows_by_the_81_fold_qutrit_lift"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_exactly_existence_of_one_nonzero_point_on_one_fixed_tail_operator_line"
    ] is True
