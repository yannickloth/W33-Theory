"""Quantum vacuum-standards bridge for the live W33 alpha theorem.

The vacuum-unity bridge already promoted the modern-SI statement

    c^2 mu0 epsilon0 = 1,
    Z0 = mu0 c = 1 / (epsilon0 c).

The physically sharper statement is that the vacuum constants sit inside the
exact quantum electrical standards:

    R_K = h / e^2,          (von Klitzing resistance)
    K_J = 2 e / h,          (Josephson constant)
    G_0 = 2 e^2 / h,        (Landauer conductance quantum)
    Phi_0 = h / (2 e),      (flux quantum)

with the exact reciprocal/closure laws

    Phi_0 K_J = 1,
    R_K G_0 = 2,
    K_J^2 R_K h = 4.

Once the live W33 theorem fixes alpha, the vacuum sits on those standards by

    Z0 = 2 alpha R_K,
    mu0 = 2 alpha R_K / c,
    epsilon0 = 1 / (2 alpha R_K c),
    Y0 = G_0 / (4 alpha),
    alpha = Z0 / (2 R_K) = Z0 G_0 / 4.

So the electromagnetic vacuum is not just a constants table: it is the exact
bridge between light propagation and the Landauer/Josephson/von-Klitzing
transport standards.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_vacuum_unity_bridge import ALPHA, ALPHA_INV, C, E_CHARGE, H, EPSILON0, MU0, Y0, Z0


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_quantum_vacuum_standards_bridge_summary.json"

getcontext().prec = 80

R_K = H / (E_CHARGE * E_CHARGE)
K_J = Fraction(2, 1) * E_CHARGE / H
G0 = Fraction(2, 1) / R_K
PHI0 = Fraction(1, 1) / K_J


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _decimal_from_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _scientific(value: Decimal, digits: int = 24) -> str:
    return format(value, f".{digits}e")


@lru_cache(maxsize=1)
def build_quantum_vacuum_standards_summary() -> dict[str, Any]:
    rk_decimal = _decimal_from_fraction(R_K)
    kj_decimal = _decimal_from_fraction(K_J)
    g0_decimal = _decimal_from_fraction(G0)
    phi0_decimal = _decimal_from_fraction(PHI0)

    return {
        "status": "ok",
        "alpha_input": {
            "alpha_inverse": _fraction_dict(ALPHA_INV),
            "alpha": _fraction_dict(ALPHA),
        },
        "exact_quantum_standards": {
            "von_klitzing_constant": {
                "formula": "h / e^2",
                "value": _fraction_dict(R_K),
                "scientific": _scientific(rk_decimal),
                "unit": "ohm",
            },
            "josephson_constant": {
                "formula": "2 e / h",
                "value": _fraction_dict(K_J),
                "scientific": _scientific(kj_decimal),
                "unit": "Hz V^-1",
            },
            "conductance_quantum": {
                "formula": "2 e^2 / h",
                "value": _fraction_dict(G0),
                "scientific": _scientific(g0_decimal),
                "unit": "siemens",
            },
            "flux_quantum": {
                "formula": "h / (2 e)",
                "value": _fraction_dict(PHI0),
                "scientific": _scientific(phi0_decimal),
                "unit": "weber",
            },
            "phi0_times_kj": _fraction_dict(PHI0 * K_J),
            "rk_times_g0": _fraction_dict(R_K * G0),
            "kj_squared_rk_h": _fraction_dict(K_J * K_J * R_K * H),
            "flux_quantum_inverse_is_josephson": PHI0 * K_J == 1,
            "conductance_quantum_is_two_over_rk": G0 == Fraction(2, 1) / R_K,
            "josephson_von_klitzing_triangle_closes": K_J * K_J * R_K * H == 4,
        },
        "vacuum_transport_dictionary": {
            "z0_equals_2_alpha_rk": Z0 == Fraction(2, 1) * ALPHA * R_K,
            "mu0_equals_2_alpha_rk_over_c": MU0 == Fraction(2, 1) * ALPHA * R_K / C,
            "epsilon0_equals_one_over_2_alpha_rk_c": EPSILON0 == Fraction(1, 1) / (Fraction(2, 1) * ALPHA * R_K * C),
            "y0_equals_g0_over_4alpha": Y0 == G0 / (Fraction(4, 1) * ALPHA),
            "alpha_from_z0_over_2rk": _fraction_dict(Z0 / (Fraction(2, 1) * R_K)),
            "alpha_from_z0_g0_over_4": _fraction_dict(Z0 * G0 / Fraction(4, 1)),
            "z0_times_g0": _fraction_dict(Z0 * G0),
            "z0_times_g0_equals_4alpha": Z0 * G0 == Fraction(4, 1) * ALPHA,
            "rk_over_z0": _fraction_dict(R_K / Z0),
            "rk_over_z0_equals_one_over_2alpha": R_K / Z0 == Fraction(1, 1) / (Fraction(2, 1) * ALPHA),
            "vacuum_unity": _fraction_dict(C * C * MU0 * EPSILON0),
        },
        "bridge_verdict": (
            "The vacuum side is now exact in the language of the quantum "
            "electrical standards. The W33 alpha theorem does not just fix mu0, "
            "epsilon0, and Z0 abstractly; it places the vacuum impedance on the "
            "von Klitzing resistance by Z0 = 2 alpha R_K and places the vacuum "
            "admittance on the Landauer conductance quantum by Y0 = G0/(4 alpha). "
            "Equivalently, alpha itself is the exact vacuum-to-transport ratio "
            "alpha = Z0/(2 R_K) = Z0 G0 / 4. Together with c^2 mu0 epsilon0 = 1, "
            "Phi_0 K_J = 1, R_K G_0 = 2, and K_J^2 R_K h = 4, this means the live "
            "vacuum sector already closes relativity, charge quantization, quantum "
            "action, Josephson/von-Klitzing standards, and Landauer transport in "
            "one exact package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_quantum_vacuum_standards_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
