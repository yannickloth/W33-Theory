from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_row_entry_failure_bridge import (
    build_current_k3_mixed_plane_row_entry_failure_summary,
)


def test_current_mixed_plane_row_entry_failure_has_expected_shape() -> None:
    summary = build_current_k3_mixed_plane_row_entry_failure_summary()
    state = summary["current_mixed_plane_row_entry_state"]
    exact = summary["exact_row_entry_witness"]

    assert state["source"] == "canonical_mixed_k3_plane_qutrit_lift"
    assert state["ordered_line_types"] == ["positive", "negative"]
    assert state["mixed_signature"] == [1, 1]
    assert state["qutrit_lift_split"] == [81, 81]
    assert state["current_slot_state"] == "zero_by_splitness"
    assert state["current_supported_row_count"] == 0
    assert state["current_supported_entry_count"] == 0

    assert exact["supported_row_count"] == 4046
    assert exact["row_support_size_distribution"] == {1: 4046}


def test_current_mixed_plane_row_entry_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_row_entry_failure_summary()[
        "current_k3_mixed_plane_row_entry_failure_theorem"
    ]
    assert all(theorem.values())
