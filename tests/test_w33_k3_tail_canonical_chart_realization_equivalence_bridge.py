from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_canonical_chart_realization_equivalence_bridge import (  # noqa: E402
    build_k3_tail_canonical_chart_realization_equivalence_summary,
)


def test_canonical_chart_realization_equivalence_theorem_holds() -> None:
    theorem = build_k3_tail_canonical_chart_realization_equivalence_summary()[
        "k3_tail_canonical_chart_realization_equivalence_theorem"
    ]
    assert theorem[
        "exact_k3_tail_realization_is_already_equivalent_to_any_one_exact_affine_increment_witness"
    ] is True
    assert theorem[
        "the_canonical_integral_chart_is_exactly_deltaC_equals_14105"
    ] is True
    assert theorem[
        "the_canonical_integral_chart_is_one_exact_affine_increment_witness_chart"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_solving_deltaC_equals_14105"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_single_integral_equation_on_the_fixed_package"
    ] is True
