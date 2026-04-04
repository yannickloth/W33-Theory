"""
Phase CDVI — K3 tail canonical integral chart.

CDV localized the wall to any promoted coordinate chart. This phase picks the
least-complexity exact chart and reduces the remaining wall to one canonical
integral equation: `ΔC = 14105`.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_canonical_integral_chart_bridge import (
    build_k3_tail_canonical_integral_chart_summary,
)


def test_phase_cdvi_exact_realization_reduces_to_delta_c_chart() -> None:
    theorem = build_k3_tail_canonical_integral_chart_summary()[
        "k3_tail_canonical_integral_chart_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_the_canonical_integral_chart_equation_deltaC_equals_14105"
    ] is True


def test_phase_cdvi_live_wall_is_one_canonical_integral_extension_problem() -> None:
    theorem = build_k3_tail_canonical_integral_chart_summary()[
        "k3_tail_canonical_integral_chart_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_canonical_integral_coordinate_extension_problem"
    ] is True
