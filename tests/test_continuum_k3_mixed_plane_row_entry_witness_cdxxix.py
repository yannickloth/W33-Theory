"""
Phase CDXXIX — K3 mixed-plane row-entry witness.

CDXXVI reduced the local geometric datum to one supported triangle row of the
off-diagonal curvature block. This phase makes the row itself rigid: every
supported row is one-sparse, so one nonzero row entry already serves as the
exact local witness.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_row_entry_witness_bridge import (
    build_k3_mixed_plane_row_entry_witness_summary,
)


def test_phase_cdxxix_realization_is_nonzero_row_entry_witness() -> None:
    theorem = build_k3_mixed_plane_row_entry_witness_summary()[
        "k3_mixed_plane_row_entry_witness_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_row_entry_witness_on_the_same_fixed_host"
    ] is True


def test_phase_cdxxix_live_wall_is_first_nonzero_row_entry_witness() -> None:
    theorem = build_k3_mixed_plane_row_entry_witness_summary()[
        "k3_mixed_plane_row_entry_witness_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_row_entry_witness_on_the_same_fixed_host"
    ] is True
