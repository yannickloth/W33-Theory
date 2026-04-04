"""
Phase CDXLIII — K3 mixed-plane fan shell split.

The fan-adjacent rank-24 sector splits exactly as 1 + 3 + 20 in full rank.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_fan_shell_split_bridge import (
    build_k3_mixed_plane_fan_shell_split_summary,
)


def test_phase_cdxliii_fan_sector_is_an_exact_full_rank_shell_split() -> None:
    theorem = build_k3_mixed_plane_fan_shell_split_summary()[
        "k3_mixed_plane_fan_shell_split_theorem"
    ]
    assert theorem[
        "therefore_the_fan_adjacent_live_sector_is_itself_an_exact_full_rank_shell_split"
    ] is True
