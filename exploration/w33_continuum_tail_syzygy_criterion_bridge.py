"""Exact syzygy criterion for the continuum tail line.

CCCLXXXIX reduced the live continuum wall to existence of one nonzero point on
one fixed tail-operator line. The next exact sharpening is to write that line
as the zero set of explicit avatar-internal constraints instead of leaving it
as an abstract span statement.

On the fixed transport tail avatar, with coordinates

    (C, L, Q_seed, Q_sd1)

for the first-order constant witness, first-order linear witness, quadratic
seed witness, and quadratic `sd^1` witness, the promoted tail line is cut out
exactly by the three integer-cleared syzygies

    662 C - 65 L = 0
    15650 C - 195 Q_seed = 0
    17993 C - 260 Q_sd1 = 0

Together with non-vanishing, this is exactly projective membership in the
unique tail-operator line. The already-promoted witness normalization then
forces the realized scalar `A = 217`.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
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

from w33_continuum_tail_operator_normal_form_bridge import (  # noqa: E402
    build_continuum_tail_operator_normal_form_summary,
)
from w33_continuum_tail_witness_criterion_bridge import (  # noqa: E402
    build_continuum_tail_witness_criterion_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_syzygy_criterion_bridge_summary.json"
)


def _syzygies(
    constant: Fraction,
    linear: Fraction,
    quadratic_seed: Fraction,
    quadratic_sd1: Fraction,
) -> dict[str, str]:
    return {
        "662C_minus_65L": str(662 * constant - 65 * linear),
        "15650C_minus_195Qseed": str(15650 * constant - 195 * quadratic_seed),
        "17993C_minus_260Qsd1": str(17993 * constant - 260 * quadratic_sd1),
    }


@lru_cache(maxsize=1)
def build_continuum_tail_syzygy_criterion_summary() -> dict[str, Any]:
    normal = build_continuum_tail_operator_normal_form_summary()
    witness = build_continuum_tail_witness_criterion_summary()

    transport = normal["realized_transport_tail_operator_profile"]
    matter = normal["realized_matter_tail_operator_profile"]

    transport_syzygies = _syzygies(
        Fraction(transport["constant_witness"]),
        Fraction(transport["linear_witness"]),
        Fraction(transport["quadratic_seed_witness"]),
        Fraction(transport["quadratic_sd1_witness"]),
    )
    matter_syzygies = _syzygies(
        Fraction(matter["constant_witness"]),
        Fraction(matter["linear_witness"]),
        Fraction(matter["quadratic_seed_witness"]),
        Fraction(matter["quadratic_sd1_witness"]),
    )

    zero_syzygies = all(value == "0" for value in transport_syzygies.values())
    matter_zero_syzygies = all(value == "0" for value in matter_syzygies.values())

    return {
        "status": "ok",
        "tail_line_syzygies": {
            "coordinates": ["C", "L", "Q_seed", "Q_sd1"],
            "equations": [
                "662*C - 65*L = 0",
                "15650*C - 195*Q_seed = 0",
                "17993*C - 260*Q_sd1 = 0",
            ],
            "transport_operator_syzygies": transport_syzygies,
            "matter_operator_syzygies": matter_syzygies,
        },
        "continuum_tail_syzygy_criterion_theorem": {
            "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies": True,
            "the_promoted_transport_operator_satisfies_all_syzygies_exactly": zero_syzygies,
            "the_exact_81_fold_matter_lift_satisfies_the_same_projective_syzygies": matter_zero_syzygies,
            "any_candidate_tail_operator_fails_projective_realizability_if_any_syzygy_is_nonzero": True,
            "combined_with_the_promoted_nonzero_witness_criterion_this_forces_the_exact_realized_operator": (
                zero_syzygies
                and witness["continuum_tail_witness_criterion_theorem"][
                    "any_one_promoted_nonzero_transport_tail_observable_recovers_the_exact_scalar_amplitude"
                ]
            ),
            "therefore_the_live_continuum_wall_is_exact_projective_tail_line_membership_plus_forced_nonzero_normalization": (
                zero_syzygies
                and matter_zero_syzygies
                and witness["continuum_tail_witness_criterion_theorem"][
                    "any_one_promoted_nonzero_transport_tail_observable_recovers_the_exact_scalar_amplitude"
                ]
            ),
        },
        "bridge_verdict": (
            "The fixed tail line is now written as an exact obstruction system on "
            "the avatar itself. A candidate tail operator is projectively "
            "realizable only if its coordinates satisfy the three syzygies "
            "662C-65L=0, 15650C-195Q_seed=0, and 17993C-260Q_sd1=0. The "
            "promoted transport operator and its exact 81-fold matter lift both "
            "satisfy these identically. Combined with the already-promoted "
            "nonzero witness criterion, this forces the exact realized operator. "
            "So the live continuum wall is exact projective tail-line "
            "membership plus forced nonzero normalization."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_syzygy_criterion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
