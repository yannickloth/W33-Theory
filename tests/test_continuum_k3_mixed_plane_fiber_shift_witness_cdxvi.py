"""
Phase CDXVI — K3 mixed-plane fiber-shift witness.

CDXIV fixed the exact slot-operator witness, and that witness is already the
qutrit lift `I_81 ⊗ [[0,1],[0,0]]`. So the only genuinely nontrivial missing
datum is the reduced fiber shift `[[0,1],[0,0]]` itself on the mixed-plane
host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_fiber_shift_witness_bridge import (
    build_k3_mixed_plane_fiber_shift_witness_summary,
)


def test_phase_cdxvi_realization_is_unique_mixed_plane_fiber_shift_witness() -> None:
    theorem = build_k3_mixed_plane_fiber_shift_witness_summary()[
        "k3_mixed_plane_fiber_shift_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_nonzero_fiber_shift_witness_on_the_canonical_mixed_plane_host"
    ] is True


def test_phase_cdxvi_live_wall_is_first_nonzero_mixed_plane_fiber_shift_witness() -> None:
    theorem = build_k3_mixed_plane_fiber_shift_witness_summary()[
        "k3_mixed_plane_fiber_shift_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_mixed_plane_fiber_shift_witness_on_the_same_fixed_host"
    ] is True
