"""
Phase CDXII — K3 mixed-plane support-preserving witness.

CDXI attached the nonzero extension witness to the canonical mixed K3 plane
lift. This phase sharpens that host-localization: any exact witness must
preserve the canonical mixed-plane support data and only change the extension
class in the existing tail slot.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_support_preserving_witness_bridge import (
    build_k3_mixed_plane_support_preserving_witness_summary,
)


def test_phase_cdxii_witness_preserves_mixed_plane_support() -> None:
    theorem = build_k3_mixed_plane_support_preserving_witness_summary()[
        "k3_mixed_plane_support_preserving_witness_theorem"
    ]
    assert theorem[
        "therefore_any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package_and_only_change_the_extension_class"
    ] is True


def test_phase_cdxii_live_wall_is_support_preserving_deformation_problem() -> None:
    theorem = build_k3_mixed_plane_support_preserving_witness_summary()[
        "k3_mixed_plane_support_preserving_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_support_preserving_mixed_plane_deformation_witness_problem"
    ] is True
