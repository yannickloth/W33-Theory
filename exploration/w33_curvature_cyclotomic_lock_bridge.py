"""Cyclotomic lock for the curved first-order gravity/topology coefficients.

The EH-continuum lock already proved:

    discrete 6-mode coefficient = 39 * continuum EH coefficient
    topological 1-mode coefficient = 28 * |chi|

This module identifies the exact q=3 cyclotomic structure behind those factors.

For W(3,3):

    39 = q * Phi_3(q) = q(q^2 + q + 1)
    28 = (q + 1) * Phi_6(q) = q^3 + 1

Therefore the first curved product moment of the full finite package obeys

    c_6 = q Phi_3 * c_EH,cont
    c_1 = (q + 1) Phi_6 * |chi|.

So the discrete gravity/topology bridge is locked directly to the same
cyclotomic factors Phi_3 = 13 and Phi_6 = 7 that already govern the rest of
the q=3 program.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_eh_continuum_lock_bridge import build_eh_continuum_lock_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curvature_cyclotomic_lock_bridge_summary.json"

Q = 3
PHI3 = Q * Q + Q + 1
PHI6 = Q * Q - Q + 1


@lru_cache(maxsize=1)
def build_curvature_cyclotomic_lock_summary() -> dict[str, Any]:
    lock = build_eh_continuum_lock_summary()
    c_eh_cont = Fraction(lock["continuum_lock"]["continuum_eh_coefficient"]["exact"])
    c6 = Fraction(lock["continuum_lock"]["discrete_eh_6_mode_coefficient"]["exact"])
    chi = Fraction(lock["topological_lock"]["absolute_euler_characteristic"])
    c1 = Fraction(lock["topological_lock"]["topological_1_mode_coefficient"]["exact"])

    return {
        "status": "ok",
        "cyclotomic_factors": {
            "q": Q,
            "phi3": PHI3,
            "phi6": PHI6,
            "q_phi3": Q * PHI3,
            "q_plus_1_phi6": (Q + 1) * PHI6,
            "q_cubic_plus_1": Q**3 + 1,
        },
        "gravity_lock": {
            "continuum_eh_coefficient": int(c_eh_cont),
            "discrete_6_mode_coefficient": int(c6),
            "discrete_equals_q_phi3_times_continuum": c6 == Fraction(Q * PHI3) * c_eh_cont,
            "q_phi3_factor": Q * PHI3,
        },
        "topology_lock": {
            "absolute_euler_characteristic": int(chi),
            "topological_1_mode_coefficient": int(c1),
            "topological_equals_q_plus_1_phi6_times_abs_chi": c1 == Fraction((Q + 1) * PHI6) * chi,
            "q_plus_1_phi6_factor": (Q + 1) * PHI6,
            "equals_q_cubic_plus_1_times_abs_chi": c1 == Fraction(Q**3 + 1) * chi,
        },
        "bridge_verdict": (
            "The first curved gravity/topology bridge for the full finite W33 "
            "package is cyclotomic. The discrete 6-mode curvature coefficient is "
            "exactly q*Phi_3(q) times the continuum Einstein-Hilbert coefficient, "
            "while the residual 1-mode topological coefficient is exactly "
            "(q+1)*Phi_6(q)|chi| = (q^3+1)|chi|. For q=3 these become 39 and 28, "
            "so the same cyclotomic factors 13 and 7 that already govern the "
            "selection and PMNS structure also lock the curved first-order bridge."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curvature_cyclotomic_lock_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
