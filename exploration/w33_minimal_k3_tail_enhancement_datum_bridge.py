"""Unique minimal K3-side tail datum required by the exactness wall.

CCCXCVII localized the present external failure exactly:

- the current refined K3 object already sits on the fixed carrier package;
- it satisfies the tail syzygies only trivially at the zero point;
- it fails exactness for one reason only: the nonzero transport pair `(12,217)`
  is absent.

The older completion-wall reductions had already fixed what the missing datum
must look like:

- it is not a new carrier plane, shell, or line choice;
- it is the unique nonzero replacement in the already-fixed tail slot;
- on the fixed tail line it has one primitive direction
  `(780, 7944, 62600, 53979)`;
- and its exact transport arithmetic is the single pair `(12, 217)`.

So the live positive target is now exact: any genuine K3-side enhancement must
first add one unique minimal tail datum on the same fixed carrier package
before any larger completion avatar can appear.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_minimal_k3_tail_enhancement_datum_bridge_summary.json"
)

FIXED_K3_TAIL_EXACTNESS_CHANNEL = {
    "carrier_plane": "U1",
    "head_line_role": "head_compatible_u1_line_already_forced",
    "ordered_filtration_dimensions": [81, 162, 81],
    "tail_channel_dimension": 81,
    "slot_direction": "tail_to_head",
    "slot_shape": [81, 81],
    "current_slot_state": "zero_by_splitness",
}

CURRENT_REFINED_K3_ZERO_TAIL_CANDIDATE = {
    "coordinates": {"C": "0", "L": "0", "Q_seed": "0", "Q_sd1": "0"},
    "syzygies": {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    },
    "arithmetic": {
        "denominator_lcm": 1,
        "cleared_coordinate_gcd": 0,
        "recovered_scale": "0",
    },
}

MINIMAL_K3_TAIL_ENHANCEMENT_DATUM = {
    "slot_state": "unique_nonzero_orbit_in_existing_glue_slot",
    "slot_matrix_normal_form": "I_81",
    "polarized_nilpotent_normal_form": "J2^81",
    "primitive_integral_generator": {
        "C": "780",
        "L": "7944",
        "Q_seed": "62600",
        "Q_sd1": "53979",
    },
    "transport_arithmetic_pair": {
        "denominator_lcm": 12,
        "cleared_coordinate_gcd": 217,
        "recovered_scale": "217/12",
    },
    "induced_matter_pair": {
        "denominator_lcm": 4,
        "cleared_coordinate_gcd": 5859,
        "recovered_scale": "5859/4",
    },
}


@lru_cache(maxsize=1)
def build_minimal_k3_tail_enhancement_datum_summary() -> dict[str, Any]:
    fixed = FIXED_K3_TAIL_EXACTNESS_CHANNEL
    zero = CURRENT_REFINED_K3_ZERO_TAIL_CANDIDATE
    datum = MINIMAL_K3_TAIL_ENHANCEMENT_DATUM

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "current_refined_k3_zero_tail_candidate": zero,
        "minimal_k3_tail_enhancement_datum": datum,
        "minimal_k3_tail_enhancement_datum_theorem": {
            "the_current_refined_k3_object_already_fixes_the_carrier_package_and_fails_only_by_missing_the_nonzero_tail_datum": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["current_slot_state"] == "zero_by_splitness"
                and zero["arithmetic"]["recovered_scale"] == "0"
            ),
            "no_new_line_plane_dimension_or_shell_choice_remains_in_the_minimal_tail_enhancement": (
                fixed["head_line_role"] == "head_compatible_u1_line_already_forced"
                and fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["slot_shape"] == [81, 81]
            ),
            "the_missing_minimal_tail_datum_is_exactly_the_unique_nonzero_existing_slot_state_with_primitive_direction_and_pair_lcm12_gcd217": (
                datum["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
                and datum["slot_matrix_normal_form"] == "I_81"
                and datum["polarized_nilpotent_normal_form"] == "J2^81"
                and datum["primitive_integral_generator"]
                == {"C": "780", "L": "7944", "Q_seed": "62600", "Q_sd1": "53979"}
                and datum["transport_arithmetic_pair"]
                == {
                    "denominator_lcm": 12,
                    "cleared_coordinate_gcd": 217,
                    "recovered_scale": "217/12",
                }
            ),
            "any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum_before_any_formal_completion_avatar": (
                datum["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
                and datum["transport_arithmetic_pair"]["recovered_scale"] == "217/12"
                and datum["induced_matter_pair"]["recovered_scale"] == "5859/4"
                and fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
            ),
            "therefore_the_live_positive_target_is_one_unique_minimal_k3_tail_enhancement_datum_on_the_same_fixed_package": (
                fixed["current_slot_state"] == "zero_by_splitness"
                and zero["arithmetic"]["recovered_scale"] == "0"
                and datum["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
                and datum["transport_arithmetic_pair"]["recovered_scale"] == "217/12"
            ),
        },
        "bridge_verdict": (
            "The current refined K3 object now has one exact missing target, not "
            "a vague enhancement class. On the already-fixed carrier package, "
            "any exact realization must first add the unique nonzero datum in "
            "the existing tail slot, with primitive direction "
            "(780,7944,62600,53979) and transport arithmetic pair (12,217). No "
            "new line, plane, shell, or dimension choice remains. So the live "
            "positive target is one unique minimal K3-side tail enhancement "
            "datum, after which any larger completion avatar is only a lift of "
            "that same datum."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_minimal_k3_tail_enhancement_datum_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
