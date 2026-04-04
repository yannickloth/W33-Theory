"""
Phase CDXXXII — current K3 mixed-plane active-column failure.

CDXXXI showed every supported curvature column is already a valid local chart for a
nonzero row-entry witness. This phase applies that fact to the current host
and shows the failure is now uniform across all 36 active columns.
"""

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


def test_phase_cdxxxii_current_host_fails_only_by_zero_everywhere_in_active_column_charts() -> None:
    theorem = build_current_k3_mixed_plane_column_chart_failure_summary()[
        "current_k3_mixed_plane_column_chart_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_active_column_chart_test_for_one_reason_only_every_active_column_remains_zero"
    ] is True


def test_phase_cdxxxii_live_wall_is_first_nonzero_active_column_anchored_row_entry_witness() -> None:
    theorem = build_current_k3_mixed_plane_column_chart_failure_summary()[
        "current_k3_mixed_plane_column_chart_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_active_column_anchored_row_entry_witness_on_the_same_fixed_host"
    ] is True
