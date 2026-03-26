"""Exact obstruction to promoting the full internal family flag externally.

Internally, the reduced Yukawa packet already carries an exact line-plane flag

    span(1,1,0) < {x = y},

with common square ``2E13``. Externally, the current K3 bridge already fixes a
canonical carrier plane ``U1`` and an exact graded shadow ``81 ⊕ 81``.

What it does not yet fix is:

- a canonical line inside ``U1`` matching the internal common line;
- a non-split extension class matching the internal transport ``162`` sector.

So the present bridge determines a carrier plane and a graded shadow, but not
the full internal family flag as an external object.
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
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary
from w33_u1_isotropic_line_obstruction_bridge import (
    build_u1_isotropic_line_obstruction_bridge_summary,
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
    semisimple = build_transport_semisimplification_shadow_bridge_summary()

    return {
        "status": "ok",
        "internal_common_line_generator": flag["common_flag"]["line_generator"],
        "internal_common_plane_equation": flag["common_flag"]["plane_equation"],
        "external_canonical_carrier_plane": carrier["canonical_external_carrier"]["plane_name"],
        "external_semisimplified_shadow": semisimple["external_split_shadow"],
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
            "external_side_is_line_blind_inside_u1": (
                u1_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"
                ]
            ),
            "external_side_matches_only_the_graded_shadow_of_the_transport_162_sector": (
                semisimple["transport_semisimplification_shadow_theorem"][
                    "transport_k3_match_is_semisimplified_shadow_not_extension_identity"
                ]
            ),
            "exact_external_identification_of_the_internal_common_line_is_not_yet_supported": (
                u1_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "exact_identification_of_the_internal_common_line_with_a_canonical_u1_line_is_not_yet_supported"
                ]
            ),
            "exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported": (
                semisimple["transport_semisimplification_shadow_theorem"][
                    "transport_k3_match_is_semisimplified_shadow_not_extension_identity"
                ]
            ),
            "current_bridge_fixes_plane_and_graded_shadow_but_not_full_internal_flag_object": (
                carrier["u1_family_a4_carrier_theorem"][
                    "canonical_external_carrier_equals_u_factor_one"
                ]
                and u1_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"
                ]
                and semisimple["transport_semisimplification_shadow_theorem"][
                    "transport_k3_match_is_semisimplified_shadow_not_extension_identity"
                ]
            ),
        },
        "bridge_verdict": (
            "The current K3 bridge already fixes a canonical carrier plane U1 "
            "and the graded transport shadow 81 ⊕ 81. What it does not yet fix "
            "is the full internal family flag as an external object: there is "
            "still no canonical external line inside U1 matching span(1,1,0), "
            "and there is still no external non-split extension matching the "
            "internal transport 162-sector. So the present exact bridge reaches "
            "the carrier plane and graded shadow, but not the full line-plus-"
            "extension family datum."
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
