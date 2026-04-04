"""
Phase CDXXXIII — K3 mixed-plane active-column basis.

The row-entry wall no longer ranges over all 45 sign channels. This phase
shows the exact off-diagonal curvature lives on a full-rank 36-column active
complement, with the remaining 9 columns forming a rigid inert block.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_active_column_basis_bridge import (
    build_k3_mixed_plane_active_column_basis_summary,
)


def test_phase_cdxxxiii_wall_lives_on_full_rank_36_column_active_complement() -> None:
    theorem = build_k3_mixed_plane_active_column_basis_summary()[
        "k3_mixed_plane_active_column_basis_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_the_first_nonzero_row_entry_witness_on_the_full_rank_36_column_active_complement"
    ] is True


def test_phase_cdxxxiii_live_wall_no_longer_ranges_over_all_45_sign_channels() -> None:
    theorem = build_k3_mixed_plane_active_column_basis_summary()[
        "k3_mixed_plane_active_column_basis_theorem"
    ]
    assert theorem[
        "the_live_external_wall_no_longer_ranges_over_all_45_sign_channels"
    ] is True
