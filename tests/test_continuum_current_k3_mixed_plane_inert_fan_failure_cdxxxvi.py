"""
Phase CDXXXVI — current K3 mixed-plane inert-fan failure.

CDXXXV identifies the inert block geometrically. This phase applies that
description back to the current host and shows the active complement to the
fan still vanishes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_inert_fan_failure_bridge import (
    build_current_k3_mixed_plane_inert_fan_failure_summary,
)


def test_phase_cdxxxvi_current_host_fails_only_by_zero_off_inert_fan() -> None:
    theorem = build_current_k3_mixed_plane_inert_fan_failure_summary()[
        "current_k3_mixed_plane_inert_fan_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_inert_fan_test_for_one_reason_only_the_active_complement_still_vanishes"
    ] is True


def test_phase_cdxxxvi_live_wall_is_first_nonzero_row_entry_off_inert_fan() -> None:
    theorem = build_current_k3_mixed_plane_inert_fan_failure_summary()[
        "current_k3_mixed_plane_inert_fan_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_row_entry_witness_off_the_rigid_inert_fan"
    ] is True
