from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_completion_datum_avatar_lift_bridge import (  # noqa: E402
    FORMAL_COMPLETION_OBJECT,
    SLOT_REPLACEMENT_DATUM,
    build_completion_datum_avatar_lift_bridge_summary,
)


def test_completion_datum_avatar_lift_states_are_exact() -> None:
    summary = build_completion_datum_avatar_lift_bridge_summary()
    assert summary["lift_states"] == [
        SLOT_REPLACEMENT_DATUM,
        FORMAL_COMPLETION_OBJECT,
    ]


def test_completion_datum_avatar_lift_theorem_flags_hold() -> None:
    summary = build_completion_datum_avatar_lift_bridge_summary()
    theorem = summary["completion_datum_avatar_lift_theorem"]
    assert theorem["minimal_and_formal_share_the_same_nonzero_slot_state"] is True
    assert theorem["minimal_and_formal_share_the_same_completion_normal_form"] is True
    assert theorem["the_minimal_state_is_only_the_slot_replacement_datum"] is True
    assert theorem["the_head_line_is_already_forced_before_avatar_assembly"] is True
    assert theorem[
        "the_formal_state_is_the_unique_minimal_common_object_carrying_that_datum"
    ] is True
    assert theorem[
        "the_difference_inside_the_shared_nonzero_slot_is_a_datum_to_avatar_lift_not_a_new_slot_or_line_choice"
    ] is True


def test_completion_object_carries_exact_plane_and_shell() -> None:
    summary = build_completion_datum_avatar_lift_bridge_summary()
    completion = summary["formal_completion_object"]
    assert completion["carrier_plane"] == "U1"
    assert completion["ordered_filtration_dimensions"] == [81, 162, 81]
    assert completion["slot_matrix_normal_form"] == "I_81"
    assert completion["polarized_nilpotent_normal_form"] == "J2^81"
