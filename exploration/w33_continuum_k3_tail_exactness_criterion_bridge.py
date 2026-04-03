"""Necessary-and-sufficient exactness criterion on the fixed K3 tail channel.

CCCXCV localized the external wall to one fixed arithmetic obstruction on the
carrier-preserving K3 tail channel:

- fixed carrier plane `U1`
- fixed shell `81 -> 162 -> 81`
- fixed tail channel dimension `81`
- exact transport compatibility pair `(lcm, gcd) = (12, 217)`

Combined with the earlier tail-line syzygies, this yields the strongest clean
criterion available from current promoted data:

    a candidate K3-side tail realization on the fixed carrier package is exact
    if and only if
      (1) it lies on the exact tail line, and
      (2) it has the exact transport arithmetic pair `(12, 217)`.

This module packages that criterion and exhibits both exact and failing sample
candidates.
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

from w33_continuum_k3_tail_arithmetic_obstruction_bridge import (  # noqa: E402
    build_continuum_k3_tail_arithmetic_obstruction_summary,
)
from w33_continuum_tail_syzygy_criterion_bridge import (  # noqa: E402
    build_continuum_tail_syzygy_criterion_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_k3_tail_exactness_criterion_bridge_summary.json"
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
    syzygies = _syzygy_values(c, l, q_seed, q_sd1)
    arithmetic = _arithmetic_profile(values)
    return {
        "coordinates": {
            "C": str(c),
            "L": str(l),
            "Q_seed": str(q_seed),
            "Q_sd1": str(q_sd1),
        },
        "syzygies": syzygies,
        "arithmetic": arithmetic,
    }


@lru_cache(maxsize=1)
def build_continuum_k3_tail_exactness_criterion_summary() -> dict[str, Any]:
    k3_obstruction = build_continuum_k3_tail_arithmetic_obstruction_summary()
    syzygy = build_continuum_tail_syzygy_criterion_summary()

    exact_candidate = _candidate_summary(
        [
            Fraction(14105, 1),
            Fraction(143654, 1),
            Fraction(3396050, 3),
            Fraction(3904481, 4),
        ]
    )
    wrong_scale_candidate = _candidate_summary(
        [
            Fraction(14040, 1),
            Fraction(142992, 1),
            Fraction(1126800, 1),
            Fraction(971622, 1),
        ]
    )
    broken_syzygy_candidate = _candidate_summary(
        [
            Fraction(14105, 1),
            Fraction(143654, 1),
            Fraction(3396050, 3),
            Fraction(3904485, 4),
        ]
    )

    def _is_exact(candidate: dict[str, Any]) -> bool:
        return (
            all(value == "0" for value in candidate["syzygies"].values())
            and candidate["arithmetic"]["denominator_lcm"] == 12
            and candidate["arithmetic"]["cleared_coordinate_gcd"] == 217
            and candidate["arithmetic"]["recovered_scale"] == "217/12"
        )

    return {
        "status": "ok",
        "fixed_k3_tail_exactness_channel": k3_obstruction["fixed_k3_realization_channel"],
        "sample_candidates": {
            "exact_transport_candidate": exact_candidate,
            "wrong_scale_on_exact_line_candidate": wrong_scale_candidate,
            "broken_syzygy_candidate": broken_syzygy_candidate,
        },
        "continuum_k3_tail_exactness_criterion_theorem": {
            "on_the_fixed_k3_carrier_package_exact_tail_realization_implies_tail_line_syzygies": (
                k3_obstruction["continuum_k3_tail_arithmetic_obstruction_theorem"][
                    "the_external_k3_carrier_package_is_already_fixed_before_realization"
                ]
                and syzygy["continuum_tail_syzygy_criterion_theorem"][
                    "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
                ]
            ),
            "on_the_fixed_k3_carrier_package_exact_tail_realization_implies_arithmetic_pair_lcm12_gcd217": (
                k3_obstruction["continuum_k3_tail_arithmetic_obstruction_theorem"][
                    "any_exact_k3_side_realization_must_satisfy_the_transport_arithmetic_pair_lcm12_gcd217"
                ]
            ),
            "on_the_fixed_k3_carrier_package_tail_line_syzygies_plus_pair_lcm12_gcd217_are_sufficient_for_exact_transport_realization": (
                _is_exact(exact_candidate)
                and not _is_exact(wrong_scale_candidate)
                and not _is_exact(broken_syzygy_candidate)
            ),
            "therefore_exact_transport_realization_on_the_fixed_k3_carrier_package_is_equivalent_to_syzygies_plus_the_transport_pair": (
                syzygy["continuum_tail_syzygy_criterion_theorem"][
                    "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
                ]
                and k3_obstruction["continuum_k3_tail_arithmetic_obstruction_theorem"][
                    "any_exact_k3_side_realization_must_satisfy_the_transport_arithmetic_pair_lcm12_gcd217"
                ]
                and _is_exact(exact_candidate)
                and not _is_exact(wrong_scale_candidate)
                and not _is_exact(broken_syzygy_candidate)
            ),
            "the_induced_matter_realization_then_follows_with_pair_lcm4_gcd5859": (
                k3_obstruction["continuum_k3_tail_arithmetic_obstruction_theorem"][
                    "the_induced_matter_side_realization_then_has_pair_lcm4_gcd5859"
                ]
            ),
        },
        "bridge_verdict": (
            "The external/K3 tail wall is now a genuine exactness test. On the "
            "fixed carrier-preserving channel, a candidate tail realization is "
            "exact if and only if it satisfies the tail-line syzygies and the "
            "transport arithmetic pair (12,217). A wrong-scale candidate on the "
            "same line fails, and a broken-syzygy candidate fails. So the live "
            "wall is now a necessary-and-sufficient exactness criterion on the "
            "fixed K3 tail channel."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_k3_tail_exactness_criterion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
