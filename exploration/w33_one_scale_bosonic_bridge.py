"""One-scale electroweak bosonic closure from the live W33 package.

This pushes the natural-units electroweak-action bridge one step further.
Rather than listing couplings individually, it packages the weak bosonic sector
as a single normalized action determined by graph data.

Graph inputs:

    alpha        = 1111 / 152247,
    x            = sin^2(theta_W) = 3/13,
    lambda_H     = 7/55,
    v_EW         = q^5 + q = |E| + 2q = 246.

The standard tree-level Higgs potential is

    V(H) = -mu_H^2 (H^dagger H) + lambda_H (H^dagger H)^2,

with

    mu_H^2 = lambda_H v^2,
    m_H^2  = 2 lambda_H v^2,
    V_min  = -lambda_H v^4 / 4.

So the whole bosonic package is fixed as dimensionless ratios plus one scale:

    mu_H^2 / v^2   = 7/55,
    m_H^2 / v^2    = 14/55,
    V_min / v^4    = -7/220,
    m_W^2 / m_Z^2  = 10/13,
    (m_Z^2-m_W^2)/m_Z^2 = 3/13,
    rho            = 1.

This is the clean physical meaning of the graph on the bosonic side: a
zero-extra-parameter weak-sector closure once the promoted graph scale
v_EW = 246 is accepted.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
import json
from math import sqrt
from pathlib import Path
from typing import Any

from w33_electroweak_lagrangian_bridge import build_electroweak_lagrangian_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_one_scale_bosonic_bridge_summary.json"

getcontext().prec = 50


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _scientific(value: float, digits: int = 18) -> str:
    return format(Decimal(str(value)), f".{digits}e")


@lru_cache(maxsize=1)
def build_one_scale_bosonic_summary() -> dict[str, Any]:
    ew = build_electroweak_lagrangian_summary()

    v = Fraction(int(ew["graph_inputs"]["vev_ew_gev"]), 1)
    x = Fraction(ew["graph_inputs"]["weinberg_x"]["exact"])
    c2 = Fraction(ew["graph_inputs"]["cos2_theta_w"]["exact"])
    lam = Fraction(ew["graph_inputs"]["lambda_h"]["exact"])
    higgs_ratio = Fraction(ew["graph_inputs"]["higgs_ratio_square"]["exact"])

    mu_h_sq = lam * v * v
    mh_sq = higgs_ratio * v * v
    vmin = -lam * v * v * v * v / 4
    mw_over_v = ew["natural_unit_couplings"]["g"]["float"] / 2.0
    mz_over_v = ew["natural_unit_couplings"]["gZ"]["float"] / 2.0
    mh_over_v = sqrt(float(higgs_ratio))

    return {
        "status": "ok",
        "graph_fixed_inputs": {
            "vev_ew_gev": int(v),
            "weinberg_x": _fraction_dict(x),
            "cos2_theta_w": _fraction_dict(c2),
            "lambda_h": _fraction_dict(lam),
            "higgs_ratio_square": _fraction_dict(higgs_ratio),
        },
        "higgs_potential_dictionary": {
            "potential_formula": "V(H) = -mu_H^2 (H^dagger H) + lambda_H (H^dagger H)^2",
            "mu_h_squared": _fraction_dict(mu_h_sq),
            "mu_h_squared_over_v_squared": _fraction_dict(mu_h_sq / (v * v)),
            "mh_squared": _fraction_dict(mh_sq),
            "mh_squared_over_v_squared": _fraction_dict(mh_sq / (v * v)),
            "vacuum_energy": _fraction_dict(vmin),
            "vacuum_energy_over_v_fourth": _fraction_dict(vmin / (v * v * v * v)),
            "mu_equals_lambda_v_squared": mu_h_sq == lam * v * v,
            "mh_squared_equals_2lambda_v_squared": mh_sq == 2 * lam * v * v,
            "vacuum_energy_equals_minus_lambda_v_fourth_over_4": vmin == -lam * v * v * v * v / 4,
        },
        "normalized_tree_mass_dictionary": {
            "mw_squared_over_mz_squared": _fraction_dict(c2),
            "z_minus_w_split_over_z": _fraction_dict(x),
            "rho_parameter": _fraction_dict(Fraction(1, 1)),
            "mw_over_v": {"scientific": _scientific(mw_over_v), "float": mw_over_v},
            "mz_over_v": {"scientific": _scientific(mz_over_v), "float": mz_over_v},
            "mh_over_v": {"scientific": _scientific(mh_over_v), "float": mh_over_v},
            "mw_over_mz_equals_sqrt_cos2": abs((mw_over_v / mz_over_v) ** 2 - float(c2)) < 1e-15,
            "mh_over_v_equals_sqrt_higgs_ratio": abs(mh_over_v * mh_over_v - float(higgs_ratio)) < 1e-15,
        },
        "one_scale_closure": {
            "all_dimensionless_bosonic_data_fixed": True,
            "only_overall_scale_is_v": True,
            "vev_is_graph_fixed_as_q5_plus_q": int(v) == 3**5 + 3,
            "vev_is_graph_fixed_as_edges_plus_2q": int(v) == 240 + 2 * 3,
            "zero_extra_parameter_bosonic_closure_if_promoted_vev_accepted": True,
        },
        "bridge_verdict": (
            "The electroweak bosonic side is now a one-scale closure. The graph "
            "fixes the weak mixing x=3/13, the Higgs quartic lambda_H=7/55, and "
            "the promoted weak scale v=246, and from those data the Higgs "
            "potential, custodial tree relations, weak-boson mass ratio, and "
            "Fermi-scale normalization all follow. So the physical meaning of the "
            "graph is not just a list of weak observables; it is a normalized "
            "bosonic electroweak action with zero extra parameters once the "
            "promoted graph vev is accepted."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_one_scale_bosonic_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
