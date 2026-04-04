"""
Phase CDXXVII — current K3 mixed-plane triangle-row curvature failure.

CDXXVI reduced the positive datum to a single supported transport-triangle row
of the off-diagonal curvature block. This phase applies that local criterion
back to the current host and shows the remaining failure is now exactly
absence of the first genuine nonzero triangle-row curvature witness on the
same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_triangle_row_curvature_failure_bridge import (
    build_current_k3_mixed_plane_triangle_row_curvature_failure_summary,
)


def test_phase_cdxxvii_current_host_fails_only_by_missing_nonzero_supported_rows() -> None:
    theorem = build_current_k3_mixed_plane_triangle_row_curvature_failure_summary()[
        "current_k3_mixed_plane_triangle_row_curvature_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_triangle_row_curvature_test_for_one_reason_only_the_nonzero_supported_rows_are_missing"
    ] is True


def test_phase_cdxxvii_live_wall_is_first_nonzero_triangle_row_curvature_witness() -> None:
    theorem = build_current_k3_mixed_plane_triangle_row_curvature_failure_summary()[
        "current_k3_mixed_plane_triangle_row_curvature_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_triangle_row_curvature_witness_on_the_same_fixed_host"
    ] is True
