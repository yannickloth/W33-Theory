from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_mixed_plane_operator_witness_failure_bridge import (  # noqa: E402
    build_current_k3_mixed_plane_operator_witness_failure_summary,
)


def test_current_mixed_plane_operator_state_is_still_zero_by_splitness() -> None:
    summary = build_current_k3_mixed_plane_operator_witness_failure_summary()
    current = summary["current_mixed_plane_operator_state"]
    assert current["source"] == "canonical_mixed_k3_plane_qutrit_lift"
    assert current["ordered_line_types"] == ["positive", "negative"]
    assert current["mixed_signature"] == [1, 1]
    assert current["qutrit_lift_split"] == [81, 81]
    assert current["slot_direction"] == "tail_to_head"
    assert current["slot_shape"] == [81, 81]
    assert current["current_rank"] == 0
    assert current["current_state"] == "zero_by_splitness"


def test_current_mixed_plane_operator_failure_theorem_holds() -> None:
    theorem = build_current_k3_mixed_plane_operator_witness_failure_summary()[
        "current_k3_mixed_plane_operator_witness_failure_theorem"
    ]
    assert theorem[
        "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package"
    ] is True
    assert theorem[
        "the_current_mixed_plane_host_still_carries_the_split_zero_operator_in_the_existing_slot"
    ] is True
    assert theorem[
        "the_exact_mixed_plane_witness_requires_the_unique_nonzero_rank_81_square_zero_operator"
    ] is True
    assert theorem[
        "therefore_the_current_mixed_plane_host_fails_the_exact_operator_witness_test_for_one_reason_only_the_nonzero_slot_operator_is_missing"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_the_first_genuine_nonzero_mixed_plane_slot_operator_witness_on_the_same_fixed_host"
    ] is True
