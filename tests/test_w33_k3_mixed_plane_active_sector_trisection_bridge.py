from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_active_sector_trisection_bridge import (
    build_k3_mixed_plane_active_sector_trisection_summary,
)


def test_active_sector_trisection_has_expected_ranks() -> None:
    summary = build_k3_mixed_plane_active_sector_trisection_summary()
    sectors = summary["mixed_plane_active_sector_trisection"]

    assert sectors["fan_adjacent_rank"] == 24
    assert sectors["upper_remote_rank"] == 6
    assert sectors["lower_remote_rank"] == 6


def test_active_sector_trisection_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_active_sector_trisection_summary()[
        "k3_mixed_plane_active_sector_trisection_theorem"
    ]
    assert all(theorem.values())
