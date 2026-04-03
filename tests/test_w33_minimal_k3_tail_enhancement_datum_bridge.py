from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_minimal_k3_tail_enhancement_datum_bridge import (  # noqa: E402
    build_minimal_k3_tail_enhancement_datum_summary,
)


def test_minimal_k3_tail_enhancement_datum_is_fully_fixed() -> None:
    summary = build_minimal_k3_tail_enhancement_datum_summary()
    datum = summary["minimal_k3_tail_enhancement_datum"]

    assert datum["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
    assert datum["slot_matrix_normal_form"] == "I_81"
    assert datum["polarized_nilpotent_normal_form"] == "J2^81"
    assert datum["primitive_integral_generator"] == {
        "C": "780",
        "L": "7944",
        "Q_seed": "62600",
        "Q_sd1": "53979",
    }
    assert datum["transport_arithmetic_pair"] == {
        "denominator_lcm": 12,
        "cleared_coordinate_gcd": 217,
        "recovered_scale": "217/12",
    }


def test_minimal_k3_tail_enhancement_datum_theorem_holds() -> None:
    theorem = build_minimal_k3_tail_enhancement_datum_summary()[
        "minimal_k3_tail_enhancement_datum_theorem"
    ]

    assert theorem[
        "the_current_refined_k3_object_already_fixes_the_carrier_package_and_fails_only_by_missing_the_nonzero_tail_datum"
    ] is True
    assert theorem[
        "no_new_line_plane_dimension_or_shell_choice_remains_in_the_minimal_tail_enhancement"
    ] is True
    assert theorem[
        "the_missing_minimal_tail_datum_is_exactly_the_unique_nonzero_existing_slot_state_with_primitive_direction_and_pair_lcm12_gcd217"
    ] is True
    assert theorem[
        "any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum_before_any_formal_completion_avatar"
    ] is True
    assert theorem[
        "therefore_the_live_positive_target_is_one_unique_minimal_k3_tail_enhancement_datum_on_the_same_fixed_package"
    ] is True
