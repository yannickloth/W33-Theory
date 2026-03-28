"""The remaining transport wall is a deformation of the rigid split avatar.

The transport bridge has now fixed enough exact data that the open wall is no
longer "find the external transport object" in any broad sense.

What is already fixed exactly:

- the head-compatible `U1` head line;
- the canonical tail-biased `U1` tail line;
- the ordered dimensions `81 -> 162 -> 81`;
- the fact that the present external glue slot is structurally zero.

So any exact external completion of the internal transport packet can only come
from a non-split deformation of this already-fixed rigid split avatar: keep the
head/tail lines and ordered dimensions, but replace zero glue by a nonzero
tail-to-head `81 x 81` operator.
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

from w33_transport_rigid_split_avatar_bridge import (
    build_transport_rigid_split_avatar_bridge_summary,
)
from w33_transport_single_glue_slot_bridge import (
    build_transport_single_glue_slot_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_avatar_deformation_wall_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_avatar_deformation_wall_bridge_summary() -> dict[str, Any]:
    avatar = build_transport_rigid_split_avatar_bridge_summary()
    slot = build_transport_single_glue_slot_bridge_summary()

    return {
        "status": "ok",
        "canonical_split_avatar": avatar["canonical_external_transport_avatar"],
        "remaining_completion_datum": {
            "slot_direction": slot["internal_transport_operator_slot"]["slot_direction"],
            "slot_shape": slot["internal_transport_operator_slot"]["slot_shape"],
            "required_internal_rank": slot["internal_transport_operator_slot"][
                "required_internal_rank"
            ],
            "required_internal_square_zero": slot["internal_transport_operator_slot"][
                "required_internal_square_zero"
            ],
            "current_external_rank": slot["external_current_slot_state"][
                "current_external_slot_rank"
            ],
            "current_external_state": slot["external_current_slot_state"][
                "current_external_slot_state"
            ],
        },
        "transport_avatar_deformation_wall_theorem": {
            "current_bridge_has_already_fixed_one_canonical_rigid_split_transport_avatar": (
                avatar["transport_rigid_split_avatar_theorem"][
                    "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
                ]
            ),
            "exact_transport_identity_would_require_adjoining_a_nonzero_tail_to_head_81_by_81_glue_operator_to_that_avatar": (
                slot["transport_single_glue_slot_theorem"][
                    "exact_transport_identity_would_require_a_tail_to_head_rank_81_square_zero_glue_operator"
                ]
            ),
            "any_exact_completion_must_preserve_the_fixed_head_line_tail_line_and_ordered_dimensions_of_the_avatar": (
                avatar["canonical_external_transport_avatar"]["ordered_filtration_dimensions"]
                == [81, 162, 81]
                and slot["internal_transport_operator_slot"]["slot_direction"]
                == "tail_to_head"
            ),
            "the_remaining_transport_wall_is_a_nonsplit_deformation_problem_not_a_search_for_an_unfixed_external_packet": (
                avatar["transport_rigid_split_avatar_theorem"][
                    "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
                ]
                and slot["transport_single_glue_slot_theorem"][
                    "the_only_missing_exact_transport_datum_is_one_tail_to_head_81_by_81_operator_slot"
                ]
            ),
        },
        "bridge_verdict": (
            "The current transport frontier is now deformation-theoretic. The "
            "bridge already fixes one canonical rigid split avatar of the "
            "internal transport packet. So exact completion can only come from "
            "a non-split deformation of that avatar: preserve the fixed head "
            "line, tail line, and ordered dimensions 81 -> 162 -> 81, and "
            "replace zero glue by a nonzero tail-to-head 81x81 square-zero "
            "operator."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_avatar_deformation_wall_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
