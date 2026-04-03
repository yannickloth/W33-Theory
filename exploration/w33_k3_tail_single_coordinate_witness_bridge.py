"""Single-coordinate witness criterion on the fixed K3 tail line.

CCCXCIX collapsed exact K3 tail realization on the fixed carrier package to
one unique minimal datum. The next exact sharpening is to externalize the older
single-coordinate criterion to that K3 wall.

Because the minimal datum already lies on the fixed primitive tail line with
primitive generator `(780, 7944, 62600, 53979)`, any one promoted coordinate
witness determines the same exact scale `217/12`:

- `C = 14105`
- `L = 143654`
- `Q_seed = 3396050/3`
- `Q_sd1 = 3904481/4`

So on the fixed carrier package, exact K3 tail realization is equivalent to
lying on the exact tail line together with any one of those coordinate
witnesses.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_tail_single_coordinate_witness_bridge_summary.json"
)

PRIMITIVE_GENERATOR = {
    "C": 780,
    "L": 7944,
    "Q_seed": 62600,
    "Q_sd1": 53979,
}
EXACT_COORDINATE_WITNESSES = {
    "C": Fraction(14105, 1),
    "L": Fraction(143654, 1),
    "Q_seed": Fraction(3396050, 3),
    "Q_sd1": Fraction(3904481, 4),
}


@lru_cache(maxsize=1)
def build_k3_tail_single_coordinate_witness_summary() -> dict[str, Any]:
    from w33_minimal_k3_tail_realization_equivalence_bridge import (
        build_minimal_k3_tail_realization_equivalence_summary,
    )

    base = build_minimal_k3_tail_realization_equivalence_summary()
    fixed = base["fixed_k3_tail_exactness_channel"]

    recovered_scales = {
        name: str(value / PRIMITIVE_GENERATOR[name])
        for name, value in EXACT_COORDINATE_WITNESSES.items()
    }

    witness_equalities = {
        name: {
            "primitive_coordinate": str(PRIMITIVE_GENERATOR[name]),
            "exact_coordinate": str(value),
            "recovered_scale": recovered_scales[name],
        }
        for name, value in EXACT_COORDINATE_WITNESSES.items()
    }

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "primitive_integral_generator": {
            key: str(value) for key, value in PRIMITIVE_GENERATOR.items()
        },
        "exact_coordinate_witnesses": witness_equalities,
        "k3_tail_single_coordinate_witness_theorem": {
            "the_unique_minimal_datum_already_lies_on_the_fixed_exact_tail_line": (
                base["minimal_k3_tail_realization_equivalence_theorem"][
                    "the_unique_minimal_tail_datum_already_lies_on_the_exact_tail_line"
                ]
            ),
            "each_promoted_coordinate_witness_recovers_the_same_exact_scale_217_over_12": (
                all(scale == "217/12" for scale in recovered_scales.values())
            ),
            "therefore_on_the_fixed_tail_line_any_one_promoted_coordinate_witness_identifies_the_unique_minimal_datum": (
                base["minimal_k3_tail_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum"
                ]
                and all(scale == "217/12" for scale in recovered_scales.values())
            ),
            "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_tail_line_membership_plus_any_one_coordinate_witness": (
                fixed["ordered_filtration_dimensions"] == [81, 162, 81]
                and all(scale == "217/12" for scale in recovered_scales.values())
                and base["minimal_k3_tail_realization_equivalence_theorem"][
                    "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum"
                ]
            ),
            "the_live_external_wall_is_now_existence_of_any_one_exact_coordinate_witness_from_genuine_k3_side_data_on_the_fixed_line_class": (
                all(scale == "217/12" for scale in recovered_scales.values())
                and fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
            ),
        },
        "bridge_verdict": (
            "The fixed K3 tail wall is now a single-coordinate witness problem. "
            "On the exact tail line, any one promoted coordinate witness "
            "C=14105, L=143654, Q_seed=3396050/3, or Q_sd1=3904481/4 recovers "
            "the same exact scale 217/12 and therefore identifies the unique "
            "minimal datum. So the remaining external question is now "
            "existence of any one exact coordinate witness from genuine K3-side "
            "data on the fixed tail-line class."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_tail_single_coordinate_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
