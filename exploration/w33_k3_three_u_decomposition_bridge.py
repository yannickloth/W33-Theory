"""Explicit primitive orthogonal 3U core inside the integral K3 lattice.

The explicit ``K3_16`` simplicial cochain complex already yields the full even
unimodular ``H^2(K3, Z)`` lattice of signature ``(3,19)``. The previous bridge
step isolated one canonical primitive hyperbolic plane ``U`` inside that
lattice. This module upgrades that further.

It records three explicit pairwise orthogonal primitive hyperbolic planes in
the same integral basis. Together they form an orthogonal ``3U`` block inside
the actual K3 lattice carried by the explicit seed. A unit maximal minor of the
resulting ``22 x 6`` coefficient matrix proves that this ``3U`` block is a
primitive sublattice of the ambient unimodular lattice.

Since both the ambient lattice and the ``3U`` block are unimodular, lattice
theory then forces an orthogonal direct-sum decomposition

    H^2(K3, Z) = 3U (+) N_16,

where ``N_16`` is an even unimodular negative-definite rank-16 lattice.
"""

from __future__ import annotations

from functools import lru_cache
import itertools
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

from w33_k3_integral_h2_lattice_bridge import (
    build_k3_integral_h2_lattice_bridge_summary,
    integral_k3_h2_basis_matrix,
    integral_k3_h2_intersection_matrix,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_three_u_decomposition_bridge_summary.json"
TOL = 1e-8


def _vector(values: list[int]) -> np.ndarray:
    return np.asarray(values, dtype=int)


def k3_three_u_block_coefficients() -> np.ndarray:
    """Return the explicit 22 x 6 coefficient matrix of the orthogonal 3U core."""
    v1 = _vector([0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0])
    w1 = _vector([0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0])
    v2 = _vector([0, -1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0])
    w2 = _vector([0, -1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1])
    v3 = _vector([0, -1, 0, 1, 1, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    w3 = _vector([1, -4, 0, 6, 6, 1, 0, 0, 0, -6, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0])
    return np.column_stack((v1, w1, v2, w2, v3, w3))


def k3_three_u_block_cochains() -> np.ndarray:
    return integral_k3_h2_basis_matrix() @ k3_three_u_block_coefficients()


def _integer_signature(matrix: np.ndarray) -> tuple[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix.astype(float))
    return int(np.sum(eigenvalues > TOL)), int(np.sum(eigenvalues < -TOL))


def _bareiss_determinant(matrix: np.ndarray) -> int:
    """Exact integer determinant via fraction-free elimination."""
    work = [[int(value) for value in row] for row in matrix.tolist()]
    size = len(work)
    sign = 1
    previous_pivot = 1

    for pivot_index in range(size - 1):
        if work[pivot_index][pivot_index] == 0:
            swap_index = None
            for row_index in range(pivot_index + 1, size):
                if work[row_index][pivot_index] != 0:
                    swap_index = row_index
                    break
            if swap_index is None:
                return 0
            work[pivot_index], work[swap_index] = work[swap_index], work[pivot_index]
            sign *= -1

        pivot = work[pivot_index][pivot_index]
        for row_index in range(pivot_index + 1, size):
            for col_index in range(pivot_index + 1, size):
                numerator = (
                    work[row_index][col_index] * pivot
                    - work[row_index][pivot_index] * work[pivot_index][col_index]
                )
                work[row_index][col_index] = numerator // previous_pivot
            work[row_index][pivot_index] = 0
        previous_pivot = pivot

    return sign * work[-1][-1]


def _first_unit_maximal_minor(matrix: np.ndarray) -> tuple[tuple[int, ...], int]:
    rows, cols = matrix.shape
    if rows < cols:
        raise ValueError("expected a tall coefficient matrix")

    for row_indices in itertools.combinations(range(rows), cols):
        minor = matrix[np.asarray(row_indices, dtype=int), :]
        determinant = _bareiss_determinant(minor)
        if abs(determinant) == 1:
            return tuple(int(index) for index in row_indices), int(determinant)
    raise AssertionError("expected a unit maximal minor witnessing primitivity")


@lru_cache(maxsize=1)
def build_k3_three_u_decomposition_bridge_summary() -> dict[str, Any]:
    ambient = build_k3_integral_h2_lattice_bridge_summary()
    ambient_profile = ambient["integral_lattice_profile"]
    ambient_intersection = integral_k3_h2_intersection_matrix()
    block = k3_three_u_block_coefficients()
    block_gram = (block.T @ ambient_intersection @ block).astype(int)
    block_positive, block_negative = _integer_signature(block_gram)
    unit_minor_rows, unit_minor_det = _first_unit_maximal_minor(block)

    ambient_positive = int(ambient_profile["positive_directions"])
    ambient_negative = int(ambient_profile["negative_directions"])
    complement_positive = ambient_positive - block_positive
    complement_negative = ambient_negative - block_negative
    complement_rank = complement_positive + complement_negative

    block_det = _bareiss_determinant(block_gram)
    ambient_is_even_unimodular = bool(
        ambient_profile["diagonal_even"] and ambient_profile["unimodular"]
    )
    block_is_three_u = np.array_equal(
        block_gram,
        np.asarray(
            [
                [0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1, 0],
            ],
            dtype=int,
        ),
    )
    block_is_primitive = abs(unit_minor_det) == 1
    block_is_even_unimodular = block_is_three_u and abs(block_det) == 1
    complement_is_even_negative_unimodular = bool(
        ambient_is_even_unimodular
        and block_is_even_unimodular
        and block_is_primitive
        and complement_positive == 0
        and complement_negative == 16
    )

    return {
        "status": "ok",
        "three_u_block_vectors": {
            "v1": block[:, 0].astype(int).tolist(),
            "w1": block[:, 1].astype(int).tolist(),
            "v2": block[:, 2].astype(int).tolist(),
            "w2": block[:, 3].astype(int).tolist(),
            "v3": block[:, 4].astype(int).tolist(),
            "w3": block[:, 5].astype(int).tolist(),
        },
        "three_u_block_supports": {
            "v1": np.nonzero(block[:, 0])[0].astype(int).tolist(),
            "w1": np.nonzero(block[:, 1])[0].astype(int).tolist(),
            "v2": np.nonzero(block[:, 2])[0].astype(int).tolist(),
            "w2": np.nonzero(block[:, 3])[0].astype(int).tolist(),
            "v3": np.nonzero(block[:, 4])[0].astype(int).tolist(),
            "w3": np.nonzero(block[:, 5])[0].astype(int).tolist(),
        },
        "three_u_block_gram_matrix": block_gram.tolist(),
        "three_u_block_profile": {
            "rank": 6,
            "determinant": block_det,
            "positive_directions": block_positive,
            "negative_directions": block_negative,
            "unit_maximal_minor_rows": list(unit_minor_rows),
            "unit_maximal_minor_determinant": unit_minor_det,
        },
        "orthogonal_complement_profile": {
            "rank": complement_rank,
            "positive_directions": complement_positive,
            "negative_directions": complement_negative,
            "determinant": 1 if complement_is_even_negative_unimodular else None,
            "diagonal_even": complement_is_even_negative_unimodular,
            "unimodular": complement_is_even_negative_unimodular,
        },
        "three_u_decomposition_theorem": {
            "explicit_vectors_realize_orthogonal_three_u_block": block_is_three_u,
            "three_u_block_has_signature_3_3": block_positive == 3 and block_negative == 3,
            "three_u_block_is_primitive_in_the_ambient_lattice": block_is_primitive,
            "ambient_k3_lattice_is_even_unimodular_signature_3_19": ambient_is_even_unimodular
            and ambient_positive == 3
            and ambient_negative == 19,
            "orthogonal_complement_has_rank_16": complement_rank == 16,
            "orthogonal_complement_is_even_negative_definite_unimodular": (
                complement_is_even_negative_unimodular
            ),
            "explicit_k3_seed_contains_primitive_orthogonal_3U_core": (
                block_is_three_u and block_is_primitive
            ),
        },
        "bridge_verdict": (
            "The explicit K3 seed does not merely carry one primitive hyperbolic "
            "plane. In the actual integral H^2 lattice extracted from the "
            "simplicial cochain complex, there are already three pairwise "
            "orthogonal primitive hyperbolic planes with block Gram 3U. A unit "
            "maximal minor witnesses that this 3U block is primitive in the "
            "ambient even unimodular K3 lattice, so the orthogonal complement is "
            "forced to be an even unimodular negative-definite rank-16 lattice. "
            "The bridge host is therefore already a full hyperbolic core on the "
            "explicit K3 seed, not just one isolated rank-2 plane."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_three_u_decomposition_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
