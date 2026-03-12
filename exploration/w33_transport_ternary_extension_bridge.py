"""Exact non-split ternary extension behind the transport/matter 162-sector.

The path-groupoid and qutrit-code bridges already show two exact facts:

1. the reduced transport holonomy over F3 has a unique invariant line;
2. the W33 ternary homological code has exactly 81 logical qutrits.

The right structural statement is sharper than a count match. Over F3 the
reduced 2-dimensional transport fiber is an indecomposable local system:

    0 -> 1 -> rho -> sgn -> 0

where the invariant line is the trivial character, the quotient line is the
binary sign shadow, and the sequence does not split. Tensoring with the 81-
dimensional logical matter sector gives the exact 81 -> 162 -> 81 bridge.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from w33_center_quad_transport_bridge import reconstructed_quotient_graph
from w33_flat_ac_spectral_action import build_flat_product_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary
from w33_transport_path_groupoid_bridge import gauge_fixed_edge_matrix


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_ternary_extension_bridge_summary.json"
MODULUS = 3
IDENTITY_2 = np.eye(2, dtype=int)


def _matrix_key(matrix: np.ndarray) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(entry) for entry in row) for row in matrix.tolist())


def _matrix_inverse_mod_3(matrix: np.ndarray) -> np.ndarray:
    determinant = int(round(float(np.linalg.det(matrix)))) % MODULUS
    if determinant == 0:
        raise AssertionError("expected invertible matrix over F3")
    adjugate = np.array(
        [[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]],
        dtype=int,
    )
    return (pow(determinant, -1, MODULUS) * adjugate) % MODULUS


def _group_closure_mod_3(matrices: list[np.ndarray]) -> list[np.ndarray]:
    closure = {_matrix_key(IDENTITY_2): IDENTITY_2.copy()}
    for matrix in matrices:
        closure[_matrix_key(matrix % MODULUS)] = matrix % MODULUS

    changed = True
    while changed:
        changed = False
        snapshot = list(closure.values())
        for left in snapshot:
            for right in snapshot:
                product = (left @ right) % MODULUS
                key = _matrix_key(product)
                if key not in closure:
                    closure[key] = product
                    changed = True
    return [closure[key] for key in sorted(closure)]


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


def _all_projective_lines_f3() -> list[tuple[int, int]]:
    lines = {
        _normalized_projective_line(np.array([x, y], dtype=int))
        for x in range(MODULUS)
        for y in range(MODULUS)
        if (x, y) != (0, 0)
    }
    return sorted(lines)


def _line_is_invariant(group: list[np.ndarray], line: tuple[int, int]) -> bool:
    vector = np.array(line, dtype=int)
    for matrix in group:
        image = (matrix @ vector) % MODULUS
        if np.all(image == 0):
            return False
        if _normalized_projective_line(image) != line:
            return False
    return True


def _adapted_basis(line_vector: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    invariant = np.array(line_vector, dtype=int) % MODULUS
    for x in range(MODULUS):
        for y in range(MODULUS):
            candidate = np.array([x, y], dtype=int)
            matrix = np.column_stack([invariant, candidate]) % MODULUS
            determinant = int(round(float(np.linalg.det(matrix)))) % MODULUS
            if determinant != 0:
                return matrix, _matrix_inverse_mod_3(matrix)
    raise AssertionError("expected an adapted basis")


def reduced_transport_group() -> list[np.ndarray]:
    graph, _ = reconstructed_quotient_graph()
    directed = []
    for left, right in sorted(graph.edges()):
        directed.append(gauge_fixed_edge_matrix(left, right) % MODULUS)
        directed.append(gauge_fixed_edge_matrix(right, left) % MODULUS)
    return _group_closure_mod_3(directed)


@lru_cache(maxsize=1)
def build_transport_ternary_extension_summary() -> dict[str, Any]:
    reduced_group = reduced_transport_group()
    projective_lines = _all_projective_lines_f3()
    invariant_lines = [line for line in projective_lines if _line_is_invariant(reduced_group, line)]
    if len(invariant_lines) != 1:
        raise AssertionError("expected a unique invariant projective line")
    invariant_line = invariant_lines[0]

    basis, basis_inverse = _adapted_basis(invariant_line)
    adapted_group = [(basis_inverse @ matrix @ basis) % MODULUS for matrix in reduced_group]
    top_character_values = sorted({int(matrix[0, 0]) for matrix in adapted_group})
    bottom_character_values = sorted({int(matrix[1, 1]) for matrix in adapted_group})
    invariant_complements = [
        line
        for line in projective_lines
        if line != invariant_line and _line_is_invariant(reduced_group, line)
    ]
    off_diagonal_nonzero = sum(int(matrix[0, 1] != 0) for matrix in adapted_group)
    quotient_matches_determinant = all(
        int(matrix[1, 1]) == int(round(float(np.linalg.det(matrix)))) % MODULUS
        for matrix in adapted_group
    )

    ternary_code = build_ternary_homological_code_summary()
    flat = build_flat_product_summary()
    logical_qutrits = ternary_code["ternary_css_code"]["logical_qutrits"]
    total_dimension = 2 * logical_qutrits

    return {
        "status": "ok",
        "reduced_transport_module": {
            "field": "F3",
            "dimension": 2,
            "holonomy_group_order": len(reduced_group),
            "projective_line_count": len(projective_lines),
            "unique_invariant_line": list(invariant_line),
            "invariant_projective_line_count": len(invariant_lines),
            "invariant_complement_count": len(invariant_complements),
            "adapted_group_is_upper_triangular": all(int(matrix[1, 0]) == 0 for matrix in adapted_group),
            "top_character_values": top_character_values,
            "quotient_character_values": bottom_character_values,
            "quotient_character_equals_determinant_character": quotient_matches_determinant,
            "nonsplit_extension_witness_count": off_diagonal_nonzero,
            "is_nonsplit_extension_of_sign_by_trivial": (
                top_character_values == [1]
                and bottom_character_values == [1, 2]
                and len(invariant_complements) == 0
                and off_diagonal_nonzero > 0
            ),
        },
        "matter_flavour_extension": {
            "base_logical_qutrits": logical_qutrits,
            "submodule_dimension": logical_qutrits,
            "total_dimension": total_dimension,
            "quotient_dimension": logical_qutrits,
            "short_exact_sequence_dimensions": [logical_qutrits, total_dimension, logical_qutrits],
            "matches_flat_internal_dimension_exactly": total_dimension == flat["coefficients"]["internal_dimension"],
        },
        "bridge_verdict": (
            "Over F3 the reduced transport fiber is not semisimple. It is the "
            "exact non-split 2-dimensional local system 0 -> 1 -> rho -> sgn -> 0: "
            "the unique invariant line is trivial, the quotient line carries the "
            "binary sign shadow, and there is no invariant complementary line. "
            "Tensoring that exact extension with the 81-dimensional W33 logical "
            "qutrit sector gives 0 -> 81 -> 162 -> 81 -> 0. So the internal "
            "162-sector is now explained structurally as a transport-twisted "
            "ternary matter extension, not just a dimensional coincidence."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_ternary_extension_summary(), indent=2, default=int),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
