"""
Phase CDII — K3 tail affine witness target.

CD made the live wall a one-witness problem, and CDI showed the present refined
K3 object still sits at the zero witness point. This phase packages the missing
positive target exactly as one affine displacement from that zero point to the
unique exact witness point.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_affine_witness_target_bridge import (
    build_k3_tail_affine_witness_target_summary,
)


def test_phase_cdii_missing_target_is_one_affine_witness_displacement() -> None:
    theorem = build_k3_tail_affine_witness_target_summary()[
        "k3_tail_affine_witness_target_theorem"
    ]
    assert theorem[
        "the_missing_k3_side_addition_is_exactly_one_affine_displacement_from_the_current_zero_point_to_that_witness_point"
    ] is True


def test_phase_cdii_live_wall_is_one_exact_affine_target() -> None:
    theorem = build_k3_tail_affine_witness_target_summary()[
        "k3_tail_affine_witness_target_theorem"
    ]
    assert theorem[
        "therefore_the_live_external_wall_is_one_exact_affine_witness_target_on_the_same_fixed_package"
    ] is True
