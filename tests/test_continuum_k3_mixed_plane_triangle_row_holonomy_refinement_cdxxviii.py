"""
Phase CDXXVIII — triangle-row support strictly refines holonomy class.

CDXXVI localized the positive datum to one supported triangle row of the
off-diagonal curvature block. This phase shows that local row support is
strictly finer than parity or reduced holonomy class: every holonomy class
already contains triangles with 0, 1, and 2 supported rows.
"""

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


def test_phase_cdxxviii_triangle_row_support_strictly_refines_holonomy_class() -> None:
    theorem = build_k3_mixed_plane_triangle_row_holonomy_refinement_summary()[
        "k3_mixed_plane_triangle_row_holonomy_refinement_theorem"
    ]
    assert theorem[
        "therefore_triangle_row_support_is_strictly_finer_than_reduced_holonomy_class"
    ] is True


def test_phase_cdxxviii_live_wall_is_genuinely_precomplex_local() -> None:
    theorem = build_k3_mixed_plane_triangle_row_holonomy_refinement_summary()[
        "k3_mixed_plane_triangle_row_holonomy_refinement_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_genuinely_precomplex_local_not_merely_a_holonomy_shadow_selection_problem"
    ] is True
