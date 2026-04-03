"""Current refined K3 side fails the exact tail-realization test.

CCCXCVI gave the strongest clean exactness test available on the fixed
carrier-preserving K3 tail channel:

1. lie on the exact tail-operator line, and
2. satisfy the exact transport arithmetic pair `(lcm, gcd) = (12, 217)`.

Separately, the refined K3 bridge already proved that the present K3-side
transport object is split with structurally zero tail-to-head glue. This module
combines those promoted layers into the sharpest external non-realization
certificate currently available:

- the current refined K3 object already sits on the fixed carrier package;
- its tail data satisfies the exact syzygies only trivially, at the zero point;
- it therefore fails the exactness test solely because the nonzero arithmetic
  pair `(12, 217)` is absent.

So the remaining wall is no longer another carrier or shell ambiguity. It is
existence of genuinely new K3-side tail data on the same fixed package.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache, reduce
import json
from math import gcd, lcm
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_continuum_k3_tail_exactness_criterion_bridge import (  # noqa: E402
    build_continuum_k3_tail_exactness_criterion_summary,
)
from w33_refined_k3_zero_orbit_bridge import (  # noqa: E402
    build_refined_k3_zero_orbit_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_tail_exactness_failure_bridge_summary.json"
)


def _syzygy_values(c: Fraction, l: Fraction, q_seed: Fraction, q_sd1: Fraction) -> dict[str, str]:
    return {
        "662C_minus_65L": str(662 * c - 65 * l),
        "15650C_minus_195Qseed": str(15650 * c - 195 * q_seed),
        "17993C_minus_260Qsd1": str(17993 * c - 260 * q_sd1),
    }


def _arithmetic_profile(values: list[Fraction]) -> dict[str, Any]:
    denominator_lcm = lcm(*[value.denominator for value in values])
    cleared = [int(value * denominator_lcm) for value in values]
    cleared_gcd = reduce(gcd, [abs(value) for value in cleared])
    return {
        "denominator_lcm": denominator_lcm,
        "cleared_coordinate_gcd": cleared_gcd,
        "recovered_scale": str(Fraction(cleared_gcd, denominator_lcm)),
    }


def _candidate_summary(values: list[Fraction]) -> dict[str, Any]:
    c, l, q_seed, q_sd1 = values
    return {
        "coordinates": {
            "C": str(c),
            "L": str(l),
            "Q_seed": str(q_seed),
            "Q_sd1": str(q_sd1),
        },
        "syzygies": _syzygy_values(c, l, q_seed, q_sd1),
        "arithmetic": _arithmetic_profile(values),
    }


@lru_cache(maxsize=1)
def build_current_k3_tail_exactness_failure_summary() -> dict[str, Any]:
    exactness = build_continuum_k3_tail_exactness_criterion_summary()
    zero_orbit = build_refined_k3_zero_orbit_bridge_summary()

    current_k3_zero_candidate = _candidate_summary(
        [
            Fraction(0, 1),
            Fraction(0, 1),
            Fraction(0, 1),
            Fraction(0, 1),
        ]
    )

    fixed_channel = exactness["fixed_k3_tail_exactness_channel"]
    current_shadow = zero_orbit["current_refined_k3_transport_shadow"]

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": fixed_channel,
        "current_refined_k3_shadow": current_shadow,
        "current_refined_k3_zero_tail_candidate": current_k3_zero_candidate,
        "current_k3_tail_exactness_failure_theorem": {
            "the_current_refined_k3_object_already_sits_on_the_fixed_carrier_package_before_tail_realization": (
                fixed_channel["ordered_filtration_dimensions"]
                == current_shadow["ordered_filtration_dimensions"]
                and fixed_channel["tail_channel_dimension"] == 81
                and current_shadow["extension_class_zero"] is True
            ),
            "the_current_refined_k3_tail_data_satisfies_the_exact_syzygies_only_trivially_at_the_zero_point": (
                all(
                    value == "0"
                    for value in current_k3_zero_candidate["syzygies"].values()
                )
                and current_k3_zero_candidate["arithmetic"]["recovered_scale"] == "0"
            ),
            "the_current_refined_k3_tail_data_fails_the_transport_pair_lcm12_gcd217": (
                current_k3_zero_candidate["arithmetic"]["denominator_lcm"] != 12
                and current_k3_zero_candidate["arithmetic"]["cleared_coordinate_gcd"] != 217
                and current_k3_zero_candidate["arithmetic"]["recovered_scale"] != "217/12"
                and zero_orbit["refined_k3_zero_orbit_theorem"][
                    "the_unique_nonzero_ternary_orbit_is_not_realized_on_the_current_refined_k3_side"
                ]
            ),
            "therefore_the_current_refined_k3_object_fails_the_exact_tail_realization_test_on_the_fixed_carrier_package": (
                exactness["continuum_k3_tail_exactness_criterion_theorem"][
                    "therefore_exact_transport_realization_on_the_fixed_k3_carrier_package_is_equivalent_to_syzygies_plus_the_transport_pair"
                ]
                and all(
                    value == "0"
                    for value in current_k3_zero_candidate["syzygies"].values()
                )
                and current_k3_zero_candidate["arithmetic"]["denominator_lcm"] != 12
                and current_k3_zero_candidate["arithmetic"]["cleared_coordinate_gcd"] != 217
            ),
            "the_failure_is_localized_to_missing_nonzero_tail_data_not_to_carrier_ambiguity": (
                exactness["continuum_k3_tail_exactness_criterion_theorem"][
                    "on_the_fixed_k3_carrier_package_exact_tail_realization_implies_tail_line_syzygies"
                ]
                and zero_orbit["refined_k3_zero_orbit_theorem"][
                    "current_refined_k3_shadow_is_split_with_zero_extension_class"
                ]
                and zero_orbit["refined_k3_zero_orbit_theorem"][
                    "any_realization_of_the_unique_nonzero_orbit_requires_new_external_data_beyond_the_current_refined_k3_bridge"
                ]
            ),
            "therefore_any_exact_k3_tail_realization_requires_genuine_new_k3_side_data_on_the_same_fixed_carrier_package": (
                zero_orbit["refined_k3_zero_orbit_theorem"][
                    "any_realization_of_the_unique_nonzero_orbit_requires_new_external_data_beyond_the_current_refined_k3_bridge"
                ]
                and exactness["continuum_k3_tail_exactness_criterion_theorem"][
                    "therefore_exact_transport_realization_on_the_fixed_k3_carrier_package_is_equivalent_to_syzygies_plus_the_transport_pair"
                ]
            ),
        },
        "bridge_verdict": (
            "The current refined K3 object already sits on the fixed carrier "
            "package, and its tail data satisfies the exact syzygies only "
            "trivially at the zero point. What fails is not carrier geometry: "
            "the present K3-side object still has zero extension class and "
            "therefore never realizes the nonzero transport arithmetic pair "
            "(12,217). So the exactness test fails for one precise reason "
            "only: the missing nonzero tail datum. Any exact realization "
            "therefore requires genuinely new K3-side data on the same fixed "
            "carrier-preserving package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_tail_exactness_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
