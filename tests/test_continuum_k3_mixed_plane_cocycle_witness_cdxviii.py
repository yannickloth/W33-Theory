"""
Phase CDXVIII — K3 mixed-plane cocycle witness.

CDXVI reduced the wall to the reduced fiber shift. This phase pushes one step
further back to the first repo-native source of that datum: one nonzero
sign-trivial cocycle value in the adapted transport cocycle package.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_cocycle_witness_bridge import (
    build_k3_mixed_plane_cocycle_witness_summary,
)


def test_phase_cdxviii_realization_is_cocycle_value_witness() -> None:
    theorem = build_k3_mixed_plane_cocycle_witness_summary()[
        "k3_mixed_plane_cocycle_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_cocycle_value_witness_on_the_canonical_mixed_plane_host"
    ] is True


def test_phase_cdxviii_live_wall_is_sign_trivial_cocycle_witness() -> None:
    theorem = build_k3_mixed_plane_cocycle_witness_summary()[
        "k3_mixed_plane_cocycle_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_sign_trivial_cocycle_witness_on_the_same_fixed_host"
    ] is True
