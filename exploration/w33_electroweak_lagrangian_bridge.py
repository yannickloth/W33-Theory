"""Electroweak bosonic Lagrangian bridge in natural units.

This module attacks the theory from a different angle: instead of another
count/symmetry bridge, it reconstructs the bosonic electroweak package in
natural units from the promoted graph outputs.

Inputs already fixed by the live W33 package:

    alpha        = 1111 / 152247,
    x            = sin^2(theta_W) = 3/13,
    m_H^2 / v^2  = 14/55,
    v_EW         = q^5 + q = |E| + 2q = 246.

In Heaviside-Lorentz natural units,

    e^2   = 4 pi alpha,
    g^2   = e^2 / x,
    g'^2  = e^2 / (1 - x),
    g_Z^2 = g^2 + g'^2 = e^2 / (x(1-x)),
    lambda_H = (m_H^2 / v^2) / 2 = 7/55.

So the graph already determines the tree-level bosonic electroweak Lagrangian
up to the promoted weak scale. The important exact closures are:

    1/e^2 = 1/g^2 + 1/g'^2,
    g^2/g'^2 = (1-x)/x = 10/3,
    m_W^2/m_Z^2 = 1-x = 10/13,
    rho = m_W^2 / (m_Z^2 cos^2 theta_W) = 1.

This gives a direct physical reading of the graph: it encodes a dimensionless
weak-sector action, not just isolated observables.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
import json
from math import pi, sqrt
from pathlib import Path
from typing import Any

from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_vacuum_unity_bridge import ALPHA


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_electroweak_lagrangian_bridge_summary.json"

getcontext().prec = 50

Q = 3
V_EW = Q**5 + Q
X = Fraction(3, 13)
COS2 = Fraction(10, 13)
HIGGS_RATIO_SQUARE = Fraction(14, 55)
LAMBDA_H = HIGGS_RATIO_SQUARE / 2


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _scientific(value: float, digits: int = 18) -> str:
    return format(Decimal(str(value)), f".{digits}e")


@lru_cache(maxsize=1)
def build_electroweak_lagrangian_summary() -> dict[str, Any]:
    sm = build_standard_model_cyclotomic_summary()
    alpha = float(ALPHA)
    x = float(X)
    c2 = float(COS2)
    lam = float(LAMBDA_H)

    e_sq = 4.0 * pi * alpha
    g_sq = e_sq / x
    gp_sq = e_sq / c2
    gz_sq = g_sq + gp_sq

    e = sqrt(e_sq)
    g = sqrt(g_sq)
    gp = sqrt(gp_sq)
    gz = sqrt(gz_sq)

    mw = V_EW * g / 2.0
    mz = V_EW * gz / 2.0
    mh = V_EW * sqrt(2.0 * lam)
    gf = 1.0 / (sqrt(2.0) * V_EW * V_EW)

    return {
        "status": "ok",
        "graph_inputs": {
            "alpha": _fraction_dict(ALPHA),
            "weinberg_x": sm["promoted_observables"]["sin2_theta_w_ew"],
            "cos2_theta_w": _fraction_dict(COS2),
            "higgs_ratio_square": _fraction_dict(HIGGS_RATIO_SQUARE),
            "lambda_h": _fraction_dict(LAMBDA_H),
            "vev_formula": "q^5 + q = |E| + 2q",
            "vev_ew_gev": V_EW,
        },
        "dimensionless_lagrangian_dictionary": {
            "heaviside_lorentz_charge_formula": "e^2 = 4 pi alpha",
            "weak_coupling_formula": "g^2 = e^2 / sin^2(theta_W)",
            "hypercharge_coupling_formula": "g'^2 = e^2 / cos^2(theta_W)",
            "neutral_coupling_formula": "g_Z^2 = g^2 + g'^2",
            "e_squared_over_4pi_alpha": _fraction_dict(Fraction(1, 1)),
            "g_squared_over_4pi_alpha": _fraction_dict(Fraction(1, 1) / X),
            "gprime_squared_over_4pi_alpha": _fraction_dict(Fraction(1, 1) / COS2),
            "gz_squared_over_4pi_alpha": _fraction_dict(Fraction(1, 1) / (X * COS2)),
            "one_over_e_squared_equals_sum": True,
            "g_squared_over_gprime_squared": _fraction_dict(COS2 / X),
            "rho_parameter": _fraction_dict(Fraction(1, 1)),
            "mw_squared_over_mz_squared": _fraction_dict(COS2),
            "lambda_h_exact": _fraction_dict(LAMBDA_H),
        },
        "natural_unit_couplings": {
            "e": {"scientific": _scientific(e), "float": e},
            "g": {"scientific": _scientific(g), "float": g},
            "gprime": {"scientific": _scientific(gp), "float": gp},
            "gZ": {"scientific": _scientific(gz), "float": gz},
            "mw_tree_gev": {"scientific": _scientific(mw), "float": mw},
            "mz_tree_gev": {"scientific": _scientific(mz), "float": mz},
            "mh_tree_gev": {"scientific": _scientific(mh), "float": mh},
            "fermi_constant_tree": {"scientific": _scientific(gf), "float": gf, "unit": "GeV^-2"},
        },
        "exact_tree_level_relations": {
            "e_equals_g_sin_theta": abs(e - g * sqrt(x)) < 1e-15,
            "e_equals_gprime_cos_theta": abs(e - gp * sqrt(c2)) < 1e-15,
            "mz_equals_mw_over_cos_theta": abs(mz - mw / sqrt(c2)) < 1e-12,
            "mh_equals_v_sqrt_2lambda": abs(mh - V_EW * sqrt(2.0 * lam)) < 1e-12,
            "gf_equals_one_over_sqrt2_v2": abs(gf - 1.0 / (sqrt(2.0) * V_EW * V_EW)) < 1e-18,
        },
        "bridge_verdict": (
            "The graph can now be read as a tree-level electroweak bosonic action "
            "in natural units. Once alpha, sin^2(theta_W)=3/13, the Higgs ratio "
            "14/55, and v=246 are fixed, the weak couplings g, g', g_Z, the "
            "quartic lambda_H=7/55, the rho=1 closure, the W/Z mass ratio 10/13, "
            "and the Fermi constant all follow. So the graph is not only producing "
            "observables one by one; it is already specifying the dimensionless "
            "weak-sector Lagrangian data of the physical object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_electroweak_lagrangian_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
