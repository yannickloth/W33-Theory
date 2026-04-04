from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_holonomy_failure_bridge import (
    build_current_k3_mixed_plane_holonomy_failure_summary,
)


def test_current_mixed_plane_holonomy_failure_has_expected_shape() -> None:
    summary = build_current_k3_mixed_plane_holonomy_failure_summary()
    state = summary["current_mixed_plane_holonomy_state"]
    exact = summary["exact_mixed_plane_holonomy_witness"]

    assert state["source"] == "canonical_mixed_k3_plane_qutrit_lift"
    assert state["ordered_line_types"] == ["positive", "negative"]
    assert state["mixed_signature"] == [1, 1]
    assert state["qutrit_lift_split"] == [81, 81]
    assert state["current_slot_state"] == "zero_by_splitness"
    assert state["current_sign_trivial_holonomy_matrices"] == [[[1, 0], [0, 1]]]
    assert state["current_sign_nontrivial_holonomy_matrices"] == []

    assert exact["canonical_nontrivial_holonomy"] == [[1, 1], [0, 1]]
    assert exact["gauge_related_nontrivial_holonomy"] == [[1, 2], [0, 1]]


def test_current_mixed_plane_holonomy_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_holonomy_failure_summary()[
        "current_k3_mixed_plane_holonomy_failure_theorem"
    ]
    assert all(theorem.values())
