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


def test_remote_bipartite_split_has_expected_structure() -> None:
    summary = build_k3_mixed_plane_remote_bipartite_split_summary()
    profiles = summary["mixed_plane_remote_bipartite_split"]["component_profiles"]

    assert profiles[0]["left_part"] == [3, 4, 5]
    assert profiles[0]["right_part"] == [12, 13, 14]
    assert profiles[0]["supporting_lines"] == list(range(9, 18))
    assert profiles[0]["restricted_curvature_rank"] == 6
    assert profiles[1]["left_part"] == [6, 7, 8]
    assert profiles[1]["right_part"] == [9, 10, 11]
    assert profiles[1]["supporting_lines"] == list(range(18, 27))
    assert profiles[1]["restricted_curvature_rank"] == 6


def test_remote_bipartite_split_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_remote_bipartite_split_summary()[
        "k3_mixed_plane_remote_bipartite_split_theorem"
    ]
    assert all(theorem.values())
