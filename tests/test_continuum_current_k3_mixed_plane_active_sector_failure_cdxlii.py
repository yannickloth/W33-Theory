"""
Phase CDXLII — current K3 mixed-plane active sector failure.

CDXLI splits the live wall into three exact full-rank sectors. This phase
shows the current host still vanishes on all three.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_active_sector_failure_bridge import (
    build_current_k3_mixed_plane_active_sector_failure_summary,
)


def test_phase_cdxlii_current_host_fails_three_sector_split_exactly() -> None:
    theorem = build_current_k3_mixed_plane_active_sector_failure_summary()[
        "current_k3_mixed_plane_active_sector_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_three_sector_test_for_one_reason_only_all_three_live_active_sectors_still_vanish"
    ] is True
