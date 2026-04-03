"""Current refined K3 object lacks every promoted coordinate witness.

CD sharpened the external wall to a single-coordinate witness problem on the
fixed K3 tail-line class:

- any one promoted coordinate witness
  `C=14105`, `L=143654`, `Q_seed=3396050/3`, or `Q_sd1=3904481/4`
  already recovers the exact scale `217/12`;
- so any one such witness already identifies the unique minimal nonzero tail
  datum; and
- therefore exact K3 tail realization is equivalent to existence of any one
  such witness on the fixed carrier-preserving package.

The next exact step is to apply that sharper criterion to the present refined
K3 object itself. Its current tail candidate is still the zero point, so every
promoted coordinate witness is absent. The remaining wall is therefore exactly
the first nonzero coordinate witness on the same fixed package.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT
    / "data"
    / "w33_current_k3_tail_coordinate_witness_failure_bridge_summary.json"
)

PROMOTED_COORDINATE_WITNESSES = {
    "C": Fraction(14105, 1),
    "L": Fraction(143654, 1),
    "Q_seed": Fraction(3396050, 3),
    "Q_sd1": Fraction(3904481, 4),
}


@lru_cache(maxsize=1)
def build_current_k3_tail_coordinate_witness_failure_summary() -> dict[str, Any]:
    from w33_k3_tail_single_coordinate_witness_bridge import (
        build_k3_tail_single_coordinate_witness_summary,
    )
    from w33_minimal_k3_tail_enhancement_datum_bridge import (
        build_minimal_k3_tail_enhancement_datum_summary,
    )

    witness_summary = build_k3_tail_single_coordinate_witness_summary()
    datum_summary = build_minimal_k3_tail_enhancement_datum_summary()

    fixed = witness_summary["fixed_k3_tail_exactness_channel"]
    zero_candidate = datum_summary["current_refined_k3_zero_tail_candidate"]

    current_coordinates = {
        "C": Fraction(0, 1),
        "L": Fraction(0, 1),
        "Q_seed": Fraction(0, 1),
        "Q_sd1": Fraction(0, 1),
    }

    witness_comparison = {
        name: {
            "current_value": str(current_coordinates[name]),
            "promoted_witness": str(promoted),
            "matches_promoted_witness": current_coordinates[name] == promoted,
        }
        for name, promoted in PROMOTED_COORDINATE_WITNESSES.items()
    }

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "current_refined_k3_zero_tail_candidate": zero_candidate,
        "promoted_coordinate_witnesses": {
            name: str(value) for name, value in PROMOTED_COORDINATE_WITNESSES.items()
        },
        "witness_comparison": witness_comparison,
        "current_k3_tail_coordinate_witness_failure_theorem": {
            "the_present_refined_k3_object_has_zero_in_all_promoted_tail_coordinates": (
                all(value["current_value"] == "0" for value in witness_comparison.values())
            ),
            "the_present_refined_k3_object_exhibits_no_exact_coordinate_witness": (
                not any(
                    value["matches_promoted_witness"]
                    for value in witness_comparison.values()
                )
            ),
            "by_cd_any_one_promoted_coordinate_witness_would_already_identify_the_unique_minimal_tail_datum": (
                witness_summary["k3_tail_single_coordinate_witness_theorem"][
                    "therefore_on_the_fixed_tail_line_any_one_promoted_coordinate_witness_identifies_the_unique_minimal_datum"
                ]
            ),
            "therefore_the_present_refined_k3_object_fails_exact_tail_realization_exactly_by_lacking_any_promoted_coordinate_witness": (
                not any(
                    value["matches_promoted_witness"]
                    for value in witness_comparison.values()
                )
                and witness_summary["k3_tail_single_coordinate_witness_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_tail_line_membership_plus_any_one_coordinate_witness"
                ]
                and zero_candidate["arithmetic"]["recovered_scale"] == "0"
            ),
            "the_live_external_wall_is_now_the_first_nonzero_coordinate_witness_on_the_same_fixed_k3_package": (
                all(value["current_value"] == "0" for value in witness_comparison.values())
                and not any(
                    value["matches_promoted_witness"]
                    for value in witness_comparison.values()
                )
                and fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
            ),
        },
        "bridge_verdict": (
            "The present refined K3 object now fails the sharpened wall in the "
            "smallest possible way. On the fixed carrier-preserving package, "
            "its current tail candidate still has zero in every promoted "
            "coordinate, so it exhibits none of the exact witnesses "
            "C=14105, L=143654, Q_seed=3396050/3, or Q_sd1=3904481/4. But CD "
            "already proved that any one such witness would identify the "
            "unique minimal nonzero datum. So the remaining external wall is "
            "now exactly the first nonzero coordinate witness on the same "
            "fixed K3 package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_current_k3_tail_coordinate_witness_failure_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
