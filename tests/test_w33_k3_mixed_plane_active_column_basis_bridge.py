from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_active_column_basis_bridge import (
    build_k3_mixed_plane_active_column_basis_summary,
)


def test_mixed_plane_active_column_basis_has_expected_counts() -> None:
    summary = build_k3_mixed_plane_active_column_basis_summary()
    basis = summary["mixed_plane_active_column_basis"]

    assert basis["total_curvature_columns"] == 45
    assert basis["active_column_count"] == 36
    assert basis["inactive_column_count"] == 9
    assert basis["off_diagonal_curvature_rank"] == 36
    assert basis["active_column_restricted_rank"] == 36
    assert basis["inactive_column_complement_triples"] == [[36, 40, 44], [37, 41, 42], [38, 39, 43]]


def test_mixed_plane_active_column_basis_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_active_column_basis_summary()[
        "k3_mixed_plane_active_column_basis_theorem"
    ]
    assert all(theorem.values())
