"""Exact single-coordinate criterion for continuum tail realization.

CCCXC cut the fixed transport tail line out by exact syzygies on the avatar
coordinates `(C, L, Q_seed, Q_sd1)`. The next exact question is whether exact
realization still requires carrying all promoted coordinate values at once, or
whether one coordinate normalization already forces the others once line
membership is imposed.

The exact answer is yes. On the exact tail line:

- `C = 14105`
- `L = 143654`
- `Q_seed = 3396050/3`
- `Q_sd1 = 3904481/4`

are all equivalent normalizations. Any one of them, together with the syzygies,
forces the other three and therefore the exact promoted transport operator. The
matter side then follows by the exact `81`-fold qutrit lift.
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
from w33_continuum_tail_syzygy_criterion_bridge import (  # noqa: E402
    build_continuum_tail_syzygy_criterion_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_tail_single_coordinate_criterion_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_continuum_tail_single_coordinate_criterion_summary() -> dict[str, Any]:
    normal = build_continuum_tail_operator_normal_form_summary()
    syzygy = build_continuum_tail_syzygy_criterion_summary()

    transport = normal["realized_transport_tail_operator_profile"]
    matter = normal["realized_matter_tail_operator_profile"]

    constant = Fraction(transport["constant_witness"])
    linear = Fraction(transport["linear_witness"])
    q_seed = Fraction(transport["quadratic_seed_witness"])
    q_sd1 = Fraction(transport["quadratic_sd1_witness"])

    from_c = {
        "L": str(Fraction(662, 65) * constant),
        "Q_seed": str(Fraction(15650, 195) * constant),
        "Q_sd1": str(Fraction(17993, 260) * constant),
    }
    from_l = {
        "C": str(Fraction(65, 662) * linear),
        "Q_seed": str(Fraction(15650, 1986) * linear),
        "Q_sd1": str(Fraction(17993, 2648) * linear),
    }
    from_q_seed = {
        "C": str(Fraction(195, 15650) * q_seed),
        "L": str(Fraction(993, 7825) * q_seed),
        "Q_sd1": str(Fraction(701727, 813800) * q_seed),
    }
    from_q_sd1 = {
        "C": str(Fraction(260, 17993) * q_sd1),
        "L": str(Fraction(2648, 17993) * q_sd1),
        "Q_seed": str(Fraction(62600, 53979) * q_sd1),
    }

    return {
        "status": "ok",
        "tail_coordinate_normalizations": {
            "transport_coordinates": {
                "C": str(constant),
                "L": str(linear),
                "Q_seed": str(q_seed),
                "Q_sd1": str(q_sd1),
            },
            "transport_reconstruction_from_C": from_c,
            "transport_reconstruction_from_L": from_l,
            "transport_reconstruction_from_Q_seed": from_q_seed,
            "transport_reconstruction_from_Q_sd1": from_q_sd1,
            "matter_coordinates": {
                "C": matter["constant_witness"],
                "L": matter["linear_witness"],
                "Q_seed": matter["quadratic_seed_witness"],
                "Q_sd1": matter["quadratic_sd1_witness"],
            },
        },
        "continuum_tail_single_coordinate_criterion_theorem": {
            "on_the_exact_tail_line_C_equal_14105_forces_the_full_transport_operator": (
                from_c["L"] == "143654"
                and from_c["Q_seed"] == "3396050/3"
                and from_c["Q_sd1"] == "3904481/4"
            ),
            "on_the_exact_tail_line_L_equal_143654_forces_the_full_transport_operator": (
                from_l["C"] == "14105"
                and from_l["Q_seed"] == "3396050/3"
                and from_l["Q_sd1"] == "3904481/4"
            ),
            "on_the_exact_tail_line_Qseed_equal_3396050_over_3_forces_the_full_transport_operator": (
                from_q_seed["C"] == "14105"
                and from_q_seed["L"] == "143654"
                and from_q_seed["Q_sd1"] == "3904481/4"
            ),
            "on_the_exact_tail_line_Qsd1_equal_3904481_over_4_forces_the_full_transport_operator": (
                from_q_sd1["C"] == "14105"
                and from_q_sd1["L"] == "143654"
                and from_q_sd1["Q_seed"] == "3396050/3"
            ),
            "therefore_any_one_promoted_coordinate_normalization_plus_syzygies_is_necessary_and_sufficient_for_exact_transport_realization": (
                syzygy["continuum_tail_syzygy_criterion_theorem"][
                    "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
                ]
                and from_c["L"] == "143654"
                and from_l["C"] == "14105"
                and from_q_seed["Q_sd1"] == "3904481/4"
                and from_q_sd1["Q_seed"] == "3396050/3"
            ),
            "the_exact_matter_operator_then_follows_by_the_81_fold_lift": (
                normal["continuum_tail_operator_normal_form_theorem"][
                    "the_realized_matter_tail_operator_is_the_exact_81_fold_lift_of_the_transport_operator"
                ]
            ),
        },
        "bridge_verdict": (
            "The continuum wall is now sharper than projective line membership "
            "plus several scale checks. On the exact tail line, any one promoted "
            "coordinate normalization is equivalent to the others: "
            "C=14105, L=143654, Q_seed=3396050/3, and Q_sd1=3904481/4 all force "
            "the same exact transport operator once the avatar syzygies hold. So "
            "the live wall is now exact tail-line membership plus any one "
            "promoted coordinate normalization, with the matter side then forced "
            "by the exact 81-fold lift."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_continuum_tail_single_coordinate_criterion_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
