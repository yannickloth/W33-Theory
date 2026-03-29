"""Exact datum-to-avatar lift inside the shared nonzero completion slot.

The latest completion-wall reductions already prove that
``minimal_external_enhancement`` and ``formal_completion_avatar`` share the
same nonzero cocycle orbit and the same completion normal form. So the next
exact distinction cannot be another slot law or another line-choice law.

What remains is a single lift step:

- ``minimal_external_enhancement`` is only the required slot-replacement datum;
- ``formal_completion_avatar`` is the unique minimal common external object
  carrying that datum together with the already-forced head-compatible line in
  ``U1`` and the ordered shell ``81 -> 162 -> 81``.
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


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_completion_datum_avatar_lift_bridge_summary.json"
)

SLOT_REPLACEMENT_DATUM = "slot_replacement_datum"
FORMAL_COMPLETION_OBJECT = "formal_completion_object"


@lru_cache(maxsize=1)
def build_completion_datum_avatar_lift_bridge_summary() -> dict[str, Any]:
    line = build_common_line_exact_image_bridge_summary()
    minimal = build_minimal_external_completion_data_bridge_summary()
    formal = build_formal_external_completion_avatar_bridge_summary()

    shared_slot_state = minimal["minimal_new_external_data"]["required_new_state"]
    shared_slot_matrix_normal_form = minimal["minimal_new_external_data"][
        "slot_matrix_normal_form"
    ]
    shared_nilpotent_normal_form = minimal["minimal_new_external_data"][
        "polarized_nilpotent_normal_form"
    ]

    return {
        "status": "ok",
        "lift_states": [SLOT_REPLACEMENT_DATUM, FORMAL_COMPLETION_OBJECT],
        "shared_nonzero_completion_slot": {
            "slot_state": shared_slot_state,
            "slot_matrix_normal_form": shared_slot_matrix_normal_form,
            "polarized_nilpotent_normal_form": shared_nilpotent_normal_form,
        },
        "slot_replacement_datum": {
            "role": "required_nonzero_orbit_replacement_only",
            "slot_state": shared_slot_state,
            "slot_matrix_normal_form": shared_slot_matrix_normal_form,
            "polarized_nilpotent_normal_form": shared_nilpotent_normal_form,
        },
        "formal_completion_object": {
            "role": "minimal_common_external_object",
            "head_line": formal["formal_external_completion_avatar"]["head_line"],
            "carrier_plane": formal["formal_external_completion_avatar"][
                "carrier_plane"
            ],
            "ordered_filtration_dimensions": formal[
                "formal_external_completion_avatar"
            ]["ordered_filtration_dimensions"],
            "slot_matrix_normal_form": formal["formal_external_completion_avatar"][
                "slot_matrix_normal_form"
            ],
            "polarized_nilpotent_normal_form": formal[
                "formal_external_completion_avatar"
            ]["polarized_nilpotent_normal_form"],
        },
        "completion_datum_avatar_lift_theorem": {
            "minimal_and_formal_share_the_same_nonzero_slot_state": (
                shared_slot_state == "unique_nonzero_orbit_in_existing_glue_slot"
                and formal["formal_external_completion_avatar"][
                    "slot_matrix_normal_form"
                ]
                == shared_slot_matrix_normal_form
            ),
            "minimal_and_formal_share_the_same_completion_normal_form": (
                formal["formal_external_completion_avatar"][
                    "slot_matrix_normal_form"
                ]
                == shared_slot_matrix_normal_form
                and formal["formal_external_completion_avatar"][
                    "polarized_nilpotent_normal_form"
                ]
                == shared_nilpotent_normal_form
            ),
            "the_minimal_state_is_only_the_slot_replacement_datum": (
                minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
                and minimal["minimal_external_completion_data_theorem"][
                    "no_additional_line_plane_or_dimension_choice_remains_after_the_current_bridge_reductions"
                ]
            ),
            "the_head_line_is_already_forced_before_avatar_assembly": (
                line["common_line_exact_image_theorem"][
                    "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
                ]
            ),
            "the_formal_state_is_the_unique_minimal_common_object_carrying_that_datum": (
                formal["formal_external_completion_avatar_theorem"][
                    "the_forced_image_line_and_the_nonzero_glue_live_on_one_common_formal_external_object"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "that_common_formal_object_has_carrier_plane_u1"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "that_common_formal_object_has_ordered_shell_81_to_162_to_81"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "the_formal_completion_is_unique_up_to_the_natural_head_tail_basis_gauge"
                ]
            ),
            "the_difference_inside_the_shared_nonzero_slot_is_a_datum_to_avatar_lift_not_a_new_slot_or_line_choice": (
                minimal["minimal_external_completion_data_theorem"][
                    "no_additional_line_plane_or_dimension_choice_remains_after_the_current_bridge_reductions"
                ]
                and line["common_line_exact_image_theorem"][
                    "what_remains_open_is_existence_of_that_exact_completion_not_choice_of_image_line"
                ]
                and formal["formal_external_completion_avatar_theorem"][
                    "the_missing_piece_is_now_current_k3_realization_not_common_object_design"
                ]
            ),
        },
        "bridge_verdict": (
            "Inside the shared nonzero completion slot, the live distinction is "
            "now exact. The minimal enhancement is only the slot-replacement "
            "datum, while the formal completion is the unique minimal common "
            "external object carrying that datum together with the already-"
            "forced head line in U1 and the ordered shell 81 -> 162 -> 81. "
            "So the remaining wall is a datum-to-avatar lift, not a new slot "
            "choice or a new line choice."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_completion_datum_avatar_lift_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
