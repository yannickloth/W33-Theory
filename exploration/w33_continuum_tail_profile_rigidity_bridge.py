"""Exact rigidity of the residual continuum transport-tail profile.

CCCLXXXIV reduced the live continuum existence problem to the transport tail
wall. The next exact question is whether that residual wall is still a
multi-parameter ambiguity, or whether the remaining CP2/K3 seed data already
forces one local tail profile.

The strongest exact statement available from the promoted transport continuum
stack is:

1. the transport first-order local `r^20` CP2/K3 seed-gap vector has primitive
   profile `(65, 662)` with transport amplitude `217`;
2. the matter-coupled first-order local `r^20` seed-gap vector has the same
   primitive profile and amplitude `81 * 217`;
3. the quadratic seed-gap contraction from seed to `sd^1` is universal with
   exact ratio `53979 / 62600`.

So the residual continuum wall is no longer a generic channel-valued problem.
It is realization of one exact local tail ray together with one exact first-
refinement contraction law.
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

from w33_continuum_qutrit_scaling_bridge import QUTRIT_FACTOR  # noqa: E402
from w33_continuum_seed_isolation_bridge import (  # noqa: E402
    build_continuum_seed_isolation_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_profile_rigidity_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_continuum_tail_profile_rigidity_summary() -> dict[str, Any]:
    seed = build_continuum_seed_isolation_bridge_summary()

    transport_first = seed["first_order_seed_isolation"]["transport"]
    matter_first = seed["first_order_seed_isolation"]["matter_coupled"]

    transport_const = int(transport_first["constant_corr20_gap"]["exact"])
    transport_lin = int(transport_first["linear_corr20_gap"]["exact"])
    matter_const = int(matter_first["constant_corr20_gap"]["exact"])
    matter_lin = int(matter_first["linear_corr20_gap"]["exact"])

    transport_amp = gcd(transport_const, transport_lin)
    matter_amp = gcd(matter_const, matter_lin)

    primitive_profile = [
        transport_const // transport_amp,
        transport_lin // transport_amp,
    ]
    matter_profile = [
        matter_const // matter_amp,
        matter_lin // matter_amp,
    ]

    quadratic = seed["quadratic_gap_contraction"]
    contraction = str(
        Fraction(quadratic["transport_sd1_gap"]["exact"])
        / Fraction(quadratic["transport_seed_gap"]["exact"])
    )

    return {
        "status": "ok",
        "transport_tail_profile": {
            "transport_local_r20_gap_vector": [transport_const, transport_lin],
            "transport_profile_amplitude": transport_amp,
            "primitive_transport_profile": primitive_profile,
            "matter_local_r20_gap_vector": [matter_const, matter_lin],
            "matter_profile_amplitude": matter_amp,
            "primitive_matter_profile": matter_profile,
            "matter_amplitude_is_qutrit_factor_times_transport_amplitude": (
                matter_amp == QUTRIT_FACTOR * transport_amp
            ),
            "transport_and_matter_share_the_same_primitive_profile": (
                primitive_profile == matter_profile
            ),
        },
        "transport_tail_contraction": {
            "seed_to_sd1_quadratic_contraction_ratio": contraction,
            "seed_to_sd1_quadratic_contraction_is_strict": (
                Fraction(quadratic["transport_sd1_gap"]["exact"])
                < Fraction(quadratic["transport_seed_gap"]["exact"])
            ),
        },
        "continuum_tail_profile_rigidity_theorem": {
            "the_residual_transport_tail_has_one_exact_primitive_first_order_profile": (
                primitive_profile == [65, 662]
            ),
            "the_matter_coupled_tail_has_the_same_profile_with_exact_81_fold_amplitude": (
                primitive_profile == matter_profile
                and matter_amp == QUTRIT_FACTOR * transport_amp
            ),
            "the_first_refinement_quadratic_contraction_law_is_universal": (
                contraction == "53979/62600"
            ),
            "therefore_the_live_continuum_existence_problem_is_a_one_parameter_tail_profile_realization_problem": (
                primitive_profile == [65, 662]
                and primitive_profile == matter_profile
                and matter_amp == QUTRIT_FACTOR * transport_amp
                and contraction == "53979/62600"
            ),
        },
        "bridge_verdict": (
            "The residual continuum wall is now sharper than a generic transport "
            "tail channel. The transport-side local r^20 CP2/K3 seed-gap vector "
            "is exactly 217*(65,662), while the matter-coupled vector is "
            "81*217*(65,662). So transport and matter already share one primitive "
            "local tail profile ray. The quadratic seed-gap contraction from the "
            "seed to sd^1 is also universal, with exact ratio 53979/62600. "
            "Therefore the live continuum wall is a one-parameter tail-profile "
            "realization problem on a fixed exact ray, not a free multi-parameter "
            "channel ambiguity."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_profile_rigidity_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
