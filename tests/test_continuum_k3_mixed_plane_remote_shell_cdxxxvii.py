"""
Phase CDXXXVII — K3 mixed-plane remote shell.

The anchored fan is exact but not exhaustive. This phase shows the 12 points
completely off that fan already form a full-rank remote shell.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_remote_shell_bridge import (
    build_k3_mixed_plane_remote_shell_summary,
)


def test_phase_cdxxxvii_live_wall_not_confined_to_fan_sector() -> None:
    theorem = build_k3_mixed_plane_remote_shell_summary()[
        "k3_mixed_plane_remote_shell_theorem"
    ]
    assert theorem[
        "therefore_the_live_mixed_plane_wall_is_not_confined_to_the_fan_sector_and_already_contains_a_full_rank_remote_12_point_shell"
    ] is True
