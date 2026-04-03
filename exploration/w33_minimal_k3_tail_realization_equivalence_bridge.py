"""Exact equivalence between K3 tail realization and the minimal tail datum.

CCCXCVIII fixed the unique positive target on the present carrier-preserving K3
package: one nonzero tail datum in the existing slot, with primitive direction
``(780, 7944, 62600, 53979)`` and exact transport pair ``(12,217)``.

The next exact reduction is to collapse the wall itself:

- exact K3 tail realization on the fixed package is not a larger target than
  that datum;
- and that datum is not merely necessary, but already sufficient.

So the remaining external question is now exactly one existence question:
whether genuine K3-side data can realize that unique minimal datum.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_minimal_k3_tail_realization_equivalence_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_minimal_k3_tail_realization_equivalence_summary() -> dict[str, Any]:
    from w33_minimal_k3_tail_enhancement_datum_bridge import (
        build_minimal_k3_tail_enhancement_datum_summary,
    )

    base = build_minimal_k3_tail_enhancement_datum_summary()
    fixed = base["fixed_k3_tail_exactness_channel"]
    datum = base["minimal_k3_tail_enhancement_datum"]

    primitive = datum["primitive_integral_generator"]
    c = int(primitive["C"])
    l = int(primitive["L"])
    q_seed = int(primitive["Q_seed"])
    q_sd1 = int(primitive["Q_sd1"])

    primitive_syzygies = {
        "662C_minus_65L": str(662 * c - 65 * l),
        "15650C_minus_195Qseed": str(15650 * c - 195 * q_seed),
        "17993C_minus_260Qsd1": str(17993 * c - 260 * q_sd1),
    }

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed,
        "minimal_k3_tail_enhancement_datum": datum,
        "primitive_generator_syzygies": primitive_syzygies,
        "minimal_k3_tail_realization_equivalence_theorem": {
            "the_unique_minimal_tail_datum_already_lies_on_the_exact_tail_line": (
                all(value == "0" for value in primitive_syzygies.values())
            ),
            "the_unique_minimal_tail_datum_already_has_the_exact_transport_pair_lcm12_gcd217": (
                datum["transport_arithmetic_pair"]
                == {
                    "denominator_lcm": 12,
                    "cleared_coordinate_gcd": 217,
                    "recovered_scale": "217/12",
                }
            ),
            "therefore_realizing_the_unique_minimal_tail_datum_is_sufficient_for_exact_tail_realization_on_the_fixed_package": (
                all(value == "0" for value in primitive_syzygies.values())
                and datum["transport_arithmetic_pair"]["recovered_scale"] == "217/12"
                and fixed["carrier_plane"] == "U1"
                and fixed["ordered_filtration_dimensions"] == [81, 162, 81]
            ),
            "by_cccxcviii_any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum": (
                base["minimal_k3_tail_enhancement_datum_theorem"][
                    "any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum_before_any_formal_completion_avatar"
                ]
            ),
            "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_the_unique_minimal_tail_datum": (
                all(value == "0" for value in primitive_syzygies.values())
                and datum["transport_arithmetic_pair"]["recovered_scale"] == "217/12"
                and base["minimal_k3_tail_enhancement_datum_theorem"][
                    "any_exact_k3_side_realization_must_factor_through_that_unique_minimal_tail_datum_before_any_formal_completion_avatar"
                ]
            ),
            "the_live_external_wall_is_now_exactly_existence_of_that_one_minimal_datum": (
                base["minimal_k3_tail_enhancement_datum_theorem"][
                    "therefore_the_live_positive_target_is_one_unique_minimal_k3_tail_enhancement_datum_on_the_same_fixed_package"
                ]
                and all(value == "0" for value in primitive_syzygies.values())
                and datum["transport_arithmetic_pair"]["recovered_scale"] == "217/12"
            ),
        },
        "bridge_verdict": (
            "The fixed K3 tail wall has now collapsed to one exact existence "
            "question. On the already-fixed carrier package, exact tail "
            "realization is equivalent to realizing the unique minimal nonzero "
            "datum in the existing slot. That datum already lies on the exact "
            "tail line and already has the forced transport pair (12,217). So "
            "the remaining wall is no longer a larger completion target at all; "
            "it is exactly existence of that one minimal datum from genuine "
            "K3-side data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_minimal_k3_tail_realization_equivalence_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
