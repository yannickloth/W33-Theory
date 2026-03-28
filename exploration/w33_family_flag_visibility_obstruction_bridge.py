"""Exact obstruction to promoting the full internal family flag externally.

Internally, the reduced Yukawa packet already carries an exact line-plane flag

    span(1,1,0) < {x = y},

with common square ``2E13``. Externally, the current K3 bridge already fixes a
canonical carrier plane ``U1``, a rigid line candidate inside it, and an exact
filtered split shadow ``81 -> 162 -> 81``.

What it does not yet fix is:

- a canonical line inside ``U1`` matching the internal common line;
- a non-split extension class matching the internal transport ``162`` sector.

So the present bridge determines a carrier plane, a line candidate, and a
filtered shadow, but not the full internal family flag as an external object.
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

from w33_transport_semisimplification_shadow_bridge import (
    build_transport_semisimplification_shadow_bridge_summary,
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
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary
from w33_u1_isotropic_line_obstruction_bridge import (
    build_u1_isotropic_line_obstruction_bridge_summary,
)
from w33_u1_selector_line_selection_bridge import (
    build_u1_selector_line_selection_bridge_summary,
)
from w33_yukawa_generation_flag_bridge import build_yukawa_generation_flag_summary


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_family_flag_visibility_obstruction_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_family_flag_visibility_obstruction_bridge_summary() -> dict[str, Any]:
    flag = build_yukawa_generation_flag_summary()
    carrier = build_u1_family_a4_carrier_bridge_summary()
    u1_obstruction = build_u1_isotropic_line_obstruction_bridge_summary()
    u1_selection = build_u1_selector_line_selection_bridge_summary()
    u1_sign_order = build_u1_filtered_shadow_line_order_bridge_summary()
    semisimple = build_transport_semisimplification_shadow_bridge_summary()
    filtered = build_transport_filtered_shadow_bridge_summary()
    nilpotent = build_transport_nilpotent_glue_obstruction_bridge_summary()

    return {
        "status": "ok",
        "internal_common_line_generator": flag["common_flag"]["line_generator"],
        "internal_common_plane_equation": flag["common_flag"]["plane_equation"],
        "external_canonical_carrier_plane": carrier["canonical_external_carrier"]["plane_name"],
        "external_canonical_line_candidate": u1_selection["dominant_isotropic_line_coefficients"],
        "external_sign_ordered_line_candidate": u1_sign_order[
            "dominant_isotropic_line_coefficients"
        ],
        "external_semisimplified_shadow": semisimple["external_split_shadow"],
        "external_filtered_split_shadow": filtered["external_canonical_split_filtration"][
            "ordered_filtration_dimensions"
        ],
        "external_nilpotent_glue_visibility": {
            "matches_internal_nilpotent_glue": False,
            "reason": "external_filtered_shadow_is_split",
        },
        "family_flag_visibility_obstruction_theorem": {
            "internal_family_flag_is_exact_line_in_plane_data": (
                flag["generation_flag_theorem"][
                    "both_generation_matrices_preserve_common_line"
                ]
                and flag["generation_flag_theorem"][
                    "both_generation_matrices_preserve_common_plane"
                ]
                and flag["generation_flag_theorem"][
                    "common_line_equals_image_of_common_square"
                ]
            ),
            "external_side_fixes_a_canonical_carrier_plane_u1": (
                carrier["u1_family_a4_carrier_theorem"][
                    "canonical_external_carrier_equals_u_factor_one"
                ]
            ),
            "carrier_metric_alone_is_line_blind_inside_u1": (
                u1_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"
                ]
            ),
            "full_external_packet_selects_a_canonical_line_candidate_inside_u1": (
                u1_selection["u1_selector_line_selection_theorem"][
                    "full_current_external_packet_selects_a_canonical_isotropic_line_candidate_inside_u1"
                ]
            ),
            "filtered_shadow_sign_order_fixes_the_same_canonical_u1_line_candidate": (
                u1_sign_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
            ),
            "external_side_still_matches_the_graded_shadow_of_the_transport_162_sector": (
                semisimple["transport_semisimplification_shadow_theorem"][
                    "transport_k3_match_is_semisimplified_shadow_not_extension_identity"
                ]
            ),
            "external_side_matches_a_canonical_filtered_split_shadow_of_the_transport_162_sector": (
                filtered["transport_filtered_shadow_theorem"][
                    "current_bridge_reaches_filtered_split_shadow_but_not_nonsplit_extension_identity"
                ]
            ),
            "external_side_does_not_yet_realize_the_internal_rank_81_nilpotent_glue": (
                nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
            "exact_external_identification_of_the_internal_common_line_is_not_yet_supported": (
                u1_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "exact_identification_of_the_internal_common_line_with_a_canonical_u1_line_is_not_yet_supported"
                ]
            ),
            "exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported": (
                filtered["transport_filtered_shadow_theorem"][
                    "current_bridge_reaches_filtered_split_shadow_but_not_nonsplit_extension_identity"
                ]
            ),
            "current_bridge_fixes_plane_line_candidate_and_filtered_shadow_but_not_full_extension_object": (
                carrier["u1_family_a4_carrier_theorem"][
                    "canonical_external_carrier_equals_u_factor_one"
                ]
                and u1_sign_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
                and filtered["transport_filtered_shadow_theorem"][
                    "current_bridge_reaches_filtered_split_shadow_but_not_nonsplit_extension_identity"
                ]
                and nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
        },
        "bridge_verdict": (
            "The current K3 bridge now goes one step further than a plane-only "
            "carrier theorem. It fixes a canonical carrier plane U1, the full "
            "external packet selects a canonical dominant isotropic-line "
            "candidate inside U1, that line candidate is canonically ordered by "
            "the positive/negative filtered-shadow basis, and the transport "
            "comparison now fixes a "
            "canonical ordered split filtered shadow 81 -> 162 -> 81 on the "
            "external side. What is still missing is an exact identification of "
            "that external line candidate with the internal line span(1,1,0), "
            "and the nontrivial rank-81 nilpotent glue operator carried by the "
            "internal transport 162-sector. So the present exact bridge reaches "
            "plane, line candidate, and filtered shadow, but not the full "
            "extension object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_family_flag_visibility_obstruction_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
