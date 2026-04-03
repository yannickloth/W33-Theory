"""
Phase CDI — Current K3 tail coordinate-witness failure certificate.

CD made the live K3 wall a one-witness problem on the fixed tail-line class.
This phase applies that criterion to the present refined K3 object itself: it
still has none of the promoted coordinate witnesses, so the remaining wall is
exactly the first nonzero witness on the same fixed package.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_tail_coordinate_witness_failure_bridge import (
    build_current_k3_tail_coordinate_witness_failure_summary,
)


def test_phase_cdi_current_k3_has_no_promoted_coordinate_witness() -> None:
    theorem = build_current_k3_tail_coordinate_witness_failure_summary()[
        "current_k3_tail_coordinate_witness_failure_theorem"
    ]
    assert theorem[
        "the_present_refined_k3_object_exhibits_no_exact_coordinate_witness"
    ] is True


def test_phase_cdi_live_wall_is_first_nonzero_coordinate_witness() -> None:
    theorem = build_current_k3_tail_coordinate_witness_failure_summary()[
        "current_k3_tail_coordinate_witness_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_coordinate_witness_on_the_same_fixed_k3_package"
    ] is True
