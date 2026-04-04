"""
Phase CDXXIV — K3 mixed-plane off-diagonal curvature witness.

CDXXII reduced the positive datum to one nonzero nilpotent holonomy increment.
This phase promotes the exact geometric source already present in the repo:
one support-preserving nonzero off-diagonal curvature witness in the
transport-twisted precomplex on the same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_off_diagonal_curvature_witness_bridge import (
    build_k3_mixed_plane_off_diagonal_curvature_witness_summary,
)


def test_phase_cdxxiv_realization_is_nonzero_off_diagonal_curvature_witness() -> None:
    theorem = build_k3_mixed_plane_off_diagonal_curvature_witness_summary()[
        "k3_mixed_plane_off_diagonal_curvature_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_off_diagonal_curvature_witness_on_the_same_fixed_host"
    ] is True


def test_phase_cdxxiv_live_wall_is_first_nonzero_off_diagonal_curvature_witness() -> None:
    theorem = build_k3_mixed_plane_off_diagonal_curvature_witness_summary()[
        "k3_mixed_plane_off_diagonal_curvature_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_off_diagonal_curvature_witness_on_the_same_fixed_host"
    ] is True
