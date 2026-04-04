"""
Phase CDXIX — current K3 mixed-plane cocycle failure.

CDXVIII reduced the positive datum to one nonzero sign-trivial cocycle value.
This phase applies that smallest cohomological criterion to the current host
and shows the remaining failure is now exactly absence of that nonzero
sign-trivial cocycle witness on the same fixed mixed-plane host.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_cocycle_failure_bridge import (
    build_current_k3_mixed_plane_cocycle_failure_summary,
)


def test_phase_cdxix_current_host_fails_only_by_missing_nonzero_sign_trivial_cocycle_value() -> None:
    theorem = build_current_k3_mixed_plane_cocycle_failure_summary()[
        "current_k3_mixed_plane_cocycle_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_cocycle_witness_test_for_one_reason_only_the_nonzero_sign_trivial_cocycle_value_is_missing"
    ] is True


def test_phase_cdxix_live_wall_is_first_nonzero_sign_trivial_cocycle_witness() -> None:
    theorem = build_current_k3_mixed_plane_cocycle_failure_summary()[
        "current_k3_mixed_plane_cocycle_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_sign_trivial_cocycle_witness_on_the_same_fixed_host"
    ] is True
