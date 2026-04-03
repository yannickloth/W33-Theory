"""Primitive integral generator for the continuum tail line.

CCCXCI showed that, on the exact tail line, any one promoted coordinate
normalization already forces the full promoted transport operator. The next
exact sharpening is arithmetic: identify the unique primitive integral
generator of that rational line.

For the exact transport tail coordinates

    (C, L, Q_seed, Q_sd1)
    = (14105, 143654, 3396050/3, 3904481/4)

clearing denominators gives

    12 * (C, L, Q_seed, Q_sd1)
    = (169260, 1723848, 13584200, 11713443)

and the common gcd is exactly `217`. So the unique primitive integral
generator of the fixed tail line is

    (780, 7944, 62600, 53979),

and the exact realized transport operator is precisely `(217/12)` times that
generator. The matter-coupled operator is the exact `81`-fold lift.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache, reduce
from math import gcd, lcm
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_continuum_tail_single_coordinate_criterion_bridge import (  # noqa: E402
    build_continuum_tail_single_coordinate_criterion_summary,
)
from w33_continuum_tail_syzygy_criterion_bridge import (  # noqa: E402
    build_continuum_tail_syzygy_criterion_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_primitive_generator_bridge_summary.json"
)


def _primitive_integral_generator(coords: list[Fraction]) -> tuple[int, int, list[int]]:
    denom_lcm = lcm(*[value.denominator for value in coords])
    cleared = [int(value * denom_lcm) for value in coords]
    cleared_gcd = reduce(gcd, [abs(value) for value in cleared])
    primitive = [value // cleared_gcd for value in cleared]
    return denom_lcm, cleared_gcd, primitive


def _syzygy_values(c: int, l: int, q_seed: int, q_sd1: int) -> dict[str, str]:
    return {
        "662C_minus_65L": str(662 * c - 65 * l),
        "15650C_minus_195Qseed": str(15650 * c - 195 * q_seed),
        "17993C_minus_260Qsd1": str(17993 * c - 260 * q_sd1),
    }


@lru_cache(maxsize=1)
def build_continuum_tail_primitive_generator_summary() -> dict[str, Any]:
    single = build_continuum_tail_single_coordinate_criterion_summary()
    syzygy = build_continuum_tail_syzygy_criterion_summary()

    transport = single["tail_coordinate_normalizations"]["transport_coordinates"]
    matter = single["tail_coordinate_normalizations"]["matter_coordinates"]

    transport_coords = [
        Fraction(transport["C"]),
        Fraction(transport["L"]),
        Fraction(transport["Q_seed"]),
        Fraction(transport["Q_sd1"]),
    ]
    matter_coords = [
        Fraction(matter["C"]),
        Fraction(matter["L"]),
        Fraction(matter["Q_seed"]),
        Fraction(matter["Q_sd1"]),
    ]

    denom_lcm, cleared_gcd, primitive = _primitive_integral_generator(transport_coords)
    primitive_c, primitive_l, primitive_q_seed, primitive_q_sd1 = primitive

    transport_scales = {
        "from_C": str(transport_coords[0] / primitive_c),
        "from_L": str(transport_coords[1] / primitive_l),
        "from_Q_seed": str(transport_coords[2] / primitive_q_seed),
        "from_Q_sd1": str(transport_coords[3] / primitive_q_sd1),
    }
    matter_scales = {
        "from_C": str(matter_coords[0] / primitive_c),
        "from_L": str(matter_coords[1] / primitive_l),
        "from_Q_seed": str(matter_coords[2] / primitive_q_seed),
        "from_Q_sd1": str(matter_coords[3] / primitive_q_sd1),
    }

    primitive_syzygies = _syzygy_values(
        primitive_c, primitive_l, primitive_q_seed, primitive_q_sd1
    )

    return {
        "status": "ok",
        "tail_primitive_generator": {
            "transport_coordinates": transport,
            "matter_coordinates": matter,
            "clearing_denominator_lcm": denom_lcm,
            "cleared_transport_coordinates": [str(int(value * denom_lcm)) for value in transport_coords],
            "cleared_transport_coordinate_gcd": cleared_gcd,
            "primitive_integral_generator": {
                "C": str(primitive_c),
                "L": str(primitive_l),
                "Q_seed": str(primitive_q_seed),
                "Q_sd1": str(primitive_q_sd1),
            },
            "primitive_generator_syzygies": primitive_syzygies,
            "transport_scale_over_primitive_generator": transport_scales,
            "matter_scale_over_primitive_generator": matter_scales,
        },
        "continuum_tail_primitive_generator_theorem": {
            "the_exact_tail_line_has_a_unique_primitive_integral_generator_up_to_sign": (
                primitive == [780, 7944, 62600, 53979]
            ),
            "the_primitive_integral_generator_satisfies_the_exact_avatar_syzygies": (
                all(value == "0" for value in primitive_syzygies.values())
            ),
            "the_exact_transport_operator_is_217_over_12_times_the_primitive_generator": (
                all(value == "217/12" for value in transport_scales.values())
            ),
            "the_exact_matter_operator_is_the_81_fold_lift_of_the_same_primitive_generator": (
                all(value == "5859/4" for value in matter_scales.values())
            ),
            "therefore_the_live_continuum_wall_is_now_a_fixed_primitive_tail_lattice_direction_plus_one_rational_scale": (
                syzygy["continuum_tail_syzygy_criterion_theorem"][
                    "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
                ]
                and primitive == [780, 7944, 62600, 53979]
                and all(value == "217/12" for value in transport_scales.values())
            ),
        },
        "bridge_verdict": (
            "The fixed continuum tail line is now arithmetic, not just projective. "
            "It has the unique primitive integral generator "
            "(780,7944,62600,53979), cut out by the exact avatar syzygies. The "
            "realized transport operator is exactly (217/12) times that "
            "generator, and the matter-coupled operator is the exact 81-fold "
            "lift. So the live wall is now one fixed primitive tail lattice "
            "direction plus one rational scale."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_primitive_generator_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
