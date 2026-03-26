"""Canonical K3 selector plane versus the primitive 3U hyperbolic core.

The explicit K3 seed now carries two exact external bridge structures:

1. the canonical mixed harmonic selector plane coming from the first mixed
   harmonic triangle; and
2. the primitive orthogonal ``3U`` core inside the integral K3 lattice.

This module computes their first exact relation in harmonic ``H^2``
coordinates. Using the cup form as the ambient bilinear form, it projects the
selector plane cup-orthogonally onto the ``3U`` core and onto its orthogonal
rank-16 negative-definite complement.

The key result is structural:

- the selector plane is not contained in the ``3U`` core;
- it is not contained in the negative-definite complement either;
- its shadow on the ``3U`` core is positive-definite; and
- its residual shadow on the rank-16 complement is negative-definite.

So the canonical mixed selector is not itself one of the hyperbolic ``U``
factors. It is a genuine bridge between the hyperbolic core and the negative
complement.
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

from w33_curved_external_hodge_product import external_hodge_laplacians
from w33_curved_h2_intersection_bridge import (
    SIGN_TOL,
    ZERO_TOL,
    _ambient_sign_projector,
    _cup_matrix_on_h2,
    _facets,
    _first_mixed_source_triangle,
    _harmonic_projector_and_basis,
    _match_orientation_to_signature,
    _oriented_fundamental_class,
    _target_signature,
)
from w33_explicit_curved_4d_complexes import faces_by_dimension
from w33_k3_three_u_decomposition_bridge import k3_three_u_block_cochains


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_selector_three_u_shadow_bridge_summary.json"


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > SIGN_TOL))
    negative = int(np.sum(eigenvalues < -SIGN_TOL))
    return positive, negative


def _canonical_selector_harmonic_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    facets = _facets("K3")
    faces = faces_by_dimension(facets)
    triangles = faces[2]
    harmonic_projector, harmonic_basis, _ = _harmonic_projector_and_basis(
        external_hodge_laplacians("K3")[2]
    )
    raw_orientation = _oriented_fundamental_class(facets)
    raw_cup_matrix = _cup_matrix_on_h2(triangles, facets, raw_orientation, harmonic_basis)
    _, cup_matrix = _match_orientation_to_signature(raw_cup_matrix, _target_signature("K3"))

    positive_projector = _ambient_sign_projector(harmonic_basis, cup_matrix, "positive")
    negative_projector = _ambient_sign_projector(harmonic_basis, cup_matrix, "negative")
    selector_triangle_index = _first_mixed_source_triangle(
        harmonic_projector,
        positive_projector,
        negative_projector,
    )
    positive_line = positive_projector[:, selector_triangle_index]
    negative_line = negative_projector[:, selector_triangle_index]
    positive_line /= float(np.linalg.norm(positive_line))
    negative_line /= float(np.linalg.norm(negative_line))
    selector_basis_harmonic = harmonic_basis.T @ np.column_stack((positive_line, negative_line))
    return harmonic_basis, cup_matrix, selector_basis_harmonic


@lru_cache(maxsize=1)
def selector_three_u_shadow_bases() -> dict[str, np.ndarray]:
    harmonic_basis, cup_matrix, selector_basis = _canonical_selector_harmonic_data()
    three_u_basis = harmonic_basis.T @ k3_three_u_block_cochains().astype(float)
    three_u_projector = (
        three_u_basis
        @ np.linalg.inv(three_u_basis.T @ cup_matrix @ three_u_basis)
        @ three_u_basis.T
        @ cup_matrix
    )

    shadow_basis = three_u_projector @ selector_basis
    residual_basis = selector_basis - shadow_basis

    return {
        "harmonic_basis": harmonic_basis,
        "cup_matrix": cup_matrix,
        "selector_harmonic_basis": selector_basis,
        "three_u_shadow_harmonic_basis": shadow_basis,
        "rank16_residual_harmonic_basis": residual_basis,
        "selector_cochain_basis": harmonic_basis @ selector_basis,
        "three_u_shadow_cochain_basis": harmonic_basis @ shadow_basis,
        "rank16_residual_cochain_basis": harmonic_basis @ residual_basis,
    }


@lru_cache(maxsize=1)
def build_k3_selector_three_u_shadow_bridge_summary() -> dict[str, Any]:
    data = selector_three_u_shadow_bases()
    harmonic_basis = data["harmonic_basis"]
    cup_matrix = data["cup_matrix"]
    selector_basis = data["selector_harmonic_basis"]
    three_u_basis = harmonic_basis.T @ k3_three_u_block_cochains().astype(float)
    three_u_gram = three_u_basis.T @ cup_matrix @ three_u_basis
    three_u_projector = three_u_basis @ np.linalg.inv(three_u_gram) @ three_u_basis.T @ cup_matrix

    shadow_basis = data["three_u_shadow_harmonic_basis"]
    residual_basis = data["rank16_residual_harmonic_basis"]
    selector_form = selector_basis.T @ cup_matrix @ selector_basis
    shadow_form = shadow_basis.T @ cup_matrix @ shadow_basis
    residual_form = residual_basis.T @ cup_matrix @ residual_basis

    selector_positive, selector_negative = _signature_counts(selector_form)
    shadow_positive, shadow_negative = _signature_counts(shadow_form)
    residual_positive, residual_negative = _signature_counts(residual_form)

    shadow_nonzero = all(float(np.linalg.norm(shadow_basis[:, column])) > ZERO_TOL for column in range(2))
    residual_nonzero = all(float(np.linalg.norm(residual_basis[:, column])) > ZERO_TOL for column in range(2))

    # Euclidean principal angles are used only as a secondary diagnostic for
    # transversality, not as the main theorem.
    q_three_u, _ = np.linalg.qr(three_u_basis)
    q_selector, _ = np.linalg.qr(selector_basis)
    principal_cosines = np.linalg.svd(q_selector.T @ q_three_u, compute_uv=False)

    return {
        "status": "ok",
        "selector_plane_form": [[float(value) for value in row] for row in selector_form.tolist()],
        "three_u_shadow_form": [[float(value) for value in row] for row in shadow_form.tolist()],
        "rank16_residual_form": [[float(value) for value in row] for row in residual_form.tolist()],
        "principal_cosines_against_three_u_core": [float(value) for value in principal_cosines.tolist()],
        "selector_three_u_shadow_theorem": {
            "selector_plane_is_mixed_signature": (
                selector_positive == 1 and selector_negative == 1
            ),
            "selector_plane_shadow_on_three_u_is_positive_definite": (
                shadow_positive == 2 and shadow_negative == 0
            ),
            "selector_plane_residual_on_rank16_complement_is_negative_definite": (
                residual_positive == 0 and residual_negative == 2
            ),
            "selector_plane_is_not_contained_in_three_u_core": residual_nonzero,
            "selector_plane_is_not_contained_in_rank16_negative_complement": shadow_nonzero,
            "selector_plane_straddles_both_k3_lattice_pieces": shadow_nonzero and residual_nonzero,
            "selector_plane_has_no_numerical_line_of_intersection_with_three_u_core": bool(
                float(np.max(principal_cosines)) < 1.0 - 1e-6
            ),
        },
        "bridge_verdict": (
            "The canonical mixed K3 selector plane is not itself one of the "
            "primitive U factors. In harmonic H^2 coordinates, its cup-"
            "orthogonal shadow on the primitive 3U core is positive-definite, "
            "while its residual shadow on the orthogonal rank-16 side is "
            "negative-definite. So the mixed selector really bridges the "
            "hyperbolic K3 core and the negative complement rather than living "
            "entirely on either side."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_selector_three_u_shadow_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
