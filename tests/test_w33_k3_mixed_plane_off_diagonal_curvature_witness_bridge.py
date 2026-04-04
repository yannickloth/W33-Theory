from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_off_diagonal_curvature_witness_bridge import (
    build_k3_mixed_plane_off_diagonal_curvature_witness_summary,
)


def test_mixed_plane_off_diagonal_curvature_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_off_diagonal_curvature_witness_summary()
    curvature = summary["transport_twisted_off_diagonal_curvature_package"]

    assert curvature["full_curvature_rank"] == 42
    assert curvature["off_diagonal_curvature_rank"] == 36
    assert curvature["off_diagonal_curvature_support_rows"] == 4046
    assert curvature["curvature_factors_through_sign_quotient"] is True
    assert curvature["upper_right_curvature_identity_exact"] is True


def test_mixed_plane_off_diagonal_curvature_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_off_diagonal_curvature_witness_summary()[
        "k3_mixed_plane_off_diagonal_curvature_witness_theorem"
    ]
    assert all(theorem.values())
