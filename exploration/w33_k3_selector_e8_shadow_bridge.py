"""Canonical K3 selector plane versus the explicit ``3U (+) E8 (+) E8`` split.

The explicit K3 bridge host now has a fully named lattice decomposition

    H^2(K3, Z) = 3U (+) E8(-1) (+) E8(-1).

The canonical mixed harmonic selector plane was already known to straddle the
``3U`` core and the negative complement. This module resolves the negative side
one step further by projecting the selector plane onto the two concrete
``E8(-1)`` factors built from their simple roots.

The resulting picture is sharper:

- the selector has a positive-definite ``3U`` shadow;
- it has a negative-definite shadow on each explicit ``E8(-1)`` factor;
- the two ``E8`` shadows are exact orthogonal pieces; and
- the full selector plane reconstructs as the orthogonal sum of those three
  pieces.

So the selector is not merely a bridge between hyperbolic core and unnamed
negative complement. It already bridges the ``3U`` core and both named
exceptional ``E8`` blocks on the explicit seed.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_curved_h2_intersection_bridge import SIGN_TOL, ZERO_TOL
from w33_k3_e8_factor_split_bridge import e8_factor_simple_roots_in_integral_coordinates
from w33_k3_integral_h2_lattice_bridge import (
    integral_k3_h2_basis_matrix,
    integral_k3_h2_intersection_matrix,
)
from w33_k3_selector_three_u_shadow_bridge import _canonical_selector_harmonic_data
from w33_k3_three_u_decomposition_bridge import k3_three_u_block_coefficients


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_selector_e8_shadow_bridge_summary.json"


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > SIGN_TOL))
    negative = int(np.sum(eigenvalues < -SIGN_TOL))
    return positive, negative


def _orthogonal_projector(basis: np.ndarray, form: np.ndarray) -> np.ndarray:
    gram = basis.T @ form @ basis
    return basis @ np.linalg.inv(gram) @ basis.T @ form


def _selector_plane_integral_coordinates() -> np.ndarray:
    harmonic_basis, _, selector_harmonic = _canonical_selector_harmonic_data()
    integral_basis_cochains = integral_k3_h2_basis_matrix().astype(float)
    change_of_basis = harmonic_basis.T @ integral_basis_cochains
    return np.linalg.solve(change_of_basis, selector_harmonic)


def _float_lists(matrix: np.ndarray) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix.tolist()]


@lru_cache(maxsize=1)
def build_k3_selector_e8_shadow_bridge_summary() -> dict[str, Any]:
    selector = _selector_plane_integral_coordinates()
    ambient_form = integral_k3_h2_intersection_matrix().astype(float)

    three_u_basis = k3_three_u_block_coefficients().astype(float)
    e8_factor_one_basis, e8_factor_two_basis = (
        basis.astype(float) for basis in e8_factor_simple_roots_in_integral_coordinates()
    )

    three_u_shadow = _orthogonal_projector(three_u_basis, ambient_form) @ selector
    e8_factor_one_shadow = _orthogonal_projector(e8_factor_one_basis, ambient_form) @ selector
    e8_factor_two_shadow = _orthogonal_projector(e8_factor_two_basis, ambient_form) @ selector

    selector_form = selector.T @ ambient_form @ selector
    three_u_form = three_u_shadow.T @ ambient_form @ three_u_shadow
    e8_factor_one_form = e8_factor_one_shadow.T @ ambient_form @ e8_factor_one_shadow
    e8_factor_two_form = e8_factor_two_shadow.T @ ambient_form @ e8_factor_two_shadow

    cross_three_u_e8_one = three_u_shadow.T @ ambient_form @ e8_factor_one_shadow
    cross_three_u_e8_two = three_u_shadow.T @ ambient_form @ e8_factor_two_shadow
    cross_e8_one_e8_two = e8_factor_one_shadow.T @ ambient_form @ e8_factor_two_shadow

    reconstruction = three_u_shadow + e8_factor_one_shadow + e8_factor_two_shadow
    reconstruction_error = float(np.max(np.abs(selector - reconstruction)))

    three_u_signature = _signature_counts(three_u_form)
    e8_factor_one_signature = _signature_counts(e8_factor_one_form)
    e8_factor_two_signature = _signature_counts(e8_factor_two_form)

    return {
        "status": "ok",
        "selector_plane_form": _float_lists(selector_form),
        "three_u_component_form": _float_lists(three_u_form),
        "e8_factor_one_component_form": _float_lists(e8_factor_one_form),
        "e8_factor_two_component_form": _float_lists(e8_factor_two_form),
        "cross_terms": {
            "three_u_vs_e8_factor_one": _float_lists(cross_three_u_e8_one),
            "three_u_vs_e8_factor_two": _float_lists(cross_three_u_e8_two),
            "e8_factor_one_vs_e8_factor_two": _float_lists(cross_e8_one_e8_two),
        },
        "selector_e8_shadow_theorem": {
            "selector_projection_on_three_u_is_positive_definite": three_u_signature == (2, 0),
            "selector_projection_on_e8_factor_one_is_negative_definite": (
                e8_factor_one_signature == (0, 2)
            ),
            "selector_projection_on_e8_factor_two_is_negative_definite": (
                e8_factor_two_signature == (0, 2)
            ),
            "selector_projection_on_e8_factor_one_is_nonzero": bool(
                float(np.linalg.norm(e8_factor_one_shadow)) > ZERO_TOL
            ),
            "selector_projection_on_e8_factor_two_is_nonzero": bool(
                float(np.linalg.norm(e8_factor_two_shadow)) > ZERO_TOL
            ),
            "e8_factor_projections_are_exactly_orthogonal": bool(
                float(np.max(np.abs(cross_e8_one_e8_two))) < ZERO_TOL
            ),
            "selector_decomposes_orthogonally_across_three_u_and_both_e8_factors": bool(
                reconstruction_error < ZERO_TOL
                and float(np.max(np.abs(cross_three_u_e8_one))) < ZERO_TOL
                and float(np.max(np.abs(cross_three_u_e8_two))) < ZERO_TOL
                and float(np.max(np.abs(cross_e8_one_e8_two))) < ZERO_TOL
            ),
            "selector_is_not_supported_on_three_u_alone": bool(
                float(np.linalg.norm(e8_factor_one_shadow + e8_factor_two_shadow)) > ZERO_TOL
            ),
            "selector_is_not_supported_on_single_e8_factor": bool(
                float(np.linalg.norm(e8_factor_one_shadow)) > ZERO_TOL
                and float(np.linalg.norm(e8_factor_two_shadow)) > ZERO_TOL
            ),
            "selector_bridges_three_u_and_both_e8_factors": bool(
                three_u_signature == (2, 0)
                and e8_factor_one_signature == (0, 2)
                and e8_factor_two_signature == (0, 2)
                and reconstruction_error < ZERO_TOL
            ),
        },
        "reconstruction_error_linf": reconstruction_error,
        "bridge_verdict": (
            "The canonical mixed K3 selector plane is now resolved against the "
            "full named lattice split 3U (+) E8(-1) (+) E8(-1). Its 3U shadow "
            "is positive-definite, its projections onto the two explicit E8 "
            "factors are both nonzero and negative-definite, and the three "
            "pieces are cup-orthogonal and reconstruct the selector exactly. So "
            "the selector is not supported on the hyperbolic core alone, and it "
            "is not supported on a single exceptional block either. It already "
            "bridges 3U and both E8 factors on the explicit seed."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_selector_e8_shadow_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
