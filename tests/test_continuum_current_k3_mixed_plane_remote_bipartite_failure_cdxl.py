"""
Phase CDXL — current K3 mixed-plane remote bipartite failure.

CDXXXIX shows the remote shell splits into two exact K3,3 components. This
phase applies that split back to the current host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_remote_bipartite_failure_bridge import (
    build_current_k3_mixed_plane_remote_bipartite_failure_summary,
)


def test_phase_cdxl_current_host_fails_remote_bipartite_split_exactly() -> None:
    theorem = build_current_k3_mixed_plane_remote_bipartite_failure_summary()[
        "current_k3_mixed_plane_remote_bipartite_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_remote_bipartite_test_for_one_reason_only_both_remote_k3_3_components_still_vanish"
    ] is True
