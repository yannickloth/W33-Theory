"""Exact K3 tail realization is a splitness-breaking condition.

CDVIII made the canonical chart equation genuinely external:

- on the fixed carrier-preserving package, solving `ΔC=14105` is equivalent
  to activating the unique nonzero tail slot.

The current refined K3 side already identifies the complementary negative
statement:

- the present transport shadow is split;
- its extension class is zero;
- the tail slot is `zero_by_splitness`.

So the next exact reduction is immediate. On the fixed K3 package, exact tail
realization is equivalent to breaking splitness in the existing tail slot:
replace `zero_by_splitness` by the unique nonzero orbit. No new carrier plane,
head line, shell, or dimension choice remains.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_splitness_breaking_criterion_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_tail_splitness_breaking_criterion_summary() -> dict[str, Any]:
    from w33_current_k3_tail_exactness_failure_bridge import (
        build_current_k3_tail_exactness_failure_summary,
    )
    from w33_k3_tail_canonical_chart_slot_equivalence_bridge import (
        build_k3_tail_canonical_chart_slot_equivalence_summary,
    )

    current = build_current_k3_tail_exactness_failure_summary()
    slot = build_k3_tail_canonical_chart_slot_equivalence_summary()

    fixed = slot["fixed_k3_tail_exactness_channel"]
    current_shadow = current["current_refined_k3_shadow"]

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "current_refined_k3_shadow": current_shadow,
        "slot_transition": {
            "from": slot["current_slot_state"],
            "to": slot["target_slot_state"],
            "canonical_chart_requirement": slot["canonical_chart_target"][
                "required_value"
            ],
        },
        "k3_tail_splitness_breaking_criterion_theorem": {
            "the_current_refined_k3_shadow_is_split_with_zero_extension_class_and_zero_slot": (
                current_shadow["extension_class_zero"] is True
                and current_shadow["current_external_slot_state"] == "zero_by_splitness"
                and fixed["current_slot_state"] == "zero_by_splitness"
            ),
            "the_exact_target_slot_is_the_unique_nonzero_orbit_in_the_existing_slot": (
                slot["target_slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
            ),
            "solving_the_canonical_chart_equation_is_equivalent_to_nonzero_slot_activation": (
                slot["k3_tail_canonical_chart_slot_equivalence_theorem"][
                    "therefore_solving_deltaC_equals_14105_on_the_fixed_package_is_equivalent_to_activating_the_unique_nonzero_tail_slot"
                ]
            ),
            "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_breaking_splitness_in_the_existing_tail_slot": (
                current_shadow["extension_class_zero"] is True
                and current_shadow["current_external_slot_state"] == "zero_by_splitness"
                and slot["target_slot_state"]
                == "unique_nonzero_orbit_in_existing_glue_slot"
                and slot["k3_tail_canonical_chart_slot_equivalence_theorem"][
                    "therefore_solving_deltaC_equals_14105_on_the_fixed_package_is_equivalent_to_activating_the_unique_nonzero_tail_slot"
                ]
            ),
            "the_live_external_wall_is_now_one_splitness_breaking_problem_on_the_same_fixed_carrier_package": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["slot_shape"] == [81, 81]
                and current_shadow["extension_class_zero"] is True
                and current_shadow["current_external_slot_state"] == "zero_by_splitness"
                and slot["target_slot_state"]
                == "unique_nonzero_orbit_in_existing_glue_slot"
            ),
        },
        "bridge_verdict": (
            "The K3 tail wall is now explicitly a splitness-breaking wall. On "
            "the fixed carrier-preserving package, the present refined K3 "
            "shadow is split with zero extension class and zero slot state, "
            "while the exact target is the unique nonzero orbit in that same "
            "existing slot. So exact K3 tail realization is equivalent to "
            "breaking splitness in the existing tail slot, not to finding new "
            "carrier geometry."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_splitness_breaking_criterion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
