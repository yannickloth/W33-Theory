"""Carrier-preserving law for any genuine K3-side nonzero enhancement.

The current bridge has already fixed essentially all carrier data on the
external side:

- the exact-completion image line is the head-compatible line in ``U1``;
- the minimal canonical family carrier plane is ``U1``;
- the ordered transport shell is ``81 -> 162 -> 81``;
- the only missing operator datum is the existing tail-to-head ``81x81`` slot;
- and the exact nonzero target is the unique ternary orbit in that slot.

So the remaining external realization problem is no longer "find a new carrier
geometry". Any genuine K3-side enhancement that realizes the unique nonzero
orbit must preserve the already-fixed carrier package and alter only the
current zero slot.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_common_line_exact_image_bridge import (
    build_common_line_exact_image_bridge_summary,
)
from w33_formal_external_completion_avatar_bridge import (
    build_formal_external_completion_avatar_bridge_summary,
)
from w33_minimal_external_completion_data_bridge import (
    build_minimal_external_completion_data_bridge_summary,
)
from w33_refined_k3_zero_orbit_bridge import (
    build_refined_k3_zero_orbit_bridge_summary,
)
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_carrier_preserving_k3_enhancement_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_carrier_preserving_k3_enhancement_bridge_summary() -> dict[str, Any]:
    current = build_refined_k3_zero_orbit_bridge_summary()
    image = build_common_line_exact_image_bridge_summary()
    carrier = build_u1_family_a4_carrier_bridge_summary()
    minimal = build_minimal_external_completion_data_bridge_summary()
    formal = build_formal_external_completion_avatar_bridge_summary()

    head_line = image["forced_external_image_line"]["line_coefficients"]
    plane_name = carrier["canonical_external_carrier"]["plane_name"]
    shell = minimal["locked_external_transport_shell"]["ordered_filtration_dimensions"]
    tail_line = minimal["locked_external_transport_shell"]["tail_line"]
    slot_direction = minimal["locked_external_transport_shell"]["slot_direction"]
    slot_shape = minimal["locked_external_transport_shell"]["slot_shape"]

    return {
        "status": "ok",
        "fixed_external_carrier_package": {
            "head_line": head_line,
            "carrier_plane": plane_name,
            "ordered_filtration_dimensions": shell,
            "tail_line": tail_line,
            "slot_direction": slot_direction,
            "slot_shape": slot_shape,
            "current_slot_state": current["current_refined_k3_transport_shadow"][
                "current_external_slot_state"
            ],
        },
        "minimal_genuine_k3_side_enhancement": {
            "required_role": "carrier_preserving_nonzero_slot_activation",
            "target_head_line": head_line,
            "target_carrier_plane": plane_name,
            "target_ordered_filtration_dimensions": shell,
            "target_tail_line": tail_line,
            "target_slot_direction": slot_direction,
            "target_slot_shape": slot_shape,
            "required_new_state": minimal["minimal_new_external_data"][
                "required_new_state"
            ],
            "target_completion_normal_form": formal[
                "formal_external_completion_avatar"
            ]["polarized_nilpotent_normal_form"],
            "realization_wall": formal["formal_external_completion_avatar"][
                "realization_status"
            ],
        },
        "carrier_preserving_k3_enhancement_theorem": {
            "the_head_line_is_already_fixed_before_any_genuine_new_realization": (
                image["common_line_exact_image_theorem"][
                    "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
                ]
            ),
            "the_canonical_plane_u1_is_already_fixed_before_any_genuine_new_realization": (
                carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
                and formal["formal_external_completion_avatar"][
                    "carrier_plane"
                ]
                == "U1"
            ),
            "the_ordered_shell_and_existing_tail_to_head_slot_are_already_fixed": (
                shell == [81, 162, 81]
                and slot_direction == "tail_to_head"
                and slot_shape == [81, 81]
            ),
            "the_current_refined_k3_side_still_realizes_only_the_zero_slot_state": (
                current["refined_k3_zero_orbit_theorem"][
                    "the_unique_nonzero_ternary_orbit_is_not_realized_on_the_current_refined_k3_side"
                ]
            ),
            "the_only_remaining_change_needed_for_nonzero_realization_is_replacing_the_existing_zero_slot_by_the_unique_nonzero_orbit": (
                minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
            ),
            "therefore_any_minimal_genuine_k3_side_enhancement_must_be_carrier_preserving_not_carrier_replacing": (
                image["common_line_exact_image_theorem"][
                    "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
                ]
                and carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
                and shell == [81, 162, 81]
                and slot_direction == "tail_to_head"
                and slot_shape == [81, 81]
                and minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
            ),
            "the_live_missing_theorem_is_current_k3_realization_of_that_already_fixed_carrier_package": (
                formal["formal_external_completion_avatar_theorem"][
                    "the_missing_piece_is_now_current_k3_realization_not_common_object_design"
                ]
                and current["refined_k3_zero_orbit_theorem"][
                    "any_realization_of_the_unique_nonzero_orbit_requires_new_external_data_beyond_the_current_refined_k3_bridge"
                ]
            ),
        },
        "bridge_verdict": (
            "The genuine K3-side enhancement problem is now carrier-preserving. "
            "The head-compatible line, the canonical plane U1, the ordered "
            "shell 81 -> 162 -> 81, and the tail-to-head 81x81 slot are "
            "already fixed. So any exact nonzero realization must preserve "
            "that carrier package and change only the current zero slot to the "
            "unique nonzero orbit. The open wall is realizing that fixed "
            "package on the K3 side, not discovering a new carrier geometry."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_carrier_preserving_k3_enhancement_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
