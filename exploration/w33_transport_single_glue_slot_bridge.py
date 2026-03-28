"""The current transport wall is a single missing glue-operator slot.

After the semisimplified-shadow, filtered-shadow, polarized-shadow, and Jordan
shadow theorems, the remaining transport ambiguity is no longer diffuse.

Internally the exact transport packet is determined by:

- head dimension ``81``,
- middle dimension ``162``,
- tail dimension ``81``,
- a tail-to-head square-zero glue operator of rank ``81``.

Externally the current bridge already fixes:

- the semisimplified shadow ``81 ⊕ 81``,
- the ordered split filtration ``81 -> 162 -> 81``,
- the head/tail polarization, and
- the polarized Jordan shadow.

So the only missing datum for exact transport identity is one operator slot:
an off-diagonal map from tail to head of shape ``81 x 81``. Internally that
slot is occupied by a nonzero rank-81 operator; externally it is currently
forced to be zero by splitness.
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

from w33_transport_jordan_shadow_bridge import (
    build_transport_jordan_shadow_bridge_summary,
)
from w33_transport_nilpotent_glue_obstruction_bridge import (
    build_transport_nilpotent_glue_obstruction_bridge_summary,
)
from w33_transport_polarized_line_shadow_bridge import (
    build_transport_polarized_line_shadow_bridge_summary,
)
from w33_transport_semisimplification_shadow_bridge import (
    build_transport_semisimplification_shadow_bridge_summary,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_single_glue_slot_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_single_glue_slot_bridge_summary() -> dict[str, object]:
    semisimple = build_transport_semisimplification_shadow_bridge_summary()
    polarized = build_transport_polarized_line_shadow_bridge_summary()
    jordan = build_transport_jordan_shadow_bridge_summary()
    nilpotent = build_transport_nilpotent_glue_obstruction_bridge_summary()

    rank = int(nilpotent["internal_transport_nilpotent_glue"]["rank"])
    nullity = int(nilpotent["internal_transport_nilpotent_glue"]["nullity"])

    return {
        "status": "ok",
        "internal_transport_operator_slot": {
            "head_dimension": rank,
            "middle_dimension": rank + nullity,
            "tail_dimension": nullity,
            "slot_direction": "tail_to_head",
            "slot_shape": [rank, nullity],
            "required_internal_rank": rank,
            "required_internal_square_zero": True,
            "required_internal_jordan_partition": jordan["internal_transport_jordan_packet"][
                "exact_jordan_partition"
            ],
        },
        "external_current_slot_state": {
            "semisimplified_shadow": semisimple["external_split_shadow"],
            "ordered_filtration_dimensions": polarized["external_polarized_split_shadow"][
                "ordered_filtration_dimensions"
            ],
            "head_biased_line_coefficients": polarized["external_polarized_split_shadow"][
                "head_biased_line_coefficients"
            ],
            "tail_biased_line_coefficients": polarized["external_polarized_split_shadow"][
                "tail_biased_line_coefficients"
            ],
            "current_external_slot_rank": 0,
            "current_external_slot_state": "zero_by_splitness",
        },
        "transport_single_glue_slot_theorem": {
            "current_bridge_fixes_the_semisimplified_shadow_of_the_transport_packet": (
                semisimple["transport_semisimplification_shadow_theorem"][
                    "internal_and_external_objects_match_exactly_at_semisimplified_shadow_level"
                ]
            ),
            "current_bridge_fixes_the_ordered_filtered_shadow_of_the_transport_packet": (
                polarized["transport_polarized_line_shadow_theorem"][
                    "current_bridge_reaches_a_canonical_head_tail_polarized_split_shadow"
                ]
            ),
            "current_bridge_fixes_the_polarized_jordan_shadow_of_the_transport_packet": (
                jordan["transport_jordan_shadow_theorem"][
                    "current_bridge_reaches_the_polarized_jordan_shadow_but_not_the_internal_jordan_identity"
                ]
            ),
            "exact_transport_identity_would_require_a_tail_to_head_rank_81_square_zero_glue_operator": (
                rank == 81
                and nullity == 81
                and nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "internal_transport_162_has_nontrivial_rank_81_square_zero_glue_operator"
                ]
            ),
            "the_current_external_bridge_forces_that_single_glue_slot_to_be_zero": (
                nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "external_transport_shadow_is_split_and_has_zero_extension_class"
                ]
            ),
            "the_only_missing_exact_transport_datum_is_one_tail_to_head_81_by_81_operator_slot": (
                semisimple["transport_semisimplification_shadow_theorem"][
                    "internal_and_external_objects_match_exactly_at_semisimplified_shadow_level"
                ]
                and polarized["transport_polarized_line_shadow_theorem"][
                    "current_bridge_reaches_a_canonical_head_tail_polarized_split_shadow"
                ]
                and jordan["transport_jordan_shadow_theorem"][
                    "current_bridge_reaches_the_polarized_jordan_shadow_but_not_the_internal_jordan_identity"
                ]
                and nilpotent["transport_nilpotent_glue_obstruction_theorem"][
                    "external_transport_shadow_is_split_and_has_zero_extension_class"
                ]
            ),
        },
        "bridge_verdict": (
            "The remaining transport wall is now operator-sized. The current "
            "bridge already fixes the semisimplified shadow, the ordered "
            "filtration, the head/tail polarization, and the polarized Jordan "
            "shadow of the internal 162-packet. So the only missing datum for "
            "exact transport identity is one tail-to-head 81x81 glue-operator "
            "slot. Internally that slot is occupied by a nonzero rank-81 "
            "square-zero operator; externally it is currently forced to be "
            "zero by splitness."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_single_glue_slot_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
