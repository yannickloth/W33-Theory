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


def test_fan_shell_split_has_expected_ranks() -> None:
    summary = build_k3_mixed_plane_fan_shell_split_summary()
    fan = summary["mixed_plane_fan_shell_split"]

    assert fan["anchor_rank"] == 1
    assert fan["spoke_rank"] == 3
    assert fan["outer_shell_rank"] == 20
    assert fan["fan_adjacent_rank"] == 24


def test_fan_shell_split_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_fan_shell_split_summary()[
        "k3_mixed_plane_fan_shell_split_theorem"
    ]
    assert all(theorem.values())
