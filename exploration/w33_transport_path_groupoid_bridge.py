"""Exact path-groupoid / local-system bridge for center-quad transport.

The transport graph already carries exact local Weyl(A2) data on every edge.
This module promotes that edge data to the right categorical object:

1. a representation of the path groupoid of the 45-point transport graph;
2. a spanning-tree gauge in which all tree edges become identity and the full
   nontrivial content sits on fundamental cycles;
3. a coefficient-sensitive comparison of the same local system over Z and F3.

The last point is the key new structural fact. Over characteristic 0 the A2
local system has no nonzero flat section. But after reduction mod 3, the same
nonabelian local system acquires a unique invariant line. This is the first
exact place where the special field F3 changes the transport side itself, not
just the W33 homology side.
"""

from __future__ import annotations

from collections import Counter, deque
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from w33_center_quad_transport_a2_bridge import a2_weyl_matrix
from w33_center_quad_transport_bridge import reconstructed_quotient_graph
from w33_center_quad_transport_holonomy_bridge import (
    edge_line_matching,
    permutation_inverse,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_path_groupoid_bridge_summary.json"
MODULUS = 3
IDENTITY_2 = np.eye(2, dtype=int)


def _matrix_key(matrix: np.ndarray) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(entry) for entry in row) for row in matrix.tolist())


def _matrix_inverse(matrix: np.ndarray) -> np.ndarray:
    determinant = int(round(float(np.linalg.det(matrix))))
    if determinant not in {-1, 1}:
        raise AssertionError("expected Weyl(A2) matrix to have determinant +/-1")
    adjugate = np.array(
        [[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]],
        dtype=int,
    )
    return determinant * adjugate


def directed_a2_edge_matrix(left: int, right: int) -> np.ndarray:
    if left < right:
        permutation = edge_line_matching(left, right)
    else:
        permutation = permutation_inverse(edge_line_matching(right, left))
    return a2_weyl_matrix(permutation)


def path_transport(path: tuple[int, ...]) -> np.ndarray:
    if len(path) < 2:
        return IDENTITY_2.copy()
    transport = IDENTITY_2.copy()
    for left, right in zip(path, path[1:]):
        transport = directed_a2_edge_matrix(left, right) @ transport
    return transport


def _spanning_tree_parent_map(root: int = 0) -> dict[int, int | None]:
    graph, _ = reconstructed_quotient_graph()
    parent: dict[int, int | None] = {root: None}
    queue = deque([root])
    while queue:
        left = queue.popleft()
        for right in sorted(graph.neighbors(left)):
            if right in parent:
                continue
            parent[right] = left
            queue.append(right)
    if len(parent) != graph.number_of_nodes():
        raise AssertionError("transport graph should be connected")
    return parent


def _tree_path(root: int, target: int, parent: dict[int, int | None]) -> tuple[int, ...]:
    path = [target]
    current = target
    while current != root:
        parent_vertex = parent[current]
        if parent_vertex is None:
            raise AssertionError("broken parent map")
        path.append(parent_vertex)
        current = parent_vertex
    path.reverse()
    return tuple(path)


@lru_cache(maxsize=1)
def spanning_tree_gauge(root: int = 0) -> dict[int, np.ndarray]:
    parent = _spanning_tree_parent_map(root)
    gauge: dict[int, np.ndarray] = {}
    for vertex in parent:
        gauge[vertex] = path_transport(_tree_path(root, vertex, parent))
    return gauge


def gauge_fixed_edge_matrix(left: int, right: int, root: int = 0) -> np.ndarray:
    gauge = spanning_tree_gauge(root)
    return (
        _matrix_inverse(gauge[right])
        @ directed_a2_edge_matrix(left, right)
        @ gauge[left]
    )


def _tree_edges(parent: dict[int, int | None]) -> set[tuple[int, int]]:
    return {
        (min(vertex, parent_vertex), max(vertex, parent_vertex))
        for vertex, parent_vertex in parent.items()
        if parent_vertex is not None
    }


def _group_closure_matrices(matrices: list[np.ndarray]) -> list[np.ndarray]:
    closure = {_matrix_key(IDENTITY_2): IDENTITY_2.copy()}
    frontier = [_matrix_key(matrix) for matrix in matrices]
    for matrix in matrices:
        closure[_matrix_key(matrix)] = matrix.copy()
    changed = True
    while changed:
        changed = False
        snapshot = list(closure.values())
        for left in snapshot:
            for right in snapshot:
                product = left @ right
                key = _matrix_key(product)
                if key not in closure:
                    closure[key] = product
                    changed = True
    return [closure[key] for key in sorted(closure)]


def _rank_mod_p(matrix: np.ndarray, modulus: int = MODULUS) -> int:
    reduced = np.array(matrix, dtype=int) % modulus
    rows, cols = reduced.shape
    rank = 0
    for column in range(cols):
        pivot = None
        for row in range(rank, rows):
            if reduced[row, column] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
        pivot_value = int(reduced[rank, column])
        inverse = 1 if pivot_value == 1 else 2
        reduced[rank, :] = (inverse * reduced[rank, :]) % modulus
        for row in range(rows):
            if row != rank and reduced[row, column] % modulus:
                reduced[row, :] = (
                    reduced[row, :] - reduced[row, column] * reduced[rank, :]
                ) % modulus
        rank += 1
        if rank == rows:
            break
    return rank


def _normalized_projective_line(vector: np.ndarray) -> tuple[int, int]:
    reduced = np.array(vector, dtype=int) % MODULUS
    if np.all(reduced == 0):
        raise AssertionError("expected nonzero vector")
    for entry in reduced:
        if entry != 0:
            inverse = 1 if entry == 1 else 2
            normalized = (inverse * reduced) % MODULUS
            return int(normalized[0]), int(normalized[1])
    raise AssertionError("unreachable")


def _f3_invariant_line(matrices: list[np.ndarray]) -> tuple[int, int]:
    invariant_lines = set()
    for x in range(MODULUS):
        for y in range(MODULUS):
            if x == y == 0:
                continue
            vector = np.array([x, y], dtype=int)
            if all(np.array_equal((matrix @ vector) % MODULUS, vector) for matrix in matrices):
                invariant_lines.add(_normalized_projective_line(vector))
    if len(invariant_lines) != 1:
        raise AssertionError("expected a unique invariant projective line over F3")
    return next(iter(invariant_lines))


def _adapted_basis(line_vector: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    invariant = np.array(line_vector, dtype=int) % MODULUS
    for x in range(MODULUS):
        for y in range(MODULUS):
            candidate = np.array([x, y], dtype=int)
            matrix = np.column_stack([invariant, candidate]) % MODULUS
            determinant = int(round(float(np.linalg.det(matrix)))) % MODULUS
            if determinant != 0:
                inverse = np.array(
                    [
                        [matrix[1, 1], -matrix[0, 1]],
                        [-matrix[1, 0], matrix[0, 0]],
                    ],
                    dtype=int,
                )
                inverse = (pow(determinant, -1, MODULUS) * inverse) % MODULUS
                return matrix, inverse
    raise AssertionError("expected to find an adapted basis")


@lru_cache(maxsize=1)
def build_transport_path_groupoid_summary() -> dict[str, Any]:
    graph, _ = reconstructed_quotient_graph()
    root = 0
    parent = _spanning_tree_parent_map(root)
    tree_edges = _tree_edges(parent)

    gauge_fixed_non_tree = []
    tree_identity_ok = True
    for left, right in sorted(graph.edges()):
        forward = gauge_fixed_edge_matrix(left, right, root)
        backward = gauge_fixed_edge_matrix(right, left, root)
        if (left, right) in tree_edges:
            tree_identity_ok &= np.array_equal(forward, IDENTITY_2)
            tree_identity_ok &= np.array_equal(backward, IDENTITY_2)
        else:
            gauge_fixed_non_tree.extend([forward, backward])

    holonomy_group = _group_closure_matrices(gauge_fixed_non_tree)
    real_constraint = np.vstack([matrix - IDENTITY_2 for matrix in holonomy_group])
    real_fixed_dimension = 2 - int(np.linalg.matrix_rank(real_constraint.astype(float)))

    reduced_group = [matrix % MODULUS for matrix in holonomy_group]
    f3_constraint = np.vstack([matrix - IDENTITY_2 for matrix in reduced_group]) % MODULUS
    f3_fixed_dimension = 2 - _rank_mod_p(f3_constraint)
    invariant_line = _f3_invariant_line(reduced_group)
    basis, basis_inverse = _adapted_basis(invariant_line)
    adapted = [(basis_inverse @ matrix @ basis) % MODULUS for matrix in reduced_group]
    quotient_character_values = sorted(
        {
            int(matrix[1, 1])
            for matrix in adapted
        }
    )

    first_neighbor = min(graph.neighbors(root))
    sample_path = (root, first_neighbor, root)
    sample_inverse = tuple(reversed(sample_path))

    return {
        "status": "ok",
        "path_groupoid": {
            "objects": graph.number_of_nodes(),
            "undirected_generating_edges": graph.number_of_edges(),
            "directed_generating_morphisms": 2 * graph.number_of_edges(),
            "sample_closed_path": list(sample_path),
            "sample_path_transport": [list(row) for row in path_transport(sample_path)],
            "sample_inverse_transport": [list(row) for row in path_transport(sample_inverse)],
            "path_transport_respects_inversion": np.array_equal(
                path_transport(sample_inverse),
                _matrix_inverse(path_transport(sample_path)),
            ),
        },
        "spanning_tree_gauge": {
            "root_vertex": root,
            "tree_edges": len(tree_edges),
            "fundamental_cycles": graph.number_of_edges() - len(tree_edges),
            "all_tree_edges_gauge_trivialized": tree_identity_ok,
            "fundamental_cycle_holonomy_group_order": len(holonomy_group),
            "fundamental_cycle_holonomies_realize_full_weyl_a2": len(holonomy_group) == 6,
        },
        "real_local_system": {
            "common_fixed_subspace_dimension": real_fixed_dimension,
            "has_nonzero_flat_section": real_fixed_dimension > 0,
        },
        "ternary_reduction": {
            "modulus": MODULUS,
            "common_fixed_subspace_dimension": f3_fixed_dimension,
            "unique_invariant_projective_line": list(invariant_line),
            "adapted_basis": [list(row) for row in basis],
            "adapted_group_is_upper_triangular": all(int(matrix[1, 0]) == 0 for matrix in adapted),
            "quotient_character_values": quotient_character_values,
            "quotient_character_is_exact_binary_shadow": quotient_character_values == [1, 2],
        },
        "bridge_verdict": (
            "The quotient transport edge data is now promoted to the correct "
            "categorical object: a path-groupoid representation into Weyl(A2). "
            "A spanning-tree gauge trivializes every tree edge, so the entire "
            "nontrivial content reduces to fundamental-cycle holonomy, and those "
            "cycle holonomies generate the full Weyl(A2) group exactly. Over Z "
            "this local system has no nonzero flat section. But after reduction "
            "mod 3 the same nonabelian local system acquires a unique invariant "
            "line, and the quotient line carries the exact {1,2} binary shadow. "
            "So q = 3 is not only the natural coefficient field for W33 homology; "
            "it is also the first field on which the transport holonomy itself "
            "develops a canonical flat one-dimensional shadow."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_path_groupoid_summary(), indent=2, default=int),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
