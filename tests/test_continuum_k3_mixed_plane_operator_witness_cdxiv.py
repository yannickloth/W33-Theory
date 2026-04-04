"""
Phase CDXIV — K3 mixed-plane operator witness.

CDXIII fixed the deformation class uniquely. This phase turns that formal
uniqueness into the concrete operator witness shape the repo can recognize:
one support-preserving rank-81 square-zero tail operator on the canonical
mixed-plane lift, with normal form `I_81 ⊗ [[0,1],[0,0]]`, equivalently
`J2^81`.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_operator_witness_bridge import (
    build_k3_mixed_plane_operator_witness_summary,
)


def test_phase_cdxiv_realization_is_unique_mixed_plane_operator_witness() -> None:
    theorem = build_k3_mixed_plane_operator_witness_summary()[
        "k3_mixed_plane_operator_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_rank_81_square_zero_slot_operator_witness_on_the_canonical_mixed_plane_lift"
    ] is True


def test_phase_cdxiv_live_wall_is_operator_witness_existence_problem() -> None:
    theorem = build_k3_mixed_plane_operator_witness_summary()[
        "k3_mixed_plane_operator_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_existence_of_that_one_operator_witness_on_genuine_k3_side_data"
    ] is True
