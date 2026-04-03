"""Exact one-witness criterion for continuum tail realization.

CCCLXXXVI reduced the residual continuum wall to one scalar tail family on the
fixed avatar. The next exact question is whether continuum realization still
requires matching the whole residual package at once, or whether any one
promoted nonzero transport-tail observable already determines the same scalar.

The exact answer is yes. The promoted transport tail observables

- first-order local constant gap `14105`
- first-order local linear gap `143654`
- quadratic seed gap `3396050/3`
- quadratic `sd^1` gap `3904481/4`

all recover the same scalar amplitude `A = 217` under the fixed normalization

- `14105 / 65`
- `143654 / 662`
- `(3396050/3) / (15650/3)`
- `(3904481/4) / (17993/4)`

So any exact realization of one nonzero transport witness on the fixed tail
channel forces the whole transport residual package, and then the whole
matter-coupled package follows by the exact `81`-fold qutrit lift.
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

from w33_continuum_tail_scalar_closure_bridge import (  # noqa: E402
    build_continuum_tail_scalar_closure_summary,
)
from w33_continuum_transport_realization_wall_bridge import (  # noqa: E402
    build_continuum_transport_realization_wall_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_witness_criterion_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_continuum_tail_witness_criterion_summary() -> dict[str, Any]:
    scalar = build_continuum_tail_scalar_closure_summary()
    wall = build_continuum_transport_realization_wall_summary()

    tail = scalar["tail_scalar_generator"]
    matter = scalar["matter_qutrit_lift_generator"]

    amplitude = int(tail["transport_amplitude"])
    a_from_const = Fraction(tail["transport_first_order_constant_gap"], 65)
    a_from_lin = Fraction(tail["transport_first_order_linear_gap"], 662)
    a_from_qseed = Fraction(tail["transport_quadratic_seed_gap"]) / Fraction(15650, 3)
    a_from_qsd1 = Fraction(tail["transport_quadratic_sd1_gap"]) / Fraction(17993, 4)

    return {
        "status": "ok",
        "fixed_tail_avatar": wall["fixed_realization_avatar"],
        "transport_tail_witnesses": {
            "scalar_amplitude": amplitude,
            "amplitude_from_first_order_constant_gap": str(a_from_const),
            "amplitude_from_first_order_linear_gap": str(a_from_lin),
            "amplitude_from_quadratic_seed_gap": str(a_from_qseed),
            "amplitude_from_quadratic_sd1_gap": str(a_from_qsd1),
            "all_witnesses_recover_the_same_scalar": (
                a_from_const == a_from_lin == a_from_qseed == a_from_qsd1 == amplitude
            ),
        },
        "continuum_tail_witness_criterion_theorem": {
            "any_one_promoted_nonzero_transport_tail_observable_recovers_the_exact_scalar_amplitude": (
                a_from_const == a_from_lin == a_from_qseed == a_from_qsd1 == amplitude
            ),
            "once_that_scalar_is_fixed_the_entire_transport_residual_package_is_forced": (
                scalar["tail_scalar_closure_theorem"][
                    "all_promoted_transport_residual_data_is_generated_by_one_scalar_amplitude"
                ]
            ),
            "the_matter_coupled_package_then_follows_by_exact_81_fold_lift": (
                scalar["tail_scalar_closure_theorem"][
                    "the_matter_coupled_residual_package_is_the_exact_81_fold_lift_of_the_same_scalar_family"
                ]
            ),
            "the_head_channel_remains_protected_and_the_witness_lives_only_on_the_fixed_tail_avatar": (
                wall["continuum_transport_realization_wall_theorem"][
                    "the_matter_coupled_transport_object_has_one_protected_flat_81_head_copy"
                ]
                and wall["continuum_transport_realization_wall_theorem"][
                    "the_remaining_81_copy_is_the_curvature_sensitive_tail_channel"
                ]
            ),
            "therefore_the_live_continuum_wall_is_existence_of_one_nonzero_tail_witness_on_the_fixed_avatar": (
                a_from_const == a_from_lin == a_from_qseed == a_from_qsd1 == amplitude
                and scalar["tail_scalar_closure_theorem"][
                    "all_promoted_transport_residual_data_is_generated_by_one_scalar_amplitude"
                ]
                and scalar["tail_scalar_closure_theorem"][
                    "the_matter_coupled_residual_package_is_the_exact_81_fold_lift_of_the_same_scalar_family"
                ]
            ),
        },
        "bridge_verdict": (
            "The remaining continuum wall is now sharper than full-package "
            "matching. Any one promoted nonzero transport-tail witness already "
            "recovers the same scalar amplitude A=217 on the fixed tail avatar: "
            "14105/65 = 143654/662 = (3396050/3)/(15650/3) = "
            "(3904481/4)/(17993/4) = 217. So a genuine realization need only "
            "produce one nonzero witness on the curvature-sensitive tail "
            "channel; the entire transport residual package and its exact "
            "81-fold matter lift are then forced."
        ),
        "matter_reference": {
            "matter_amplitude": matter["matter_amplitude"],
            "matter_quadratic_seed_gap": matter["matter_quadratic_seed_gap"],
            "matter_quadratic_sd1_gap": matter["matter_quadratic_sd1_gap"],
        },
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_witness_criterion_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
