"""Exact K3 tail realization is equivalent to a nonzero extension witness.

CDIX reduced the remaining K3 wall to one splitness-breaking problem on the
fixed carrier-preserving package:

- the present refined K3 shadow is split with zero extension class;
- the exact target is the unique nonzero orbit in that same existing slot.

Separately, the older transport cocycle reduction had already shown that over
`F3` there is only one nonzero gauge orbit for the ternary tail-to-head glue.

Therefore the external wall sharpens one more step. On the fixed K3 package,
exact tail realization is equivalent to realizing any nonzero extension-class
witness in the existing tail slot. There is no further choice among distinct
nonzero slot types.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_nonzero_extension_criterion_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_tail_nonzero_extension_criterion_summary() -> dict[str, Any]:
    from w33_k3_tail_splitness_breaking_criterion_bridge import (
        build_k3_tail_splitness_breaking_criterion_summary,
    )
    from w33_transport_unique_nonzero_cocycle_orbit_bridge import (
        build_transport_unique_nonzero_cocycle_orbit_bridge_summary,
    )

    splitness = build_k3_tail_splitness_breaking_criterion_summary()
    orbit = build_transport_unique_nonzero_cocycle_orbit_bridge_summary()

    fixed = splitness["fixed_k3_tail_exactness_channel"]
    transition = splitness["slot_transition"]

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "slot_transition": transition,
        "nonzero_extension_witness": {
            "field": orbit["ternary_fiber_shift_orbit"]["field"],
            "base_shift": orbit["ternary_fiber_shift_orbit"]["base_shift"],
            "other_nonzero_scalar_multiple": orbit["ternary_fiber_shift_orbit"][
                "other_nonzero_scalar_multiple"
            ],
            "nonzero_orbit_size": orbit["ternary_fiber_shift_orbit"][
                "nonzero_scalar_orbit_size"
            ],
        },
        "k3_tail_nonzero_extension_criterion_theorem": {
            "the_current_k3_state_still_has_zero_extension_class_in_the_existing_tail_slot": (
                splitness["k3_tail_splitness_breaking_criterion_theorem"][
                    "the_current_refined_k3_shadow_is_split_with_zero_extension_class_and_zero_slot"
                ]
            ),
            "the_exact_target_is_the_unique_nonzero_orbit_in_that_same_existing_tail_slot": (
                splitness["k3_tail_splitness_breaking_criterion_theorem"][
                    "the_exact_target_slot_is_the_unique_nonzero_orbit_in_the_existing_slot"
                ]
            ),
            "up_to_the_natural_gauge_there_is_only_one_nonzero_extension_orbit_available": (
                orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
            "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot": (
                splitness["k3_tail_splitness_breaking_criterion_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_breaking_splitness_in_the_existing_tail_slot"
                ]
                and orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
                and transition["from"] == "zero_by_splitness"
                and transition["to"] == "unique_nonzero_orbit_in_existing_glue_slot"
            ),
            "the_live_external_wall_is_now_one_nonzero_extension_witness_problem_on_the_same_fixed_k3_package": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["slot_shape"] == [81, 81]
                and transition["from"] == "zero_by_splitness"
                and transition["to"] == "unique_nonzero_orbit_in_existing_glue_slot"
                and orbit["ternary_fiber_shift_orbit"]["nonzero_scalar_orbit_size"] == 2
                and orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
        },
        "bridge_verdict": (
            "The K3 tail wall is now a clean positive existence test. On the "
            "fixed carrier-preserving package, the current state still has "
            "zero extension class, while the exact target is the unique "
            "nonzero orbit in that same existing slot. Because over F3 there "
            "is only one nonzero gauge orbit available, exact K3 tail "
            "realization is equivalent to realizing any nonzero extension-"
            "class witness in the existing tail slot."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_nonzero_extension_criterion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
