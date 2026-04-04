"""
Phase CDXLIV — current K3 mixed-plane fan shell failure.

CDXLIII splits the fan-adjacent sector into exact shell pieces. This phase
shows the current host still vanishes on all three.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_fan_shell_failure_bridge import (
    build_current_k3_mixed_plane_fan_shell_failure_summary,
)


def test_phase_cdxliv_current_host_fails_fan_shell_split_exactly() -> None:
    theorem = build_current_k3_mixed_plane_fan_shell_failure_summary()[
        "current_k3_mixed_plane_fan_shell_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_fan_shell_test_for_one_reason_only_all_three_fan_shells_still_vanish"
    ] is True
