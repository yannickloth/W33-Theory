"""
Phase CDXV — current K3 mixed-plane operator-witness failure.

CDXIV fixed the exact witness shape. This phase applies it to the actual
current mixed-plane host and shows the failure is now completely explicit:
the host is already correct, but the existing tail slot still carries only the
split zero operator instead of the unique nonzero rank-81 square-zero one.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_operator_witness_failure_bridge import (
    build_current_k3_mixed_plane_operator_witness_failure_summary,
)


def test_phase_cdxv_current_host_fails_only_by_missing_nonzero_slot_operator() -> None:
    theorem = build_current_k3_mixed_plane_operator_witness_failure_summary()[
        "current_k3_mixed_plane_operator_witness_failure_theorem"
    ]
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_operator_witness_test_for_one_reason_only_the_nonzero_slot_operator_is_missing"
    ] is True


def test_phase_cdxv_live_wall_is_first_genuine_nonzero_mixed_plane_operator_witness() -> None:
    theorem = build_current_k3_mixed_plane_operator_witness_failure_summary()[
        "current_k3_mixed_plane_operator_witness_failure_theorem"
    ]
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_mixed_plane_slot_operator_witness_on_the_same_fixed_host"
    ] is True
