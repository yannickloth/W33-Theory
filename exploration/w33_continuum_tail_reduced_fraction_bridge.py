"""Reduced-fraction criterion for continuum tail realization.

CCCXCII fixed the exact primitive integral generator of the continuum tail line
as `(780, 7944, 62600, 53979)`. Any rational point on that line therefore has
a unique reduced-fraction description

    T = (a / b) * p

with `p` the primitive generator and `gcd(a, b) = 1`.

The next exact sharpening is to identify the promoted transport and matter
realizations in that canonical arithmetic chart. The exact answer is:

- transport realization: `(a, b) = (217, 12)`
- matter realization: `(a, b) = (5859, 4) = (81*217, 4)`

So the live continuum wall is now one fixed primitive lattice direction plus
one exact reduced fraction.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from math import gcd
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_continuum_tail_primitive_generator_bridge import (  # noqa: E402
    build_continuum_tail_primitive_generator_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_reduced_fraction_bridge_summary.json"
)


def _reduced_fraction_pair(value: Fraction) -> tuple[int, int]:
    return value.numerator, value.denominator


@lru_cache(maxsize=1)
def build_continuum_tail_reduced_fraction_summary() -> dict[str, Any]:
    primitive = build_continuum_tail_primitive_generator_summary()
    generator = primitive["tail_primitive_generator"]

    transport_scale = Fraction(generator["transport_scale_over_primitive_generator"]["from_C"])
    matter_scale = Fraction(generator["matter_scale_over_primitive_generator"]["from_C"])

    transport_num, transport_den = _reduced_fraction_pair(transport_scale)
    matter_num, matter_den = _reduced_fraction_pair(matter_scale)

    return {
        "status": "ok",
        "tail_reduced_fraction_coordinates": {
            "primitive_integral_generator": generator["primitive_integral_generator"],
            "transport_reduced_fraction_scale": {
                "numerator": transport_num,
                "denominator": transport_den,
                "fraction": str(transport_scale),
                "coprime_gcd": gcd(transport_num, transport_den),
            },
            "matter_reduced_fraction_scale": {
                "numerator": matter_num,
                "denominator": matter_den,
                "fraction": str(matter_scale),
                "coprime_gcd": gcd(matter_num, matter_den),
            },
        },
        "continuum_tail_reduced_fraction_theorem": {
            "every_rational_tail_operator_on_the_fixed_primitive_line_has_a_unique_reduced_fraction_description": True,
            "the_exact_transport_realization_has_reduced_fraction_scale_217_over_12": (
                transport_num == 217 and transport_den == 12 and gcd(transport_num, transport_den) == 1
            ),
            "the_exact_matter_realization_has_reduced_fraction_scale_5859_over_4": (
                matter_num == 5859 and matter_den == 4 and gcd(matter_num, matter_den) == 1
            ),
            "the_matter_reduced_fraction_is_the_exact_81_fold_lift_of_the_transport_scale": (
                matter_scale == 81 * transport_scale
            ),
            "therefore_the_live_continuum_wall_is_now_one_fixed_primitive_tail_direction_plus_one_exact_reduced_fraction": (
                transport_num == 217
                and transport_den == 12
                and matter_num == 5859
                and matter_den == 4
            ),
        },
        "bridge_verdict": (
            "The fixed continuum tail line is now canonically charted by one "
            "reduced fraction. Relative to the primitive generator "
            "(780,7944,62600,53979), the exact transport realization is "
            "(217/12) times that generator and the exact matter realization is "
            "(5859/4) times it. So the live continuum wall is now one fixed "
            "primitive tail direction plus one exact reduced fraction."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_reduced_fraction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
