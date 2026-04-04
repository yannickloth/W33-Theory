from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_canonical_integral_chart_bridge import (  # noqa: E402
    build_k3_tail_canonical_integral_chart_summary,
)


def test_canonical_integral_chart_is_dc() -> None:
    summary = build_k3_tail_canonical_integral_chart_summary()
    chart = summary["canonical_integral_chart"]
    assert chart["name"] == "dC"
    assert chart["exact_increment"] == "14105"


def test_canonical_integral_chart_theorem_holds() -> None:
    theorem = build_k3_tail_canonical_integral_chart_summary()[
        "k3_tail_canonical_integral_chart_theorem"
    ]
    assert theorem[
        "all_promoted_coordinate_charts_are_already_equivalent_local_extension_problems"
    ] is True
    assert theorem["the_promoted_integral_charts_are_exactly_dC_and_dL"] is True
    assert theorem[
        "among_integral_charts_dC_is_the_least_complexity_chart_by_absolute_size"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_the_canonical_integral_chart_equation_deltaC_equals_14105"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_canonical_integral_coordinate_extension_problem"
    ] is True
