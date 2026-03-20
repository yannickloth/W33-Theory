"""Natural-units electroweak root-gap bridge for the promoted W33 package.

The recent natural-units bridges already prove the two exact inputs

    x + y = 1,
    xy    = q Theta(W33) / Phi_3^2 = 30/169,

where

    x = (4 pi alpha) / g^2   = sin^2(theta_W)  = 3/13,
    y = (4 pi alpha) / g'^2  = cos^2(theta_W)  = 10/13.

So the weak and hypercharge reciprocal shares are already forced as the roots
of the single quadratic

    t^2 - t + 30/169 = 0.

The discriminant is then

    1 - 4 * 30/169 = 49/169 = (Phi_6 / Phi_3)^2,

so the exact root gap is

    y - x = Phi_6 / Phi_3 = 7/13 = sin^2(theta_23).

This turns the neutral-current shell into a full reconstruction law for the
electroweak split: the sum is the electric unit law, the product is the neutral
shell, and the gap is the atmospheric selector.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_heawood_weinberg_denominator_bridge import (
    build_heawood_weinberg_denominator_summary,
)
from w33_natural_units_electroweak_split_bridge import (
    build_natural_units_electroweak_split_summary,
)
from w33_natural_units_neutral_shell_bridge import (
    build_natural_units_neutral_shell_summary,
)
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_root_gap_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_root_gap_summary() -> dict[str, Any]:
    electroweak = build_natural_units_electroweak_split_summary()
    neutral = build_natural_units_neutral_shell_summary()
    heawood = build_heawood_weinberg_denominator_summary()
    standard_model = build_standard_model_cyclotomic_summary()

    weak_share = Fraction(electroweak["electroweak_split_dictionary"]["reciprocal_g"]["exact"])
    hypercharge_share = Fraction(
        electroweak["electroweak_split_dictionary"]["reciprocal_gprime"]["exact"]
    )
    neutral_product = Fraction(
        neutral["neutral_shell_dictionary"]["neutral_reciprocal"]["exact"]
    )
    atmospheric_share = Fraction(
        standard_model["promoted_observables"]["sin2_theta_23"]["exact"]
    )
    phi3 = Fraction(standard_model["cyclotomic_data"]["phi3"])
    phi6 = Fraction(standard_model["cyclotomic_data"]["phi6"])
    q = Fraction(standard_model["cyclotomic_data"]["q"])
    theta = Fraction(electroweak["nested_complement_dictionary"]["theta_w33"])

    discriminant = Fraction(1, 1) - 4 * neutral_product
    root_gap = hypercharge_share - weak_share
    reconstructed_weak = (Fraction(1, 1) - atmospheric_share) / 2
    reconstructed_hypercharge = (Fraction(1, 1) + atmospheric_share) / 2

    return {
        "status": "ok",
        "root_gap_dictionary": {
            "quadratic_formula": "t^2 - t + q Theta(W33) / Phi_3^2 = 0",
            "sum_formula": "x + y = 1",
            "product_formula": "xy = q Theta(W33) / Phi_3^2",
            "discriminant_formula": "1 - 4 q Theta(W33) / Phi_3^2 = Phi_6^2 / Phi_3^2",
            "gap_formula": "y - x = Phi_6 / Phi_3 = sin^2(theta_23)",
            "weak_root_formula": "x = (1 - Phi_6 / Phi_3) / 2 = q / Phi_3",
            "hypercharge_root_formula": "y = (1 + Phi_6 / Phi_3) / 2 = Theta(W33) / Phi_3",
            "q": int(q),
            "theta_w33": int(theta),
            "phi3": int(phi3),
            "phi6": int(phi6),
            "weak_share": _fraction_dict(weak_share),
            "hypercharge_share": _fraction_dict(hypercharge_share),
            "neutral_product": _fraction_dict(neutral_product),
            "discriminant": _fraction_dict(discriminant),
            "root_gap": _fraction_dict(root_gap),
            "atmospheric_share": _fraction_dict(atmospheric_share),
        },
        "exact_factorizations": {
            "weak_plus_hypercharge_equals_unity": weak_share + hypercharge_share == 1,
            "weak_times_hypercharge_equals_neutral_product": (
                weak_share * hypercharge_share == neutral_product
            ),
            "discriminant_equals_phi6_squared_over_phi3_squared": (
                discriminant == (phi6 * phi6) / (phi3 * phi3)
            ),
            "root_gap_equals_phi6_over_phi3": root_gap == phi6 / phi3,
            "root_gap_equals_atmospheric_share": root_gap == atmospheric_share,
            "weak_root_reconstructs_from_gap": reconstructed_weak == weak_share,
            "hypercharge_root_reconstructs_from_gap": (
                reconstructed_hypercharge == hypercharge_share
            ),
            "weak_root_equals_q_over_phi3": weak_share == q / phi3,
            "hypercharge_root_equals_theta_over_phi3": hypercharge_share == theta / phi3,
            "heawood_denominator_matches_root_gap": (
                heawood["electroweak_from_heawood_dictionary"]["phi6_over_heawood_denominator"]["exact"]
                == str(root_gap.numerator) + "/" + str(root_gap.denominator)
            ),
        },
        "bridge_verdict": (
            "The neutral-current shell now forces the whole electroweak split as a "
            "quadratic reconstruction law. The weak and hypercharge reciprocal "
            "shares x=(4 pi alpha)/g^2 and y=(4 pi alpha)/g'^2 obey x+y=1 and "
            "xy=30/169, so they are exactly the roots of t^2-t+30/169=0. The "
            "discriminant is 49/169=(Phi_6/Phi_3)^2, hence the exact root gap is "
            "y-x=Phi_6/Phi_3=7/13. So the same 7/13 selector that controls the "
            "promoted atmospheric PMNS channel also measures the asymmetry between "
            "the weak and hypercharge shares. In the live natural-units package, "
            "the electric unit law gives the sum, the neutral shell gives the "
            "product, and the atmospheric selector gives the gap."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_root_gap_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
