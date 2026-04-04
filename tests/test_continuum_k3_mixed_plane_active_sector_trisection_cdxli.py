"""
Phase CDXLI — K3 mixed-plane active sector trisection.

The live 36-column active block splits exactly as 24 + 6 + 6 in full rank.
"""

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


def test_phase_cdxli_live_wall_splits_into_three_exact_full_rank_sectors() -> None:
    theorem = build_k3_mixed_plane_active_sector_trisection_summary()[
        "k3_mixed_plane_active_sector_trisection_theorem"
    ]
    assert theorem[
        "therefore_the_live_wall_splits_into_three_exact_full_rank_sectors"
    ] is True
