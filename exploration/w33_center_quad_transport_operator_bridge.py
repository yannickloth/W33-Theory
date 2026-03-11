"""Operator-level transport bundle on the exact W33 center-quad quotient.

Each edge of the exact 45-point quotient transport graph carries a unique
permutation of the three quotient lines through its endpoints. This gives a
canonical rank-3 permutation-bundle connection over the transport graph.

The exact statements established here are:

1. The resulting connection adjacency acts on a 135-dimensional bundle
   (45 points x 3 local lines).
2. Because every edge permutation fixes the all-ones vector, the bundle splits
   exactly as a 45-dimensional trivial sector plus a 90-dimensional standard
   sector.
3. The trivial sector is exactly the adjacency of the transport graph
   SRG(45,32,22,24).
4. The 90-dimensional standard sector has exact integer spectrum
   8^20, (-1)^64, (-16)^6.
5. Taking only the parity of each edge permutation gives a signed line-bundle
   operator S with exact quadratic identity S^2 = 4S + 32I and spectrum
   8^15, (-4)^30.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

from w33_center_quad_transport_bridge import (
    quotient_triangle_parity_stats,
    reconstructed_quotient_graph,
)
from w33_center_quad_transport_complement_bridge import permutation_parity
from w33_center_quad_transport_holonomy_bridge import edge_line_matching


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_center_quad_transport_operator_bridge_summary.json"
TOL = 1e-8


def permutation_matrix(permutation: tuple[int, int, int]) -> np.ndarray:
    matrix = np.zeros((3, 3), dtype=float)
    for source, target in enumerate(permutation):
        matrix[source, target] = 1.0
    return matrix


def transport_connection_adjacency() -> np.ndarray:
    graph, _ = reconstructed_quotient_graph()
    node_count = graph.number_of_nodes()
    matrix = np.zeros((3 * node_count, 3 * node_count), dtype=float)
    for left, right in sorted(graph.edges()):
        block = permutation_matrix(edge_line_matching(left, right))
        matrix[3 * left : 3 * left + 3, 3 * right : 3 * right + 3] = block
        matrix[3 * right : 3 * right + 3, 3 * left : 3 * left + 3] = block.T
    return matrix


def signed_matching_adjacency() -> np.ndarray:
    graph, _ = reconstructed_quotient_graph()
    node_count = graph.number_of_nodes()
    matrix = np.zeros((node_count, node_count), dtype=int)
    for left, right in sorted(graph.edges()):
        sign = -1 if permutation_parity(edge_line_matching(left, right)) else 1
        matrix[left, right] = sign
        matrix[right, left] = sign
    return matrix


def local_trivial_and_standard_bases(node_count: int) -> tuple[np.ndarray, np.ndarray]:
    trivial = np.array([1.0, 1.0, 1.0], dtype=float) / np.sqrt(3.0)
    standard_1 = np.array([1.0, -1.0, 0.0], dtype=float) / np.sqrt(2.0)
    standard_2 = np.array([1.0, 1.0, -2.0], dtype=float) / np.sqrt(6.0)

    trivial_basis = np.zeros((3 * node_count, node_count), dtype=float)
    standard_basis = np.zeros((3 * node_count, 2 * node_count), dtype=float)
    for node in range(node_count):
        trivial_basis[3 * node : 3 * node + 3, node] = trivial
        standard_basis[3 * node : 3 * node + 3, 2 * node] = standard_1
        standard_basis[3 * node : 3 * node + 3, 2 * node + 1] = standard_2
    return trivial_basis, standard_basis


def rounded_integer_spectrum(matrix: np.ndarray) -> dict[int, int]:
    eigenvalues = np.linalg.eigvalsh(matrix)
    rounded = [int(round(float(value))) for value in eigenvalues]
    if max(abs(float(value) - rounded_value) for value, rounded_value in zip(eigenvalues, rounded)) > TOL:
        raise AssertionError("expected integer spectrum")
    return dict(sorted(Counter(rounded).items()))


def _transport_adjacency_matrix() -> np.ndarray:
    graph, _ = reconstructed_quotient_graph()
    return nx.to_numpy_array(graph, nodelist=sorted(graph.nodes()), dtype=float)


def build_center_quad_transport_operator_summary() -> dict[str, Any]:
    graph, _ = reconstructed_quotient_graph()
    node_count = graph.number_of_nodes()
    full = transport_connection_adjacency()
    trivial_basis, standard_basis = local_trivial_and_standard_bases(node_count)
    trivial_block = trivial_basis.T @ full @ trivial_basis
    standard_block = standard_basis.T @ full @ standard_basis
    cross_block = trivial_basis.T @ full @ standard_basis
    sign_block = signed_matching_adjacency()
    transport_adjacency = _transport_adjacency_matrix()
    triangle_stats = quotient_triangle_parity_stats()

    quadratic_identity = sign_block @ sign_block - 4 * sign_block - 32 * np.eye(node_count, dtype=int)
    signed_triangle_excess = triangle_stats["parity0"] - triangle_stats["parity1"]

    return {
        "status": "ok",
        "connection_bundle": {
            "base_vertices": node_count,
            "fiber_dimension": 3,
            "total_dimension": int(full.shape[0]),
            "adjacency_spectrum": rounded_integer_spectrum(full),
            "laplacian_spectrum": rounded_integer_spectrum(32.0 * np.eye(full.shape[0]) - full),
            "trace_a_squared": int(round(float(np.trace(full @ full)))),
            "trace_a_cubed": int(round(float(np.trace(full @ full @ full)))),
        },
        "trivial_standard_split": {
            "trivial_dimension": int(trivial_block.shape[0]),
            "standard_dimension": int(standard_block.shape[0]),
            "trivial_standard_coupling_max_abs": float(np.max(np.abs(cross_block))),
            "trivial_block_equals_transport_adjacency": float(
                np.max(np.abs(trivial_block - transport_adjacency))
            )
            < TOL,
            "trivial_block_spectrum": rounded_integer_spectrum(trivial_block),
            "standard_block_spectrum": rounded_integer_spectrum(standard_block),
            "standard_block_laplacian_spectrum": rounded_integer_spectrum(
                32.0 * np.eye(standard_block.shape[0]) - standard_block
            ),
            "standard_block_cubic_relation_exact_up_to_tolerance": float(
                np.max(
                    np.abs(
                        standard_block @ standard_block @ standard_block
                        + 9.0 * (standard_block @ standard_block)
                        - 120.0 * standard_block
                        - 128.0 * np.eye(standard_block.shape[0])
                    )
                )
            )
            < TOL,
        },
        "signed_holonomy_operator": {
            "dimension": int(sign_block.shape[0]),
            "spectrum": rounded_integer_spectrum(sign_block.astype(float)),
            "quadratic_identity_s_squared_equals_4s_plus_32i": bool(
                np.array_equal(quadratic_identity, np.zeros_like(quadratic_identity))
            ),
            "laplacian_spectrum": rounded_integer_spectrum(32.0 * np.eye(node_count) - sign_block),
            "trace_s_squared": int(np.trace(sign_block @ sign_block)),
            "trace_s_cubed": int(np.trace(sign_block @ sign_block @ sign_block)),
            "triangle_parity_counts": {
                "parity0": triangle_stats["parity0"],
                "parity1": triangle_stats["parity1"],
            },
            "signed_triangle_excess": signed_triangle_excess,
            "trace_s_cubed_equals_six_times_signed_triangle_excess": int(
                np.trace(sign_block @ sign_block @ sign_block)
            )
            == 6 * signed_triangle_excess,
        },
        "bridge_verdict": (
            "The center-quad transport refinement is now an explicit operator, not "
            "just a graph-and-holonomy count package. The unique S3 line-matchings "
            "on transport edges define a canonical 135-dimensional connection "
            "adjacency on the local-line bundle over the exact 45-point transport "
            "graph. Because the permutation representation on three letters splits "
            "as 1+2, this bundle decomposes exactly into a 45-dimensional trivial "
            "sector and a 90-dimensional standard sector. The trivial sector is "
            "exactly the transport graph adjacency with spectrum 32, 2, -4, while "
            "the standard sector has exact spectrum 8, -1, -16. Independently, "
            "the parity of the same edge matchings defines a signed holonomy "
            "operator with exact quadratic identity S^2 = 4S + 32I and spectrum "
            "8, -4, and its cubic trace is exactly six times the signed triangle "
            "excess 3120 - 2160 from the holonomy theorem."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_center_quad_transport_operator_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
