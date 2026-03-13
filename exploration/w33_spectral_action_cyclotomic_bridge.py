"""Cyclotomic unification of the internal spectral action and curved gravity lock.

The recent bridge stack has isolated several exact quantities for the full finite
W(3,3) package:

    a0 = 480,  a2 = 2240,  a4 = 17600,
    c_EH,cont = 320,  c_6 = 12480,
    m_H^2 / v^2 = 14 / 55.

This module shows these are not independent numerics. They are all determined by
the same q=3 cyclotomic pair

    Phi_3(q) = q^2 + q + 1,   Phi_6(q) = q^2 - q + 1.

For q = 3 the full exact package obeys

    a2 / a0         = 2 Phi_6 / q,
    a4 / a0         = 2 (4 Phi_3 + q) / q,
    2 a2 / a4       = 2 Phi_6 / (4 Phi_3 + q),
    c_EH,cont / a0  = 2 / q,
    c_6 / a0        = 2 Phi_3,
    c_6 / c_EH,cont = q Phi_3.

So the internal spectral-action ratios, the Higgs ratio, and the curved
Einstein-Hilbert coefficient are one exact cyclotomic object.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_eh_continuum_lock_bridge import build_eh_continuum_lock_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_spectral_action_cyclotomic_bridge_summary.json"

Q = 3
PHI3 = Q * Q + Q + 1
PHI6 = Q * Q - Q + 1


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_spectral_action_cyclotomic_summary() -> dict[str, Any]:
    finite = build_adjacency_dirac_closure_summary()["finite_dirac_closure"]
    eh_lock = build_eh_continuum_lock_summary()["continuum_lock"]

    a0 = Fraction(finite["seeley_dewitt_moments"]["a0_f"])
    a2 = Fraction(finite["seeley_dewitt_moments"]["a2_f"])
    a4 = Fraction(finite["seeley_dewitt_moments"]["a4_f"])
    c_eh_cont = Fraction(eh_lock["continuum_eh_coefficient"]["exact"])
    c6 = Fraction(eh_lock["discrete_eh_6_mode_coefficient"]["exact"])

    a2_over_a0 = Fraction(a2, a0)
    a4_over_a0 = Fraction(a4, a0)
    higgs_ratio_square = Fraction(2 * a2, a4)
    c_eh_cont_over_a0 = Fraction(c_eh_cont, a0)
    c6_over_a0 = Fraction(c6, a0)
    c6_over_c_eh_cont = Fraction(c6, c_eh_cont)

    return {
        "status": "ok",
        "cyclotomic_data": {
            "q": Q,
            "phi3": PHI3,
            "phi6": PHI6,
            "four_phi3_plus_q": 4 * PHI3 + Q,
            "q_phi3": Q * PHI3,
        },
        "internal_spectral_action": {
            "a0_f": int(a0),
            "a2_f": int(a2),
            "a4_f": int(a4),
            "a2_over_a0": _fraction_dict(a2_over_a0),
            "a2_over_a0_formula": "2 Phi_6(q) / q",
            "a2_over_a0_matches_formula": a2_over_a0 == Fraction(2 * PHI6, Q),
            "a4_over_a0": _fraction_dict(a4_over_a0),
            "a4_over_a0_formula": "2 (4 Phi_3(q) + q) / q",
            "a4_over_a0_matches_formula": a4_over_a0 == Fraction(2 * (4 * PHI3 + Q), Q),
            "higgs_ratio_square": _fraction_dict(higgs_ratio_square),
            "higgs_ratio_square_formula": "2 Phi_6(q) / (4 Phi_3(q) + q)",
            "higgs_ratio_square_matches_formula": higgs_ratio_square == Fraction(2 * PHI6, 4 * PHI3 + Q),
        },
        "gravity_lock": {
            "continuum_eh_over_a0": _fraction_dict(c_eh_cont_over_a0),
            "continuum_eh_over_a0_formula": "2 / q",
            "continuum_eh_over_a0_matches_formula": c_eh_cont_over_a0 == Fraction(2, Q),
            "discrete_6_mode_over_a0": _fraction_dict(c6_over_a0),
            "discrete_6_mode_over_a0_formula": "2 Phi_3(q)",
            "discrete_6_mode_over_a0_matches_formula": c6_over_a0 == Fraction(2 * PHI3),
            "discrete_to_continuum_ratio": _fraction_dict(c6_over_c_eh_cont),
            "discrete_to_continuum_formula": "q Phi_3(q)",
            "discrete_to_continuum_matches_formula": c6_over_c_eh_cont == Fraction(Q * PHI3),
        },
        "bridge_verdict": (
            "The full finite W33 spectral-action package is cyclotomic. The "
            "internal moments a2/a0 and a4/a0, the Higgs ratio 2a2/a4, the "
            "continuum Einstein-Hilbert coefficient per internal degree of "
            "freedom, and the discrete curved 6-mode coefficient per internal "
            "degree of freedom are all forced by the same q=3 pair "
            "Phi_3=13, Phi_6=7. So the matter/Higgs side and the gravity side "
            "are not parallel numerologies; they are one exact cyclotomic law."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_spectral_action_cyclotomic_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
