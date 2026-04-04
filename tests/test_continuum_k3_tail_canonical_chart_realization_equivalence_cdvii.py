"""
Phase CDVII — K3 tail canonical-chart realization equivalence.

CDVI reduced the live wall to the canonical integral chart `ΔC=14105`. This
phase collapses the wall completely in that chart: exact K3 tail realization
is equivalent to solving that one canonical integral equation on the fixed
carrier-preserving package.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_canonical_chart_realization_equivalence_bridge import (
    build_k3_tail_canonical_chart_realization_equivalence_summary,
)


def test_phase_cdvii_realization_is_equivalent_to_delta_c_equation() -> None:
    theorem = build_k3_tail_canonical_chart_realization_equivalence_summary()[
        "k3_tail_canonical_chart_realization_equivalence_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_solving_deltaC_equals_14105"
    ] is True


def test_phase_cdvii_live_wall_is_one_integral_equation() -> None:
    theorem = build_k3_tail_canonical_chart_realization_equivalence_summary()[
        "k3_tail_canonical_chart_realization_equivalence_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_single_integral_equation_on_the_fixed_package"
    ] is True
