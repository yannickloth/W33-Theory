"""Structural zero theorem for the current external transport glue slot.

The transport frontier has already been reduced to one explicit operator slot:

    tail -> head  (81 x 81)

on the transport 162-packet. Internally that slot is occupied by a nonzero
rank-81 square-zero glue operator. The sharper question is whether the current
external K3 bridge data could ever support a nonzero canonical operator in the
same slot.

The answer is no, and the reason is structural rather than computational:

1. the current external 162-packet is exactly the split qutrit lift
   ``81(+) ⊕ 81(-)`` of the canonical mixed K3 plane;
2. the current external ordered transport shadow is explicitly split with zero
   extension class;
3. therefore the unique tail-to-head glue slot is canonically zero on the
   present external object.

So any nonzero external glue operator would require genuinely new external data
beyond the current bridge objects.
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

from w33_curved_h2_cup_plane_bridge import build_curved_h2_cup_plane_bridge_summary
from w33_transport_filtered_shadow_bridge import (
    build_transport_filtered_shadow_bridge_summary,
)
from w33_transport_mixed_plane_obstruction_bridge import (
    build_transport_mixed_plane_obstruction_summary,
)
from w33_transport_single_glue_slot_bridge import (
    build_transport_single_glue_slot_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_external_glue_zero_forcing_bridge_summary.json"


@lru_cache(maxsize=1)
def build_external_glue_zero_forcing_bridge_summary() -> dict[str, Any]:
    plane = build_curved_h2_cup_plane_bridge_summary()["k3_canonical_mixed_plane"]
    filtered = build_transport_filtered_shadow_bridge_summary()
    obstruction = build_transport_mixed_plane_obstruction_summary()
    slot = build_transport_single_glue_slot_bridge_summary()

    return {
        "status": "ok",
        "current_external_transport_object": {
            "source": "canonical_mixed_k3_plane_qutrit_lift",
            "selector_triangle": plane["selector_triangle"],
            "qutrit_lift_split": plane["qutrit_lift_split"],
            "total_qutrit_lift_dimension": plane["total_qutrit_lift_dimension"],
            "split_qutrit_package": plane["split_qutrit_package"],
            "mixed_signature": plane["mixed_signature"],
            "ordered_line_types": filtered["external_canonical_split_filtration"][
                "ordered_line_types"
            ],
            "ordered_filtration_dimensions": filtered["external_canonical_split_filtration"][
                "ordered_filtration_dimensions"
            ],
            "extension_class_zero": filtered["external_canonical_split_filtration"][
                "is_split"
            ],
        },
        "external_glue_slot": {
            "slot_direction": slot["internal_transport_operator_slot"]["slot_direction"],
            "slot_shape": slot["internal_transport_operator_slot"]["slot_shape"],
            "current_external_rank": slot["external_current_slot_state"][
                "current_external_slot_rank"
            ],
            "current_external_state": slot["external_current_slot_state"][
                "current_external_slot_state"
            ],
        },
        "external_glue_zero_forcing_theorem": {
            "current_external_162_sector_is_exactly_the_split_qutrit_lift_of_the_canonical_mixed_k3_plane": (
                plane["total_qutrit_lift_dimension"] == 162
                and plane["qutrit_lift_split"] == [81, 81]
                and plane["split_qutrit_package"] is True
            ),
            "current_external_transport_shadow_has_zero_extension_class": (
                filtered["external_canonical_split_filtration"]["is_split"] is True
            ),
            "split_vs_nonsplit_obstruction_is_already_exact_at_the_current_bridge_level": (
                obstruction["comparison_theorem"][
                    "exact_split_vs_nonsplit_obstruction_is_present"
                ]
            ),
            "the_unique_external_tail_to_head_glue_slot_is_structurally_zero_on_the_present_bridge_object": (
                slot["external_current_slot_state"]["current_external_slot_rank"] == 0
                and slot["external_current_slot_state"]["current_external_slot_state"]
                == "zero_by_splitness"
                and filtered["external_canonical_split_filtration"]["is_split"] is True
            ),
            "any_nonzero_external_glue_operator_would_require_new_external_data_beyond_the_current_bridge_objects": (
                plane["split_qutrit_package"] is True
                and filtered["external_canonical_split_filtration"]["is_split"] is True
                and slot["external_current_slot_state"]["current_external_slot_state"]
                == "zero_by_splitness"
            ),
        },
        "bridge_verdict": (
            "The missing external glue is not merely absent in the current "
            "calculations. It is structurally excluded by the present bridge "
            "objects. The current external transport 162-sector is exactly the "
            "split qutrit lift of the canonical mixed K3 plane, so its "
            "extension class is zero and the unique tail-to-head 81x81 glue "
            "slot is canonically zero. Any nonzero external glue operator "
            "would require genuinely new external data beyond the current "
            "bridge."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_external_glue_zero_forcing_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
