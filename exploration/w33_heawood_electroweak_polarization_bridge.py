"""Electroweak polarization bridge on the Heawood Clifford packet.

The natural-units electroweak stack already proves

    x = q / Phi_3       = 3/13,
    y = Theta(W33)/Phi_3 = 10/13,
    xy = q Theta(W33) / Phi_3^2 = 30/169,
    y - x = Phi_6 / Phi_3 = 7/13.

Separately, the Heawood middle shell already carries an exact finite Clifford
packet:

    P_mid        = middle-shell projector,          rank(P_mid) = 12,
    J_mid^2      = P_mid,
    Pi_+         = (P_mid + J_mid)/2,               rank(Pi_+) = 6,
    Pi_-         = (P_mid - J_mid)/2,               rank(Pi_-) = 6.

This lets the electroweak split be promoted from two fractions to an exact
operator on the Heawood packet:

    R_EW = (q Pi_- + Theta(W33) Pi_+) / Phi_3.

Then

    R_EW = P_mid/2 + (Phi_6 / (2 Phi_3)) J_mid,
    2 R_EW - P_mid = (Phi_6 / Phi_3) J_mid,
    R_EW^2 - R_EW + (q Theta(W33)/Phi_3^2) P_mid = 0.

So the weak/hypercharge split is an exact polarization of the Heawood
Clifford packet, and the atmospheric selector 7/13 is literally the
centered polarization coefficient.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_heawood_clifford_bridge import build_heawood_clifford_summary
from w33_natural_units_electroweak_split_bridge import (
    build_natural_units_electroweak_split_summary,
)
from w33_natural_units_root_gap_bridge import build_natural_units_root_gap_summary
from w33_natural_units_sigma_shell_bridge import build_natural_units_sigma_shell_summary
from w33_mobius_szilassi_dual import heawood_incidence_from_mobius


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_heawood_electroweak_polarization_bridge_summary.json"
)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _incidence_matrix() -> sp.Matrix:
    incidence = heawood_incidence_from_mobius()
    matrix = sp.zeros(7, 7)
    for line_index, points in incidence.items():
        for point in points:
            matrix[line_index, point] = 1
    return matrix


@lru_cache(maxsize=1)
def build_heawood_electroweak_polarization_summary() -> dict[str, Any]:
    clifford = build_heawood_clifford_summary()
    electroweak = build_natural_units_electroweak_split_summary()
    root_gap = build_natural_units_root_gap_summary()
    sigma_shell = build_natural_units_sigma_shell_summary()

    q = Fraction(electroweak["nested_complement_dictionary"]["q"])
    theta = Fraction(electroweak["nested_complement_dictionary"]["theta_w33"])
    phi3 = Fraction(electroweak["nested_complement_dictionary"]["phi3"])
    phi6 = Fraction(root_gap["root_gap_dictionary"]["phi6"])
    neutral_product = Fraction(root_gap["root_gap_dictionary"]["neutral_product"]["exact"])
    weak_share = Fraction(root_gap["root_gap_dictionary"]["weak_share"]["exact"])
    hypercharge_share = Fraction(root_gap["root_gap_dictionary"]["hypercharge_share"]["exact"])
    gap = Fraction(root_gap["root_gap_dictionary"]["root_gap"]["exact"])

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
    j_mid = sp.simplify(middle_projector * (L - 3 * I14) * middle_projector / sp.sqrt(2))
    pi_plus = sp.simplify((middle_projector + j_mid) / 2)
    pi_minus = sp.simplify((middle_projector - j_mid) / 2)

    r_ew = sp.simplify((sp.Rational(q) * pi_minus + sp.Rational(theta) * pi_plus) / sp.Rational(phi3))
    polarization_form = sp.simplify(
        middle_projector / 2 + sp.Rational(phi6, 2 * phi3) * j_mid
    )
    reduced_packet = sp.Matrix(
        [
            [sp.Rational(1, 2), sp.Rational(phi6, 2 * phi3)],
            [sp.Rational(phi6, 2 * phi3), sp.Rational(1, 2)],
        ]
    )

    middle_rank = int(sp.trace(middle_projector))
    complex_rank = int(sp.trace(pi_plus))
    middle_trace = int(sigma_shell["trace_ladder_dictionary"]["heawood_middle_trace"])

    return {
        "status": "ok",
        "polarization_dictionary": {
            "operator_formula": "R_EW = (q Pi_- + Theta(W33) Pi_+) / Phi_3",
            "projector_form_formula": "R_EW = P_mid/2 + (Phi_6 / (2 Phi_3)) J_mid",
            "centered_gap_formula": "2 R_EW - P_mid = (Phi_6 / Phi_3) J_mid",
            "quadratic_formula": "R_EW^2 - R_EW + (q Theta(W33)/Phi_3^2) P_mid = 0",
            "reduced_packet_formula": "M_EW = [[1/2, Phi_6/(2 Phi_3)], [Phi_6/(2 Phi_3), 1/2]]",
            "q": int(q),
            "theta_w33": int(theta),
            "phi3": int(phi3),
            "phi6": int(phi6),
            "middle_rank": middle_rank,
            "complex_rank": complex_rank,
            "weak_share": _fraction_dict(weak_share),
            "hypercharge_share": _fraction_dict(hypercharge_share),
            "neutral_product": _fraction_dict(neutral_product),
            "root_gap": _fraction_dict(gap),
            "polarization_amplitude": _fraction_dict(Fraction(phi6, 2 * phi3)),
            "middle_trace": middle_trace,
        },
        "reduced_packet_dictionary": {
            "trace": _fraction_dict(Fraction(reduced_packet.trace())),
            "determinant": _fraction_dict(Fraction(reduced_packet.det())),
            "eigenvalue_minus": _fraction_dict(weak_share),
            "eigenvalue_plus": _fraction_dict(hypercharge_share),
        },
        "exact_factorizations": {
            "pi_plus_rank_is_6": int(sp.trace(pi_plus)) == 6,
            "pi_minus_rank_is_6": int(sp.trace(pi_minus)) == 6,
            "polarization_operator_has_expected_trace": sp.trace(r_ew) == 6,
            "average_trace_on_middle_shell_equals_half": sp.simplify(sp.trace(r_ew) / middle_rank) == sp.Rational(1, 2),
            "operator_equals_projector_plus_polarization_form": sp.simplify(r_ew - polarization_form) == sp.zeros(14),
            "centered_gap_is_atmospheric_selector": sp.simplify(2 * r_ew - middle_projector - sp.Rational(phi6, phi3) * j_mid) == sp.zeros(14),
            "operator_satisfies_neutral_shell_quadratic": sp.simplify(r_ew * r_ew - r_ew + sp.Rational(neutral_product) * middle_projector) == sp.zeros(14),
            "reduced_packet_trace_is_one": reduced_packet.trace() == 1,
            "reduced_packet_determinant_is_neutral_product": reduced_packet.det() == sp.Rational(neutral_product),
            "reduced_packet_eigenvalues_match_weak_and_hypercharge": set(sp.nsimplify(v) for v in reduced_packet.eigenvals()) == {sp.Rational(3, 13), sp.Rational(10, 13)},
            "neutral_numerator_is_heawood_trace_minus_clifford_rank": middle_trace - complex_rank == int(q * theta),
            "clifford_packet_is_available": clifford["exact_factorizations"]["pi_plus_rank_is_6"] and clifford["exact_factorizations"]["pi_minus_rank_is_6"],
        },
        "bridge_verdict": (
            "The electroweak split is now an exact finite operator on the Heawood "
            "Clifford packet. The rank-12 middle shell already carries the centered "
            "involution J_mid and the exact rank-6 projectors Pi_+, Pi_-. Weighting "
            "those projectors by q=3 and Theta(W33)=10 gives an operator R_EW whose "
            "eigenvalues are exactly 3/13 and 10/13. Equivalently, R_EW is the "
            "mid-shell half-projector polarized by the centered involution: "
            "R_EW = P_mid/2 + (7/26) J_mid. So the atmospheric selector 7/13 is not "
            "only the weak/hypercharge gap; it is the exact centered polarization "
            "strength of the finite Heawood electroweak packet."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_electroweak_polarization_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
