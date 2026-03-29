from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_carrier_preserving_k3_enhancement_bridge import (  # noqa: E402
    build_carrier_preserving_k3_enhancement_bridge_summary,
)


def test_carrier_preserving_k3_enhancement_bridge_summary() -> None:
    summary = build_carrier_preserving_k3_enhancement_bridge_summary()
    theorem = summary["carrier_preserving_k3_enhancement_theorem"]
    fixed = summary["fixed_external_carrier_package"]
    target = summary["minimal_genuine_k3_side_enhancement"]

    assert fixed["carrier_plane"] == "U1"
    assert fixed["ordered_filtration_dimensions"] == [81, 162, 81]
    assert fixed["slot_direction"] == "tail_to_head"
    assert fixed["slot_shape"] == [81, 81]
    assert fixed["current_slot_state"] == "zero_by_splitness"

    assert target["required_role"] == "carrier_preserving_nonzero_slot_activation"
    assert target["target_carrier_plane"] == "U1"
    assert target["target_ordered_filtration_dimensions"] == [81, 162, 81]
    assert target["target_slot_direction"] == "tail_to_head"
    assert target["target_slot_shape"] == [81, 81]
    assert target["required_new_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
    assert target["target_completion_normal_form"] == "J2^81"

    assert theorem[
        "the_head_line_is_already_fixed_before_any_genuine_new_realization"
    ] is True
    assert theorem[
        "the_canonical_plane_u1_is_already_fixed_before_any_genuine_new_realization"
    ] is True
    assert theorem[
        "the_ordered_shell_and_existing_tail_to_head_slot_are_already_fixed"
    ] is True
    assert theorem[
        "the_current_refined_k3_side_still_realizes_only_the_zero_slot_state"
    ] is True
    assert theorem[
        "the_only_remaining_change_needed_for_nonzero_realization_is_replacing_the_existing_zero_slot_by_the_unique_nonzero_orbit"
    ] is True
    assert theorem[
        "therefore_any_minimal_genuine_k3_side_enhancement_must_be_carrier_preserving_not_carrier_replacing"
    ] is True
    assert theorem[
        "the_live_missing_theorem_is_current_k3_realization_of_that_already_fixed_carrier_package"
    ] is True
