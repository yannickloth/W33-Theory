"""Support stratification for the live ``2E13`` / ``A4`` bridge.

The transport and family reductions now distinguish three exact support levels:

1. the central image-side family channel localizes to one line;
2. the first family-sensitive ``A4`` bridge packet has minimal canonical
   carrier plane ``U1``;
3. exact transport completion uses the full rigid split avatar shell
   ``81 -> 162 -> 81``.

So the remaining Yukawa/transport bridge is not ambiguous among line, plane,
and avatar support. Those roles are already stratified exactly.
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
from w33_global_local_carrier_split_bridge import (
    build_global_local_carrier_split_bridge_summary,
)
from w33_transport_rigid_split_avatar_bridge import (
    build_transport_rigid_split_avatar_bridge_summary,
)
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_e13_a4_support_stratification_bridge_summary.json"


@lru_cache(maxsize=1)
def build_e13_a4_support_stratification_bridge_summary() -> dict[str, Any]:
    image = build_common_line_exact_image_bridge_summary()
    carrier = build_u1_family_a4_carrier_bridge_summary()
    avatar = build_transport_rigid_split_avatar_bridge_summary()
    packet = build_global_local_carrier_split_bridge_summary()

    return {
        "status": "ok",
        "support_levels": {
            "central_image_line": image["forced_external_image_line"]["line_coefficients"],
            "minimal_a4_carrier_plane": carrier["canonical_external_carrier"][
                "plane_name"
            ],
            "rigid_transport_avatar_dimensions": avatar[
                "canonical_external_transport_avatar"
            ]["ordered_filtration_dimensions"],
            "broader_local_packet_dominant_piece": packet[
                "dominant_hyperbolic_packet_piece"
            ],
        },
        "e13_a4_support_stratification_theorem": {
            "the_central_image_side_2e13_channel_localizes_to_the_head_line_in_any_exact_completion": (
                image["common_line_exact_image_theorem"][
                    "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
                ]
            ),
            "the_first_family_sensitive_a4_bridge_packet_has_minimal_canonical_plane_carrier_u1": (
                carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
            ),
            "exact_transport_completion_uses_the_full_rigid_avatar_shell_81_to_162_to_81": (
                avatar["transport_rigid_split_avatar_theorem"][
                    "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
                ]
            ),
            "the_broader_five_factor_packet_is_local_selector_context_not_the_minimal_exact_family_carrier": (
                packet["global_local_carrier_split_theorem"][
                    "canonical_global_carrier_is_u1"
                ]
                and packet["global_local_carrier_split_theorem"][
                    "canonical_global_carrier_differs_from_dominant_hyperbolic_packet_piece"
                ]
            ),
            "the_live_2e13_a4_bridge_is_exactly_stratified_as_head_line_inside_u1_inside_avatar": (
                image["common_line_exact_image_theorem"][
                    "the_head_compatible_u1_line_is_the_exact_bridge_image_of_the_internal_common_line_in_any_exact_completion"
                ]
                and carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
                and avatar["transport_rigid_split_avatar_theorem"][
                    "current_bridge_fixes_one_canonical_rigid_split_avatar_of_the_internal_transport_packet"
                ]
            ),
        },
        "bridge_verdict": (
            "The live 2E13 / A4 bridge is now support-stratified. The central "
            "image-side family channel localizes to the head-compatible line in "
            "any exact completion, the first family-sensitive A4 bridge packet "
            "has minimal canonical plane carrier U1, and exact transport "
            "completion uses the full rigid avatar shell 81 -> 162 -> 81. The "
            "broader packet geometry remains real, but it is not the minimal "
            "exact carrier."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_e13_a4_support_stratification_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
