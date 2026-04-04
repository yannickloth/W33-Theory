from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_coordinate_extension_equivalence_bridge import (  # noqa: E402
    build_k3_tail_coordinate_extension_equivalence_summary,
)


def test_each_coordinate_chart_is_exact_extension_chart() -> None:
    summary = build_k3_tail_coordinate_extension_equivalence_summary()
    charts = summary["coordinate_extension_charts"]
    assert charts["dC"]["is_exact_extension_chart"] is True
    assert charts["dL"]["is_exact_extension_chart"] is True
    assert charts["dQ_seed"]["is_exact_extension_chart"] is True
    assert charts["dQ_sd1"]["is_exact_extension_chart"] is True


def test_coordinate_extension_equivalence_theorem_holds() -> None:
    theorem = build_k3_tail_coordinate_extension_equivalence_summary()[
        "k3_tail_coordinate_extension_equivalence_theorem"
    ]
    assert theorem[
        "each_promoted_coordinate_chart_recovers_the_same_exact_scale_217_over_12"
    ] is True
    assert theorem[
        "exact_k3_tail_realization_is_already_equivalent_to_any_one_exact_affine_increment_witness"
    ] is True
    assert theorem[
        "therefore_each_promoted_coordinate_chart_gives_an_equivalent_local_extension_problem"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_coordinate_anchored_extension_problem_in_any_promoted_chart"
    ] is True
