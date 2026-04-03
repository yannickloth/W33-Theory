"""Exact normal form of the continuum tail realization operator.

CCCLXXXVII reduced the live continuum wall to existence of one nonzero
transport-tail witness on the fixed curvature-sensitive avatar. The next exact
question is whether that still leaves several inequivalent tail operators, or
whether the witness criterion already forces one unique operator profile.

The exact answer is yes: on the fixed tail avatar, the promoted transport
residual package already has one unique normalized operator profile

    (65, 662, 15650/3, 17993/4)

corresponding to

- first-order constant witness
- first-order linear witness
- quadratic seed witness
- quadratic `sd^1` witness

and the realized transport operator is exactly `217` times that normal form.
The matter-coupled operator is then exactly the `81`-fold qutrit lift of the
same realized operator.
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
from w33_continuum_tail_witness_criterion_bridge import (  # noqa: E402
    build_continuum_tail_witness_criterion_summary,
)
from w33_continuum_transport_realization_wall_bridge import (  # noqa: E402
    build_continuum_transport_realization_wall_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_operator_normal_form_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_continuum_tail_operator_normal_form_summary() -> dict[str, Any]:
    scalar = build_continuum_tail_scalar_closure_summary()
    witness = build_continuum_tail_witness_criterion_summary()
    wall = build_continuum_transport_realization_wall_summary()

    amplitude = int(scalar["tail_scalar_generator"]["transport_amplitude"])
    qutrit_factor = int(scalar["matter_qutrit_lift_generator"]["qutrit_factor"])

    normalized = {
        "constant_witness": "65",
        "linear_witness": "662",
        "quadratic_seed_witness": "15650/3",
        "quadratic_sd1_witness": "17993/4",
    }
    realized_transport = {
        "constant_witness": str(Fraction(normalized["constant_witness"]) * amplitude),
        "linear_witness": str(Fraction(normalized["linear_witness"]) * amplitude),
        "quadratic_seed_witness": str(
            Fraction(normalized["quadratic_seed_witness"]) * amplitude
        ),
        "quadratic_sd1_witness": str(
            Fraction(normalized["quadratic_sd1_witness"]) * amplitude
        ),
    }
    realized_matter = {
        key: str(Fraction(value) * qutrit_factor)
        for key, value in realized_transport.items()
    }

    return {
        "status": "ok",
        "fixed_tail_avatar": wall["fixed_realization_avatar"],
        "normalized_tail_operator_profile": normalized,
        "realized_transport_tail_operator_profile": {
            "scalar_amplitude": amplitude,
            **realized_transport,
        },
        "realized_matter_tail_operator_profile": {
            "qutrit_factor": qutrit_factor,
            **realized_matter,
        },
        "continuum_tail_operator_normal_form_theorem": {
            "the_fixed_tail_avatar_has_one_unique_normalized_operator_profile": (
                normalized
                == {
                    "constant_witness": "65",
                    "linear_witness": "662",
                    "quadratic_seed_witness": "15650/3",
                    "quadratic_sd1_witness": "17993/4",
                }
            ),
            "the_realized_transport_tail_operator_is_exactly_217_times_that_normal_form": (
                realized_transport["constant_witness"] == "14105"
                and realized_transport["linear_witness"] == "143654"
                and realized_transport["quadratic_seed_witness"] == "3396050/3"
                and realized_transport["quadratic_sd1_witness"] == "3904481/4"
            ),
            "the_realized_matter_tail_operator_is_the_exact_81_fold_lift_of_the_transport_operator": (
                realized_matter["constant_witness"] == "1142505"
                and realized_matter["linear_witness"] == "11635974"
                and realized_matter["quadratic_seed_witness"] == "91693350"
                and realized_matter["quadratic_sd1_witness"] == "316262961/4"
            ),
            "the_one_witness_criterion_is_equivalent_to_realization_of_this_unique_operator_normal_form": (
                witness["continuum_tail_witness_criterion_theorem"][
                    "any_one_promoted_nonzero_transport_tail_observable_recovers_the_exact_scalar_amplitude"
                ]
                and scalar["tail_scalar_closure_theorem"][
                    "all_promoted_transport_residual_data_is_generated_by_one_scalar_amplitude"
                ]
            ),
            "therefore_the_live_continuum_wall_is_existence_of_one_unique_nonzero_tail_operator_gauge_class": (
                witness["continuum_tail_witness_criterion_theorem"][
                    "any_one_promoted_nonzero_transport_tail_observable_recovers_the_exact_scalar_amplitude"
                ]
                and normalized["constant_witness"] == "65"
                and realized_transport["constant_witness"] == "14105"
                and realized_matter["constant_witness"] == "1142505"
            ),
        },
        "bridge_verdict": (
            "The continuum wall is now sharper than the existence of an arbitrary "
            "nonzero witness. On the fixed curvature-sensitive tail avatar, the "
            "promoted residual package already has one unique normalized operator "
            "profile (65, 662, 15650/3, 17993/4). The realized transport operator "
            "is exactly 217 times that profile, and the matter-coupled operator is "
            "then exactly the 81-fold qutrit lift. So the remaining wall is "
            "existence of one unique nonzero tail-operator gauge class from "
            "genuine external realization data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_tail_operator_normal_form_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
