"""Visibility wall for the internal central ``2E13`` channel.

On the finite Yukawa side, the exact one-versus-two normal form carries common
square ``2E13``. That square is not a decorative matrix identity: its image is
exactly the common family line ``span(1,1,0)``.

The current K3 bridge does not yet determine a canonical external
representative of that line or of the associated non-split extension class. It
fixes:

- the canonical carrier plane ``U1`` for the first family-sensitive ``A4``
  packet;
- a canonical dominant line candidate inside ``U1``; and
- the filtered split shadow ``81 -> 162 -> 81`` of the transport ``162``
  sector.

So the conservative exact theorem is: the current bridge sees the carrier plane
and filtered shadow of the central channel, but not the central ``2E13``
channel itself as a canonical external object.
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

from w33_family_flag_visibility_obstruction_bridge import (
    build_family_flag_visibility_obstruction_bridge_summary,
)
from w33_transport_filtered_shadow_bridge import (
    build_transport_filtered_shadow_bridge_summary,
)
from w33_transport_nilpotent_glue_obstruction_bridge import (
    build_transport_nilpotent_glue_obstruction_bridge_summary,
)
from w33_u1_filtered_shadow_line_order_bridge import (
    build_u1_filtered_shadow_line_order_bridge_summary,
)
from w33_u1_selector_line_selection_bridge import (
    build_u1_selector_line_selection_bridge_summary,
)
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary
from w33_yukawa_family_normal_form_bridge import build_yukawa_family_normal_form_summary
from w33_yukawa_generation_flag_bridge import build_yukawa_generation_flag_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_e13_visibility_obstruction_bridge_summary.json"


@lru_cache(maxsize=1)
def build_e13_visibility_obstruction_bridge_summary() -> dict[str, Any]:
    family = build_yukawa_family_normal_form_summary()
    flag = build_yukawa_generation_flag_summary()
    carrier = build_u1_family_a4_carrier_bridge_summary()
    line_selection = build_u1_selector_line_selection_bridge_summary()
    line_order = build_u1_filtered_shadow_line_order_bridge_summary()
    obstruction = build_family_flag_visibility_obstruction_bridge_summary()
    filtered = build_transport_filtered_shadow_bridge_summary()
    nilpotent = build_transport_nilpotent_glue_obstruction_bridge_summary()

    return {
        "status": "ok",
        "internal_common_square": family["generation_normal_form"]["common_square"],
        "internal_common_line_generator": flag["common_flag"]["line_generator"],
        "external_canonical_carrier_plane": carrier["canonical_external_carrier"]["plane_name"],
        "external_canonical_line_candidate": line_selection["dominant_isotropic_line_coefficients"],
        "external_sign_ordered_line_candidate": line_order["dominant_isotropic_line_coefficients"],
        "external_graded_shadow": obstruction["external_semisimplified_shadow"],
        "external_filtered_shadow": filtered["external_canonical_split_filtration"][
            "ordered_filtration_dimensions"
        ],
        "external_nilpotent_glue_visibility": {
            "matches_internal_central_channel_glue": False,
            "reason": "external_filtered_shadow_is_split",
        },
        "e13_visibility_obstruction_theorem": {
            "internal_common_square_is_exact_central_2e13_channel": (
                family["finite_family_theorem"]["common_square_is_exact_central_e13_channel"]
            ),
            "image_of_the_common_square_is_the_internal_common_line": (
                flag["generation_flag_theorem"]["common_line_equals_image_of_common_square"]
            ),
            "current_external_bridge_fixes_the_canonical_u1_carrier_plane": (
                carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
            ),
            "current_external_bridge_picks_a_canonical_line_candidate_for_the_e13_image": (
                line_selection["u1_selector_line_selection_theorem"][
                    "full_current_external_packet_selects_a_canonical_isotropic_line_candidate_inside_u1"
                ]
            ),
            "current_external_bridge_sign_orders_that_line_candidate_by_the_filtered_shadow_basis": (
                line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
            ),
            "exact_external_identification_of_the_e13_image_with_the_internal_common_line_is_not_yet_supported": (
                obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_common_line_is_not_yet_supported"
                ]
            ),
            "current_external_bridge_matches_a_canonical_filtered_split_shadow_of_the_transport_channel": (
                filtered["transport_filtered_shadow_theorem"][
                    "current_bridge_reaches_filtered_split_shadow_but_not_nonsplit_extension_identity"
                ]
            ),
            "current_external_bridge_does_not_yet_realize_the_rank_81_nilpotent_glue_of_the_transport_channel": (
                nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
            "current_bridge_captures_carrier_plane_line_candidate_and_filtered_shadow_of_the_central_channel": (
                carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
                and line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
                and filtered["transport_filtered_shadow_theorem"][
                    "current_bridge_reaches_filtered_split_shadow_but_not_nonsplit_extension_identity"
                ]
            ),
            "exact_external_realization_of_the_central_2e13_channel_is_not_yet_supported": (
                family["finite_family_theorem"]["common_square_is_exact_central_e13_channel"]
                and flag["generation_flag_theorem"]["common_line_equals_image_of_common_square"]
                and obstruction["family_flag_visibility_obstruction_theorem"][
                    "current_bridge_fixes_plane_line_candidate_and_filtered_shadow_but_not_full_extension_object"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge does not erase the finite central channel; it "
            "sharpens its status. Internally, the common square is exactly "
            "2E13 and its image is exactly the common family line. Externally, "
            "the current K3 bridge now fixes the carrier plane U1, a canonical "
            "dominant isotropic-line candidate inside that plane, sign-orders "
            "that candidate by the positive/negative filtered-shadow basis, and the "
            "canonical filtered split shadow 81 -> 162 -> 81. What it still "
            "does not fix is an exact "
            "identification of that external line candidate with the internal "
            "line, or the nontrivial rank-81 nilpotent glue carried by the "
            "internal transport extension. So the central 2E13 channel is "
            "still exact internally, while externally it is presently visible "
            "through its carrier plane, line candidate, and filtered shadow, "
            "but not yet as a full extension object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_e13_visibility_obstruction_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
