"""
Phase CDXXX — current K3 mixed-plane row-entry failure.

CDXXIX reduced the positive datum to one supported row entry of the
off-diagonal curvature block. This phase applies that criterion back to the
current host and shows the remaining failure is now exactly absence of the
first genuine nonzero row-entry witness on the same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_row_entry_failure_bridge import (
    build_current_k3_mixed_plane_row_entry_failure_summary,
)


def test_phase_cdxxx_current_host_fails_only_by_missing_nonzero_supported_entry() -> None:
    theorem = build_current_k3_mixed_plane_row_entry_failure_summary()[
        "current_k3_mixed_plane_row_entry_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_row_entry_test_for_one_reason_only_the_nonzero_supported_entry_is_missing"
    ] is True


def test_phase_cdxxx_live_wall_is_first_nonzero_row_entry_witness() -> None:
    theorem = build_current_k3_mixed_plane_row_entry_failure_summary()[
        "current_k3_mixed_plane_row_entry_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_row_entry_witness_on_the_same_fixed_host"
    ] is True
