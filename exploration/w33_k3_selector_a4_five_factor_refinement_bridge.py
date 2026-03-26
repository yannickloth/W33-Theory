"""First-refinement rigidity of the fine selector-side ``A4`` split on K3.

After resolving the selector-side reduced external packet over the five named
pieces

    U1, U2, U3, E8_1, E8_2,

the next exact question is whether those individual pieces survive the first
barycentric pullback or whether only the coarser ``3U (+) E8 (+) E8`` grouping
is rigid.

They survive individually. On the explicit ``K3_16`` chain model, the
restricted form on every one of the five packet pieces is carried exactly to
``120`` times itself at ``sd^1``.
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
    SIGN_TOL,
    _cup_matrix_on_h2,
    _facets,
    _oriented_fundamental_class,
)
from w33_explicit_curved_4d_complexes import faces_by_dimension
from w33_k3_refined_plane_persistence_bridge import restricted_first_barycentric_pullback_form
from w33_k3_selector_a4_five_factor_bridge import (
    FACTOR_ORDER,
    selector_five_factor_cochain_components,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_selector_a4_five_factor_refinement_bridge_summary.json"
TOL = 1e-8


def _matrix_to_list(matrix: np.ndarray) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix.tolist()]


def _signature_counts(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    positive = int(np.sum(eigenvalues > SIGN_TOL))
    negative = int(np.sum(eigenvalues < -SIGN_TOL))
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
        raise AssertionError("expected nondegenerate restricted form")
    return matrix / np.sqrt(abs(determinant))


@lru_cache(maxsize=1)
def build_k3_selector_a4_five_factor_refinement_bridge_summary() -> dict[str, Any]:
    cochain_components = selector_five_factor_cochain_components()
    seed_forms = {
        name: _seed_form(component)
        for name, component in cochain_components.items()
    }
    refined_forms = {
        name: restricted_first_barycentric_pullback_form(component)
        for name, component in cochain_components.items()
    }

    for name in FACTOR_ORDER:
        if not np.allclose(refined_forms[name], 120 * seed_forms[name], atol=1e-8):
            raise AssertionError(f"expected {name} packet piece to scale by 120")

    return {
        "status": "ok",
        "u_factor_one_seed_form": _matrix_to_list(seed_forms["U1"]),
        "u_factor_one_first_refinement_form": _matrix_to_list(refined_forms["U1"]),
        "u_factor_two_seed_form": _matrix_to_list(seed_forms["U2"]),
        "u_factor_two_first_refinement_form": _matrix_to_list(refined_forms["U2"]),
        "u_factor_three_seed_form": _matrix_to_list(seed_forms["U3"]),
        "u_factor_three_first_refinement_form": _matrix_to_list(refined_forms["U3"]),
        "e8_factor_one_seed_form": _matrix_to_list(seed_forms["E8_1"]),
        "e8_factor_one_first_refinement_form": _matrix_to_list(refined_forms["E8_1"]),
        "e8_factor_two_seed_form": _matrix_to_list(seed_forms["E8_2"]),
        "e8_factor_two_first_refinement_form": _matrix_to_list(refined_forms["E8_2"]),
        "selector_a4_five_factor_refinement_theorem": {
            "u_factor_one_packet_piece_scales_by_120": True,
            "u_factor_two_packet_piece_scales_by_120": True,
            "u_factor_three_packet_piece_scales_by_120": True,
            "e8_factor_one_packet_piece_scales_by_120": True,
            "e8_factor_two_packet_piece_scales_by_120": True,
            "all_five_normalized_packet_forms_are_refinement_invariant": all(
                np.allclose(
                    _normalized_form(seed_forms[name]),
                    _normalized_form(refined_forms[name]),
                    atol=1e-8,
                )
                for name in FACTOR_ORDER
            ),
            "all_three_u_factor_packet_pieces_stay_mixed_signature": all(
                _signature_counts(seed_forms[name]) == (1, 1)
                and _signature_counts(refined_forms[name]) == (1, 1)
                for name in ("U1", "U2", "U3")
            ),
            "both_e8_packet_pieces_stay_negative_definite": all(
                _signature_counts(seed_forms[name]) == (0, 2)
                and _signature_counts(refined_forms[name]) == (0, 2)
                for name in ("E8_1", "E8_2")
            ),
            "fine_selector_packet_split_is_first_refinement_rigid": True,
        },
        "bridge_verdict": (
            "The selector-side reduced A4 packet is now first-refinement rigid "
            "down to its finest current named split. On the explicit K3 chain "
            "model, each of U1, U2, U3, E8_1, and E8_2 is carried by the first "
            "barycentric pullback to exactly 120 times itself. So the finer "
            "five-factor packet decomposition is not a seed-only artifact: it "
            "already survives the first exact refinement step piece by piece."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_selector_a4_five_factor_refinement_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
