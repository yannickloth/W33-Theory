"""Formal minimal external completion carrying both line and nonzero glue.

The current K3 bridge does not yet realize the non-split transport extension.
But once the shell, image line, and nonzero glue orbit are all fixed, there is
one minimal formal completion object up to the natural head/tail gauge.

That formal object is the smallest common external carrier of:

- the forced image line of ``span(1,1,0)``;
- the canonical plane ``U1`` containing that line;
- and the nonzero tail-to-head glue needed for the transport completion.
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
from w33_minimal_external_completion_data_bridge import (
    build_minimal_external_completion_data_bridge_summary,
)
from w33_transport_internal_operator_normal_form_match_bridge import (
    build_transport_internal_operator_normal_form_match_bridge_summary,
)
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_formal_external_completion_avatar_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_formal_external_completion_avatar_bridge_summary() -> dict[str, Any]:
    image = build_common_line_exact_image_bridge_summary()
    minimal = build_minimal_external_completion_data_bridge_summary()
    operator = build_transport_internal_operator_normal_form_match_bridge_summary()
    carrier = build_u1_family_a4_carrier_bridge_summary()

    return {
        "status": "ok",
        "formal_external_completion_avatar": {
            "head_line": image["forced_external_image_line"]["line_coefficients"],
            "carrier_plane": image["forced_external_image_line"]["carrier_plane"],
            "ordered_filtration_dimensions": minimal[
                "locked_external_transport_shell"
            ]["ordered_filtration_dimensions"],
            "tail_line": minimal["locked_external_transport_shell"]["tail_line"],
            "slot_direction": minimal["locked_external_transport_shell"][
                "slot_direction"
            ],
            "slot_matrix_normal_form": minimal["minimal_new_external_data"][
                "slot_matrix_normal_form"
            ],
            "polarized_nilpotent_normal_form": minimal["minimal_new_external_data"][
                "polarized_nilpotent_normal_form"
            ],
            "realization_status": "formal_minimal_completion_not_current_k3_realization",
        },
        "formal_external_completion_avatar_theorem": {
            "the_forced_image_line_and_the_nonzero_glue_live_on_one_common_formal_external_object": (
                image["common_line_exact_image_theorem"][
                    "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
                ]
                and minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
            ),
            "that_common_formal_object_has_carrier_plane_u1": (
                image["forced_external_image_line"]["carrier_plane"] == "U1"
                and carrier["canonical_external_carrier"]["plane_name"] == "U1"
            ),
            "that_common_formal_object_has_ordered_shell_81_to_162_to_81": (
                minimal["locked_external_transport_shell"][
                    "ordered_filtration_dimensions"
                ]
                == [81, 162, 81]
            ),
            "that_common_formal_object_has_unique_nonzero_completion_normal_form_j2_power_81": (
                minimal["minimal_new_external_data"]["polarized_nilpotent_normal_form"]
                == "J2^81"
                and operator[
                    "transport_internal_operator_normal_form_match_theorem"
                ][
                    "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
                ]
            ),
            "the_formal_completion_is_unique_up_to_the_natural_head_tail_basis_gauge": (
                minimal["minimal_external_completion_data_theorem"][
                    "there_is_only_one_nonzero_orbit_available_for_exact_completion"
                ]
            ),
            "the_missing_piece_is_now_current_k3_realization_not_common_object_design": (
                image["common_line_exact_image_theorem"][
                    "what_remains_open_is_existence_of_that_exact_completion_not_choice_of_image_line"
                ]
                and minimal["minimal_external_completion_data_theorem"][
                    "the_minimal_new_external_data_is_exactly_replacing_zero_by_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
            ),
        },
        "bridge_verdict": (
            "Once the current exact reductions are taken seriously, the line "
            "and glue no longer fight over support. There is one minimal formal "
            "external completion object up to head/tail gauge: the forced head "
            "line inside U1, the ordered shell 81 -> 162 -> 81, and the unique "
            "nonzero glue normal form J2^81. The remaining wall is realizing "
            "that object from actual K3-side data, not designing it."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_formal_external_completion_avatar_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
