"""
Phase CDXXXIX — K3 mixed-plane remote bipartite split.

The remote shell is not irreducible. This phase shows it splits into two exact
K3,3 witness components.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_remote_bipartite_split_bridge import (
    build_k3_mixed_plane_remote_bipartite_split_summary,
)


def test_phase_cdxxxix_remote_wall_may_first_appear_in_either_k33_component() -> None:
    theorem = build_k3_mixed_plane_remote_bipartite_split_summary()[
        "k3_mixed_plane_remote_bipartite_split_theorem"
    ]
    assert theorem[
        "therefore_the_live_remote_wall_may_first_appear_in_either_exact_k3_3_component"
    ] is True
