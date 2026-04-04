"""
Phase CDXIII — K3 mixed-plane unique slot-only deformation.

CDXII fixed the witness to be support-preserving on the canonical mixed-plane
lift. This phase sharpens the remaining wall again: because only one nonzero
orbit exists up to gauge in the existing slot, the live wall is now existence
of one unique support-preserving slot-only deformation class.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_unique_slot_deformation_bridge import (
    build_k3_mixed_plane_unique_slot_deformation_summary,
)


def test_phase_cdxiii_realization_is_unique_slot_only_deformation() -> None:
    theorem = build_k3_mixed_plane_unique_slot_deformation_summary()[
        "k3_mixed_plane_unique_slot_deformation_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_slot_only_deformation_class_on_the_canonical_mixed_plane_lift"
    ] is True


def test_phase_cdxiii_live_wall_is_unique_deformation_existence_problem() -> None:
    theorem = build_k3_mixed_plane_unique_slot_deformation_summary()[
        "k3_mixed_plane_unique_slot_deformation_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_unique_support_preserving_slot_only_deformation_existence_problem"
    ] is True
