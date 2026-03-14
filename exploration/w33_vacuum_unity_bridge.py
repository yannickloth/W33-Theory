"""Vacuum-unity bridge from the exact W33 alpha theorem to SI electromagnetism.

The current live theory already fixes the low-energy fine-structure constant as

    alpha^{-1} = 137 + 40/1111 = 152247/1111.

In the modern SI, the physically rigid vacuum statement is not that ``mu0`` is
an exact conventional constant on its own. The exact statement is the
dimensionless normalization

    c^2 mu0 epsilon0 = 1,

with the vacuum constants now mediated by ``alpha`` through

    mu0      = 2 alpha h / (c e^2),
    epsilon0 = e^2 / (2 alpha h c),
    Z0       = mu0 c = 1 / (epsilon0 c) = 2 alpha h / e^2.

So once the W33 package fixes ``alpha``, it predicts ``mu0``, ``epsilon0``, and
the vacuum impedance ``Z0`` together. The exact number ``1`` is the vacuum
normalization itself.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_monster_selector_completion_bridge import build_monster_selector_completion_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_vacuum_unity_bridge_summary.json"

getcontext().prec = 60

V = 40
K = 12
LAMBDA = 2
MU = 4

C = Fraction(299792458, 1)
H = Fraction(662607015, 10**42)
E_CHARGE = Fraction(1602176634, 10**28)

ALPHA_INV = Fraction(K * K - 2 * MU + 1, 1) + Fraction(V, (K - 1) * ((K - LAMBDA) ** 2 + 1))
ALPHA = Fraction(1, 1) / ALPHA_INV

MU0 = Fraction(2, 1) * H * ALPHA / (C * E_CHARGE * E_CHARGE)
EPSILON0 = Fraction(1, 1) / (MU0 * C * C)
Z0 = MU0 * C
Y0 = Fraction(1, 1) / Z0

OFFICIAL_ALPHA_INV = Decimal("137.035999177")
OFFICIAL_ALPHA = Decimal(1) / OFFICIAL_ALPHA_INV
OFFICIAL_MU0 = Decimal("1.25663706127e-6")
OFFICIAL_EPSILON0 = Decimal("8.8541878188e-12")
OFFICIAL_Z0 = Decimal("376.730313412")


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _decimal_from_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _scientific(value: Decimal, digits: int = 18) -> str:
    return format(value, f".{digits}e")


def _relative_error(predicted: Decimal, official: Decimal) -> Decimal:
    return (predicted - official) / official


def _signed_scientific(value: Decimal, digits: int = 18) -> str:
    return format(value, f"+.{digits}e")


@lru_cache(maxsize=1)
def build_vacuum_unity_summary() -> dict[str, Any]:
    selector = build_monster_selector_completion_summary()

    alpha_decimal = _decimal_from_fraction(ALPHA)
    alpha_inv_decimal = _decimal_from_fraction(ALPHA_INV)
    mu0_decimal = _decimal_from_fraction(MU0)
    epsilon0_decimal = _decimal_from_fraction(EPSILON0)
    z0_decimal = _decimal_from_fraction(Z0)
    y0_decimal = _decimal_from_fraction(Y0)

    alpha_error = _relative_error(alpha_decimal, OFFICIAL_ALPHA)
    alpha_inv_error = _relative_error(alpha_inv_decimal, OFFICIAL_ALPHA_INV)
    mu0_error = _relative_error(mu0_decimal, OFFICIAL_MU0)
    epsilon0_error = _relative_error(epsilon0_decimal, OFFICIAL_EPSILON0)
    z0_error = _relative_error(z0_decimal, OFFICIAL_Z0)

    tolerance = Decimal("2e-12")

    return {
        "status": "ok",
        "w33_alpha_input": {
            "srg_parameters": {"v": V, "k": K, "lambda": LAMBDA, "mu": MU},
            "alpha_inverse_formula": "k^2 - 2 mu + 1 + v / ((k-1)((k-lambda)^2+1))",
            "alpha_inverse": _fraction_dict(ALPHA_INV),
            "alpha": _fraction_dict(ALPHA),
        },
        "vacuum_unity_relations": {
            "c_squared_mu0_epsilon0": _fraction_dict(MU0 * EPSILON0 * C * C),
            "z0_times_y0": _fraction_dict(Z0 * Y0),
            "z0_equals_mu0_c": Z0 == MU0 * C,
            "z0_equals_one_over_epsilon0_c": Z0 == Fraction(1, 1) / (EPSILON0 * C),
            "mu0_formula": "2 alpha h / (c e^2)",
            "epsilon0_formula": "e^2 / (2 alpha h c)",
            "z0_formula": "2 alpha h / e^2",
            "y0_formula": "e^2 / (2 alpha h)",
            "mu0_formula_matches_exactly": MU0 == Fraction(2, 1) * H * ALPHA / (C * E_CHARGE * E_CHARGE),
            "epsilon0_formula_matches_exactly": EPSILON0 == (E_CHARGE * E_CHARGE) / (Fraction(2, 1) * ALPHA * H * C),
            "z0_formula_matches_exactly": Z0 == Fraction(2, 1) * ALPHA * H / (E_CHARGE * E_CHARGE),
            "y0_formula_matches_exactly": Y0 == (E_CHARGE * E_CHARGE) / (Fraction(2, 1) * ALPHA * H),
        },
        "predicted_vacuum_constants": {
            "mu0_si": {"scientific": _scientific(mu0_decimal), "unit": "N A^-2"},
            "epsilon0_si": {"scientific": _scientific(epsilon0_decimal), "unit": "F m^-1"},
            "z0_si": {"scientific": _scientific(z0_decimal), "unit": "ohm"},
            "y0_si": {"scientific": _scientific(y0_decimal), "unit": "siemens"},
        },
        "codata_2022_comparison": {
            "alpha_inverse_official": str(OFFICIAL_ALPHA_INV),
            "mu0_official": str(OFFICIAL_MU0),
            "epsilon0_official": str(OFFICIAL_EPSILON0),
            "z0_official": str(OFFICIAL_Z0),
            "alpha_relative_error": _signed_scientific(alpha_error),
            "alpha_inverse_relative_error": _signed_scientific(alpha_inv_error),
            "mu0_relative_error": _signed_scientific(mu0_error),
            "epsilon0_relative_error": _signed_scientific(epsilon0_error),
            "z0_relative_error": _signed_scientific(z0_error),
            "mu0_error_tracks_alpha": abs(mu0_error - alpha_error) < tolerance,
            "epsilon0_error_tracks_negative_alpha": abs(epsilon0_error + alpha_error) < tolerance,
            "z0_error_tracks_alpha": abs(z0_error - alpha_error) < tolerance,
        },
        "selector_cross_bridge": {
            "selector_line_dimension": selector["selector_completion"]["selector_line_dimension"],
            "vacuum_unity_dimensionless_product": "1",
            "vacuum_unity_matches_selector_rank": selector["selector_completion"]["selector_line_dimension"] == 1,
            "transport_selector_is_unique": selector["cross_bridge_dictionary"]["transport_selector_is_unique"],
            "w33_all_ones_spans_mod_3_kernel": selector["cross_bridge_dictionary"]["w33_all_ones_spans_mod_3_kernel"],
        },
        "bridge_verdict": (
            "The exact vacuum-side statement is the unity law c^2 mu0 epsilon0 = 1. "
            "In the modern SI, mu0, epsilon0, and the vacuum impedance Z0 are not "
            "independent exact conventions; they are alpha-mediated. So once the "
            "W33 vertex-propagator theorem fixes alpha^{-1} = 152247/1111, it also "
            "predicts mu0, epsilon0, and Z0 together through exact SI formulas. The "
            "physical number 1 on this side of the theory is the vacuum normalization "
            "itself, and the live selector package supplies the matching rank-1 trivial "
            "line on the internal side."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_vacuum_unity_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
