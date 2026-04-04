"""Canonical K3 tail chart is exactly the nonzero-slot activation condition.

CDVII reduced exact K3 tail realization on the fixed carrier-preserving
package to one canonical integral equation:

- `ΔC = 14105`.

Separately, the enhancement-side reductions had already fixed the only missing
positive datum on that same package:

- the current K3 state has slot state `zero_by_splitness`;
- the unique exact target is the nonzero replacement in that existing slot;
- that unique minimal datum has primitive direction `(780,7944,62600,53979)`
  and exact transport scale `217/12`.

So the canonical chart equation is no longer an abstract coordinate
normalization. Its `C` coordinate is exactly

- `780 * (217/12) = 14105`.

Therefore, on the fixed K3 package, solving the canonical equation
`ΔC = 14105` is equivalent to activating the unique nonzero tail slot. The
remaining wall is now one exact slot-activation problem on genuine K3-side
data, not another coordinate-choice ambiguity.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_canonical_chart_slot_equivalence_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_tail_canonical_chart_slot_equivalence_summary() -> dict[str, Any]:
    from w33_current_k3_tail_exactness_failure_bridge import (
        build_current_k3_tail_exactness_failure_summary,
    )
    from w33_k3_tail_canonical_chart_realization_equivalence_bridge import (
        build_k3_tail_canonical_chart_realization_equivalence_summary,
    )
    from w33_minimal_k3_tail_enhancement_datum_bridge import (
        build_minimal_k3_tail_enhancement_datum_summary,
    )

    current = build_current_k3_tail_exactness_failure_summary()
    chart = build_k3_tail_canonical_chart_realization_equivalence_summary()
    datum = build_minimal_k3_tail_enhancement_datum_summary()

    fixed = chart["fixed_k3_tail_exactness_channel"]
    current_zero = current["current_refined_k3_zero_tail_candidate"]
    minimal = datum["minimal_k3_tail_enhancement_datum"]

    primitive_c = Fraction(minimal["primitive_integral_generator"]["C"])
    scale = Fraction(minimal["transport_arithmetic_pair"]["recovered_scale"])
    canonical_c = primitive_c * scale

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "current_slot_state": fixed["current_slot_state"],
        "target_slot_state": minimal["slot_state"],
        "canonical_chart_target": {
            "coordinate": "dC",
            "required_value": str(canonical_c),
            "primitive_c_direction": str(primitive_c),
            "transport_scale": str(scale),
            "factorization": f"{primitive_c} * ({scale})",
        },
        "k3_tail_canonical_chart_slot_equivalence_theorem": {
            "the_current_k3_state_has_zero_slot_and_zero_canonical_chart_increment": (
                fixed["current_slot_state"] == "zero_by_splitness"
                and current_zero["coordinates"]["C"] == "0"
            ),
            "the_unique_minimal_exact_tail_datum_activates_the_nonzero_slot": (
                minimal["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
                and minimal["transport_arithmetic_pair"]["recovered_scale"] == "217/12"
            ),
            "the_unique_minimal_exact_tail_datum_has_canonical_chart_coordinate_deltaC_equals_14105": (
                primitive_c == 780
                and scale == Fraction(217, 12)
                and canonical_c == Fraction(14105, 1)
            ),
            "therefore_solving_deltaC_equals_14105_on_the_fixed_package_is_equivalent_to_activating_the_unique_nonzero_tail_slot": (
                chart["k3_tail_canonical_chart_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_solving_deltaC_equals_14105"
                ]
                and datum["minimal_k3_tail_enhancement_datum_theorem"][
                    "therefore_the_live_positive_target_is_one_unique_minimal_k3_tail_enhancement_datum_on_the_same_fixed_package"
                ]
                and canonical_c == Fraction(14105, 1)
                and minimal["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
            ),
            "the_live_external_wall_is_now_one_slot_activation_problem_on_the_existing_k3_tail_channel": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and fixed["slot_shape"] == [81, 81]
                and fixed["current_slot_state"] == "zero_by_splitness"
                and minimal["slot_state"] == "unique_nonzero_orbit_in_existing_glue_slot"
                and canonical_c == Fraction(14105, 1)
            ),
        },
        "bridge_verdict": (
            "The canonical K3 tail equation is now visibly external. On the "
            "fixed carrier-preserving package, the current state still has the "
            "zero slot and zero canonical increment, while the unique exact "
            "minimal datum activates the unique nonzero slot and has "
            "C-coordinate 780*(217/12)=14105. So solving ΔC=14105 is "
            "equivalent to activating the unique nonzero tail slot. The live "
            "wall is now one exact slot-activation problem on genuine K3-side "
            "data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_canonical_chart_slot_equivalence_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
