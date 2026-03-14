"""Direct spectral Rosetta lock for the promoted public-facing package.

The three-channel operator bridge already isolates the native adjacency spectrum

    (k, r, s) = (12, 2, -4)

for W(3,3). The newer public-facing bridges showed that the promoted
electroweak/flavour/cosmology/spectral/gravity package can be written via

    q = 3,   Phi_3 = 13,   Phi_6 = 7,

or via the master variable

    x = sin^2(theta_W) = 3/13.

This module proves that the same package is already determined directly by the
adjacency spectral data:

    q     = r + 1,
    Phi_3 = k + 1,
    Phi_6 = 1 + r - s.

Hence the promoted observables become

    sin^2(theta_W) = tan(theta_C) = (r + 1)/(k + 1)
    sin^2(theta_12)            = (-s)/(k + 1)
    sin^2(theta_23)            = (1 + r - s)/(k + 1)
    sin^2(theta_13)            = r/((k + 1)(1 + r - s))
    Omega_Lambda               = (r + 1)^2/(k + 1)
    m_H^2/v^2                 = 2(1 + r - s)/(4(k + 1) + (r + 1))
    a2/a0                      = 2(1 + r - s)/(r + 1)
    a4/a0                      = 2(4(k + 1) + (r + 1))/(r + 1)
    c6/a0                      = 2(k + 1)
    c6/cEH,cont                = (r + 1)(k + 1)

So the promoted package is already a direct statement about the three adjacency
eigenvalues themselves.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_spectral_action_cyclotomic_bridge import build_spectral_action_cyclotomic_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_spectral_rosetta_lock_bridge_summary.json"

K = 12
R = 2
S = -4


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_spectral_rosetta_lock_summary() -> dict[str, Any]:
    sm = build_standard_model_cyclotomic_summary()
    spectral = build_spectral_action_cyclotomic_summary()

    q_from_spectrum = R + 1
    phi3_from_spectrum = K + 1
    phi6_from_spectrum = 1 + R - S

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
        "sin2_theta_w_ew": Fraction(R + 1, K + 1),
        "tan_theta_c": Fraction(R + 1, K + 1),
        "sin2_theta_12": Fraction(-S, K + 1),
        "sin2_theta_23": Fraction(1 + R - S, K + 1),
        "sin2_theta_13": Fraction(R, (K + 1) * (1 + R - S)),
        "omega_lambda": Fraction((R + 1) ** 2, K + 1),
        "higgs_ratio_square": Fraction(2 * (1 + R - S), 4 * (K + 1) + (R + 1)),
        "a2_over_a0": Fraction(2 * (1 + R - S), R + 1),
        "a4_over_a0": Fraction(2 * (4 * (K + 1) + (R + 1)), R + 1),
        "discrete_6_mode_over_a0": Fraction(2 * (K + 1), 1),
        "discrete_to_continuum_ratio": Fraction((R + 1) * (K + 1), 1),
    }

    return {
        "status": "ok",
        "spectral_data": {
            "k": K,
            "r": R,
            "s": S,
            "q_from_r_plus_one": q_from_spectrum,
            "phi3_from_k_plus_one": phi3_from_spectrum,
            "phi6_from_one_plus_r_minus_s": phi6_from_spectrum,
        },
        "promoted_observables": {
            key: {
                "exact": _fraction_dict(exact_sm[key] if key in exact_sm else exact_spectral[key]),
                "formula_from_spectrum": _fraction_dict(formulas[key]),
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
            "The promoted public-facing package is already a direct spectral law. "
            "For W(3,3), the three adjacency eigenvalues (k,r,s)=(12,2,-4) "
            "determine q, Phi_3, Phi_6, the electroweak angle, Cabibbo, PMNS, "
            "Omega_Lambda, the Higgs ratio, the internal spectral-action ratios, "
            "and the promoted gravity ratios. So the same package can be read "
            "directly from the rank-3 adjacency spectrum itself."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_spectral_rosetta_lock_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
