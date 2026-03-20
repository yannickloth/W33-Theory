"""Natural-units electroweak unit-balance bridge.

The Heawood electroweak packet already satisfies the exact reduced quadratic

    M_EW^2 - M_EW + 30/169 I_2 = 0

with eigenvalues 3/13 and 10/13 and centered gap 7/13. The new point is that
the full natural-unit ``1`` already splits into two exact finite packets:

    I_2 = (2 M_EW - I_2)^2 + 4 det(M_EW) I_2
        = 49/169 I_2 + 120/169 I_2.

So the finite electroweak unit decomposes into

    - a pure polarization square 49/169 = (7/13)^2
    - a depolarized complement 120/169

and the numerators are already live geometric shells:

    49  = 42 + 7,
    120 = 84 + 36,
    169 = 84 + 36 + 42 + 7.

Here 42 is the toroidal K7 nontrivial trace, 7 is the QCD selector Phi_6,
84 is the single-surface flag shell, and 36 is the Heawood middle-shell trace.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_heawood_electroweak_polarization_bridge import (
    build_heawood_electroweak_polarization_summary,
)
from w33_natural_units_cosmological_complement_bridge import (
    build_natural_units_cosmological_complement_summary,
)
from w33_natural_units_root_gap_bridge import build_natural_units_root_gap_summary
from w33_natural_units_sigma_shell_bridge import build_natural_units_sigma_shell_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_unit_balance_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_unit_balance_summary() -> dict[str, Any]:
    polarization = build_heawood_electroweak_polarization_summary()
    complement = build_natural_units_cosmological_complement_summary()
    root_gap = build_natural_units_root_gap_summary()
    sigma_shell = build_natural_units_sigma_shell_summary()

    phi3 = Fraction(root_gap["root_gap_dictionary"]["phi3"])
    phi6 = Fraction(root_gap["root_gap_dictionary"]["phi6"])
    root_gap_fraction = Fraction(root_gap["root_gap_dictionary"]["root_gap"]["exact"])
    cosmological_fraction = Fraction(
        complement["cosmological_complement_dictionary"]["cosmological_fraction"]["exact"]
    )
    reduced_det = Fraction(polarization["reduced_packet_dictionary"]["determinant"]["exact"])
    surface_flags = Fraction(
        complement["cosmological_complement_dictionary"]["single_surface_flags"]
    )
    heawood_middle_trace = Fraction(
        complement["cosmological_complement_dictionary"]["heawood_middle_trace"]
    )
    toroidal_trace = Fraction(sigma_shell["trace_ladder_dictionary"]["toroidal_trace"])

    reduced_packet = sp.Matrix(
        [
            [sp.Rational(1, 2), sp.Rational(phi6, 2 * phi3)],
            [sp.Rational(phi6, 2 * phi3), sp.Rational(1, 2)],
        ]
    )
    reduced_identity = sp.eye(2)
    reduced_polarization = sp.simplify((2 * reduced_packet - reduced_identity) ** 2)
    reduced_balance = sp.simplify(reduced_polarization + 4 * sp.Rational(reduced_det) * reduced_identity)

    polarization_fraction = Fraction(phi6 * phi6, phi3 * phi3)
    denominator_square = int(phi3 * phi3)
    polarization_numerator = int(phi6 * phi6)
    cosmological_numerator = int(
        complement["cosmological_complement_dictionary"]["cosmological_numerator"]
    )
    qcd_selector = int(phi6)

    return {
        "status": "ok",
        "unit_balance_dictionary": {
            "reduced_balance_formula": "I_2 = (2 M_EW - I_2)^2 + 4 det(M_EW) I_2",
            "lifted_balance_formula": "P_mid = (2 R_EW - P_mid)^2 + ((Phi_3^2 - Phi_6^2)/Phi_3^2) P_mid",
            "mixed_product_formula": "I_2 - (2 M_EW - I_2)^2 = 4 M_EW (I_2 - M_EW)",
            "fraction_formula": "1 = (Phi_6/Phi_3)^2 + (Phi_3^2 - Phi_6^2)/Phi_3^2",
            "numerator_formula": "Phi_3^2 = Phi_6^2 + (Phi_3^2 - Phi_6^2)",
            "shell_balance_formula": "169 = 84 + 36 + 49",
            "shell_formula": "169 = 84 + 36 + 42 + 7",
            "phi3": int(phi3),
            "phi6": int(phi6),
            "denominator_square": denominator_square,
            "polarization_fraction": _fraction_dict(polarization_fraction),
            "cosmological_fraction": _fraction_dict(cosmological_fraction),
            "polarization_numerator": polarization_numerator,
            "cosmological_numerator": cosmological_numerator,
            "single_surface_flags": int(surface_flags),
            "heawood_middle_trace": int(heawood_middle_trace),
            "toroidal_trace": int(toroidal_trace),
            "qcd_selector": qcd_selector,
        },
        "exact_factorizations": {
            "reduced_balance_is_identity": reduced_balance == reduced_identity,
            "polarization_fraction_equals_gap_squared": polarization_fraction == root_gap_fraction * root_gap_fraction,
            "cosmological_fraction_equals_four_det": cosmological_fraction == 4 * reduced_det,
            "unit_splits_into_polarization_plus_complement": polarization_fraction + cosmological_fraction == 1,
            "denominator_square_equals_two_numerators": denominator_square == polarization_numerator + cosmological_numerator,
            "polarization_numerator_equals_toroidal_trace_plus_qcd_selector": (
                polarization_numerator == toroidal_trace + qcd_selector
            ),
            "cosmological_numerator_equals_surface_plus_heawood_trace": (
                cosmological_numerator == surface_flags + heawood_middle_trace
            ),
            "denominator_square_equals_surface_heawood_plus_polarization": (
                denominator_square == surface_flags + heawood_middle_trace + polarization_numerator
            ),
            "denominator_square_equals_surface_heawood_toroidal_qcd_shells": (
                denominator_square
                == surface_flags + heawood_middle_trace + toroidal_trace + qcd_selector
            ),
        },
        "bridge_verdict": (
            "The finite electroweak unit now has an exact operator decomposition. "
            "The reduced packet satisfies I_2 = (2 M_EW - I_2)^2 + 4 det(M_EW) I_2, "
            "so the unit splits as 1 = 49/169 + 120/169. The first term is the pure "
            "polarization square (7/13)^2, while the second term is the depolarized "
            "cosmological precursor already isolated by the Heawood complement law. "
            "The same numerators are geometric too: 49 = 42 + 7 is the toroidal K7 "
            "trace plus the QCD selector, 120 = 84 + 36 is the surface flag shell "
            "plus the Heawood middle-shell trace, and therefore 169 = 84 + 36 + 42 + 7. "
            "So the full finite electroweak normalization is already one exact surface/"
            "Heawood/toroidal/QCD shell balance."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_unit_balance_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
