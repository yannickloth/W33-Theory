"""
Phase CDXXV — current K3 mixed-plane off-diagonal curvature failure.

CDXXIV localized the positive datum at the level of the transport-twisted
precomplex. This phase applies that criterion back to the current host and
shows the remaining failure is now exactly absence of the first genuine
nonzero off-diagonal curvature witness on the same fixed mixed-plane host.
"""

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


def test_phase_cdxxv_current_host_fails_only_by_missing_nonzero_off_diagonal_curvature() -> None:
    theorem = build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary()[
        "current_k3_mixed_plane_off_diagonal_curvature_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_off_diagonal_curvature_test_for_one_reason_only_the_nonzero_curvature_coupling_is_missing"
    ] is True


def test_phase_cdxxv_live_wall_is_first_nonzero_off_diagonal_curvature_witness() -> None:
    theorem = build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary()[
        "current_k3_mixed_plane_off_diagonal_curvature_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_off_diagonal_curvature_witness_on_the_same_fixed_host"
    ] is True
