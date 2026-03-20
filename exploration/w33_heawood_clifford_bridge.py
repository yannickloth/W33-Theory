"""Finite Clifford bridge on the Heawood middle shell.

The Heawood middle-shell bridge already proves that

    J_mid = P_mid (L_H - qI) P_mid / sqrt(lambda)

is an exact involution on the 12-dimensional middle shell:

    J_mid^2 = P_mid.

The bipartite Heawood grading supplies a second exact involution. If

    Gamma = diag(I_7, -I_7),
    Gamma_mid = P_mid Gamma P_mid,

then on the same middle shell

    Gamma_mid^2 = P_mid,
    Gamma_mid J_mid + J_mid Gamma_mid = 0.

Therefore the middle shell carries an exact finite Cl(1,1) packet, and

    K_mid = Gamma_mid J_mid

satisfies

    K_mid^2 = -P_mid.

So the real 12-dimensional Heawood middle shell is canonically a 6-dimensional
complex packet. Equivalently, the centered involution splits it into two exact
rank-6 projectors

    Pi_+ = (P_mid + J_mid)/2,
    Pi_- = (P_mid - J_mid)/2.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

import sympy as sp

from w33_heawood_involution_bridge import build_heawood_involution_summary
from w33_mobius_szilassi_dual import heawood_incidence_from_mobius


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_clifford_bridge_summary.json"


def _incidence_matrix() -> sp.Matrix:
    incidence = heawood_incidence_from_mobius()
    matrix = sp.zeros(7, 7)
    for line_index, points in incidence.items():
        for point in points:
            matrix[line_index, point] = 1
    return matrix


@lru_cache(maxsize=1)
def build_heawood_clifford_summary() -> dict[str, object]:
    involution = build_heawood_involution_summary()
    q = int(involution["centered_shell_dictionary"]["q"])
    lam = int(involution["centered_shell_dictionary"]["lambda"])

    B = _incidence_matrix()
    H = sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(7), B),
        sp.Matrix.hstack(B.T, sp.zeros(7)),
    )
    I14 = sp.eye(14)
    L = sp.simplify(3 * I14 - H)

    ones = sp.Matrix([1] * 14)
    signs = sp.Matrix([1] * 7 + [-1] * 7)
    constant_projector = sp.Rational(1, 14) * (ones * ones.T)
    sign_projector = sp.Rational(1, 14) * (signs * signs.T)
    middle_projector = sp.simplify(I14 - constant_projector - sign_projector)

    gamma = sp.diag(*([1] * 7 + [-1] * 7))
    gamma_mid = sp.simplify(middle_projector * gamma * middle_projector)
    j_mid = sp.simplify(middle_projector * (L - q * I14) * middle_projector / sp.sqrt(lam))
    k_mid = sp.simplify(gamma_mid * j_mid)
    pi_plus = sp.simplify((middle_projector + j_mid) / 2)
    pi_minus = sp.simplify((middle_projector - j_mid) / 2)

    return {
        "status": "ok",
        "clifford_dictionary": {
            "gamma_formula": "Gamma = diag(I_7,-I_7)",
            "gamma_mid_formula": "Gamma_mid = P_mid Gamma P_mid",
            "j_mid_formula": "J_mid = P_mid (L_H - qI) P_mid / sqrt(lambda)",
            "k_mid_formula": "K_mid = Gamma_mid J_mid",
            "pi_plus_formula": "Pi_+ = (P_mid + J_mid)/2",
            "pi_minus_formula": "Pi_- = (P_mid - J_mid)/2",
            "middle_shell_rank": int(sp.trace(middle_projector)),
            "complex_rank": int(sp.trace(pi_plus)),
        },
        "exact_factorizations": {
            "gamma_mid_squared_equals_middle_projector": sp.simplify(gamma_mid * gamma_mid) == middle_projector,
            "j_mid_squared_equals_middle_projector": sp.simplify(j_mid * j_mid) == middle_projector,
            "gamma_and_j_anticommute": sp.simplify(gamma_mid * j_mid + j_mid * gamma_mid) == sp.zeros(14),
            "k_mid_squared_equals_minus_middle_projector": sp.simplify(k_mid * k_mid) == -middle_projector,
            "pi_plus_is_projector": sp.simplify(pi_plus * pi_plus) == pi_plus,
            "pi_minus_is_projector": sp.simplify(pi_minus * pi_minus) == pi_minus,
            "pi_plus_pi_minus_zero": sp.simplify(pi_plus * pi_minus) == sp.zeros(14),
            "pi_plus_rank_is_6": int(sp.trace(pi_plus)) == 6,
            "pi_minus_rank_is_6": int(sp.trace(pi_minus)) == 6,
            "middle_shell_is_12_equals_6_plus_6": int(sp.trace(middle_projector)) == int(sp.trace(pi_plus)) + int(sp.trace(pi_minus)),
        },
        "bridge_verdict": (
            "The Heawood middle shell carries an exact finite Clifford packet. "
            "The bipartite grading and the centered radical involution are both "
            "exact involutions on the 12-dimensional middle shell and they "
            "anticommute. Their product therefore squares to -1 on that shell, "
            "so the real 12-dimensional packet is canonically a 6-dimensional "
            "complex packet. Equivalently, the centered involution splits the "
            "middle shell into two exact rank-6 projectors."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_clifford_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
