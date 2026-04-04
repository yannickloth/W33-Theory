"""
Phase CDV — K3 tail coordinate-extension equivalence.

CDIV reduced exact K3 tail realization to any one affine increment witness.
This phase packages the same wall as a local extension problem: each promoted
coordinate chart gives an equivalent anchored extension problem on the fixed
carrier-preserving K3 package.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_coordinate_extension_equivalence_bridge import (
    build_k3_tail_coordinate_extension_equivalence_summary,
)


def test_phase_cdv_each_chart_gives_equivalent_local_extension_problem() -> None:
    theorem = build_k3_tail_coordinate_extension_equivalence_summary()[
        "k3_tail_coordinate_extension_equivalence_theorem"
    ]
    assert theorem[
        "therefore_each_promoted_coordinate_chart_gives_an_equivalent_local_extension_problem"
    ] is True


def test_phase_cdv_live_wall_is_coordinate_anchored_extension_problem() -> None:
    theorem = build_k3_tail_coordinate_extension_equivalence_summary()[
        "k3_tail_coordinate_extension_equivalence_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_one_coordinate_anchored_extension_problem_in_any_promoted_chart"
    ] is True
