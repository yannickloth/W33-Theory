from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_column_chart_failure_bridge import (
    build_current_k3_mixed_plane_column_chart_failure_summary,
)


def test_current_mixed_plane_column_chart_failure_has_expected_counts() -> None:
    summary = build_current_k3_mixed_plane_column_chart_failure_summary()
    current = summary["current_mixed_plane_column_chart_state"]
    exact = summary["exact_column_chart_universality"]

    assert current["current_supported_column_count"] == 0
    assert current["current_supported_entry_count"] == 0
    assert exact["supported_column_count"] == 36


def test_current_mixed_plane_column_chart_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_column_chart_failure_summary()[
        "current_k3_mixed_plane_column_chart_failure_theorem"
    ]
    assert all(theorem.values())
