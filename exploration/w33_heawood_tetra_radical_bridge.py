"""Exact Heawood middle-shell refinement on the Klein GF(3) tetra packet.

The promoted torus/Fano route already carries three exact operator packets:

    - the toroidal ``K7`` shell with nontrivial Laplacian mode ``7``;
    - the Heawood harmonic shell with Laplacian spectrum
      ``{0, (3-sqrt(2))^6, (3+sqrt(2))^6, 6}``;
    - the Klein quartic ``GF(3)`` tetra packet, which is exactly ``K4``.

This module isolates the genuinely new exact statement tying those packets
together.

If ``L_H`` is the Heawood Laplacian, then after removing the constant line and
the bipartite sign line, the remaining 12-dimensional shell satisfies

    x^2 - 6x + 7 = 0.

So the Heawood middle shell is an exact radical refinement of the toroidal
``7``-mode:

    (3-sqrt(2)) + (3+sqrt(2)) = 6,
    (3-sqrt(2))(3+sqrt(2)) = 7.

The same roots are realized locally on the exact Klein ``K4`` packet by the
two weighted tetrahedral Laplacians

    L_-(K4) = ((3-sqrt(2))/4) * (4I - J),
    L_+(K4) = ((3+sqrt(2))/4) * (4I - J).

So the torus/Klein route is now an operator refinement chain:

    K7 shell (7) -> Heawood middle quadratic (x^2 - 6x + 7) -> Klein weighted K4.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_heawood_harmonic_bridge import build_heawood_harmonic_summary
from w33_klein_quartic_gf3_tetra_bridge import build_klein_quartic_gf3_tetra_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary
from w33_toroidal_k7_spectral_bridge import build_toroidal_k7_spectral_summary
from w33_mobius_szilassi_dual import heawood_incidence_from_mobius


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_tetra_radical_bridge_summary.json"


def _spectral_strings(values: list[sp.Expr]) -> list[str]:
    return [str(sp.simplify(v)) for v in values]


def _incidence_matrix() -> sp.Matrix:
    incidence = heawood_incidence_from_mobius()
    matrix = sp.zeros(7, 7)
    for line_index, points in incidence.items():
        for point in points:
            matrix[line_index, point] = 1
    return matrix


def _weighted_k4_laplacian(weight: sp.Expr) -> sp.Matrix:
    return sp.simplify(weight * (4 * sp.eye(4) - sp.ones(4)))


@lru_cache(maxsize=1)
def build_heawood_tetra_radical_summary() -> dict[str, Any]:
    heawood = build_heawood_harmonic_summary()
    toroidal = build_toroidal_k7_spectral_summary()
    klein_tetra = build_klein_quartic_gf3_tetra_summary()
    surface_physics = build_surface_physics_shell_summary()

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

    minus_branch = sp.simplify(3 - sp.sqrt(2))
    plus_branch = sp.simplify(3 + sp.sqrt(2))
    middle_quadratic = sp.expand(L**2 - 6 * L + 7 * I14)
    middle_relation = sp.simplify(middle_projector * middle_quadratic)
    projector_three = sp.simplify((H**2 - 2 * I14) * (H + 3 * I14) / 42)
    projector_sqrt2 = sp.simplify((9 * I14 - H**2) * (H + sp.sqrt(2) * I14) / (14 * sp.sqrt(2)))
    low_shell_projector = sp.simplify(projector_three + projector_sqrt2)

    minus_weight = sp.simplify(minus_branch / 4)
    plus_weight = sp.simplify(plus_branch / 4)
    L4_minus = _weighted_k4_laplacian(minus_weight)
    L4_plus = _weighted_k4_laplacian(plus_weight)

    minus_spectrum = [sp.Integer(0)] + [minus_branch] * 3
    plus_spectrum = [sp.Integer(0)] + [plus_branch] * 3

    gauge_dimension = int(surface_physics["standard_model_gauge_dictionary"]["gauge_dimension"])
    shared_six_channel = int(surface_physics["standard_model_gauge_dictionary"]["shared_six_channel"])
    phi6 = int(toroidal["toroidal_k7_dictionary"]["phi6"])
    middle_shell_trace = sp.simplify(6 * minus_branch + 6 * plus_branch)
    middle_shell_pseudodeterminant = sp.simplify((minus_branch * plus_branch) ** 6)

    return {
        "status": "ok",
        "heawood_middle_shell": {
            "full_laplacian_minimal_polynomial": "x (x - 6) (x^2 - 6x + 7)",
            "constant_line_dimension": 1,
            "sign_line_dimension": 1,
            "middle_shell_dimension": 12,
            "middle_projector_rank": int(sp.trace(middle_projector)),
            "middle_quadratic_polynomial": "x^2 - 6x + 7",
            "middle_quadratic_relation_holds": middle_relation == sp.zeros(14),
            "middle_branch_eigenvalues_exact": {
                "minus": str(minus_branch),
                "plus": str(plus_branch),
            },
            "middle_branch_multiplicity_each": 6,
            "middle_shell_trace_exact": str(middle_shell_trace),
            "middle_shell_pseudodeterminant_exact": str(middle_shell_pseudodeterminant),
        },
        "heawood_spectral_projectors": {
            "projector_three_formula": "((H^2 - 2I)(H + 3I)) / 42",
            "projector_sqrt2_formula": "((9I - H^2)(H + sqrt(2)I)) / (14 sqrt(2))",
            "low_shell_projector_formula": "P_3 + P_sqrt(2)",
            "projector_three_is_idempotent": sp.simplify(projector_three**2 - projector_three) == sp.zeros(14),
            "projector_sqrt2_is_idempotent": sp.simplify(projector_sqrt2**2 - projector_sqrt2) == sp.zeros(14),
            "projector_three_and_sqrt2_are_orthogonal": sp.simplify(projector_three * projector_sqrt2) == sp.zeros(14),
            "projector_three_rank": int(sp.trace(projector_three)),
            "projector_sqrt2_rank": int(sp.trace(projector_sqrt2)),
            "low_shell_projector_rank": int(sp.trace(low_shell_projector)),
        },
        "klein_tetra_local_packet": {
            "packet_is_k4": klein_tetra["gf3_klein_quartic_packet"]["induced_projective_packet_is_k4"],
            "tetra_packet_size": klein_tetra["gf3_klein_quartic_packet"]["point_count"],
            "tetra_packet_automorphism_order": klein_tetra["gf3_klein_quartic_packet"]["tetra_automorphism_order"],
            "weighted_tetra_branch_weights_exact": {
                "minus": str(minus_weight),
                "plus": str(plus_weight),
            },
            "weighted_tetra_minus_spectrum_exact": _spectral_strings(minus_spectrum),
            "weighted_tetra_plus_spectrum_exact": _spectral_strings(plus_spectrum),
            "weighted_tetra_minus_matches_exactly": L4_minus.eigenvals() == {sp.Integer(0): 1, minus_branch: 3},
            "weighted_tetra_plus_matches_exactly": L4_plus.eigenvals() == {sp.Integer(0): 1, plus_branch: 3},
            "tetra_nonzero_multiplicity": 3,
        },
        "exact_factorizations": {
            "middle_shell_dimension_equals_gauge_dimension": 12 == gauge_dimension,
            "low_shell_rank_equals_toroidal_seed_order": int(sp.trace(low_shell_projector)) == toroidal["toroidal_k7_dictionary"]["toroidal_seed_order"],
            "middle_branch_multiplicity_equals_shared_six_channel": 6 == shared_six_channel,
            "middle_quadratic_linear_term_equals_shared_six_channel": 6 == shared_six_channel,
            "middle_quadratic_constant_term_equals_phi6": 7 == phi6,
            "middle_branch_sum_equals_shared_six_channel": sp.simplify(minus_branch + plus_branch) == shared_six_channel,
            "middle_branch_product_equals_phi6": sp.simplify(minus_branch * plus_branch) == phi6,
            "middle_shell_trace_equals_q_times_gauge_dimension": middle_shell_trace == 3 * gauge_dimension,
            "middle_shell_pseudodeterminant_equals_phi6_to_shared_six": middle_shell_pseudodeterminant == phi6**shared_six_channel,
            "weighted_klein_tetra_minus_realizes_middle_minus_branch": L4_minus.eigenvals() == {sp.Integer(0): 1, minus_branch: 3},
            "weighted_klein_tetra_plus_realizes_middle_plus_branch": L4_plus.eigenvals() == {sp.Integer(0): 1, plus_branch: 3},
            "toroidal_selector_refines_to_heawood_middle_quadratic": (
                sp.simplify(minus_branch * plus_branch) == toroidal["toroidal_k7_dictionary"]["phi6"]
            ),
            "tetra_packet_size_equals_mu": klein_tetra["gf3_klein_quartic_packet"]["point_count_equals_mu"],
        },
        "bridge_verdict": (
            "The Heawood shell now has an exact middle-sector refinement. After "
            "removing the constant line and the bipartite sign line, the remaining "
            "12-dimensional shell satisfies x^2 - 6x + 7 = 0. So the toroidal "
            "7-mode is refined into the radical pair 3 - sqrt(2), 3 + sqrt(2), "
            "whose sum is the shared six-channel coefficient and whose product is "
            "the same Phi_6 = 7 already carried by the toroidal K7 shell and "
            "beta_0(QCD). The same roots are realized locally on the exact "
            "GF(3) Klein tetra packet by the two weighted K4 Laplacians "
            "((3-sqrt(2))/4)(4I-J) and ((3+sqrt(2))/4)(4I-J). So the torus/Klein "
            "route already contains an exact operator chain from the toroidal "
            "selector shell to a local tetrahedral normal-mode packet."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_tetra_radical_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
