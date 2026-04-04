"""
Phase CDXXXV — K3 mixed-plane inert-fan geometry.

The inert 9-column block is not arbitrary. This phase identifies it
geometrically as the non-anchor, non-spoke part of the three quotient lines
through a common anchor point.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_inert_fan_geometry_bridge import (
    build_k3_mixed_plane_inert_fan_geometry_summary,
)


def test_phase_cdxxxv_wall_lives_off_rigid_anchored_inert_fan() -> None:
    theorem = build_k3_mixed_plane_inert_fan_geometry_summary()[
        "k3_mixed_plane_inert_fan_geometry_theorem"
    ]
    assert theorem[
        "therefore_exact_k3_tail_realization_lives_on_the_active_complement_to_one_rigid_anchored_3_line_inert_fan_in_the_45_point_quotient_geometry"
    ] is True


def test_phase_cdxxxv_live_wall_is_first_nonzero_row_entry_off_inert_fan() -> None:
    theorem = build_k3_mixed_plane_inert_fan_geometry_summary()[
        "k3_mixed_plane_inert_fan_geometry_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_row_entry_witness_off_that_rigid_inert_fan"
    ] is True
