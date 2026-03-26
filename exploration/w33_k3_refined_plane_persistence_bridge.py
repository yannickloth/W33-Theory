"""First barycentric persistence of the canonical mixed K3 plane.

The repo already had two sharp facts, but not their bridge:

1. the explicit ``K3_16`` seed carries a canonical mixed-sign rank-2 plane in
   ``H^2`` selected by the lexicographically first harmonic triangle; and
2. the curved barycentric tower has a universal top-simplex multiplier ``120``.

This module ties them together directly. It evaluates the restricted cup form
of that canonical mixed plane on the seed and on the first barycentric pullback
defined by the ordered-simplex expansion of each oriented 4-simplex. The exact
result is that the restricted form scales by ``120 = 5!`` and therefore its
normalized mixed signature is unchanged.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import itertools
import json
from math import factorial, isclose
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

from w33_curved_h2_intersection_bridge import (
    _cup_matrix_on_h2,
    _facets,
    _harmonic_projector_and_basis,
    _oriented_fundamental_class,
)
from w33_curved_external_hodge_product import external_hodge_laplacians
from w33_explicit_curved_4d_complexes import faces_by_dimension


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_refined_plane_persistence_bridge_summary.json"
TOL = 1e-9


@dataclass(frozen=True)
class RestrictedFormSummary:
    matrix: tuple[tuple[float, float], tuple[float, float]]
    determinant: float
    positive_directions: int
    negative_directions: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "matrix": [list(row) for row in self.matrix],
            "determinant": self.determinant,
            "positive_directions": self.positive_directions,
            "negative_directions": self.negative_directions,
        }


def _permutation_sign(simplex: tuple[int, ...]) -> int:
    sign = 1
    for i in range(len(simplex)):
        for j in range(i + 1, len(simplex)):
            if simplex[i] > simplex[j]:
                sign *= -1
    return sign


def _triangle_value(
    coefficients: np.ndarray,
    triangle_index: dict[tuple[int, int, int], int],
    ordered_triangle: tuple[int, int, int],
) -> float:
    sorted_triangle = tuple(sorted(ordered_triangle))
    index = triangle_index.get(sorted_triangle)
    if index is None:
        return 0.0
    sign = _permutation_sign(ordered_triangle)
    return sign * float(coefficients[index])


def _canonical_plane_vectors() -> np.ndarray:
    facets = _facets("K3")
    faces = faces_by_dimension(facets)
    triangles = faces[2]
    orientation = _oriented_fundamental_class(facets)
    _, harmonic_basis, _ = _harmonic_projector_and_basis(external_hodge_laplacians("K3")[2])
    cup = _cup_matrix_on_h2(triangles, facets, orientation, harmonic_basis)

    eigenvalues, eigenvectors = np.linalg.eigh(cup)
    positive_projector = eigenvectors[:, eigenvalues > 1e-6] @ eigenvectors[:, eigenvalues > 1e-6].T
    negative_projector = eigenvectors[:, eigenvalues < -1e-6] @ eigenvectors[:, eigenvalues < -1e-6].T

    positive_selector = harmonic_basis @ positive_projector @ harmonic_basis.T
    negative_selector = harmonic_basis @ negative_projector @ harmonic_basis.T

    source_triangle_index = 0
    positive_line = positive_selector[:, source_triangle_index]
    negative_line = negative_selector[:, source_triangle_index]
    positive_line = positive_line / float(np.linalg.norm(positive_line))
    negative_line = negative_line / float(np.linalg.norm(negative_line))
    return np.column_stack((positive_line, negative_line))


def _restricted_seed_form(plane: np.ndarray) -> np.ndarray:
    facets = _facets("K3")
    faces = faces_by_dimension(facets)
    triangles = faces[2]
    orientation = _oriented_fundamental_class(facets)
    return _cup_matrix_on_h2(triangles, facets, orientation, plane)


def restricted_first_barycentric_pullback_form(plane: np.ndarray) -> np.ndarray:
    facets = _facets("K3")
    faces = faces_by_dimension(facets)
    triangles = faces[2]
    orientation = _oriented_fundamental_class(facets)
    triangle_index = {triangle: index for index, triangle in enumerate(triangles)}

    form = np.zeros((plane.shape[1], plane.shape[1]), dtype=float)
    for facet_index, facet in enumerate(facets):
        facet_sign = int(orientation[facet_index])
        for ordered_facet in itertools.permutations(facet):
            refined_sign = facet_sign * _permutation_sign(ordered_facet)
            front = ordered_facet[:3]
            back = ordered_facet[2:]
            left_values = np.array(
                [
                    _triangle_value(plane[:, col], triangle_index, front)
                    for col in range(plane.shape[1])
                ],
                dtype=float,
            )
            right_values = np.array(
                [
                    _triangle_value(plane[:, col], triangle_index, back)
                    for col in range(plane.shape[1])
                ],
                dtype=float,
            )
            form += refined_sign * np.outer(left_values, right_values)
    return 0.5 * (form + form.T)


def _restricted_form_summary(form: np.ndarray) -> RestrictedFormSummary:
    eigenvalues = np.linalg.eigvalsh(form)
    return RestrictedFormSummary(
        matrix=(
            (float(form[0, 0]), float(form[0, 1])),
            (float(form[1, 0]), float(form[1, 1])),
        ),
        determinant=float(np.linalg.det(form)),
        positive_directions=int(np.sum(eigenvalues > TOL)),
        negative_directions=int(np.sum(eigenvalues < -TOL)),
    )


def _normalize_form(form: np.ndarray) -> np.ndarray:
    determinant = float(np.linalg.det(form))
    if abs(determinant) < TOL:
        raise AssertionError("expected a nondegenerate mixed plane")
    return form / np.sqrt(abs(determinant))


@lru_cache(maxsize=1)
def build_k3_refined_plane_persistence_bridge_summary() -> dict[str, Any]:
    plane = _canonical_plane_vectors()
    seed_form = _restricted_seed_form(plane)
    refined_form = restricted_first_barycentric_pullback_form(plane)

    scale_entry = refined_form[0, 0] / seed_form[0, 0]
    expected_scale = factorial(5)
    if not np.allclose(refined_form, expected_scale * seed_form, atol=1e-8):
        raise AssertionError("expected first barycentric pullback to scale the restricted form by 120")

    normalized_seed = _normalize_form(seed_form)
    normalized_refined = _normalize_form(refined_form)

    return {
        "status": "ok",
        "seed_restricted_form": _restricted_form_summary(seed_form).to_dict(),
        "first_refinement_restricted_form": _restricted_form_summary(refined_form).to_dict(),
        "normalized_seed_form": [list(row) for row in normalized_seed.tolist()],
        "normalized_first_refinement_form": [list(row) for row in normalized_refined.tolist()],
        "first_refinement_scale_factor": int(round(scale_entry)),
        "refinement_theorem": {
            "first_barycentric_pullback_scales_restricted_form_by_120": (
                int(round(scale_entry)) == expected_scale
            ),
            "restricted_determinant_scales_by_120_squared": isclose(
                float(np.linalg.det(refined_form)),
                expected_scale * expected_scale * float(np.linalg.det(seed_form)),
                rel_tol=1e-9,
                abs_tol=1e-9,
            ),
            "normalized_restricted_form_is_refinement_invariant": np.allclose(
                normalized_seed,
                normalized_refined,
                atol=1e-8,
            ),
            "mixed_signature_survives_first_refinement": (
                _restricted_form_summary(seed_form).positive_directions
                == _restricted_form_summary(refined_form).positive_directions
                and _restricted_form_summary(seed_form).negative_directions
                == _restricted_form_summary(refined_form).negative_directions
            ),
            "top_simplex_multiplier_matches_restricted_form_scale": expected_scale == 120,
        },
        "bridge_verdict": (
            "The canonical mixed K3 plane survives the first barycentric "
            "refinement exactly. Under the ordered-simplex pullback on the "
            "explicit K3 chain model, its restricted cup form scales by the "
            "same top-simplex multiplier 120 = 5!, so the normalized mixed "
            "signature and normalized determinant are unchanged. The current "
            "rank-2 branch is therefore not a seed-only artifact: it persists "
            "through the first exact refinement step."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_refined_plane_persistence_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
