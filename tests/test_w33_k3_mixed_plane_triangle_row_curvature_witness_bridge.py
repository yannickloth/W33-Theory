from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_triangle_row_curvature_witness_bridge import (
    build_k3_mixed_plane_triangle_row_curvature_witness_summary,
)


def test_mixed_plane_triangle_row_curvature_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_triangle_row_curvature_witness_summary()
    witness = summary["triangle_row_curvature_witness"]

    assert witness["total_transport_triangles"] == 5280
    assert witness["supported_triangle_count"] == 2428
    assert witness["supported_row_count"] == 4046
    assert witness["triangle_row_support_distribution"] == {1: 810, 2: 1618}
    assert witness["first_supported_triangle"] == (0, 1, 2)
    assert witness["first_supported_row_index"] == 1
    assert witness["first_supported_row_component"] == "sign_row"
    assert witness["first_supported_row_nonzero_columns"] == [0]
    assert witness["first_supported_row_nonzero_values"] == [1]


def test_mixed_plane_triangle_row_curvature_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_triangle_row_curvature_witness_summary()[
        "k3_mixed_plane_triangle_row_curvature_witness_theorem"
    ]
    assert all(theorem.values())
