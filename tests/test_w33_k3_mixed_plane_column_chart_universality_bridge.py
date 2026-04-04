from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_column_chart_universality_bridge import (
    build_k3_mixed_plane_column_chart_universality_summary,
)


def test_mixed_plane_column_chart_universality_has_expected_counts() -> None:
    summary = build_k3_mixed_plane_column_chart_universality_summary()
    universality = summary["column_chart_universality"]

    assert universality["curvature_column_count"] == 45
    assert universality["supported_column_count"] == 36
    assert universality["columns_with_both_row_components"] == 36
    assert universality["columns_with_both_nonzero_values"] == 36


def test_mixed_plane_column_chart_universality_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_column_chart_universality_summary()[
        "k3_mixed_plane_column_chart_universality_theorem"
    ]
    assert all(theorem.values())
