"""Carrier-preserving transport-twisted lift as the localized K3 realization wall.

The current completion-wall reductions have already fixed the external carrier
package:

- the head-compatible image line;
- the canonical plane ``U1``;
- the ordered shell ``81 -> 162 -> 81``;
- the existing tail-to-head ``81x81`` slot.

Independently, the missing internal datum is no longer a bare slot value. It
already exists internally as:

- a genuine twisted 1-cocycle that is not a coboundary;
- an exact curved transport-twisted precomplex;

So the open external realization problem is now localized very tightly:
any genuine K3-side realization compatible with the existing exact bridge must
be a carrier-preserving transport-twisted lift of that already-fixed external
carrier package.
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

from w33_carrier_preserving_k3_enhancement_bridge import (
    build_carrier_preserving_k3_enhancement_bridge_summary,
)
from w33_completion_datum_avatar_lift_bridge import (
    build_completion_datum_avatar_lift_bridge_summary,
)
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_carrier_preserving_transport_twisted_k3_lift_bridge_summary.json"
)
TERNARY_COCYCLE_SUMMARY_PATH = ROOT / "data" / "w33_transport_ternary_cocycle_bridge_summary.json"
TWISTED_PRECOMPLEX_SUMMARY_PATH = ROOT / "data" / "w33_transport_twisted_precomplex_bridge_summary.json"


def _load_json_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def build_carrier_preserving_transport_twisted_k3_lift_bridge_summary() -> dict[str, Any]:
    carrier = build_carrier_preserving_k3_enhancement_bridge_summary()
    lift = build_completion_datum_avatar_lift_bridge_summary()
    cocycle = _load_json_summary(TERNARY_COCYCLE_SUMMARY_PATH)
    precomplex = _load_json_summary(TWISTED_PRECOMPLEX_SUMMARY_PATH)

    return {
        "status": "ok",
        "fixed_external_carrier_package": carrier["fixed_external_carrier_package"],
        "internal_transport_twisted_package": {
            "twisted_cocycle_not_coboundary": cocycle["extension_cocycle"][
                "cocycle_is_not_a_coboundary"
            ],
            "matter_extension_dimension": cocycle["matter_extension_operator"][
                "dimension"
            ],
            "matter_extension_rank": cocycle["matter_extension_operator"]["rank"],
            "precomplex_curvature_rank": precomplex["curved_extension_package"][
                "full_curvature_rank"
            ],
            "precomplex_off_diagonal_rank": precomplex["curved_extension_package"][
                "off_diagonal_curvature_rank"
            ],
        },
        "carrier_preserving_transport_twisted_k3_lift_theorem": {
            "the_external_carrier_package_is_already_fixed_before_any_genuine_k3_realization": (
                carrier["carrier_preserving_k3_enhancement_theorem"][
                    "therefore_any_minimal_genuine_k3_side_enhancement_must_be_carrier_preserving_not_carrier_replacing"
                ]
            ),
            "the_missing_internal_datum_is_already_a_nontrivial_twisted_cocycle": (
                cocycle["extension_cocycle"]["twisted_cocycle_identity_exact"]
                and cocycle["extension_cocycle"]["cocycle_is_not_a_coboundary"]
            ),
            "the_missing_internal_datum_already_assembles_into_an_exact_transport_twisted_precomplex": (
                precomplex["adapted_block_decomposition"]["d0_lower_left_block_vanishes"]
                and precomplex["adapted_block_decomposition"]["d1_lower_left_block_vanishes"]
                and precomplex["curved_extension_package"][
                    "curvature_factors_through_sign_quotient"
                ]
            ),
            "the_shared_nonzero_completion_wall_is_already_localized_as_datum_to_avatar_lift": (
                lift["completion_datum_avatar_lift_theorem"][
                    "the_difference_inside_the_shared_nonzero_slot_is_a_datum_to_avatar_lift_not_a_new_slot_or_line_choice"
                ]
            ),
            "therefore_any_exact_k3_side_realization_must_be_a_carrier_preserving_transport_twisted_lift": (
                carrier["carrier_preserving_k3_enhancement_theorem"][
                    "therefore_any_minimal_genuine_k3_side_enhancement_must_be_carrier_preserving_not_carrier_replacing"
                ]
                and cocycle["extension_cocycle"]["cocycle_is_not_a_coboundary"]
                and precomplex["curved_extension_package"][
                    "curvature_factors_through_sign_quotient"
                ]
                and lift["completion_datum_avatar_lift_theorem"][
                    "the_difference_inside_the_shared_nonzero_slot_is_a_datum_to_avatar_lift_not_a_new_slot_or_line_choice"
                ]
            ),
            "the_open_wall_is_existence_of_that_carrier_preserving_transport_twisted_k3_lift": (
                carrier["carrier_preserving_k3_enhancement_theorem"][
                    "the_live_missing_theorem_is_current_k3_realization_of_that_already_fixed_carrier_package"
                ]
                and lift["completion_datum_avatar_lift_theorem"][
                    "the_difference_inside_the_shared_nonzero_slot_is_a_datum_to_avatar_lift_not_a_new_slot_or_line_choice"
                ]
            ),
        },
        "bridge_verdict": (
            "The K3 realization wall is now localized more tightly than a generic "
            "enhancement problem. The external carrier package is already fixed, "
            "and the missing internal datum already exists as a nontrivial "
            "transport-twisted cocycle and precomplex package. "
            "So any exact K3-side realization compatible with the current bridge "
            "must be a carrier-preserving transport-twisted lift of that fixed "
            "external package. What remains open is existence of that lift on "
            "the K3 side, not the slot, line, shell, or internal operator shape."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_carrier_preserving_transport_twisted_k3_lift_bridge_summary(),
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
