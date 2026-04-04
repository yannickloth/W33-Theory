"""
Phase CDVIII — K3 tail canonical-chart slot equivalence.

CDVII reduced the external wall to the canonical integral equation
`ΔC=14105`. This phase makes that equation genuinely external: on the fixed
carrier-preserving package, solving `ΔC=14105` is equivalent to activating the
unique nonzero tail slot.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_canonical_chart_slot_equivalence_bridge import (
    build_k3_tail_canonical_chart_slot_equivalence_summary,
)


def test_phase_cdviii_delta_c_equation_matches_nonzero_slot_activation() -> None:
    theorem = build_k3_tail_canonical_chart_slot_equivalence_summary()[
        "k3_tail_canonical_chart_slot_equivalence_theorem"
    ]
    assert theorem[
        "therefore_solving_deltaC_equals_14105_on_the_fixed_package_is_equivalent_to_activating_the_unique_nonzero_tail_slot"
    ] is True


def test_phase_cdviii_live_wall_is_one_slot_activation_problem() -> None:
    theorem = build_k3_tail_canonical_chart_slot_equivalence_summary()[
        "k3_tail_canonical_chart_slot_equivalence_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_slot_activation_problem_on_the_existing_k3_tail_channel"
    ] is True
