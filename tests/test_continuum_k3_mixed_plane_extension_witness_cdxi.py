"""
Phase CDXI — K3 mixed-plane extension witness.

CDX turned the K3 wall into a nonzero extension-class witness problem on the
fixed package. This phase attaches that witness to the actual external object:
the canonical mixed K3 plane qutrit lift.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_extension_witness_bridge import (
    build_k3_mixed_plane_extension_witness_summary,
)


def test_phase_cdxi_realization_is_mixed_plane_extension_witness() -> None:
    theorem = build_k3_mixed_plane_extension_witness_summary()[
        "k3_mixed_plane_extension_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_extension_witness_on_the_canonical_mixed_k3_plane_qutrit_lift"
    ] is True


def test_phase_cdxi_live_wall_is_mixed_plane_deformation_problem() -> None:
    theorem = build_k3_mixed_plane_extension_witness_summary()[
        "k3_mixed_plane_extension_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_mixed_plane_deformation_witness_problem_not_a_search_for_a_new_162_host"
    ] is True
