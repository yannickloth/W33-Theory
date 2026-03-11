"""UOR-style Z2 shadow of the exact W33 transport holonomy.

The strongest structural clue in the external UOR framework is not the
Monster numerology. It is the combination of:

1. coefficient-level cohomology over Z/2Z;
2. monodromy / holonomy observables;
3. lift-obstruction language that remembers a binary shadow of richer
   transport data.

The exact W33 transport package now realizes that pattern concretely:

  - the native local transport group is Weyl(A2) ~= S3 ~= D3;
  - its determinant / sign character gives a surjective map to Z2;
  - the old v14 triangle parity is exactly that sign shadow on triangle
    holonomy;
  - parity-0 conflates identity holonomy with 3-cycles, so the Z2 shadow
    forgets real non-abelian information.

This makes the right UOR-style bridge precise: the meaningful binary shadow on
the W33 transport side is the holonomy sign, not the raw edge-voltage bit.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from w33_center_quad_transport_a2_bridge import a2_weyl_matrix
from w33_center_quad_transport_bridge import reconstructed_quotient_graph
from w33_center_quad_transport_complement_bridge import permutation_parity
from w33_center_quad_transport_holonomy_bridge import (
    build_center_quad_transport_holonomy_summary,
    edge_line_matching,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_uor_transport_shadow_bridge_summary.json"


def _matrix_key(matrix: np.ndarray) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(entry) for entry in row) for row in matrix.tolist())


def _multiply_keys(
    left: tuple[tuple[int, ...], ...],
    right: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    left_matrix = np.array(left, dtype=int)
    right_matrix = np.array(right, dtype=int)
    return _matrix_key(left_matrix @ right_matrix)


def _determinant_sign(matrix_key: tuple[tuple[int, ...], ...]) -> int:
    determinant = int(round(float(np.linalg.det(np.array(matrix_key, dtype=float)))))
    if determinant not in {-1, 1}:
        raise AssertionError("expected Weyl(A2) determinant to be +/-1")
    return 0 if determinant == 1 else 1


def _weyl_group_closure(
    generators: set[tuple[tuple[int, ...], ...]]
) -> set[tuple[tuple[int, ...], ...]]:
    closure = set(generators)
    changed = True
    while changed:
        changed = False
        snapshot = list(closure)
        for left in snapshot:
            for right in snapshot:
                product = _multiply_keys(left, right)
                if product not in closure:
                    closure.add(product)
                    changed = True
    return closure


@lru_cache(maxsize=1)
def build_w33_uor_transport_shadow_summary() -> dict[str, Any]:
    holonomy = build_center_quad_transport_holonomy_summary()
    graph, _ = reconstructed_quotient_graph()

    edge_weyl_matrices: set[tuple[tuple[int, ...], ...]] = set()
    edge_parity_classes: dict[int, set[tuple[tuple[int, ...], ...]]] = defaultdict(set)
    permutation_parity_classes = Counter()

    for left, right in sorted(graph.edges()):
        permutation = edge_line_matching(left, right)
        parity = permutation_parity(permutation)
        permutation_parity_classes[parity] += 1
        matrix_key = _matrix_key(a2_weyl_matrix(permutation))
        edge_weyl_matrices.add(matrix_key)
        edge_parity_classes[parity].add(matrix_key)

    group_closure = _weyl_group_closure(edge_weyl_matrices)
    determinant_kernel = {matrix_key for matrix_key in group_closure if _determinant_sign(matrix_key) == 0}
    determinant_coset = {matrix_key for matrix_key in group_closure if _determinant_sign(matrix_key) == 1}

    triangle_cycle_counts = holonomy["triangle_holonomy"]["cycle_type_counts"]
    even_triangle_types = {
        key: value
        for key, value in triangle_cycle_counts.items()
        if key in {"identity", "three_cycle"}
    }
    odd_triangle_types = {
        key: value
        for key, value in triangle_cycle_counts.items()
        if key == "transposition"
    }

    return {
        "status": "ok",
        "uor_alignment": {
            "coefficient_shadow_ring": "Z/2Z",
            "nonabelian_transport_group": "Weyl(A2) ~= S3 ~= D3",
            "shadow_character": "det = sign: Weyl(A2) -> {+1,-1} ~= Z/2Z",
            "right_binary_shadow_is_holonomy_sign_not_raw_edge_voltage": True,
        },
        "weyl_group_shadow": {
            "realized_edge_weyl_matrices": len(edge_weyl_matrices),
            "group_closure_order": len(group_closure),
            "sign_kernel_order": len(determinant_kernel),
            "sign_nontrivial_coset_order": len(determinant_coset),
            "even_weyl_edge_classes": len(edge_parity_classes[0]),
            "odd_weyl_edge_classes": len(edge_parity_classes[1]),
            "edge_sign_character_is_surjective": bool(edge_parity_classes[0] and edge_parity_classes[1]),
            "transport_edge_counts_by_permutation_parity": dict(sorted(permutation_parity_classes.items())),
        },
        "triangle_shadow": {
            "triangle_cycle_type_counts": dict(sorted(triangle_cycle_counts.items())),
            "even_triangle_types": even_triangle_types,
            "odd_triangle_types": odd_triangle_types,
            "triangle_parity_equals_holonomy_sign_exactly": holonomy["triangle_holonomy"][
                "z2_parity_equals_holonomy_sign_exactly"
            ],
            "z2_shadow_forgets_identity_vs_three_cycle": (
                even_triangle_types.get("identity", 0) > 0
                and even_triangle_types.get("three_cycle", 0) > 0
            ),
        },
        "bridge_verdict": (
            "The strongest exact UOR-style bridge on the transport side is a "
            "binary shadow theorem. The full local holonomy group carried by the "
            "W33 quotient transport graph is Weyl(A2) ~= S3 ~= D3, but its "
            "determinant / sign character gives an exact Z2 shadow. The old v14 "
            "triangle parity is exactly that sign on triangle holonomy, while "
            "parity-0 conflates identity holonomy with 3-cycles. So the binary "
            "shadow is real, but it is only the coefficient-level shadow of a "
            "genuinely non-abelian local system."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_w33_uor_transport_shadow_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
