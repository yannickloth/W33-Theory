from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_off_diagonal_curvature_failure_bridge import (
    build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary,
)


def test_current_mixed_plane_off_diagonal_curvature_failure_has_expected_shape() -> None:
    summary = build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary()
    state = summary["current_mixed_plane_off_diagonal_curvature_state"]
    exact = summary["exact_transport_twisted_off_diagonal_curvature"]

    assert state["source"] == "canonical_mixed_k3_plane_qutrit_lift"
    assert state["ordered_line_types"] == ["positive", "negative"]
    assert state["mixed_signature"] == [1, 1]
    assert state["qutrit_lift_split"] == [81, 81]
    assert state["current_slot_state"] == "zero_by_splitness"
    assert state["current_nilpotent_increment"] == [[0, 0], [0, 0]]
    assert state["current_off_diagonal_curvature_rank"] == 0
    assert state["current_off_diagonal_curvature_support_rows"] == 0

    assert exact["off_diagonal_curvature_rank"] == 36
    assert exact["off_diagonal_curvature_support_rows"] == 4046


def test_current_mixed_plane_off_diagonal_curvature_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary()[
        "current_k3_mixed_plane_off_diagonal_curvature_failure_theorem"
    ]
    assert all(theorem.values())
