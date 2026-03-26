"""Visibility wall for the internal central ``2E13`` channel.

On the finite Yukawa side, the exact one-versus-two normal form carries common
square ``2E13``. That square is not a decorative matrix identity: its image is
exactly the common family line ``span(1,1,0)``.

The current K3 bridge does not yet determine a canonical external
representative of that line or of the associated non-split extension class. It
fixes only:

- the canonical carrier plane ``U1`` for the first family-sensitive ``A4``
  packet;
- the graded shadow ``81 ⊕ 81`` of the transport ``162`` sector.

So the conservative exact theorem is: the current bridge sees the carrier plane
and graded shadow of the central channel, but not the central ``2E13`` channel
itself as a canonical external object.
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
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary
from w33_yukawa_family_normal_form_bridge import build_yukawa_family_normal_form_summary
from w33_yukawa_generation_flag_bridge import build_yukawa_generation_flag_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_e13_visibility_obstruction_bridge_summary.json"


@lru_cache(maxsize=1)
def build_e13_visibility_obstruction_bridge_summary() -> dict[str, Any]:
    family = build_yukawa_family_normal_form_summary()
    flag = build_yukawa_generation_flag_summary()
    carrier = build_u1_family_a4_carrier_bridge_summary()
    obstruction = build_family_flag_visibility_obstruction_bridge_summary()

    return {
        "status": "ok",
        "internal_common_square": family["generation_normal_form"]["common_square"],
        "internal_common_line_generator": flag["common_flag"]["line_generator"],
        "external_canonical_carrier_plane": carrier["canonical_external_carrier"]["plane_name"],
        "external_graded_shadow": obstruction["external_semisimplified_shadow"],
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
            "current_external_bridge_does_not_pick_a_canonical_line_for_the_e13_image": (
                obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_common_line_is_not_yet_supported"
                ]
            ),
            "current_external_bridge_matches_only_the_graded_shadow_of_the_transport_channel": (
                obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported"
                ]
            ),
            "current_bridge_captures_only_carrier_plane_and_graded_shadow_of_the_central_channel": (
                carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
                and obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_common_line_is_not_yet_supported"
                ]
                and obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported"
                ]
            ),
            "exact_external_realization_of_the_central_2e13_channel_is_not_yet_supported": (
                family["finite_family_theorem"]["common_square_is_exact_central_e13_channel"]
                and flag["generation_flag_theorem"]["common_line_equals_image_of_common_square"]
                and obstruction["family_flag_visibility_obstruction_theorem"][
                    "current_bridge_fixes_plane_and_graded_shadow_but_not_full_internal_flag_object"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge does not erase the finite central channel; it "
            "sharpens its status. Internally, the common square is exactly "
            "2E13 and its image is exactly the common family line. Externally, "
            "the current K3 bridge fixes the carrier plane U1 and the graded "
            "shadow 81 ⊕ 81, but it still does not pick a canonical external "
            "line for the image or a non-split external extension class. So the "
            "central 2E13 channel is still exact internally, while externally "
            "it is presently visible only through its carrier plane and graded "
            "shadow."
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
