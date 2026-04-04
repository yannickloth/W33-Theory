"""
Phase CDXXXIV — current K3 mixed-plane active-basis failure.

CDXXXIII shows the live wall sits on a full-rank 36-column active complement.
This phase applies that to the current host and shows the whole active basis
block still vanishes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_active_basis_failure_bridge import (
    build_current_k3_mixed_plane_active_basis_failure_summary,
)


def test_phase_cdxxxiv_current_host_fails_only_by_zero_on_full_rank_active_complement() -> None:
    theorem = build_current_k3_mixed_plane_active_basis_failure_summary()[
        "current_k3_mixed_plane_active_basis_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_active_basis_test_for_one_reason_only_the_full_rank_36_column_complement_remains_zero"
    ] is True


def test_phase_cdxxxiv_live_wall_is_first_nonzero_row_entry_on_active_basis_block() -> None:
    theorem = build_current_k3_mixed_plane_active_basis_failure_summary()[
        "current_k3_mixed_plane_active_basis_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_row_entry_witness_on_the_full_rank_36_column_active_complement"
    ] is True
