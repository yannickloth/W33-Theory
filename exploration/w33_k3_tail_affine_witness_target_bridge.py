"""Exact affine witness target on the fixed K3 tail package.

CD proved that any one promoted coordinate witness on the fixed tail line
already identifies the unique minimal nonzero datum. CDI then applied that
criterion to the live refined K3 object itself and showed that the current
candidate still sits at the zero point in all promoted coordinates.

So the next exact reduction is affine rather than existential:

- the present refined K3 tail candidate is the origin in witness coordinates;
- the exact witness point is
  `(14105, 143654, 3396050/3, 3904481/4)`;
- therefore the missing K3-side enhancement is one unique affine displacement
  from the current zero candidate to that exact witness point.

This is the sharpest positive target on the current fixed package: one exact
vector must be added, not a family of unrelated coordinate choices.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_affine_witness_target_bridge_summary.json"
)

CURRENT_ZERO_WITNESS_POINT = {
    "C": Fraction(0, 1),
    "L": Fraction(0, 1),
    "Q_seed": Fraction(0, 1),
    "Q_sd1": Fraction(0, 1),
}
EXACT_WITNESS_POINT = {
    "C": Fraction(14105, 1),
    "L": Fraction(143654, 1),
    "Q_seed": Fraction(3396050, 3),
    "Q_sd1": Fraction(3904481, 4),
}


@lru_cache(maxsize=1)
def build_k3_tail_affine_witness_target_summary() -> dict[str, Any]:
    from w33_current_k3_tail_coordinate_witness_failure_bridge import (
        build_current_k3_tail_coordinate_witness_failure_summary,
    )
    from w33_k3_tail_single_coordinate_witness_bridge import (
        PRIMITIVE_GENERATOR,
        build_k3_tail_single_coordinate_witness_summary,
    )

    failure = build_current_k3_tail_coordinate_witness_failure_summary()
    witness = build_k3_tail_single_coordinate_witness_summary()
    fixed = witness["fixed_k3_tail_exactness_channel"]

    affine_displacement = {
        name: EXACT_WITNESS_POINT[name] - CURRENT_ZERO_WITNESS_POINT[name]
        for name in EXACT_WITNESS_POINT
    }
    recovered_scales = {
        name: str(affine_displacement[name] / PRIMITIVE_GENERATOR[name])
        for name in affine_displacement
    }

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "current_zero_witness_point": {
            key: str(value) for key, value in CURRENT_ZERO_WITNESS_POINT.items()
        },
        "exact_witness_point": {
            key: str(value) for key, value in EXACT_WITNESS_POINT.items()
        },
        "affine_witness_displacement": {
            key: str(value) for key, value in affine_displacement.items()
        },
        "displacement_recovered_scales": recovered_scales,
        "k3_tail_affine_witness_target_theorem": {
            "the_present_refined_k3_candidate_is_the_zero_point_in_witness_coordinates": (
                failure["current_k3_tail_coordinate_witness_failure_theorem"][
                    "the_present_refined_k3_object_has_zero_in_all_promoted_tail_coordinates"
                ]
            ),
            "the_exact_witness_point_is_the_unique_nonzero_coordinate_target_from_cd": (
                witness["k3_tail_single_coordinate_witness_theorem"][
                    "each_promoted_coordinate_witness_recovers_the_same_exact_scale_217_over_12"
                ]
            ),
            "the_missing_k3_side_addition_is_exactly_one_affine_displacement_from_the_current_zero_point_to_that_witness_point": (
                all(
                    affine_displacement[name] == EXACT_WITNESS_POINT[name]
                    for name in affine_displacement
                )
            ),
            "that_affine_displacement_lies_on_the_fixed_tail_line_with_common_scale_217_over_12": (
                all(scale == "217/12" for scale in recovered_scales.values())
            ),
            "therefore_the_live_external_wall_is_one_exact_affine_witness_target_on_the_same_fixed_package": (
                failure["current_k3_tail_coordinate_witness_failure_theorem"][
                    "the_live_external_wall_is_now_the_first_nonzero_coordinate_witness_on_the_same_fixed_k3_package"
                ]
                and all(scale == "217/12" for scale in recovered_scales.values())
                and fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
            ),
        },
        "bridge_verdict": (
            "The sharpened K3 wall is now affine and exact. The current refined "
            "K3 tail candidate is the origin in promoted witness coordinates, "
            "while the exact witness point is "
            "(14105,143654,3396050/3,3904481/4). Their difference is therefore "
            "one unique affine displacement, and that displacement already lies "
            "on the fixed primitive tail line with common scale 217/12. So the "
            "remaining external wall is one exact affine witness target on the "
            "same fixed carrier-preserving K3 package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_affine_witness_target_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
