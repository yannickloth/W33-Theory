"""
Phase CDXXXI — K3 mixed-plane active-column universality.

CDXXIX reduced the positive mixed-plane wall to one nonzero row entry. This
phase shows there is no residual choice among the 36 active curvature columns:
every supported column is already a valid local chart for such a witness.
"""

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


def test_phase_cdxxxi_every_active_curvature_column_is_a_viable_local_chart() -> None:
    theorem = build_k3_mixed_plane_column_chart_universality_summary()[
        "k3_mixed_plane_column_chart_universality_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_row_entry_witness_in_any_fixed_supported_curvature_column"
    ] is True


def test_phase_cdxxxi_live_wall_is_not_a_choice_among_active_columns() -> None:
    theorem = build_k3_mixed_plane_column_chart_universality_summary()[
        "k3_mixed_plane_column_chart_universality_theorem"
    ]
    assert theorem["the_live_external_wall_is_not_a_choice_among_the_36_active_columns"] is True
