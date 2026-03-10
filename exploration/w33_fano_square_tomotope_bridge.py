"""Canonical square induced by a Fano flag and its tomotope interpretation.

This module sharpens the D8 bridge. A Fano flag (p, L) determines:

- 4 points off the chosen line L;
- for each q in L, a perfect matching on those 4 off-line points by joining
  pairs whose connecting line meets L at q.

These are the 3 perfect matchings of K4. The matching attached to the fixed
point p becomes the diagonal pairing, and the other 2 matchings become the
2 edge-color classes of a square. Therefore:

- a Fano flag canonically determines a square on 4 vertices;
- the Fano flag stabilizer of order 8 is exactly the automorphism group of that
  square;
- this supplies a direct local model for the 4 triangles around a tomotope edge.

The resulting count bridge is:

    192 = 12 x (4 x 2 x 2) = 24 x 8,

with the order-8 factor now interpreted as the square symmetry of the flag-
induced local 4-cycle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_fano_group_bridge import (
    Matrix,
    apply_matrix_to_line,
    dihedral_square_permutations,
    fano_flags,
    fano_lines,
    fano_points,
    flag_stabilizer,
    mat_vec_mul,
    off_line_points,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_fano_square_tomotope_bridge_summary.json"

Vector = tuple[int, int, int]
Matching = tuple[tuple[Vector, Vector], tuple[Vector, Vector]]
Edge = tuple[Vector, Vector]


@dataclass(frozen=True)
class FanoSquareSummary:
    off_line_point_count: int
    fixed_point_matching_size: int
    square_edge_count: int
    square_automorphism_group_order: int
    flag_stabilizer_order: int
    local_tomotope_triangle_count: int
    local_tomotope_flags_per_edge: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalized_edge(left: Vector, right: Vector) -> Edge:
    return tuple(sorted((left, right)))


def line_through(point_a: Vector, point_b: Vector) -> tuple[Vector, Vector, Vector]:
    if point_a == point_b:
        raise ValueError("points must be distinct")
    target = tuple(sorted((point_a, point_b, (point_a[0] ^ point_b[0], point_a[1] ^ point_b[1], point_a[2] ^ point_b[2]))))
    if target not in fano_lines():
        raise ValueError("line not found in Fano plane")
    return target


def matching_via_line_point(flag_point: Vector, flag_line: tuple[Vector, Vector, Vector], target_point_on_line: Vector) -> Matching:
    """Perfect matching on the 4 off-line points by line intersection with flag_line."""

    if target_point_on_line not in flag_line:
        raise ValueError("target_point_on_line must lie on flag_line")
    remaining = list(off_line_points(flag_line))
    pairs: list[tuple[Vector, Vector]] = []
    while remaining:
        point = remaining.pop(0)
        partner_index = None
        for index, candidate in enumerate(remaining):
            if target_point_on_line in line_through(point, candidate):
                partner_index = index
                break
        if partner_index is None:
            raise ValueError("matching partner not found")
        partner = remaining.pop(partner_index)
        pairs.append(normalized_edge(point, partner))
    return tuple(sorted(pairs))


def all_flag_line_matchings(flag_point: Vector, flag_line: tuple[Vector, Vector, Vector]) -> dict[Vector, Matching]:
    return {
        point_on_line: matching_via_line_point(flag_point, flag_line, point_on_line)
        for point_on_line in flag_line
    }


def canonical_square_edges(flag_point: Vector, flag_line: tuple[Vector, Vector, Vector]) -> tuple[Edge, ...]:
    matchings = all_flag_line_matchings(flag_point, flag_line)
    edges = []
    for point_on_line in flag_line:
        if point_on_line == flag_point:
            continue
        edges.extend(matchings[point_on_line])
    return tuple(sorted(edges))


def diagonal_matching(flag_point: Vector, flag_line: tuple[Vector, Vector, Vector]) -> Matching:
    return matching_via_line_point(flag_point, flag_line, flag_point)


def induced_flag_stabilizer_square_permutations(
    flag_point: Vector,
    flag_line: tuple[Vector, Vector, Vector],
) -> tuple[tuple[int, ...], ...]:
    points = off_line_points(flag_line)
    index = {candidate: i for i, candidate in enumerate(points)}
    perms = set()
    for matrix in flag_stabilizer(flag_point, flag_line):
        perm = tuple(index[mat_vec_mul(matrix, candidate)] for candidate in points)
        perms.add(perm)
    return tuple(sorted(perms))


def preserves_square_edges(
    matrix: Matrix,
    flag_point: Vector,
    flag_line: tuple[Vector, Vector, Vector],
) -> bool:
    edges = set(canonical_square_edges(flag_point, flag_line))
    moved_edges = {
        normalized_edge(mat_vec_mul(matrix, left), mat_vec_mul(matrix, right))
        for left, right in edges
    }
    return moved_edges == edges


def local_tomotope_edge_flag_count() -> int:
    return 4 * 2 * 2


def build_fano_square_tomotope_summary() -> dict[str, Any]:
    flag_point, flag_line = fano_flags()[0]
    off_points = off_line_points(flag_line)
    diagonal = diagonal_matching(flag_point, flag_line)
    square_edges = canonical_square_edges(flag_point, flag_line)
    stabilizer = flag_stabilizer(flag_point, flag_line)
    summary = FanoSquareSummary(
        off_line_point_count=len(off_points),
        fixed_point_matching_size=len(diagonal),
        square_edge_count=len(square_edges),
        square_automorphism_group_order=len(dihedral_square_permutations()),
        flag_stabilizer_order=len(stabilizer),
        local_tomotope_triangle_count=4,
        local_tomotope_flags_per_edge=local_tomotope_edge_flag_count(),
    )
    return {
        "status": "ok",
        "summary": summary.to_dict(),
        "chosen_flag": {
            "point": flag_point,
            "line": flag_line,
        },
        "off_line_points": off_points,
        "perfect_matchings_by_line_point": {
            str(point_on_line): matching
            for point_on_line, matching in all_flag_line_matchings(flag_point, flag_line).items()
        },
        "diagonal_matching": diagonal,
        "canonical_square_edges": square_edges,
        "stabilizer_checks": {
            "flag_stabilizer_order_is_8": len(stabilizer) == 8,
            "induced_permutations_are_d8": (
                induced_flag_stabilizer_square_permutations(flag_point, flag_line) == dihedral_square_permutations()
            ),
            "every_stabilizer_element_preserves_square_edges": all(
                preserves_square_edges(matrix, flag_point, flag_line) for matrix in stabilizer
            ),
        },
        "tomotope_local_bridge": {
            "triangles_around_edge": 4,
            "endpoint_choices": 2,
            "cell_choices_per_edge_triangle": 2,
            "flags_around_edge": local_tomotope_edge_flag_count(),
            "note": (
                "The 4 off-line Fano points form a canonical square attached to a "
                "flag. This square models the 4 triangles around a tomotope edge; "
                "adding endpoint and cell choices gives the 16 local edge flags."
            ),
        },
        "bridge_verdict": (
            "The order-8 factor in 192 = 24 x 8 is not merely abstract. A Fano flag "
            "canonically produces a 4-cycle, and its stabilizer is the full square "
            "symmetry group D8. This gives an explicit local square model for the "
            "tomotope edge star."
        ),
        "scope_note": (
            "This is still a local model. It does not yet glue the 12 local edge "
            "squares into the full tomotope incidence complex."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_fano_square_tomotope_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
