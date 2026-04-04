"""
Phase CDIX — K3 tail splitness-breaking criterion.

CDVIII identified the canonical chart `ΔC=14105` with nonzero slot activation.
This phase makes the remaining external wall more concrete: exact K3 tail
realization is equivalent to breaking splitness in the existing tail slot on
the fixed carrier-preserving package.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_splitness_breaking_criterion_bridge import (
    build_k3_tail_splitness_breaking_criterion_summary,
)


def test_phase_cdix_realization_is_splitness_breaking() -> None:
    theorem = build_k3_tail_splitness_breaking_criterion_summary()[
        "k3_tail_splitness_breaking_criterion_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_breaking_splitness_in_the_existing_tail_slot"
    ] is True


def test_phase_cdix_live_wall_is_splitness_breaking_problem() -> None:
    theorem = build_k3_tail_splitness_breaking_criterion_summary()[
        "k3_tail_splitness_breaking_criterion_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_splitness_breaking_problem_on_the_same_fixed_carrier_package"
    ] is True
