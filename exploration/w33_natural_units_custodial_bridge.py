"""Natural-units custodial weak-mass bridge for the promoted W33 package.

The natural-units denominator batch already reconstructs the exact weak
denominator

    Phi_3 = 13

in two ways:

    Phi_3 = 6 + Phi_6,
    Phi_3 = 1 + q + R_K G_0 + Phi_6.

This module promotes the next exact physical consequence: the same denominator
is already the custodial weak-mass split.

Using the promoted bosonic action package,

    m_W^2 / m_Z^2 = cos^2(theta_W),
    (m_Z^2 - m_W^2) / m_Z^2 = sin^2(theta_W),
    rho = 1.

The new point is that the same ratios are already the normalized shell shares
of the natural-units denominator:

    cos^2(theta_W) = Theta(W33) / Phi_3
                   = (1 + R_K G_0 + Phi_6) / (1 + q + R_K G_0 + Phi_6)
                   = 10/13,

    sin^2(theta_W) = q / Phi_3
                   = q / (1 + q + R_K G_0 + Phi_6)
                   = 3/13.

So the tree-level custodial weak-mass split is already a natural-units shell
identity, not an additional input.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_electroweak_lagrangian_bridge import build_electroweak_lagrangian_summary
from w33_natural_units_projective_denominator_bridge import (
    build_natural_units_projective_denominator_summary,
)
from w33_one_scale_bosonic_bridge import build_one_scale_bosonic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_custodial_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_custodial_summary() -> dict[str, Any]:
    projective = build_natural_units_projective_denominator_summary()
    ew = build_electroweak_lagrangian_summary()
    one_scale = build_one_scale_bosonic_summary()

    q = Fraction(projective["metrology_shell_dictionary"]["q"])
    phi6 = Fraction(projective["metrology_shell_dictionary"]["phi6"])
    rk_times_g0 = Fraction(projective["metrology_shell_dictionary"]["rk_times_g0"]["exact"])
    selector_line = Fraction(projective["metrology_shell_dictionary"]["selector_line"])
    phi3 = Fraction(projective["projective_denominator_dictionary"]["phi3"])
    theta_w33 = Fraction(projective["projective_denominator_dictionary"]["theta_w33"])

    sin2 = Fraction(ew["graph_inputs"]["weinberg_x"]["exact"])
    cos2 = Fraction(ew["graph_inputs"]["cos2_theta_w"]["exact"])
    mw_over_mz_sq = Fraction(one_scale["normalized_tree_mass_dictionary"]["mw_squared_over_mz_squared"]["exact"])
    z_gap_over_z = Fraction(one_scale["normalized_tree_mass_dictionary"]["z_minus_w_split_over_z"]["exact"])
    rho = Fraction(one_scale["normalized_tree_mass_dictionary"]["rho_parameter"]["exact"])

    denominator = selector_line + q + rk_times_g0 + phi6
    custodial_numerator = selector_line + rk_times_g0 + phi6

    return {
        "status": "ok",
        "custodial_shell_dictionary": {
            "phi3": int(phi3),
            "theta_w33": int(theta_w33),
            "selector_line": int(selector_line),
            "q": int(q),
            "rk_times_g0": _fraction_dict(rk_times_g0),
            "phi6": int(phi6),
            "custodial_numerator_formula": "Theta(W33) = 1 + R_K G_0 + Phi_6",
            "denominator_formula": "Phi_3 = 1 + q + R_K G_0 + Phi_6",
            "mass_ratio_formula": "m_W^2 / m_Z^2 = Theta(W33) / Phi_3",
            "gap_formula": "(m_Z^2 - m_W^2) / m_Z^2 = q / Phi_3",
        },
        "weak_mass_dictionary": {
            "mw_squared_over_mz_squared": _fraction_dict(mw_over_mz_sq),
            "z_gap_over_z_squared": _fraction_dict(z_gap_over_z),
            "sin2_theta_w": _fraction_dict(sin2),
            "cos2_theta_w": _fraction_dict(cos2),
            "theta_over_phi3": _fraction_dict(custodial_numerator / denominator),
            "q_over_phi3": _fraction_dict(q / denominator),
            "rho_parameter": _fraction_dict(rho),
        },
        "exact_factorizations": {
            "theta_equals_selector_plus_metrology_plus_qcd": theta_w33 == custodial_numerator,
            "phi3_equals_selector_plus_projective_plus_metrology_plus_qcd": phi3 == denominator,
            "mw_over_mz_squared_equals_cos2_theta_w": mw_over_mz_sq == cos2,
            "z_gap_over_z_squared_equals_sin2_theta_w": z_gap_over_z == sin2,
            "cos2_equals_theta_over_phi3": cos2 == custodial_numerator / denominator,
            "sin2_equals_q_over_phi3": sin2 == q / denominator,
            "custodial_split_sums_to_unity": mw_over_mz_sq + z_gap_over_z == 1,
            "rho_equals_one": rho == 1,
        },
        "bridge_verdict": (
            "The natural-units denominator split already lifts exactly to the "
            "custodial weak-mass split. The same shell data that gives "
            "Phi_3 = 1 + q + R_K G_0 + Phi_6 also gives "
            "Theta(W33) = 1 + R_K G_0 + Phi_6, so "
            "m_W^2/m_Z^2 = Theta(W33)/Phi_3 = 10/13 and "
            "(m_Z^2 - m_W^2)/m_Z^2 = q/Phi_3 = 3/13. Thus the tree-level "
            "custodial relation rho = 1 is already encoded as the normalized "
            "natural-units shell split of the weak denominator."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_custodial_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
