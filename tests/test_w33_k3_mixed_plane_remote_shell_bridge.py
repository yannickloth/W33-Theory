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


def test_mixed_plane_remote_shell_has_expected_structure() -> None:
    summary = build_k3_mixed_plane_remote_shell_summary()
    remote = summary["mixed_plane_remote_shell"]

    assert remote["remote_points"] == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    assert remote["remote_line_count"] == 18
    assert remote["remote_graph_degree_distribution"] == {3: 12}
    assert remote["remote_column_rank"] == 12


def test_mixed_plane_remote_shell_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_remote_shell_summary()[
        "k3_mixed_plane_remote_shell_theorem"
    ]
    assert all(theorem.values())
