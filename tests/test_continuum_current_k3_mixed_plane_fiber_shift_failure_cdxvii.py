"""
Phase CDXVII — current K3 mixed-plane fiber-shift failure.

CDXVI reduced the positive datum to the reduced nonzero fiber shift
`[[0,1],[0,0]]`. This phase applies that smallest witness criterion to the
actual current host and shows the remaining failure is now exactly absence of
that reduced nonzero fiber shift on the same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_fiber_shift_failure_bridge import (
    build_current_k3_mixed_plane_fiber_shift_failure_summary,
)


def test_phase_cdxvii_current_host_fails_only_by_missing_nonzero_reduced_fiber_shift() -> None:
    theorem = build_current_k3_mixed_plane_fiber_shift_failure_summary()[
        "current_k3_mixed_plane_fiber_shift_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_fiber_shift_witness_test_for_one_reason_only_the_nonzero_reduced_fiber_shift_is_missing"
    ] is True


def test_phase_cdxvii_live_wall_is_first_nonzero_reduced_fiber_shift_witness() -> None:
    theorem = build_current_k3_mixed_plane_fiber_shift_failure_summary()[
        "current_k3_mixed_plane_fiber_shift_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_reduced_fiber_shift_witness_on_the_same_fixed_host"
    ] is True
