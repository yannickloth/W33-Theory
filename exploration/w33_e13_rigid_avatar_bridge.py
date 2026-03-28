"""Current external realization of the central ``2E13`` channel via the rigid avatar.

The bridge stack is now strong enough to package the central family channel and
the transport side together.

Internally:
- the common square is exactly ``2E13``;
- its image is exactly the common line ``span(1,1,0)``.

Externally:
- the unique bridge-compatible line image is the head-compatible `U1` line;
- that line is the head of the canonical rigid split transport avatar;
- exact completion would therefore require a non-split deformation of that
  avatar, not a different external carrier object.
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

from w33_e13_visibility_obstruction_bridge import (
    build_e13_visibility_obstruction_bridge_summary,
)
from w33_transport_avatar_deformation_wall_bridge import (
    build_transport_avatar_deformation_wall_bridge_summary,
)
from w33_transport_full_rank_glue_normal_form_bridge import (
    build_transport_full_rank_glue_normal_form_bridge_summary,
)
from w33_transport_internal_operator_normal_form_match_bridge import (
    build_transport_internal_operator_normal_form_match_bridge_summary,
)
from w33_transport_rigid_split_avatar_bridge import (
    build_transport_rigid_split_avatar_bridge_summary,
)
from w33_u1_head_compatible_line_bridge import (
    build_u1_head_compatible_line_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_e13_rigid_avatar_bridge_summary.json"


@lru_cache(maxsize=1)
def build_e13_rigid_avatar_bridge_summary() -> dict[str, Any]:
    e13 = build_e13_visibility_obstruction_bridge_summary()
    head_line = build_u1_head_compatible_line_bridge_summary()
    avatar = build_transport_rigid_split_avatar_bridge_summary()
    deformation = build_transport_avatar_deformation_wall_bridge_summary()
    normal_form = build_transport_full_rank_glue_normal_form_bridge_summary()
    operator_match = build_transport_internal_operator_normal_form_match_bridge_summary()

    return {
        "status": "ok",
        "internal_central_channel": {
            "common_square": e13["internal_common_square"],
            "common_line_generator": e13["internal_common_line_generator"],
        },
        "current_external_avatar_realization": {
            "head_line": avatar["canonical_external_transport_avatar"]["head_line"],
            "tail_line": avatar["canonical_external_transport_avatar"]["tail_line"],
            "ordered_filtration_dimensions": avatar["canonical_external_transport_avatar"][
                "ordered_filtration_dimensions"
            ],
            "external_glue_state": avatar["canonical_external_transport_avatar"][
                "external_glue_state"
            ],
        },
        "e13_rigid_avatar_theorem": {
            "internal_central_2e13_channel_is_exact": (
                e13["e13_visibility_obstruction_theorem"][
                    "internal_common_square_is_exact_central_2e13_channel"
                ]
            ),
            "the_unique_bridge_compatible_external_image_of_the_internal_common_line_is_the_head_line_of_the_rigid_avatar": (
                head_line["u1_head_compatible_line_theorem"][
                    "the_current_external_line_ambiguity_collapses_to_one_head_compatible_candidate"
                ]
                and head_line["external_u1_line_roles"][
                    "head_compatible_line_candidate"
                ]
                == avatar["canonical_external_transport_avatar"]["head_line"]
            ),
            "the_current_external_realization_of_the_central_channel_factors_through_the_canonical_rigid_split_avatar": (
                avatar["transport_rigid_split_avatar_theorem"][
                    "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
                ]
                and head_line["external_u1_line_roles"][
                    "head_compatible_line_candidate"
                ]
                == avatar["canonical_external_transport_avatar"]["head_line"]
            ),
            "exact_external_realization_of_the_central_2e13_channel_would_require_a_nonsplit_deformation_of_that_avatar": (
                deformation["transport_avatar_deformation_wall_theorem"][
                    "the_remaining_transport_wall_is_a_nonsplit_deformation_problem_not_a_search_for_an_unfixed_external_packet"
                ]
            ),
            "any_exact_completion_of_that_avatar_has_the_unique_full_rank_glue_normal_form_two_power_81": (
                normal_form["transport_full_rank_glue_normal_form_theorem"][
                    "up_to_polarized_isomorphism_any_exact_completion_has_canonical_jordan_normal_form_two_power_81"
                ]
            ),
            "any_exact_completion_of_that_avatar_matches_the_internal_transport_operator_normal_form_up_to_basis_gauge": (
                operator_match[
                    "transport_internal_operator_normal_form_match_theorem"
                ][
                    "any_exact_external_completion_of_the_rigid_avatar_has_the_same_linear_algebraic_normal_form_up_to_head_tail_basis_gauge"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge now packages the central 2E13 family channel "
            "through the rigid split transport avatar. The unique bridge-"
            "compatible external image of the internal common line is the "
            "head line of that avatar, and exact completion would require a "
            "non-split deformation of the same avatar in the unique full-rank "
            "glue normal form, matching the internal transport operator model, "
            "rather than a new external carrier object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_e13_rigid_avatar_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
