"""Canonical head/tail polarization of the current transport split shadow.

The bridge now carries two exact ingredients that were previously separate:

1. internally, the transport ``162``-sector is an ordered non-split packet
   ``81 -> 162 -> 81`` with a square-zero rank-81 glue operator whose image is
   the invariant head and whose quotient is the sign tail;
2. externally, the current K3 bridge fixes an ordered split filtered shadow
   ``81(+) -> 162 -> 81(-)`` together with a sign-ordered dominant/recessive
   null-line pair inside the canonical carrier plane ``U1``.

This module packages the strongest conservative consequence. Even though the
external side still does not realize the internal nilpotent glue, it already
fixes a canonical *polarized* split shadow:

- a head-biased line candidate inside ``U1``;
- a tail-biased line candidate inside ``U1``; and
- the ordered head/middle/tail dimension pattern ``81 -> 162 -> 81``.

So the current bridge reaches a canonical head/tail polarized shadow, but not
yet the non-split tail-to-head glue operator.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_transport_nilpotent_glue_obstruction_bridge import (
    build_transport_nilpotent_glue_obstruction_bridge_summary,
)
from w33_u1_filtered_shadow_line_order_bridge import (
    build_u1_filtered_shadow_line_order_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_polarized_line_shadow_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_polarized_line_shadow_bridge_summary() -> dict[str, object]:
    nilpotent = build_transport_nilpotent_glue_obstruction_bridge_summary()
    line_order = build_u1_filtered_shadow_line_order_bridge_summary()

    return {
        "status": "ok",
        "internal_transport_polarization": {
            "ordered_filtration_dimensions": [81, 162, 81],
            "head_type": "invariant",
            "tail_type": "sign",
            "nilpotent_glue_direction": "tail_to_head",
            "nilpotent_glue_rank": nilpotent["internal_transport_nilpotent_glue"]["rank"],
        },
        "external_polarized_split_shadow": {
            "ordered_filtration_dimensions": [81, 162, 81],
            "ordered_filtered_shadow_line_types": line_order[
                "ordered_filtered_shadow_line_types"
            ],
            "head_biased_line_coefficients": line_order[
                "dominant_isotropic_line_coefficients"
            ],
            "tail_biased_line_coefficients": line_order[
                "recessive_isotropic_line_coefficients"
            ],
            "positive_selector_weights": line_order["u1_positive_selector_weights"],
            "negative_selector_weights": line_order["u1_negative_selector_weights"],
            "positive_minus_negative_selector_gaps": line_order[
                "u1_positive_minus_negative_selector_gaps"
            ],
        },
        "transport_polarized_line_shadow_theorem": {
            "internal_transport_has_canonical_head_middle_tail_structure": (
                nilpotent["internal_transport_nilpotent_glue"]["rank"] == 81
                and nilpotent["external_split_filtered_shadow"][
                    "ordered_filtration_dimensions"
                ]
                == [81, 162, 81]
            ),
            "external_bridge_has_canonical_head_biased_and_tail_biased_u1_lines": (
                line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
            ),
            "dominant_u1_line_is_head_biased_and_recessive_u1_line_is_tail_biased": (
                line_order["u1_filtered_shadow_line_order_theorem"][
                    "dominant_u1_line_has_strictly_larger_positive_selector_weight"
                ]
                and line_order["u1_filtered_shadow_line_order_theorem"][
                    "dominant_u1_line_has_strictly_smaller_negative_selector_contamination"
                ]
                and line_order["u1_filtered_shadow_line_order_theorem"][
                    "dominant_u1_line_maximizes_positive_minus_negative_selector_gap"
                ]
            ),
            "current_bridge_reaches_a_canonical_head_tail_polarized_split_shadow": (
                line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
                and nilpotent["external_split_filtered_shadow"][
                    "ordered_filtration_dimensions"
                ]
                == [81, 162, 81]
            ),
            "current_bridge_does_not_yet_realize_the_internal_tail_to_head_nilpotent_glue": (
                nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
            "polarized_shadow_is_stronger_than_filtered_dimension_match_but_weaker_than_extension_identity": (
                line_order["u1_filtered_shadow_line_order_theorem"][
                    "current_bridge_fixes_a_rigid_positive_ordered_line_candidate_inside_u1"
                ]
                and nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "current_bridge_reaches_head_middle_tail_and_ordering_but_not_nilpotent_glue"
                ]
            ),
        },
        "bridge_verdict": (
            "The current bridge now reaches more than an ordered dimension "
            "pattern. Internally the transport 162-sector has a canonical "
            "head/middle/tail structure with a square-zero rank-81 glue "
            "operator pointing from tail to head. Externally the current K3 "
            "bridge already fixes a canonical head-biased line and a canonical "
            "tail-biased line inside U1, together with the ordered split shadow "
            "81 -> 162 -> 81. So the bridge now carries a canonical polarized "
            "split shadow, but still not the non-split nilpotent glue itself."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_polarized_line_shadow_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
