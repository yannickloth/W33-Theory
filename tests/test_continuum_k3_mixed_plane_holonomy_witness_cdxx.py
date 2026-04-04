"""
Phase CDXX — K3 mixed-plane holonomy witness.

CDXVIII reduced the positive datum to one nonzero sign-trivial cocycle value.
This phase makes that datum concrete in adapted holonomy language: one
non-identity unipotent sign-trivial holonomy matrix on the fixed mixed-plane
host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_holonomy_witness_bridge import (
    build_k3_mixed_plane_holonomy_witness_summary,
)


def test_phase_cdxx_realization_is_nontrivial_sign_trivial_holonomy_witness() -> None:
    theorem = build_k3_mixed_plane_holonomy_witness_summary()[
        "k3_mixed_plane_holonomy_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nontrivial_sign_trivial_holonomy_witness_on_the_same_fixed_host"
    ] is True


def test_phase_cdxx_live_wall_is_first_nontrivial_sign_trivial_holonomy_witness() -> None:
    theorem = build_k3_mixed_plane_holonomy_witness_summary()[
        "k3_mixed_plane_holonomy_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nontrivial_sign_trivial_holonomy_witness_on_the_same_fixed_host"
    ] is True
