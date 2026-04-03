"""
Phase CDIV — K3 tail increment-realization equivalence.

CDIII reduced the current affine target to any one exact affine increment
witness. This phase collapses the wall completely on the fixed package:
exact K3 tail realization is equivalent to existence of any one such increment
witness from genuine K3-side data.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_increment_realization_equivalence_bridge import (
    build_k3_tail_increment_realization_equivalence_summary,
)


def test_phase_cdiv_increment_witness_is_exact_realization_equivalence() -> None:
    theorem = build_k3_tail_increment_realization_equivalence_summary()[
        "k3_tail_increment_realization_equivalence_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness"
    ] is True


def test_phase_cdiv_live_wall_is_one_increment_witness_existence_problem() -> None:
    theorem = build_k3_tail_increment_realization_equivalence_summary()[
        "k3_tail_increment_realization_equivalence_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_exactly_one_affine_increment_witness_existence_problem"
    ] is True
