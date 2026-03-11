"""Native A2 local-system realization of the W33 transport standard sector.

The 90-dimensional standard sector of the transport bundle is not an arbitrary
projected block. It is the canonical A2 root-lattice local system carried by
the exact 45-point quotient transport graph:

1. Each quotient point has 3 incident quotient lines, hence a local S3 action.
2. The difference lattice of those three local line states is the A2 root
   lattice of rank 2.
3. Every transport edge carries a unique local line matching, hence a Weyl(A2)
   matrix.
4. The resulting 90-dimensional transport operator is the exact native A2
   local-system operator over the quotient geometry.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from w33_center_quad_transport_bridge import reconstructed_quotient_graph
from w33_center_quad_transport_complement_bridge import permutation_parity
from w33_center_quad_transport_holonomy_bridge import (
    cycle_type,
    directed_edge_matching,
    edge_line_matching,
    permutation_compose,
)
from w33_center_quad_transport_operator_bridge import (
    TOL,
    local_trivial_and_standard_bases,
    transport_connection_adjacency,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_center_quad_transport_a2_bridge_summary.json"

A2_ROOT_BASIS = np.array([[1, 0], [-1, 1], [0, -1]], dtype=int)
A2_CARTAN = np.array([[2, -1], [-1, 2]], dtype=int)
A2_DUAL_LEFT_INVERSE = np.array([[2, -1, -1], [1, 1, -2]], dtype=float) / 3.0


def permutation_matrix(permutation: tuple[int, int, int]) -> np.ndarray:
    matrix = np.zeros((3, 3), dtype=int)
    for source, target in enumerate(permutation):
        matrix[source, target] = 1
    return matrix


def a2_weyl_matrix(permutation: tuple[int, int, int]) -> np.ndarray:
    matrix = A2_DUAL_LEFT_INVERSE @ permutation_matrix(permutation) @ A2_ROOT_BASIS
    result = np.rint(matrix).astype(int)
    if np.max(np.abs(matrix - result)) > TOL:
        raise AssertionError("expected integral A2 Weyl matrix")
    return result


@lru_cache(maxsize=1)
def a2_transport_operator() -> np.ndarray:
    graph, _ = reconstructed_quotient_graph()
    node_count = graph.number_of_nodes()
    operator = np.zeros((2 * node_count, 2 * node_count), dtype=int)
    for left, right in sorted(graph.edges()):
        forward = a2_weyl_matrix(edge_line_matching(left, right))
        reverse = a2_weyl_matrix(edge_line_matching(right, left))
        operator[2 * left : 2 * left + 2, 2 * right : 2 * right + 2] = forward
        operator[2 * right : 2 * right + 2, 2 * left : 2 * left + 2] = reverse
    return operator


def a2_character_trace(permutation: tuple[int, int, int]) -> int:
    return int(np.trace(a2_weyl_matrix(permutation)))


def rounded_real_spectrum(matrix: np.ndarray) -> dict[int, int]:
    eigenvalues = np.linalg.eigvals(matrix)
    rounded = []
    for value in eigenvalues:
        if abs(float(value.imag)) > TOL:
            raise AssertionError("expected real spectrum")
        rounded.append(int(round(float(value.real))))
    if max(abs(float(value.real) - rounded_value) for value, rounded_value in zip(eigenvalues, rounded)) > TOL:
        raise AssertionError("expected integer spectrum")
    return dict(sorted(Counter(rounded).items()))


def local_standard_basis() -> np.ndarray:
    node_count = reconstructed_quotient_graph()[0].number_of_nodes()
    _, standard_basis = local_trivial_and_standard_bases(node_count)
    return standard_basis[:3, :2]


def standard_sector_similarity_error() -> float:
    node_count = reconstructed_quotient_graph()[0].number_of_nodes()
    full = transport_connection_adjacency()
    _, standard_basis = local_trivial_and_standard_bases(node_count)
    standard_block = standard_basis.T @ full @ standard_basis
    local_change = local_standard_basis().T @ A2_ROOT_BASIS
    global_change = np.zeros((2 * node_count, 2 * node_count), dtype=float)
    for node in range(node_count):
        global_change[2 * node : 2 * node + 2, 2 * node : 2 * node + 2] = local_change
    a2_operator = a2_transport_operator().astype(float)
    return float(np.max(np.abs(global_change @ a2_operator - standard_block @ global_change)))


@lru_cache(maxsize=1)
def build_center_quad_transport_a2_summary() -> dict[str, Any]:
    graph, _ = reconstructed_quotient_graph()
    operator = a2_transport_operator()
    edge_matrix_counts = Counter()
    parity_match = True
    for left, right in sorted(graph.edges()):
        permutation = edge_line_matching(left, right)
        matrix = a2_weyl_matrix(permutation)
        edge_matrix_counts[tuple(map(tuple, matrix))] += 1
        if round(np.linalg.det(matrix)) != (-1 if permutation_parity(permutation) else 1):
            parity_match = False

    cycle_type_counts = Counter()
    character_sum = 0
    triangle_count = 0
    for a, b, c in combinations(sorted(graph.nodes()), 3):
        if not (graph.has_edge(a, b) and graph.has_edge(a, c) and graph.has_edge(b, c)):
            continue
        holonomy = permutation_compose(
            directed_edge_matching(a, b),
            permutation_compose(directed_edge_matching(b, c), directed_edge_matching(c, a)),
        )
        cycle_type_counts[cycle_type(holonomy)] += 1
        character_sum += a2_character_trace(holonomy)
        triangle_count += 1

    cubic_relation = operator @ operator @ operator + 9 * (operator @ operator) - 120 * operator
    cubic_relation -= 128 * np.eye(operator.shape[0], dtype=int)

    return {
        "status": "ok",
        "local_a2_fiber": {
            "rank": 2,
            "cartan_matrix": A2_CARTAN.tolist(),
            "weyl_group_order": 6,
            "simple_root_basis": A2_ROOT_BASIS.tolist(),
            "all_six_weyl_matrices_realized": len(edge_matrix_counts) == 6,
            "edge_matrix_counts": {
                str([list(row) for row in matrix]): count
                for matrix, count in sorted(edge_matrix_counts.items())
            },
            "all_edge_weyl_matrices_preserve_cartan": all(
                np.array_equal(np.array(matrix).T @ A2_CARTAN @ np.array(matrix), A2_CARTAN)
                for matrix in edge_matrix_counts
            ),
            "determinant_character_equals_permutation_parity": parity_match,
        },
        "a2_transport_operator": {
            "dimension": int(operator.shape[0]),
            "spectrum": rounded_real_spectrum(operator.astype(float)),
            "laplacian_spectrum": rounded_real_spectrum(
                32.0 * np.eye(operator.shape[0]) - operator.astype(float)
            ),
            "trace_h_squared": int(np.trace(operator @ operator)),
            "trace_h_cubed": int(np.trace(operator @ operator @ operator)),
            "cubic_relation_h3_plus_9h2_minus_120h_minus_128i": bool(
                np.array_equal(cubic_relation, np.zeros_like(cubic_relation))
            ),
            "matches_standard_sector_up_to_fixed_local_basis_change": (
                standard_sector_similarity_error() < TOL
            ),
        },
        "triangle_character_formula": {
            "transport_triangles": triangle_count,
            "holonomy_cycle_type_counts": dict(sorted(cycle_type_counts.items())),
            "a2_character_values": {
                "identity": 2,
                "three_cycle": -1,
                "transposition": 0,
            },
            "character_sum_over_triangle_holonomies": character_sum,
            "trace_h_cubed_equals_six_character_sum": int(np.trace(operator @ operator @ operator))
            == 6 * character_sum,
        },
        "bridge_verdict": (
            "The 90-dimensional standard transport sector is a native W33 object: "
            "it is the A2 root-lattice local system over the exact 45-point "
            "center-quad quotient transport graph. The local S3 line-matchings on "
            "transport edges act by exact Weyl(A2) matrices preserving the A2 "
            "Cartan form, their determinant character is exactly the transport "
            "parity sign, and the resulting 90-dimensional operator has exact "
            "spectrum 8, -1, -16 and exact cubic relation H^3 + 9H^2 - 120H - "
            "128I = 0. So the standard block is not auxiliary projection data; it "
            "is the canonical A2 local-system operator already carried by the exact "
            "quotient geometry."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_center_quad_transport_a2_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
