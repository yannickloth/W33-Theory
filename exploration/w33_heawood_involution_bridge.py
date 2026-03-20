"""Centered involution bridge for the promoted Heawood middle shell.

The promoted Heawood shell already satisfies

    x^2 - 6x + 7 = 0

on the exact 12-dimensional middle sector. The sharper operator statement is
that this shell is centered at q and normalized by lambda:

    x^2 - 2q x + Phi_6 = 0,
    q = 3,
    lambda = q^2 - Phi_6 = 2.

Therefore on the Heawood middle shell,

    (L_H - q I)^2 = lambda I,

and the normalized centered operator

    J_mid = (L_H - q I) / sqrt(lambda)

is an exact involution.

So the surface shell is not only a radical packet. It already carries a
centered sign-like structure with eigenvalues +-1 after normalization.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_heawood_harmonic_bridge import build_heawood_harmonic_summary
from w33_srg_rosetta_lock_bridge import build_srg_rosetta_lock_summary
from w33_mobius_szilassi_dual import heawood_incidence_from_mobius


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_involution_bridge_summary.json"


def _incidence_matrix() -> sp.Matrix:
    incidence = heawood_incidence_from_mobius()
    matrix = sp.zeros(7, 7)
    for line_index, points in incidence.items():
        for point in points:
            matrix[line_index, point] = 1
    return matrix


@lru_cache(maxsize=1)
def build_heawood_involution_summary() -> dict[str, Any]:
    heawood = build_heawood_harmonic_summary()
    srg = build_srg_rosetta_lock_summary()

    q = int(srg["srg_data"]["q_from_lambda_plus_one"])
    lam = int(srg["srg_data"]["lambda"])
    phi6 = int(srg["srg_data"]["phi6_from_k_minus_lambda_minus_mu_plus_one"])

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

    centered = sp.simplify(middle_projector * (L - q * I14) * middle_projector)
    centered_square = sp.simplify(centered * centered)
    normalized = sp.simplify(centered / sp.sqrt(lam))
    normalized_square = sp.simplify(normalized * normalized)

    return {
        "status": "ok",
        "centered_shell_dictionary": {
            "middle_quadratic_polynomial": "x^2 - 6x + 7",
            "centered_quadratic_formula": "(x - q)^2 = lambda",
            "operator_formula": "(P_mid (L_H - qI) P_mid)^2 = lambda P_mid",
            "normalized_involution_formula": "J_mid = P_mid (L_H - qI) P_mid / sqrt(lambda)",
            "q": q,
            "lambda": lam,
            "phi6": phi6,
            "adjacency_quartic_polynomial": heawood["heawood_operator"]["adjacency_minimal_polynomial"],
            "middle_projector_rank": int(sp.trace(middle_projector)),
        },
        "exact_factorizations": {
            "q_squared_minus_phi6_equals_lambda": q * q - phi6 == lam,
            "centered_shell_relation_holds": centered_square == lam * middle_projector,
            "normalized_operator_is_involution": normalized_square == middle_projector,
            "middle_projector_is_idempotent": sp.simplify(middle_projector * middle_projector) == middle_projector,
            "middle_shell_rank_is_12": int(sp.trace(middle_projector)) == 12,
        },
        "bridge_verdict": (
            "The Heawood middle shell now has an exact centered involution form. "
            "Because x^2 - 6x + 7 = x^2 - 2q x + Phi_6 with q=3 and "
            "lambda = q^2 - Phi_6 = 2, the restricted operator satisfies "
            "(L_H - qI)^2 = lambda I on the middle shell. After dividing by "
            "sqrt(lambda), the centered operator becomes an exact involution. "
            "So the radical Heawood packet already carries a normalized "
            "sign-like structure, not just two floating irrational branches."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_involution_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
