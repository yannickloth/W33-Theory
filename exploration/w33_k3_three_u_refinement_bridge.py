"""First barycentric persistence of the primitive 3U core on K3.

The explicit ``K3_16`` seed already carries a primitive orthogonal ``3U`` block
inside the integral ``H^2`` lattice. This module checks whether that full
hyperbolic core, not only the selector-derived shadows, survives the first
barycentric pullback on the explicit chain model.

It does: the restricted cup form on the six explicit ``3U`` cochain vectors is
scaled exactly by ``120 = 5!``. So the normalized hyperbolic core is already
refinement-invariant at ``sd^1``.
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

from w33_curved_h2_intersection_bridge import (
    _cup_matrix_on_h2,
    _facets,
    _oriented_fundamental_class,
)
from w33_explicit_curved_4d_complexes import faces_by_dimension
from w33_k3_refined_plane_persistence_bridge import restricted_first_barycentric_pullback_form
from w33_k3_three_u_decomposition_bridge import k3_three_u_block_cochains


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_three_u_refinement_bridge_summary.json"
TOL = 1e-8
EXPECTED_THREE_U = np.asarray(
    [
        [0, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0],
    ],
    dtype=int,
)


def _matrix_to_int_lists(matrix: np.ndarray) -> list[list[int]]:
    rounded = np.rint(matrix).astype(int)
    return rounded.tolist()


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > TOL))
    negative = int(np.sum(eigenvalues < -TOL))
    return positive, negative


def _normalized_form(matrix: np.ndarray) -> np.ndarray:
    determinant = float(np.linalg.det(matrix))
    if abs(determinant) < TOL:
        raise AssertionError("expected a nondegenerate 3U block")
    return matrix / (abs(determinant) ** (1.0 / matrix.shape[0]))


@lru_cache(maxsize=1)
def build_k3_three_u_refinement_bridge_summary() -> dict[str, Any]:
    cochains = k3_three_u_block_cochains()
    facets = _facets("K3")
    faces = faces_by_dimension(facets)
    seed_form = _cup_matrix_on_h2(
        faces[2],
        facets,
        _oriented_fundamental_class(facets),
        cochains,
    )
    refined_form = restricted_first_barycentric_pullback_form(cochains)

    if not np.allclose(seed_form, EXPECTED_THREE_U, atol=1e-8):
        raise AssertionError("expected the seed restricted form to be the exact 3U block")
    if not np.allclose(refined_form, 120 * EXPECTED_THREE_U, atol=1e-8):
        raise AssertionError("expected the refined restricted form to be exactly 120 times the 3U block")

    seed_signature = _signature_counts(seed_form)
    refined_signature = _signature_counts(refined_form)

    return {
        "status": "ok",
        "three_u_seed_form": _matrix_to_int_lists(seed_form),
        "three_u_first_refinement_form": _matrix_to_int_lists(refined_form),
        "normalized_three_u_seed_form": np.rint(_normalized_form(seed_form)).astype(int).tolist(),
        "normalized_three_u_first_refinement_form": np.rint(
            _normalized_form(refined_form)
        ).astype(int).tolist(),
        "three_u_refinement_theorem": {
            "three_u_block_scales_by_120": np.allclose(
                refined_form,
                120 * seed_form,
                atol=1e-8,
            ),
            "seed_form_is_exact_3u": np.array_equal(
                np.rint(seed_form).astype(int),
                EXPECTED_THREE_U,
            ),
            "first_refinement_form_is_exact_120_times_3u": np.array_equal(
                np.rint(refined_form).astype(int),
                120 * EXPECTED_THREE_U,
            ),
            "normalized_three_u_block_is_refinement_invariant": np.allclose(
                _normalized_form(seed_form),
                _normalized_form(refined_form),
                atol=1e-8,
            ),
            "three_u_signature_survives_first_refinement": (
                seed_signature == (3, 3) and refined_signature == (3, 3)
            ),
            "three_u_determinant_scales_by_120_to_the_6": int(
                round(np.linalg.det(refined_form) / np.linalg.det(seed_form))
            )
            == 120**6,
        },
        "bridge_verdict": (
            "The explicit K3 hyperbolic core is not merely present on the seed. "
            "The same ordered-simplex pullback that preserves the canonical mixed "
            "selector also carries the full primitive 3U block to exactly 120 "
            "times itself. So the normalized hyperbolic core is already "
            "refinement-invariant at first barycentric order on the explicit K3 host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_three_u_refinement_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
