"""First barycentric persistence of the selector-versus-3U shadow split.

The K3-side bridge now has three exact seed-level objects:

1. the canonical mixed harmonic selector plane;
2. its cup-orthogonal positive-definite shadow on the primitive ``3U`` core;
3. its cup-orthogonal negative-definite residual on the orthogonal rank-16
   complement.

This module checks whether that whole split survives the first barycentric
refinement on the explicit ``K3_16`` seed. It does: all three restricted forms
scale by the same exact factor ``120 = 5!``.
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
from w33_k3_selector_three_u_shadow_bridge import selector_three_u_shadow_bases


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_selector_shadow_refinement_bridge_summary.json"
TOL = 1e-8


def _matrix_to_list(matrix: np.ndarray) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix.tolist()]


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > TOL))
    negative = int(np.sum(eigenvalues < -TOL))
    return positive, negative


def _seed_form(cochain_basis: np.ndarray) -> np.ndarray:
    facets = _facets("K3")
    faces = faces_by_dimension(facets)
    return _cup_matrix_on_h2(
        faces[2],
        facets,
        _oriented_fundamental_class(facets),
        cochain_basis,
    )


def _normalized_form(matrix: np.ndarray) -> np.ndarray:
    determinant = float(np.linalg.det(matrix))
    if abs(determinant) < TOL:
        raise AssertionError("expected a nondegenerate restricted form")
    return matrix / np.sqrt(abs(determinant))


@lru_cache(maxsize=1)
def build_k3_selector_shadow_refinement_bridge_summary() -> dict[str, Any]:
    bases = selector_three_u_shadow_bases()
    selector = bases["selector_cochain_basis"]
    shadow = bases["three_u_shadow_cochain_basis"]
    residual = bases["rank16_residual_cochain_basis"]

    selector_seed = _seed_form(selector)
    selector_refined = restricted_first_barycentric_pullback_form(selector)
    shadow_seed = _seed_form(shadow)
    shadow_refined = restricted_first_barycentric_pullback_form(shadow)
    residual_seed = _seed_form(residual)
    residual_refined = restricted_first_barycentric_pullback_form(residual)

    if not np.allclose(selector_refined, 120 * selector_seed, atol=1e-8):
        raise AssertionError("expected selector plane to scale by 120")
    if not np.allclose(shadow_refined, 120 * shadow_seed, atol=1e-8):
        raise AssertionError("expected three_u shadow to scale by 120")
    if not np.allclose(residual_refined, 120 * residual_seed, atol=1e-8):
        raise AssertionError("expected rank16 residual to scale by 120")

    shadow_seed_sig = _signature_counts(shadow_seed)
    shadow_refined_sig = _signature_counts(shadow_refined)
    residual_seed_sig = _signature_counts(residual_seed)
    residual_refined_sig = _signature_counts(residual_refined)

    return {
        "status": "ok",
        "selector_seed_form": _matrix_to_list(selector_seed),
        "selector_first_refinement_form": _matrix_to_list(selector_refined),
        "three_u_shadow_seed_form": _matrix_to_list(shadow_seed),
        "three_u_shadow_first_refinement_form": _matrix_to_list(shadow_refined),
        "rank16_residual_seed_form": _matrix_to_list(residual_seed),
        "rank16_residual_first_refinement_form": _matrix_to_list(residual_refined),
        "selector_shadow_refinement_theorem": {
            "selector_plane_scales_by_120": True,
            "three_u_shadow_scales_by_120": True,
            "rank16_residual_scales_by_120": True,
            "normalized_selector_form_is_refinement_invariant": np.allclose(
                _normalized_form(selector_seed),
                _normalized_form(selector_refined),
                atol=1e-8,
            ),
            "normalized_three_u_shadow_form_is_refinement_invariant": np.allclose(
                _normalized_form(shadow_seed),
                _normalized_form(shadow_refined),
                atol=1e-8,
            ),
            "normalized_rank16_residual_form_is_refinement_invariant": np.allclose(
                _normalized_form(residual_seed),
                _normalized_form(residual_refined),
                atol=1e-8,
            ),
            "three_u_shadow_stays_positive_definite": (
                shadow_seed_sig == (2, 0) and shadow_refined_sig == (2, 0)
            ),
            "rank16_residual_stays_negative_definite": (
                residual_seed_sig == (0, 2) and residual_refined_sig == (0, 2)
            ),
        },
        "bridge_verdict": (
            "The selector-versus-core split is not a seed-only accident. On the "
            "explicit K3 chain model, the canonical selector plane, its "
            "positive-definite shadow on the primitive 3U core, and its "
            "negative-definite residual on the rank-16 complement all scale by "
            "the same exact factor 120 under first barycentric pullback. So the "
            "core/complement split itself survives the first exact refinement "
            "step without changing normalized signature data."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_selector_shadow_refinement_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
