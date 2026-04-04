from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_triangle_row_holonomy_refinement_bridge import (
    build_k3_mixed_plane_triangle_row_holonomy_refinement_summary,
)


def test_triangle_row_holonomy_refinement_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_triangle_row_holonomy_refinement_summary()
    refinement = summary["triangle_row_holonomy_refinement"]

    assert refinement["holonomy_class_count"] == 6
    assert refinement["row_support_distribution_by_holonomy_class"]["[[1, 0], [0, 1]]"] == {
        0: 224,
        1: 103,
        2: 201,
    }
    assert refinement["row_support_distribution_by_holonomy_class"]["[[1, 1], [0, 1]]"] == {
        0: 718,
        1: 196,
        2: 403,
    }
    assert refinement["row_support_distribution_by_holonomy_class"]["[[1, 2], [0, 1]]"] == {
        0: 723,
        1: 189,
        2: 363,
    }


def test_triangle_row_holonomy_refinement_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_triangle_row_holonomy_refinement_summary()[
        "k3_mixed_plane_triangle_row_holonomy_refinement_theorem"
    ]
    assert all(theorem.values())
