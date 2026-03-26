"""Exact separation between global carrier and local dominant packet pieces.

The current bridge already proves two different kinds of exact statements:

- globally, the first family-sensitive ``A4`` packet has a canonical minimal
  external carrier ``U1`` with exact reduced coefficient ``351/(4 pi^2)``;
- locally, the fine selector-side packet is unevenly distributed across
  ``U1 (+) U2 (+) U3 (+) E8_1 (+) E8_2`` and is dominated by ``U3`` on the
  hyperbolic side and by ``E8_2`` on the exceptional side.

This module packages the conservative conclusion forced by those facts:
the exact global carrier and the exact local dominant carrier are different
objects. ``U1`` is the canonical minimal carrier, but it is not the dominant
local packet piece.
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

from w33_selector_a4_weight_hierarchy_bridge import (
    build_selector_a4_weight_hierarchy_bridge_summary,
)
from w33_u1_family_a4_carrier_bridge import build_u1_family_a4_carrier_bridge_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_global_local_carrier_split_bridge_summary.json"


@lru_cache(maxsize=1)
def build_global_local_carrier_split_bridge_summary() -> dict[str, Any]:
    carrier = build_u1_family_a4_carrier_bridge_summary()
    hierarchy = build_selector_a4_weight_hierarchy_bridge_summary()

    norms = hierarchy["factor_frobenius_norms"]
    hyperbolic_dominant = max(("U1", "U2", "U3"), key=norms.__getitem__)
    exceptional_dominant = max(("E8_1", "E8_2"), key=norms.__getitem__)

    return {
        "status": "ok",
        "canonical_global_carrier": carrier["canonical_external_carrier"]["plane_name"],
        "dominant_hyperbolic_packet_piece": hyperbolic_dominant,
        "dominant_exceptional_packet_piece": exceptional_dominant,
        "hyperbolic_dominance_ratio_u3_over_u1": norms["U3"] / norms["U1"],
        "exceptional_dominance_ratio_e8_factor_two_over_e8_factor_one": (
            norms["E8_2"] / norms["E8_1"]
        ),
        "global_local_carrier_split_theorem": {
            "canonical_global_carrier_is_u1": (
                carrier["u1_family_a4_carrier_theorem"][
                    "canonical_external_carrier_equals_u_factor_one"
                ]
                and carrier["canonical_external_carrier"]["plane_name"] == "U1"
            ),
            "dominant_hyperbolic_packet_piece_is_u3": (
                hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "hyperbolic_weight_order_is_u3_gt_u1_gt_u2"
                ]
                and hyperbolic_dominant == "U3"
            ),
            "dominant_exceptional_packet_piece_is_e8_factor_two": (
                hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "exceptional_weight_order_is_e8_factor_two_gt_e8_factor_one"
                ]
                and exceptional_dominant == "E8_2"
            ),
            "canonical_global_carrier_differs_from_dominant_hyperbolic_packet_piece": (
                carrier["canonical_external_carrier"]["plane_name"] != hyperbolic_dominant
            ),
            "first_family_packet_has_canonical_global_support_but_non_u1_local_dominance": (
                carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
                and hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "hyperbolic_weight_order_is_u3_gt_u1_gt_u2"
                ]
            ),
            "global_local_carrier_split_is_refinement_invariant": (
                hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "fine_weight_hierarchy_is_refinement_invariant"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge distinguishes two exact notions that should not "
            "be conflated. Globally, the first family-sensitive packet has "
            "canonical minimal carrier U1. Locally, the selector-side packet is "
            "dominated by U3 on the hyperbolic side and by E8_2 on the "
            "exceptional side. So the canonical global carrier and the locally "
            "dominant packet piece are already exact, but they are not the same "
            "object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_global_local_carrier_split_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
