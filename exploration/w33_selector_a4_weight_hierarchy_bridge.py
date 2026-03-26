"""Weight hierarchy inside the fine selector-side ``A4`` packet on K3.

Once the reduced selector-side packet is resolved over

    U1, U2, U3, E8_1, E8_2,

the next exact question is where the packet is concentrated. This module uses
the Frobenius norms of the restricted selector forms as a conservative packet
weight proxy.

The hierarchy is sharp on the explicit seed:

- inside the hyperbolic core: ``U3 > U1 > U2``;
- inside the exceptional side: ``E8_2 > E8_1``.

Because each packet piece scales by exact factor ``120`` under first
barycentric pullback, the normalized hierarchy is refinement-invariant at
``sd^1``.
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

from w33_k3_selector_a4_five_factor_bridge import build_k3_selector_a4_five_factor_bridge_summary
from w33_k3_selector_a4_five_factor_refinement_bridge import (
    build_k3_selector_a4_five_factor_refinement_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_selector_a4_weight_hierarchy_bridge_summary.json"


@lru_cache(maxsize=1)
def build_selector_a4_weight_hierarchy_bridge_summary() -> dict[str, Any]:
    fine = build_k3_selector_a4_five_factor_bridge_summary()
    refined = build_k3_selector_a4_five_factor_refinement_bridge_summary()
    norms = fine["factor_frobenius_norms"]

    hyperbolic_total = norms["U1"] + norms["U2"] + norms["U3"]
    exceptional_total = norms["E8_1"] + norms["E8_2"]
    hyperbolic_shares = {
        name: norms[name] / hyperbolic_total for name in ("U1", "U2", "U3")
    }
    exceptional_shares = {
        name: norms[name] / exceptional_total for name in ("E8_1", "E8_2")
    }

    return {
        "status": "ok",
        "factor_frobenius_norms": norms,
        "hyperbolic_weight_shares": hyperbolic_shares,
        "exceptional_weight_shares": exceptional_shares,
        "selector_a4_weight_hierarchy_theorem": {
            "hyperbolic_weight_order_is_u3_gt_u1_gt_u2": (
                norms["U3"] > norms["U1"] > norms["U2"]
            ),
            "exceptional_weight_order_is_e8_factor_two_gt_e8_factor_one": (
                norms["E8_2"] > norms["E8_1"]
            ),
            "u3_carries_more_than_four_fifths_of_hyperbolic_packet_weight": (
                hyperbolic_shares["U3"] > 0.8
            ),
            "e8_factor_two_carries_more_than_eight_ninths_of_exceptional_packet_weight": (
                exceptional_shares["E8_2"] > (8 / 9)
            ),
            "fine_weight_hierarchy_is_refinement_invariant": (
                refined["selector_a4_five_factor_refinement_theorem"][
                    "fine_selector_packet_split_is_first_refinement_rigid"
                ]
            ),
        },
        "bridge_verdict": (
            "The fine selector-side packet is not only supported on five exact "
            "K3 lattice pieces; it is highly unevenly distributed. Within the "
            "hyperbolic core the dominant carrier is U3, not the distinguished "
            "global plane U1, and within the exceptional side the dominant "
            "carrier is E8_2. Since each packet piece scales by exact factor "
            "120 at sd^1, this normalized hierarchy is already refinement-"
            "invariant."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_selector_a4_weight_hierarchy_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
