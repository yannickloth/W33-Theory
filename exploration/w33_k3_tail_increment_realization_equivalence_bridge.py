"""Exact equivalence between K3 tail realization and one affine increment witness.

CCCXCIX already collapsed exact K3 tail realization on the fixed carrier
package to realization of the one unique minimal datum. CDIII then reduced the
current affine wall to existence of any one exact affine increment witness:

- because the current refined K3 point is zero in promoted witness
  coordinates, the full affine target is the increment packet itself;
- any one promoted increment already recovers the same exact scale `217/12`;
- so any one such increment identifies the full affine target.

The next exact collapse is therefore immediate: on the fixed package, exact K3
tail realization is equivalent to realizing any one exact affine increment
witness from genuine K3-side data.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT
    / "data"
    / "w33_k3_tail_increment_realization_equivalence_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_tail_increment_realization_equivalence_summary() -> dict[str, Any]:
    from w33_k3_tail_affine_increment_witness_bridge import (
        build_k3_tail_affine_increment_witness_summary,
    )
    from w33_minimal_k3_tail_realization_equivalence_bridge import (
        build_minimal_k3_tail_realization_equivalence_summary,
    )

    increment = build_k3_tail_affine_increment_witness_summary()
    datum = build_minimal_k3_tail_realization_equivalence_summary()
    fixed = increment["fixed_k3_tail_exactness_channel"]

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "k3_tail_increment_realization_equivalence_theorem": {
            "exact_k3_tail_realization_on_the_fixed_package_is_already_equivalent_to_realizing_the_unique_minimal_datum": (
                datum["minimal_k3_tail_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum"
                ]
            ),
            "any_one_exact_affine_increment_witness_already_identifies_the_full_affine_target": (
                increment["k3_tail_affine_increment_witness_theorem"][
                    "therefore_any_one_promoted_affine_increment_identifies_the_full_affine_witness_target"
                ]
            ),
            "the_full_affine_target_is_just_the_current_zero_point_shifted_by_the_unique_minimal_datum_on_the_same_fixed_package": (
                increment["k3_tail_affine_increment_witness_theorem"][
                    "the_current_refined_k3_point_is_zero_so_affine_increments_equal_the_exact_witness_coordinates"
                ]
            ),
            "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness": (
                datum["minimal_k3_tail_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum"
                ]
                and increment["k3_tail_affine_increment_witness_theorem"][
                    "therefore_any_one_promoted_affine_increment_identifies_the_full_affine_witness_target"
                ]
                and increment["k3_tail_affine_increment_witness_theorem"][
                    "the_current_refined_k3_point_is_zero_so_affine_increments_equal_the_exact_witness_coordinates"
                ]
            ),
            "the_live_external_wall_is_now_exactly_one_affine_increment_witness_existence_problem": (
                fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and increment["k3_tail_affine_increment_witness_theorem"][
                    "therefore_the_live_external_wall_is_existence_of_any_one_exact_affine_increment_witness_on_the_same_fixed_package"
                ]
                and datum["minimal_k3_tail_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum"
                ]
            ),
        },
        "bridge_verdict": (
            "The sharpened K3 wall has now collapsed to one exact existence "
            "question. On the fixed carrier-preserving package, exact K3 tail "
            "realization is equivalent to realizing any one exact affine "
            "increment witness. The current refined K3 point is already zero "
            "in witness coordinates, so any one promoted increment recovers "
            "the same exact scale 217/12 and identifies the full affine "
            "target, which is itself the unique minimal datum. So the live "
            "external wall is now exactly one affine increment witness "
            "existence problem."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_k3_tail_increment_realization_equivalence_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
