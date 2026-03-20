"""Natural-units electroweak split bridge for the promoted W33 package.

The live stack already contains two exact natural-units statements:

    (lambda + Phi_6) / q^2 = 1

from the torus/Fano vacuum packet, and

    1/e^2 = 1/g^2 + 1/g'^2

from the electroweak action in Heaviside-Lorentz units.

This module closes them together with the exact Lovasz-theta selector:

    Theta(W33) = 10,
    Phi_3      = q + Theta(W33) = 13.

So the electroweak unit split is itself an exact normalized complement law:

    1 = q/Phi_3 + Theta(W33)/Phi_3
      = sin^2(theta_W) + cos^2(theta_W).

Equivalently,

    (4 pi alpha)/g^2   = q/Phi_3,
    (4 pi alpha)/g'^2  = Theta(W33)/Phi_3,
    (4 pi alpha)/g_Z^2 = q Theta(W33) / Phi_3^2.

The physical meaning is that, in natural units, the electric coupling is the
harmonic sum of a projective ``q`` channel and a capacity/topological
``Theta(W33)`` channel, while the deeper vacuum unit remains the local shell
normalization ``(lambda + Phi_6)/q^2 = 1``.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_electroweak_lagrangian_bridge import build_electroweak_lagrangian_summary
from w33_natural_units_topological_bridge import build_natural_units_topological_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_theta_hierarchy_bridge import build_theta_hierarchy_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_electroweak_split_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_electroweak_split_summary() -> dict[str, Any]:
    natural_topology = build_natural_units_topological_summary()
    electroweak = build_electroweak_lagrangian_summary()
    theta = build_theta_hierarchy_summary()
    standard_model = build_standard_model_cyclotomic_summary()

    q = Fraction(natural_topology["local_shell_dictionary"]["q"])
    lam = Fraction(natural_topology["local_shell_dictionary"]["lambda"])
    phi6 = Fraction(natural_topology["local_shell_dictionary"]["phi6"])
    q_squared = Fraction(natural_topology["local_shell_dictionary"]["q_squared"])
    theta_w33 = Fraction(theta["theta_dictionary"]["lovasz_theta"])
    phi3 = Fraction(standard_model["cyclotomic_data"]["phi3"])

    sin2 = Fraction(standard_model["promoted_observables"]["sin2_theta_w_ew"]["exact"])
    cos2 = Fraction(electroweak["graph_inputs"]["cos2_theta_w"]["exact"])
    g_sq_over_4pi_alpha = Fraction(
        electroweak["dimensionless_lagrangian_dictionary"]["g_squared_over_4pi_alpha"]["exact"]
    )
    gp_sq_over_4pi_alpha = Fraction(
        electroweak["dimensionless_lagrangian_dictionary"]["gprime_squared_over_4pi_alpha"]["exact"]
    )
    gz_sq_over_4pi_alpha = Fraction(
        electroweak["dimensionless_lagrangian_dictionary"]["gz_squared_over_4pi_alpha"]["exact"]
    )

    reciprocal_g = Fraction(1, 1) / g_sq_over_4pi_alpha
    reciprocal_gp = Fraction(1, 1) / gp_sq_over_4pi_alpha
    reciprocal_gz = Fraction(1, 1) / gz_sq_over_4pi_alpha

    return {
        "status": "ok",
        "nested_complement_dictionary": {
            "q": int(q),
            "lambda": int(lam),
            "phi6": int(phi6),
            "q_squared": int(q_squared),
            "theta_w33": int(theta_w33),
            "phi3": int(phi3),
            "local_unit_formula": "(lambda + Phi_6) / q^2 = 1",
            "electroweak_unit_formula": "1 = q/Phi_3 + Theta(W33)/Phi_3",
            "local_unit_value": _fraction_dict((lam + phi6) / q_squared),
            "electroweak_unit_value": _fraction_dict((q + theta_w33) / phi3),
        },
        "electroweak_split_dictionary": {
            "weinberg_formula": "sin^2(theta_W) = q / Phi_3",
            "cosine_formula": "cos^2(theta_W) = Theta(W33) / Phi_3",
            "electric_reciprocal_formula": "(4 pi alpha) / e^2 = 1",
            "weak_reciprocal_formula": "(4 pi alpha) / g^2 = q / Phi_3",
            "hypercharge_reciprocal_formula": "(4 pi alpha) / g'^2 = Theta(W33) / Phi_3",
            "neutral_reciprocal_formula": "(4 pi alpha) / g_Z^2 = q Theta(W33) / Phi_3^2",
            "sin2_theta_w": _fraction_dict(sin2),
            "cos2_theta_w": _fraction_dict(cos2),
            "q_over_phi3": _fraction_dict(q / phi3),
            "theta_over_phi3": _fraction_dict(theta_w33 / phi3),
            "reciprocal_g": _fraction_dict(reciprocal_g),
            "reciprocal_gprime": _fraction_dict(reciprocal_gp),
            "reciprocal_gz": _fraction_dict(reciprocal_gz),
            "tan2_theta_w": _fraction_dict(sin2 / cos2),
            "theta_over_q": _fraction_dict(theta_w33 / q),
        },
        "exact_factorizations": {
            "lambda_plus_phi6_equals_q_squared": lam + phi6 == q_squared,
            "theta_equals_q_plus_phi6": theta_w33 == q + phi6,
            "q_plus_theta_equals_phi3": q + theta_w33 == phi3,
            "phi3_equals_2q_plus_phi6": phi3 == 2 * q + phi6,
            "weinberg_equals_q_over_phi3": sin2 == q / phi3,
            "cosine_equals_theta_over_phi3": cos2 == theta_w33 / phi3,
            "sin2_plus_cos2_equals_unity": sin2 + cos2 == 1,
            "weak_reciprocal_matches_weinberg": reciprocal_g == sin2,
            "hypercharge_reciprocal_matches_cosine": reciprocal_gp == cos2,
            "electric_reciprocal_harmonic_sum_closes": reciprocal_g + reciprocal_gp == 1,
            "g_squared_over_gprime_squared_equals_theta_over_q": (
                g_sq_over_4pi_alpha / gp_sq_over_4pi_alpha == theta_w33 / q
            ),
            "neutral_reciprocal_equals_q_theta_over_phi3_squared": (
                reciprocal_gz == q * theta_w33 / (phi3 * phi3)
            ),
            "local_and_electroweak_are_nested_unit_laws": (
                (lam + phi6) / q_squared == 1 and (q + theta_w33) / phi3 == 1
            ),
        },
        "bridge_verdict": (
            "The natural-units story now has a nested complement structure. "
            "Locally, the torus/Fano packet gives the vacuum unit law "
            "(lambda + Phi_6)/q^2 = 1, i.e. (2 + 7)/9 = 1. On the electroweak "
            "side, the reciprocal gauge couplings give a second exact unit law "
            "1 = q/Phi_3 + Theta(W33)/Phi_3, i.e. 1 = 3/13 + 10/13. So "
            "sin^2(theta_W) is the normalized projective share of the same unit "
            "package, while cos^2(theta_W) is the normalized capacity/topological "
            "share. In natural units, the electric coupling is therefore the "
            "harmonic merge of a projective q-channel and a Lovasz-theta channel, "
            "with the deeper vacuum normalization already fixed geometrically by "
            "the torus/Fano complement law."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_electroweak_split_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
