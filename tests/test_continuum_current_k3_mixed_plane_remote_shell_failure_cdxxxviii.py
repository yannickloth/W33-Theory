"""
Phase CDXXXVIII — current K3 mixed-plane remote-shell failure.

CDXXXVII shows the live wall is not confined to the fan sector. This phase
applies that to the current host and shows the remote shell still vanishes.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_remote_shell_failure_bridge import (
    build_current_k3_mixed_plane_remote_shell_failure_summary,
)


def test_phase_cdxxxviii_current_host_fails_remote_shell_exactly() -> None:
    theorem = build_current_k3_mixed_plane_remote_shell_failure_summary()[
        "current_k3_mixed_plane_remote_shell_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_remote_shell_test_for_one_reason_only_the_full_rank_remote_shell_still_vanishes"
    ] is True
