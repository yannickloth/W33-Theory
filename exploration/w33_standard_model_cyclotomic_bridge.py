"""Cyclotomic Rosetta layer for the promoted Standard Model observables.

The public-facing theory already contains several exact q=3 formulas:

    sin^2(theta_W)      = q / Phi_3(q)            = 3/13
    tan(theta_C)        = q / Phi_3(q)            = 3/13
    sin^2(theta_12)     = (q + 1) / Phi_3(q)      = 4/13
    sin^2(theta_23)     = Phi_6(q) / Phi_3(q)     = 7/13
    sin^2(theta_13)     = (q - 1)/(Phi_3 Phi_6)   = 2/91
    m_H^2 / v^2         = 2 Phi_6(q)/(4Phi_3(q)+q)= 14/55
    Omega_Lambda        = q^2 / Phi_3(q)          = 9/13

This module packages them as one exact Standard Model/cosmology Rosetta object.
The important structural relations are:

    tan(theta_C) = sin^2(theta_W),
    sin^2(theta_23) = sin^2(theta_W) + sin^2(theta_12),
    Omega_Lambda = q * sin^2(theta_W).

So the electroweak, flavour, Higgs, and cosmology formulas are not isolated
fractions; they are a single cyclotomic package built from q, Phi_3, and Phi_6.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_standard_model_cyclotomic_bridge_summary.json"

Q = 3
PHI3 = Q * Q + Q + 1
PHI6 = Q * Q - Q + 1


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_standard_model_cyclotomic_summary() -> dict[str, Any]:
    sin2_theta_w = Fraction(Q, PHI3)
    tan_theta_c = Fraction(Q, PHI3)
    sin2_theta_12 = Fraction(Q + 1, PHI3)
    sin2_theta_23 = Fraction(PHI6, PHI3)
    sin2_theta_13 = Fraction(Q - 1, PHI3 * PHI6)
    higgs_ratio_square = Fraction(2 * PHI6, 4 * PHI3 + Q)
    omega_lambda = Fraction(Q * Q, PHI3)

    return {
        "status": "ok",
        "cyclotomic_data": {
            "q": Q,
            "phi3": PHI3,
            "phi6": PHI6,
            "four_phi3_plus_q": 4 * PHI3 + Q,
        },
        "promoted_observables": {
            "sin2_theta_w_ew": _fraction_dict(sin2_theta_w),
            "tan_theta_c": _fraction_dict(tan_theta_c),
            "sin2_theta_12": _fraction_dict(sin2_theta_12),
            "sin2_theta_23": _fraction_dict(sin2_theta_23),
            "sin2_theta_13": _fraction_dict(sin2_theta_13),
            "higgs_ratio_square": _fraction_dict(higgs_ratio_square),
            "omega_lambda": _fraction_dict(omega_lambda),
        },
        "closure_relations": {
            "tan_cabibbo_equals_ew_weinberg": tan_theta_c == sin2_theta_w,
            "pmns_23_equals_weinberg_plus_pmns_12": sin2_theta_23 == sin2_theta_w + sin2_theta_12,
            "omega_lambda_equals_q_times_weinberg": omega_lambda == Fraction(Q) * sin2_theta_w,
            "reactor_has_phi3_phi6_denominator": sin2_theta_13.denominator == PHI3 * PHI6,
            "higgs_uses_four_phi3_plus_q_denominator": higgs_ratio_square.denominator == 4 * PHI3 + Q,
        },
        "bridge_verdict": (
            "The promoted Standard Model layer is one exact q=3 cyclotomic object. "
            "The electroweak angle, Cabibbo angle, PMNS angles, Higgs ratio, and "
            "Omega_Lambda are all built from the same Phi_3=13 and Phi_6=7 data, "
            "with exact closure relations tan(theta_C)=sin^2(theta_W), "
            "sin^2(theta_23)=sin^2(theta_W)+sin^2(theta_12), and "
            "Omega_Lambda=q sin^2(theta_W)."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_standard_model_cyclotomic_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
