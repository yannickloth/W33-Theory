"""Exact enhancement hierarchy for the external transport wall.

The remaining transport wall is no longer vague. Three exact strata are now
distinguished:

1. the current refined K3 bridge object, which still realizes only the zero
   ternary orbit;
2. the minimal exact enhancement datum, which is just replacing that zero slot
   by the unique nonzero orbit in the already-fixed 81x81 tail-to-head slot;
3. the resulting formal completion avatar carrying the forced head line and the
   unique nonzero completion normal form.

This module packages that hierarchy as one exact discrete theorem.
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

from w33_formal_external_completion_avatar_bridge import (
    build_formal_external_completion_avatar_bridge_summary,
)
from w33_minimal_external_completion_data_bridge import (
    build_minimal_external_completion_data_bridge_summary,
)
from w33_refined_k3_zero_orbit_bridge import (
    build_refined_k3_zero_orbit_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_external_enhancement_hierarchy_bridge_summary.json"
)

CURRENT_K3_ZERO_ORBIT = "current_k3_zero_orbit"
MINIMAL_EXTERNAL_ENHANCEMENT = "minimal_external_enhancement"
FORMAL_COMPLETION_AVATAR = "formal_completion_avatar"


@lru_cache(maxsize=1)
def build_external_enhancement_hierarchy_bridge_summary() -> dict[str, Any]:
    current = build_refined_k3_zero_orbit_bridge_summary()
    minimal = build_minimal_external_completion_data_bridge_summary()
    formal = build_formal_external_completion_avatar_bridge_summary()

    return {
        "status": "ok",
        "enhancement_states": {
            CURRENT_K3_ZERO_ORBIT: {
                "ordered_filtration_dimensions": current[
                    "current_refined_k3_transport_shadow"
                ]["ordered_filtration_dimensions"],
                "slot_state": current["current_refined_k3_transport_shadow"][
                    "current_external_slot_state"
                ],
                "extension_class_zero": current["current_refined_k3_transport_shadow"][
                    "extension_class_zero"
                ],
            },
            MINIMAL_EXTERNAL_ENHANCEMENT: {
                "required_new_state": minimal["minimal_new_external_data"][
                    "required_new_state"
                ],
                "slot_matrix_normal_form": minimal["minimal_new_external_data"][
                    "slot_matrix_normal_form"
                ],
                "polarized_nilpotent_normal_form": minimal[
                    "minimal_new_external_data"
                ]["polarized_nilpotent_normal_form"],
            },
            FORMAL_COMPLETION_AVATAR: {
                "carrier_plane": formal["formal_external_completion_avatar"][
                    "carrier_plane"
                ],
                "ordered_filtration_dimensions": formal[
                    "formal_external_completion_avatar"
                ]["ordered_filtration_dimensions"],
                "slot_matrix_normal_form": formal["formal_external_completion_avatar"][
                    "slot_matrix_normal_form"
                ],
                "realization_status": formal["formal_external_completion_avatar"][
                    "realization_status"
                ],
            },
        },
        "external_enhancement_hierarchy_theorem": {
            "the_current_refined_k3_side_is_exactly_the_zero_orbit_state": (
                current["refined_k3_zero_orbit_theorem"][
                    "current_refined_k3_shadow_is_split_with_zero_extension_class"
                ]
                and current["current_refined_k3_transport_shadow"][
                    "current_external_slot_state"
                ]
                == "zero_by_splitness"
            ),
            "the_minimal_exact_enhancement_is_one_nonzero_slot_replacement_not_a_new_shell": (
                minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
                and minimal["minimal_external_completion_data_theorem"][
                    "no_additional_line_plane_or_dimension_choice_remains_after_the_current_bridge_reductions"
                ]
            ),
            "the_formal_completion_avatar_is_the_resulting_minimal_common_object": (
                formal["formal_external_completion_avatar_theorem"][
                    "the_forced_image_line_and_the_nonzero_glue_live_on_one_common_formal_external_object"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "that_common_formal_object_has_ordered_shell_81_to_162_to_81"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "that_common_formal_object_has_unique_nonzero_completion_normal_form_j2_power_81"
                ]
            ),
            "the_live_external_wall_is_exactly_current_object_vs_minimal_enhancement_vs_formal_completion": (
                current["refined_k3_zero_orbit_theorem"][
                    "the_unique_nonzero_ternary_orbit_is_not_realized_on_the_current_refined_k3_side"
                ]
                and minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "the_missing_piece_is_now_current_k3_realization_not_common_object_design"
                ]
            ),
        },
        "bridge_verdict": (
            "The external transport wall is now a three-state hierarchy, not a "
            "foggy continuum. The current refined K3 bridge is the zero-orbit "
            "state, the minimal exact enhancement is one nonzero slot "
            "replacement in the already-fixed shell, and the resulting target "
            "object is the formal completion avatar."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_external_enhancement_hierarchy_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
