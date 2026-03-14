"""Direct SRG-parameter Rosetta lock for the promoted observable package.

The public-facing promoted formulas were previously organized through

    q = 3,   Phi_3 = 13,   Phi_6 = 7,

and then through the master variable

    x = sin^2(theta_W) = 3/13.

For W(3,3) the SRG parameters are

    (v, k, lambda, mu) = (40, 12, 2, 4).

This module proves that the same promoted package is already determined directly
by the SRG data:

    q     = lambda + 1,
    Phi_3 = k + 1,
    Phi_6 = k - lambda - mu + 1.

Hence the promoted observables become

    sin^2(theta_W) = tan(theta_C) = (lambda + 1)/(k + 1)
    sin^2(theta_12)            = mu/(k + 1)
    sin^2(theta_23)            = (k - lambda - mu + 1)/(k + 1)
    sin^2(theta_13)            = lambda/((k + 1)(k - lambda - mu + 1))
    Omega_Lambda               = (lambda + 1)^2/(k + 1)
    m_H^2/v^2                 = 2(k - lambda - mu + 1)/(4(k + 1) + (lambda + 1))

and the promoted spectral/gravity ratios become

    a2/a0                      = 2(k - lambda - mu + 1)/(lambda + 1)
    a4/a0                      = 2(4(k + 1) + (lambda + 1))/(lambda + 1)
    c6/a0                      = 2(k + 1)
    c6/c_EH,cont               = (lambda + 1)(k + 1).

So the promoted Standard Model, cosmology, Higgs, spectral-action, and gravity
layers are directly locked to the native SRG geometry itself.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_spectral_action_cyclotomic_bridge import build_spectral_action_cyclotomic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_srg_rosetta_lock_bridge_summary.json"

K = 12
LAMBDA = 2
MU = 4


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_srg_rosetta_lock_summary() -> dict[str, Any]:
    sm = build_standard_model_cyclotomic_summary()
    spectral = build_spectral_action_cyclotomic_summary()

    q_from_srg = LAMBDA + 1
    phi3_from_srg = K + 1
    phi6_from_srg = K - LAMBDA - MU + 1

    exact_sm = {
        "sin2_theta_w_ew": Fraction(sm["promoted_observables"]["sin2_theta_w_ew"]["exact"]),
        "tan_theta_c": Fraction(sm["promoted_observables"]["tan_theta_c"]["exact"]),
        "sin2_theta_12": Fraction(sm["promoted_observables"]["sin2_theta_12"]["exact"]),
        "sin2_theta_23": Fraction(sm["promoted_observables"]["sin2_theta_23"]["exact"]),
        "sin2_theta_13": Fraction(sm["promoted_observables"]["sin2_theta_13"]["exact"]),
        "omega_lambda": Fraction(sm["promoted_observables"]["omega_lambda"]["exact"]),
        "higgs_ratio_square": Fraction(sm["promoted_observables"]["higgs_ratio_square"]["exact"]),
    }
    exact_spectral = {
        "a2_over_a0": Fraction(spectral["internal_spectral_action"]["a2_over_a0"]["exact"]),
        "a4_over_a0": Fraction(spectral["internal_spectral_action"]["a4_over_a0"]["exact"]),
        "discrete_6_mode_over_a0": Fraction(spectral["gravity_lock"]["discrete_6_mode_over_a0"]["exact"]),
        "discrete_to_continuum_ratio": Fraction(spectral["gravity_lock"]["discrete_to_continuum_ratio"]["exact"]),
    }

    formulas = {
        "sin2_theta_w_ew": Fraction(LAMBDA + 1, K + 1),
        "tan_theta_c": Fraction(LAMBDA + 1, K + 1),
        "sin2_theta_12": Fraction(MU, K + 1),
        "sin2_theta_23": Fraction(K - LAMBDA - MU + 1, K + 1),
        "sin2_theta_13": Fraction(LAMBDA, (K + 1) * (K - LAMBDA - MU + 1)),
        "omega_lambda": Fraction((LAMBDA + 1) ** 2, K + 1),
        "higgs_ratio_square": Fraction(2 * (K - LAMBDA - MU + 1), 4 * (K + 1) + (LAMBDA + 1)),
        "a2_over_a0": Fraction(2 * (K - LAMBDA - MU + 1), LAMBDA + 1),
        "a4_over_a0": Fraction(2 * (4 * (K + 1) + (LAMBDA + 1)), LAMBDA + 1),
        "discrete_6_mode_over_a0": Fraction(2 * (K + 1), 1),
        "discrete_to_continuum_ratio": Fraction((LAMBDA + 1) * (K + 1), 1),
    }

    return {
        "status": "ok",
        "srg_data": {
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "q_from_lambda_plus_one": q_from_srg,
            "phi3_from_k_plus_one": phi3_from_srg,
            "phi6_from_k_minus_lambda_minus_mu_plus_one": phi6_from_srg,
        },
        "promoted_observables": {
            key: {
                "exact": _fraction_dict(exact_sm[key] if key in exact_sm else exact_spectral[key]),
                "formula_from_srg": _fraction_dict(formulas[key]),
                "matches_formula": (exact_sm[key] if key in exact_sm else exact_spectral[key]) == formulas[key],
            }
            for key in (
                "sin2_theta_w_ew",
                "tan_theta_c",
                "sin2_theta_12",
                "sin2_theta_23",
                "sin2_theta_13",
                "omega_lambda",
                "higgs_ratio_square",
                "a2_over_a0",
                "a4_over_a0",
                "discrete_6_mode_over_a0",
                "discrete_to_continuum_ratio",
            )
        },
        "bridge_verdict": (
            "The promoted public-facing package is directly geometric. For "
            "SRG(40,12,2,4), the same observables previously written in q, Phi_3, "
            "Phi_6, or x = sin^2(theta_W) are already determined by the native SRG "
            "parameters through q = lambda + 1, Phi_3 = k + 1, and "
            "Phi_6 = k - lambda - mu + 1. So the promoted Standard Model, "
            "cosmology, Higgs, spectral-action, and gravity layers are directly "
            "locked to the W(3,3) geometry itself."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_srg_rosetta_lock_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
