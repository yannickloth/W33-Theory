"""
Phase CDIII — K3 tail affine increment witness criterion.

CDII packaged the missing target as one affine displacement from the current
zero point. Since the current refined K3 point is exactly zero in promoted
witness coordinates, this phase reduces the wall one more step: any one exact
affine increment already identifies the full affine target.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_affine_increment_witness_bridge import (
    build_k3_tail_affine_increment_witness_summary,
)


def test_phase_cdiii_any_one_affine_increment_identifies_full_target() -> None:
    theorem = build_k3_tail_affine_increment_witness_summary()[
        "k3_tail_affine_increment_witness_theorem"
    ]
    assert theorem[
        "therefore_any_one_promoted_affine_increment_identifies_the_full_affine_witness_target"
    ] is True


def test_phase_cdiii_live_wall_is_one_affine_increment_witness() -> None:
    theorem = build_k3_tail_affine_increment_witness_summary()[
        "k3_tail_affine_increment_witness_theorem"
    ]
    assert theorem[
        "therefore_the_live_external_wall_is_existence_of_any_one_exact_affine_increment_witness_on_the_same_fixed_package"
    ] is True
