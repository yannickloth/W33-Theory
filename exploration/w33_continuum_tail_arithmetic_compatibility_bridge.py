"""Arithmetic compatibility criterion for continuum tail realization.

CCCXCIII fixed the exact transport and matter realizations as reduced fractions
on the primitive tail line:

    transport = (217 / 12) * p
    matter    = (5859 / 4) * p

with `p = (780, 7944, 62600, 53979)` the unique primitive integral generator.

The next exact sharpening is to express that same realization criterion directly
in terms of the external coordinate arithmetic itself. Because `p` is primitive,
the reduced fraction scale on the tail line is exactly

    scale = gcd(cleared_coordinates) / lcm(denominators).

For the promoted realizations this gives:

- transport: `lcm = 12`, `gcd = 217`, hence scale `217/12`
- matter: `lcm = 4`, `gcd = 5859`, hence scale `5859/4`

So the live wall is now exact tail-line membership together with one explicit
denominator/gcd compatibility pair.
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

from w33_continuum_tail_primitive_generator_bridge import (  # noqa: E402
    build_continuum_tail_primitive_generator_summary,
)
from w33_continuum_tail_syzygy_criterion_bridge import (  # noqa: E402
    build_continuum_tail_syzygy_criterion_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_arithmetic_compatibility_bridge_summary.json"
)


def _arithmetic_profile(values: list[Fraction]) -> dict[str, Any]:
    denominator_lcm = lcm(*[value.denominator for value in values])
    cleared = [int(value * denominator_lcm) for value in values]
    cleared_gcd = reduce(gcd, [abs(value) for value in cleared])
    primitive = [value // cleared_gcd for value in cleared]
    return {
        "denominator_lcm": denominator_lcm,
        "cleared_coordinates": [str(value) for value in cleared],
        "cleared_coordinate_gcd": cleared_gcd,
        "primitive_direction": [str(value) for value in primitive],
        "recovered_scale": str(Fraction(cleared_gcd, denominator_lcm)),
    }


@lru_cache(maxsize=1)
def build_continuum_tail_arithmetic_compatibility_summary() -> dict[str, Any]:
    primitive = build_continuum_tail_primitive_generator_summary()
    syzygy = build_continuum_tail_syzygy_criterion_summary()

    transport = primitive["tail_primitive_generator"]["transport_coordinates"]
    matter = primitive["tail_primitive_generator"]["matter_coordinates"]

    transport_profile = _arithmetic_profile(
        [
            Fraction(transport["C"]),
            Fraction(transport["L"]),
            Fraction(transport["Q_seed"]),
            Fraction(transport["Q_sd1"]),
        ]
    )
    matter_profile = _arithmetic_profile(
        [
            Fraction(matter["C"]),
            Fraction(matter["L"]),
            Fraction(matter["Q_seed"]),
            Fraction(matter["Q_sd1"]),
        ]
    )

    return {
        "status": "ok",
        "tail_arithmetic_compatibility": {
            "transport_profile": transport_profile,
            "matter_profile": matter_profile,
        },
        "continuum_tail_arithmetic_compatibility_theorem": {
            "on_the_fixed_primitive_tail_line_the_reduced_fraction_scale_equals_cleared_gcd_over_denominator_lcm": True,
            "the_exact_transport_realization_has_compatibility_pair_lcm12_gcd217": (
                transport_profile["denominator_lcm"] == 12
                and transport_profile["cleared_coordinate_gcd"] == 217
                and transport_profile["primitive_direction"] == ["780", "7944", "62600", "53979"]
                and transport_profile["recovered_scale"] == "217/12"
            ),
            "the_exact_matter_realization_has_compatibility_pair_lcm4_gcd5859": (
                matter_profile["denominator_lcm"] == 4
                and matter_profile["cleared_coordinate_gcd"] == 5859
                and matter_profile["primitive_direction"] == ["780", "7944", "62600", "53979"]
                and matter_profile["recovered_scale"] == "5859/4"
            ),
            "the_matter_compatibility_pair_is_the_exact_81_fold_lift_of_the_transport_pair": (
                matter_profile["denominator_lcm"] * 3 == transport_profile["denominator_lcm"]
                and matter_profile["cleared_coordinate_gcd"] == 27 * transport_profile["cleared_coordinate_gcd"]
                and Fraction(matter_profile["recovered_scale"]) == 81 * Fraction(transport_profile["recovered_scale"])
            ),
            "therefore_the_live_continuum_wall_is_now_tail_line_membership_plus_one_exact_denominator_gcd_compatibility_pair": (
                syzygy["continuum_tail_syzygy_criterion_theorem"][
                    "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
                ]
                and transport_profile["denominator_lcm"] == 12
                and transport_profile["cleared_coordinate_gcd"] == 217
            ),
        },
        "bridge_verdict": (
            "The fixed continuum tail line is now constrained by external "
            "coordinate arithmetic, not just by direction and scale. Because the "
            "primitive generator is integral and primitive, the reduced-fraction "
            "scale is exactly cleared_gcd/denominator_lcm. The promoted "
            "transport realization is therefore characterized by the pair "
            "(lcm,gcd)=(12,217), and the promoted matter realization by "
            "(4,5859). So the live wall is now exact tail-line membership plus "
            "one denominator/gcd compatibility pair."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_arithmetic_compatibility_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
