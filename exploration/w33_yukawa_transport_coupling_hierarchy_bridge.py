"""Coupling hierarchy for the unresolved Yukawa/transport bridge.

The current frontier no longer supports a single flat answer to
"what does the unresolved family packet couple to?" The exact bridge data now
distinguish nested support levels:

- image-side central channel at line level;
- first family-sensitive ``A4`` packet at plane level;
- non-split transport completion at avatar level.

So the remaining closure is support-filtered rather than attached to one
undifferentiated external carrier.
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

from w33_e13_a4_support_stratification_bridge import (
    build_e13_a4_support_stratification_bridge_summary,
)
from w33_formal_external_completion_avatar_bridge import (
    build_formal_external_completion_avatar_bridge_summary,
)
from w33_global_local_carrier_split_bridge import (
    build_global_local_carrier_split_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_yukawa_transport_coupling_hierarchy_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_yukawa_transport_coupling_hierarchy_bridge_summary() -> dict[str, Any]:
    support = build_e13_a4_support_stratification_bridge_summary()
    completion = build_formal_external_completion_avatar_bridge_summary()
    local_split = build_global_local_carrier_split_bridge_summary()

    return {
        "status": "ok",
        "coupling_levels": {
            "line_level": support["support_levels"]["central_image_line"],
            "plane_level": support["support_levels"]["minimal_a4_carrier_plane"],
            "avatar_level": completion["formal_external_completion_avatar"][
                "ordered_filtration_dimensions"
            ],
            "broader_local_context": local_split["dominant_hyperbolic_packet_piece"],
        },
        "yukawa_transport_coupling_hierarchy_theorem": {
            "the_central_image_channel_couples_at_line_level": (
                support["e13_a4_support_stratification_theorem"][
                    "the_central_image_side_2e13_channel_localizes_to_the_head_line_in_any_exact_completion"
                ]
            ),
            "the_first_family_sensitive_a4_entry_couples_at_plane_level": (
                support["e13_a4_support_stratification_theorem"][
                    "the_first_family_sensitive_a4_bridge_packet_has_minimal_canonical_plane_carrier_u1"
                ]
            ),
            "non_split_transport_identity_requires_avatar_level_support": (
                completion["formal_external_completion_avatar_theorem"][
                    "the_forced_image_line_and_the_nonzero_glue_live_on_one_common_formal_external_object"
                ]
                and completion["formal_external_completion_avatar_theorem"][
                    "that_common_formal_object_has_ordered_shell_81_to_162_to_81"
                ]
            ),
            "the_broader_five_factor_packet_remains_local_context_not_the_minimal_exact_coupling_target": (
                local_split["global_local_carrier_split_theorem"][
                    "first_family_packet_has_canonical_global_support_but_non_u1_local_dominance"
                ]
            ),
            "the_live_unresolved_family_closure_is_support_filtered_as_line_inside_plane_inside_avatar": (
                support["e13_a4_support_stratification_theorem"][
                    "the_central_image_side_2e13_channel_localizes_to_the_head_line_in_any_exact_completion"
                ]
                and support["e13_a4_support_stratification_theorem"][
                    "the_first_family_sensitive_a4_bridge_packet_has_minimal_canonical_plane_carrier_u1"
                ]
                and completion["formal_external_completion_avatar_theorem"][
                    "the_forced_image_line_and_the_nonzero_glue_live_on_one_common_formal_external_object"
                ]
            ),
            "the_unresolved_family_packet_does_not_reduce_to_u3_even_though_u3_is_locally_dominant": (
                local_split["dominant_hyperbolic_packet_piece"] == "U3"
                and support["support_levels"]["minimal_a4_carrier_plane"] == "U1"
            ),
        },
        "bridge_verdict": (
            "The unresolved Yukawa/transport closure is now best read as a "
            "coupling hierarchy, not a single support guess. The central 2E13 "
            "image channel is line-level, the first family-sensitive A4 packet "
            "is plane-level on U1, and the non-split transport identity is "
            "avatar-level on the formal 81 -> 162 -> 81 completion. U3 remains "
            "the dominant local selector piece, but not the minimal exact "
            "carrier of the live family closure."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_transport_coupling_hierarchy_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
